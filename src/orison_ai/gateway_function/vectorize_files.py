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
from concurrent.futures import ThreadPoolExecutor
from langchain_community.document_loaders.powerpoint import UnstructuredPowerPointLoader
from langchain_community.document_loaders.word_document import (
    UnstructuredWordDocumentLoader,
)
from langchain_community.document_loaders.xml import UnstructuredXMLLoader
from langchain_community.document_loaders.excel import UnstructuredExcelLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain.text_splitter import RecursiveCharacterTextSplitter
import numpy as np
from qdrant_client.http import models
import nltk

nltk.data.path.append(os.path.join(os.path.dirname(__file__), "nltk_data"))

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
    MIN_TOKEN_SIZE = 144
    CHUNK_SIZE = 512
    CHUNK_OVERLAP = 50

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
            case ".docs":
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
            case ".xml":
                # Use UnstructuredXMLLoader for XML files
                loader = UnstructuredXMLLoader(file_path)
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
            # Asynchronously embed and prepare payload
            embedding = await VectorizeFiles.embedding_client.aembed_query(
                chunk["content"]
            )
            payload = index_data | {
                "page_content": chunk["content"],
                "metadata": chunk["metadata"],
            }
            return embedding, payload

        # Process chunks concurrently
        tasks = [process_chunk(chunk, index_data) for chunk in chunks]
        results = await asyncio.gather(*tasks)

        embeddings, payloads = zip(*results)

        # Upload vectors to vector database
        logger.info("Uploading vectors")
        async_db_client.upload_collection(
            collection_name=collection_name,
            vectors=np.array(embeddings),
            payload=payloads,
            parallel=1,
            ids=None,  # Generate IDs automatically
        )
        logger.info("Uploading vectors....DONE")

    @staticmethod
    async def _vectorize(documents, tag, collection_name, filename, logger):
        async_db_client = VectorizeFiles.async_db_client
        embedding_client = VectorizeFiles.embedding_client

        # Ensure the vector DB collection exists
        sample_embedding = embedding_client.embed_query("Sample for vector size")
        collection_exists = await async_db_client.collection_exists(
            collection_name=collection_name
        )
        if not collection_exists:
            await async_db_client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=len(sample_embedding),
                    distance=models.Distance.COSINE,
                ),
            )

        index_data = {"tag": tag.lower(), "filename": filename}

        # Use LangChain's RecursiveCharacterTextSplitter
        logger.info(f"Splitting documents. Length of documents: {len(documents)}")
        import time

        start = time.time()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=VectorizeFiles.CHUNK_SIZE,
            chunk_overlap=VectorizeFiles.CHUNK_OVERLAP,
        )

        # Offload document processing to ThreadPoolExecutor
        def process_document(doc, index):
            # Split document into chunks
            chunks = text_splitter.split_text(doc.page_content)
            # Add metadata to each chunk
            enriched_chunks = [
                {"content": chunk, "metadata": {"source": filename, "page": index}}
                for chunk in chunks
            ]
            return enriched_chunks

        with ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(executor, process_document, doc, idx)
                for idx, doc in enumerate(documents)
            ]
            results = await asyncio.gather(*tasks)

        logger.info(f"Time taken to split documents: {time.time() - start}")
        start = time.time()

        # Flatten the list of enriched chunks
        all_chunks = [chunk for result in results for chunk in result]

        # Merge smaller chunks to meet token size requirements
        logger.info("Merging smaller chunks")
        merged_chunks = []
        current_chunk = None

        for chunk in all_chunks:
            token_count = OrisonMessenger.number_tokens(chunk["content"])
            if current_chunk is None:
                current_chunk = chunk
            elif (
                token_count + OrisonMessenger.number_tokens(current_chunk["content"])
                <= VectorizeFiles.CHUNK_SIZE
            ):
                current_chunk["content"] += " " + chunk["content"]
                current_chunk["metadata"][
                    "source"
                ] += f", {chunk['metadata']['source']}"
            else:
                merged_chunks.append(current_chunk)
                current_chunk = chunk

        if current_chunk:
            merged_chunks.append(current_chunk)

        # Filter out chunks below the minimum token size
        filtered_chunks = [
            chunk
            for chunk in merged_chunks
            if OrisonMessenger.number_tokens(chunk["content"])
            >= VectorizeFiles.MIN_TOKEN_SIZE
        ]
        logger.info(f"Time taken to merge chunks: {time.time() - start}")
        start = time.time()
        logger.info("Splitting documents....DONE")

        if filtered_chunks:
            logger.info(f"Storing {len(filtered_chunks)} filtered chunks in vector DB.")
            await VectorizeFiles._store_chunks(
                chunks=filtered_chunks,
                async_db_client=async_db_client,
                logger=logger,
                collection_name=collection_name,
                index_data=index_data,
            )
            logger.info(f"Time taken to store chunks: {time.time() - start}")
            logger.info("Storing chunks in vector DB....DONE")

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
            await client.update_collection_document(
                collection_name="applicants",
                document_name=applicant_id,
                field="vectorize_in_progress",
                value=file_id,
            )
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
            local_file_path = (
                f"/tmp/to_be_processed" + file_extension(bucket_file_path).lower()
            )
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
        finally:
            await client.remove_value_from_field(
                collection_name="applicants",
                document_name=applicant_id,
                field="vectorize_in_progress",
                value=file_id,
            )
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
