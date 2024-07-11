#! /usr/bin/env python3.10

# ==========================================================================
#  Copyright (c) Orison AI, 2024.
#
#  All rights reserved. All hardware and software names used are registered
#  trade names and/or registered trademarks of the respective manufacturers.
#
#  The user of this computer program acknowledges that the above copyright
#  notice, which constitutes the Universal Copyright Convention, will be
#  attached at the position in the function of the computer program which the
#  author has deemed to sufficiently express the reservation of copyright.
#  It is prohibited for customers, users and/or third parties to remove,
#  modify or move this copyright notice.
# ==========================================================================

# External
import os
import asyncio

## File Loader and Embeddings Imports
from langchain_community.document_loaders import (
    PyPDFLoader,
    CSVLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    JSONLoader,
)
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings

# Internal
from request_handler import RequestHandler, OKResponse, ErrorResponse
from or_store.firebase_storage import FirebaseStorage
from or_store.firebase import FireStoreDB
from utils import raise_and_log_error, file_extension
from or_store.firebase import OrisonSecrets
from or_llm.openai_interface import OrisonEmbeddings, EMBEDDING_MODEL, OrisonMessenger

# Vectorization Imports
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models


class VectorizeFiles(RequestHandler):
    embedding_client = None

    def __init__(self):
        super().__init__(str(self.__class__.__qualname__))

    @staticmethod
    def embedding(secrets):
        if not VectorizeFiles.embedding_client:
            VectorizeFiles.embedding_client = OrisonEmbeddings(
                model=EMBEDDING_MODEL,
                api_key=secrets.openai_api_key,
                max_retries=5,
            )

    @staticmethod
    def _file_path_builder(
        attorney_id: str, applicant_id: str, bucket_name: str, file_path: str
    ):
        return os.path.join(
            *[
                "documents",
                "attorneys",
                attorney_id,
                "applicants",
                applicant_id,
                bucket_name,
                file_path,
            ]
        )

    @staticmethod
    async def _download_file(remote_file_path: str, local_file_path: str, logger):
        # Download file from Firebase Storage
        await FirebaseStorage.download_file(
            remote_file_path=remote_file_path, local_file_path=local_file_path
        )
        if os.path.exists(local_file_path):
            logger.debug(f"File written to {local_file_path}")
        else:
            raise_and_log_error(f"Could not download file to {local_file_path}", logger)

    @staticmethod
    def _load_file(file_path: str, logger, filename: str):
        logger.debug(f"Attempting to load file from {file_path}")
        match file_extension(file_path):
            case ".txt":
                # Use TextLoader for text-based files
                loader = TextLoader(file_path)
            case ".json":
                # Use JSONLoader for JSON files
                loader = JSONLoader(file_path)
            case ".md":
                # Use UnstructuredMarkdownLoader for text-based files
                loader = UnstructuredMarkdownLoader(file_path)
            case ".csv":
                # Use CSVLoader for CSV files
                loader = CSVLoader(file_path)
            case ".pdf":
                # Use PyPDFLoader for PDF files
                loader = PyPDFLoader(file_path)
            case _:
                raise_and_log_error(
                    f"Unsupported file format: {file_extension}", logger, ValueError
                )
        # Load the file and return the documents
        # Each document is a dictionary with the keys "page_content" and "metadata"
        # Each document page_content is literally whatever is on that page
        documents = loader.load()
        logger.debug(f"Loaded file from {file_path}")
        # Update metadata filename
        for document in documents:
            document.metadata["source"] = filename
        return documents

    @staticmethod
    def _apply_semantic_splitter(documents, openai_api_key, logger):

        MIN_TOKEN_SIZE = 144

        # Initialize the text splitter
        text_splitter = SemanticChunker(
            OpenAIEmbeddings(model="text-embedding-ada-002", api_key=openai_api_key),
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=75,
            buffer_size=10,
        )
        # Apply the splitter to the document. It will internally call create_documents
        # which will internally call split_text
        # Returns a List[Document]
        # ToDo: Need async here. Make sure source is only file name
        logger.info("Splitting documents")
        chunks = text_splitter.split_documents(documents)
        logger.info("Splitting documents....DONE")
        filtered_chunks = [
            chunk
            for chunk in chunks
            if OrisonMessenger.number_tokens(chunk.page_content) >= MIN_TOKEN_SIZE
        ]
        return filtered_chunks

    @staticmethod
    async def _store_chunks(
        chunks, qdrant_client, logger, tag, collection_name, filename
    ):
        async def process_chunk(chunk, tag):
            embedding = VectorizeFiles.embedding_client.embed_query(chunk.page_content)
            payload = {
                "page_content": chunk.page_content,
                "metadata": chunk.metadata,
                "tag": tag,
                "filename": filename,
            }
            return embedding, payload

        tasks = [process_chunk(chunk, tag) for chunk in chunks]
        results = await asyncio.gather(*tasks)
        embeddings, payloads = zip(*results)

        # Ensure the collection exists
        if not qdrant_client.collection_exists(collection_name=collection_name):
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=len(embeddings[0]),  # Length of the embedding vectors
                    distance=models.Distance.COSINE,  # Distance metric
                ),
            )

        # Upload vectors to Qdrant
        logger.info("Uploading vectors to Qdrant")
        qdrant_client.upload_collection(
            collection_name=collection_name,
            vectors=np.array(embeddings),
            payload=payloads,
            ids=None,  # Let Qdrant generate IDs
        )
        logger.info("Uploading vectors to Qdrant....DONE")

    async def handle_request(self, request_json):
        """
        Handle the request to vectorize the files.
        1. Download the file from Firebase Storage
        2. Load the file
        3. Chunk the file
        4. Store the chunks in Qdrant
        5. Update the applicant document in Firestore

        :param request_json: The request JSON
        :return: OKResponse if successful, ErrorResponse if not
        """
        try:
            client = FireStoreDB()
            attorney_id = request_json["attorneyId"]
            applicant_id = request_json["applicantId"]
            file_id = request_json["fileId"]
            bucket_name = request_json["bucket"]
            tag = bucket_name  # Change to something else if needed
            secrets = OrisonSecrets.from_attorney_applicant(attorney_id, applicant_id)
            self.logger.info(
                f"Processing file for attorney {attorney_id} and applicant {applicant_id}"
            )
            VectorizeFiles.embedding(secrets)

            # ToDo: Currently supporting only one file.
            # We should make multiple calls from the frontend instead for scalability
            # Download the file
            bucket_file_path = VectorizeFiles._file_path_builder(
                attorney_id, applicant_id, bucket_name, file_id
            )
            local_file_path = f"/tmp/to_be_processed.pdf"
            self.logger.info(f"Remote File path: {bucket_file_path}")
            self.logger.info(f"Local File path: {local_file_path}")
            await VectorizeFiles._download_file(
                bucket_file_path, local_file_path, logger=self.logger
            )

            # Load the file
            documents = VectorizeFiles._load_file(
                local_file_path, logger=self.logger, filename=file_id
            )
            # Getting secrets
            qdrant_url = secrets.qdrant_url
            qdrant_api_key = secrets.qdrant_api_key
            openai_api_key = secrets.openai_api_key

            # Chunk the file
            chunks = VectorizeFiles._apply_semantic_splitter(
                documents, openai_api_key=openai_api_key, logger=self.logger
            )

            self.logger.debug(
                f"Storing chunks in Qdrant in collection {secrets.collection_name}"
            )
            await VectorizeFiles._store_chunks(
                chunks,
                qdrant_client=QdrantClient(url=qdrant_url, api_key=qdrant_api_key),
                logger=self.logger,
                tag=tag,
                collection_name=secrets.collection_name,
                filename=file_id,
            )
            await client.update_collection_document(
                collection_name="applicants",
                document_name=applicant_id,
                field="vectorized_files",
                value=file_id,
            )
        except Exception as e:
            self.logger.error(f"Error processing files: {e}")
            return ErrorResponse(str(e))
        return OKResponse("Success!")


class DeleteFileVectors(RequestHandler):
    def __init__(self):
        super().__init__(str(self.__class__.__qualname__))

    @staticmethod
    async def _delete_vectors(qdrant_client, collection_name, file_name, tag, logger):
        if not qdrant_client.collection_exists(collection_name=collection_name):
            logger.error(
                f"Error deleting vector-files. Collection {collection_name} does not exist"
            )
            return
        points_selector = models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="tag",
                        match=models.MatchValue(value=tag),
                    ),
                    models.FieldCondition(
                        key="filename",
                        match=models.MatchValue(value=file_name),
                    ),
                ],
            )
        )
        qdrant_client.delete(
            collection_name=collection_name, points_selector=points_selector
        )

    async def handle_request(self, request_json):
        try:
            client = FireStoreDB()
            attorney_id = request_json["attorneyId"]
            applicant_id = request_json["applicantId"]
            file_id = request_json["fileId"]
            bucket_name = request_json["bucket"]
            tag = bucket_name  # Change to something else if needed
            secrets = OrisonSecrets.from_attorney_applicant(attorney_id, applicant_id)
            self.logger.info(
                f"Processing delete file vectors for attorney {attorney_id}, applicant {applicant_id}, and file: {file_id}"
            )
            await DeleteFileVectors._delete_vectors(
                qdrant_client=QdrantClient(
                    url=secrets.qdrant_url, api_key=secrets.qdrant_api_key
                ),
                collection_name=secrets.collection_name,
                file_name=file_id,
                tag=tag,
                logger=self.logger,
            )
            await client.remove_value_from_field(
                collection_name="applicants",
                document_name=applicant_id,
                field="vectorized_files",
                value=file_id,
            )
        except Exception as e:
            self.logger.error(f"Error deleting file vectors: {e}")
            return ErrorResponse(str(e))

        return OKResponse("Success!")


if __name__ == "__main__":
    request_json = {
        "attorneyId": "xlMsyQpatdNCTvgRfW4TcysSDgX2",
        "applicantId": "tYdtBdc7lJHyVCxquubj",
        "fileId": "MalhanCV.pdf",
        "bucket_name": "research",
    }
    vectorizer = VectorizeFiles()
    asyncio.run(vectorizer.handle_request(request_json))
