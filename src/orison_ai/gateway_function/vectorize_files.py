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
from or_store.firebase import build_secret_url, read_remote_secret_url_as_string
from request_handler import RequestHandler, OKResponse, ErrorResponse
from or_store.firebase_storage import FirebaseStorage
from utils import raise_and_log_error, file_extension
from or_store.firebase import OrisonSecrets

# Vectorization Imports
import numpy as np
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.http import models


class VectorizeFiles(RequestHandler):
    def __init__(self):
        super().__init__(str(self.__class__.__qualname__))

    @staticmethod
    def _file_path_builder(
        attorney_id: str, applicant_id: str, bucketName: str, file_path: str
    ):
        return os.path.join(
            *[
                "documents",
                "attorneys",
                attorney_id,
                "applicants",
                applicant_id,
                bucketName,
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
    def _load_file(file_path: str, logger):
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
        return documents

    @staticmethod
    def _apply_semantic_splitter(documents, openai_api_key, logger):

        MIN_CHUNK_SIZE = 256

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
        chunks = text_splitter.split_documents(documents)
        filtered_chunks = [
            chunk for chunk in chunks if len(chunk.page_content) >= MIN_CHUNK_SIZE
        ]
        return filtered_chunks

    @staticmethod
    def _get_openai_embedding(text, openaiClient):
        response = openaiClient.embeddings.create(
            input=[text], model="text-embedding-ada-002"
        )  # Use the appropriate OpenAI model)
        return response.data[0].embedding

    @staticmethod
    def _store_chunks(
        chunks, openai_client, qdrant_client, logger, tag, collection_name
    ):
        embeddings = [
            VectorizeFiles._get_openai_embedding(chunk.page_content, openai_client)
            for chunk in chunks
        ]
        payloads = [
            {"page_content": chunk.page_content, "metadata": chunk.metadata, "tag": tag}
            for chunk in chunks
        ]

        # Ensure the collection exists
        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=len(embeddings[0]),  # Length of the embedding vectors
                distance=models.Distance.COSINE,  # Distance metric
            ),
        )

        # Upload vectors to Qdrant
        qdrant_client.upload_collection(
            collection_name=collection_name,
            vectors=np.array(embeddings),
            payload=payloads,
            ids=None,  # Let Qdrant generate IDs
        )

    async def handle_request(self, request_json):
        try:
            attorney_id = request_json["attorneyId"]
            applicant_id = request_json["applicantId"]
            file_ids = request_json["fileIds"]
            bucketName = "research"  # Hardcoding for now
            tag = bucketName
            # bucketName = request_json["bucketName"]
            # tag = request_json["tag"]
            if len(file_ids) != 1:
                raise ValueError("Only one file per request is supported ATM")

            secrets = OrisonSecrets.from_attorney_applicant(attorney_id, applicant_id)
            self.logger.debug(
                f"Processing file for attorney {attorney_id} and applicant {applicant_id}"
            )

            # Download the file
            bucket_file_path = VectorizeFiles._file_path_builder(
                attorney_id, applicant_id, bucketName, file_ids[0]
            )
            local_file_path = f"/tmp/to_be_processed" + file_extension(bucket_file_path)
            self.logger.debug(f"Remote File path: {bucket_file_path}")
            self.logger.debug(f"Local File path: {local_file_path}")
            await VectorizeFiles._download_file(
                bucket_file_path, local_file_path, logger=self.logger
            )

            # Load the file
            documents = VectorizeFiles._load_file(local_file_path, logger=self.logger)
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
            VectorizeFiles._store_chunks(
                chunks,
                openai_client=OpenAI(api_key=openai_api_key),
                qdrant_client=QdrantClient(url=qdrant_url, api_key=qdrant_api_key),
                logger=self.logger,
                tag=tag,
                collection_name=secrets.collection_name,
            )
        except Exception as e:
            self.logger.error(f"Error processing files: {e}")
            return ErrorResponse(str(e))
        return OKResponse("Success!")
