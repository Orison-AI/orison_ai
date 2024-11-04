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
import logging
import asyncio
from langchain_community.document_loaders import (
    PyPDFLoader,
    CSVLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    UnstructuredHTMLLoader,
    JSONLoader,
)
from langchain_community.document_loaders.powerpoint import UnstructuredPowerPointLoader
from langchain_community.document_loaders.word_document import (
    UnstructuredWordDocumentLoader,
)
from langchain_community.document_loaders.excel import UnstructuredExcelLoader
from langchain_experimental.text_splitter import SemanticChunker
import numpy as np
from qdrant_client.http import models

# Internal

from request_handler import RequestHandler, OKResponse, ErrorResponse
from or_store.firebase_storage import FirebaseStorage
from or_store.firebase import FireStoreDB
from utils import raise_and_log_error, file_extension
from or_store.firebase import OrisonSecrets
from or_llm.orison_messenger import OrisonMessenger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorizeFiles(RequestHandler):
    orison_messenger = None
    embedding_client = None
    async_db_client = None

    def __init__(self):
        super().__init__(str(self.__class__.__qualname__))

    @staticmethod
    def _orison_messenger(secrets):
        VectorizeFiles.orison_messenger = OrisonMessenger(secrets=secrets)
        VectorizeFiles.embedding_client = VectorizeFiles.orison_messenger._embeddings
        VectorizeFiles.async_db_client = (
            VectorizeFiles.orison_messenger.async_qdrant_client
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
        extension = file_extension(file_path).lower()
        match extension:
            case ".txt":
                # Use TextLoader for text-based files
                loader = TextLoader(file_path)
            case ".json":
                # Use JSONLoader for JSON files
                loader = JSONLoader(file_path)
            case ".md":
                # Use UnstructuredMarkdownLoader for text-based files
                loader = UnstructuredMarkdownLoader(file_path)
            case ".html":
                # Use UnstructuredHTMLLoader for HTML files
                loader = UnstructuredHTMLLoader(file_path)
            case ".csv":
                # Use CSVLoader for CSV files
                loader = CSVLoader(file_path)
            case ".pdf":
                # Use PyPDFLoader for PDF files
                loader = PyPDFLoader(file_path)
            case ".docx":
                # Use UnstructuredWordDocumentLoader for Word files
                loader = UnstructuredWordDocumentLoader(file_path)
            case ".doc":
                # Use UnstructuredWordDocumentLoader for Word files
                loader = UnstructuredWordDocumentLoader(file_path)
            case ".pptx":
                # Use Uns for UnstructuredPowerPointLoader files
                loader = UnstructuredPowerPointLoader(file_path)
            case ".xls":
                # Use UnstructuredExcelLoader for Excel files
                loader = UnstructuredExcelLoader(file_path)
            case ".xlsx":
                # Use UnstructuredExcelLoader for Excel files
                loader = UnstructuredExcelLoader(file_path)
            case _:
                # Use TextLoader for unknown file types
                loader = TextLoader(file_path)
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
    async def _store_chunks(
        chunks, async_db_client, logger, collection_name, index_data
    ):
        async def process_chunk(chunk, index_data):
            embedding = await VectorizeFiles.embedding_client.aembed_query(
                chunk.page_content
            )
            payload = index_data | {
                "page_content": chunk.page_content,
                "metadata": chunk.metadata,
            }

            return embedding, payload

        # Process each chunk in parallel
        tasks = [process_chunk(chunk, index_data) for chunk in chunks]
        results = await asyncio.gather(*tasks)
        embeddings, payloads = zip(*results)

        # Upload vectors to the vector database
        logger.info("Uploading vectors")
        async_db_client.upload_collection(
            collection_name=collection_name,
            vectors=np.array(embeddings),
            payload=payloads,
            parallel=4,
            ids=None,  # Let Qdrant generate IDs
        )
        logger.info("Uploading vectors....DONE")

    @staticmethod
    async def _vectorize(
        documents,
        tag,
        collection_name,
        filename,
        logger,
    ):
        MIN_TOKEN_SIZE = 144
        async_db_client = VectorizeFiles.async_db_client
        logger.info(
            f"Chunking, indexing, and storing in collection {collection_name}.\nChunker type: {SemanticChunker.__name__}. Collection type: {VectorizeFiles.async_db_client.__class__.__name__}"
        )
        sample_embedding = VectorizeFiles.embedding_client.embed_query(
            "Generate a sample embedding to get the length of the vector"
        )
        # Ensure the collection exists
        collection_exists = await VectorizeFiles.async_db_client.collection_exists(
            collection_name=collection_name
        )
        if not collection_exists:
            await VectorizeFiles.async_db_client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=len(sample_embedding),  # Length of the embedding vectors
                    distance=models.Distance.COSINE,  # Distance metric
                ),
            )
        index_data = {
            "tag": tag.lower(),
            "filename": filename,
        }
        logger.info("Splitting documents")
        text_splitter = SemanticChunker(
            VectorizeFiles.embedding_client,
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=75,
            buffer_size=10,
        )
        chunks = text_splitter.split_documents(documents)
        # Filter chunks based on token size
        filtered_chunks = [
            chunk
            for chunk in chunks
            if OrisonMessenger.number_tokens(chunk.page_content) >= MIN_TOKEN_SIZE
        ]
        logger.info("Splitting documents....DONE")
        logger.info(
            f"Number of chunks: {len(chunks)}. Number of filtered chunks: {len(filtered_chunks)}"
        )
        if len(filtered_chunks) > 0:
            # Store the filtered chunks in the vector DB
            logger.info(f"Storing filtered chunks in vector DB.")
            await VectorizeFiles._store_chunks(
                chunks=filtered_chunks,
                async_db_client=async_db_client,
                logger=logger,
                collection_name=collection_name,
                index_data=index_data,
            )
            logger.info(f"Storing chunks in vector DB....DONE")
        return

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
            tag = request_json["tag"]
            secrets = OrisonSecrets.from_attorney_applicant(attorney_id, applicant_id)
            VectorizeFiles._orison_messenger(secrets)
            self.logger.info(
                f"Processing file for attorney {attorney_id} and applicant {applicant_id}"
            )
            # ToDo: Currently supporting only one file.
            # We should make multiple calls from the frontend instead for scalability
            # Download the file
            bucket_file_path = VectorizeFiles._file_path_builder(
                attorney_id, applicant_id, tag, file_id
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
            await VectorizeFiles._vectorize(
                documents=documents,
                collection_name=secrets.collection_name,
                logger=self.logger,
                tag=tag,
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
    async def _delete_vectors(async_db_client, collection_name, file_name, tag, logger):
        collection_exists = await async_db_client.collection_exists(
            collection_name=collection_name
        )
        if not collection_exists:
            logger.error(
                f"Error deleting vector-files. Collection {collection_name} does not exist"
            )
            return
        points_selector = models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="tag",
                        match=models.MatchValue(value=tag.lower()),
                    ),
                    models.FieldCondition(
                        key="filename",
                        match=models.MatchValue(value=file_name),
                    ),
                ],
            )
        )
        logger.info(
            f"Deleting vectors for file {file_name} in collection {collection_name}"
        )
        await async_db_client.delete(
            collection_name=collection_name, points_selector=points_selector
        )

    async def handle_request(self, request_json):
        try:
            client = FireStoreDB()
            attorney_id = request_json["attorneyId"]
            applicant_id = request_json["applicantId"]
            file_id = request_json["fileId"]
            tag = request_json["tag"]
            secrets = OrisonSecrets.from_attorney_applicant(attorney_id, applicant_id)
            self.logger.info(
                f"Processing delete file vectors for attorney {attorney_id}, applicant {applicant_id}, and file: {file_id}"
            )
            VectorizeFiles._orison_messenger(secrets)
            await DeleteFileVectors._delete_vectors(
                async_db_client=VectorizeFiles.async_db_client,
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
    import time

    start_time = time.time()
    vectorizer = VectorizeFiles()
    secrets = OrisonSecrets.from_attorney_applicant("test_attorney", "test_applicant")
    VectorizeFiles._orison_messenger(secrets)
    current_dir = os.path.dirname(__file__)
    template_file_path = os.path.join(current_dir, "templates", "test_vectorize.txt")
    documents = VectorizeFiles._load_file(
        file_path=template_file_path, logger=logger, filename="test_vectorize.txt"
    )

    async def test_vectorization():
        await VectorizeFiles._vectorize(
            documents=documents,
            collection_name=secrets.collection_name,
            logger=logger,
            tag="test",
            filename="test_vectorize.txt",
        )

        await DeleteFileVectors._delete_vectors(
            async_db_client=VectorizeFiles.async_db_client,
            collection_name=secrets.collection_name,
            file_name="test_vectorize.txt",
            tag="test",
            logger=logger,
        )

        await VectorizeFiles.async_db_client.delete_collection(
            collection_name=secrets.collection_name
        )

    asyncio.run(test_vectorization())
    logger.info(f"Time taken: {time.time() - start_time}")
