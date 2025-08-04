#! /usr/bin/env python3.11

# ==========================================================================
#  Copyright (c) Orison AI, 2025.
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
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
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
from langchain_community.document_loaders.xml import UnstructuredXMLLoader
from langchain_community.document_loaders.excel import UnstructuredExcelLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker

# Internal

from orison_ai.core.config import VectorConfig
from orison_ai.core.client import LLMClient
from orison_ai.database.firebase_storage import FirebaseStorage


class DocumentProcessor:
    """Document processing with exact original behavior preserved"""

    def __init__(self, config: VectorConfig, llm_client: LLMClient):
        self.config = config
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)

    async def download_file(self, remote_path: str, local_path: str) -> None:
        """Download file from Firebase Storage - preserved from original"""
        await FirebaseStorage.download_file(
            remote_file_path=remote_path, local_file_path=local_path
        )

        if not os.path.exists(local_path):
            raise FileNotFoundError(f"Could not download file to {local_path}")

    def load_document(self, file_path: str, filename: str) -> List[Any]:
        """Load document with exact original file type support"""
        extension = self.file_extension(file_path).lower()
        self.logger.info(f"Loading document: {filename} (type: {extension})")
        self.logger.info(f"File path: {file_path}, Extension: '{extension}'")

        # Exact match statement preserved from original
        match extension:
            case ".txt":
                loader = TextLoader(file_path)
            case ".json":
                loader = JSONLoader(file_path)
            case ".md":
                loader = UnstructuredMarkdownLoader(file_path)
            case ".html":
                loader = UnstructuredHTMLLoader(file_path)
            case ".csv":
                loader = CSVLoader(file_path)
            case ".pdf":
                loader = PyPDFLoader(file_path)
            case ".docx":
                loader = UnstructuredWordDocumentLoader(file_path)
            case ".doc":
                loader = UnstructuredWordDocumentLoader(file_path)
            case ".docs":
                loader = UnstructuredWordDocumentLoader(file_path)
            case ".pptx":
                loader = UnstructuredPowerPointLoader(file_path)
            case ".xls":
                loader = UnstructuredExcelLoader(file_path)
            case ".xlsx":
                loader = UnstructuredExcelLoader(file_path)
            case ".xml":
                loader = UnstructuredXMLLoader(file_path)
            case _:
                loader = TextLoader(file_path)

        try:
            # Load and update metadata exactly as original
            self.logger.info(f"Attempting to load document: {file_path}")
            documents = loader.load()
            self.logger.info(
                f"Successfully loaded {len(documents)} pages from {file_path}"
            )

            for document in documents:
                document.metadata["source"] = filename

            self.logger.info(f"Loaded {len(documents)} document pages from: {filename}")
            return documents

        except Exception as e:
            self.logger.error(
                f"Error loading document {filename} from {file_path}: {e}"
            )
            import traceback

            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            raise

    async def chunk_documents(
        self, documents: List[Any], tag: str, filename: str
    ) -> tuple[List[str], List[Dict[str, Any]]]:
        """Chunk documents with sophisticated merging logic from original"""

        self.logger.info(f"Starting document chunking for: {filename} (tag: {tag})")

        # Text splitter with exact original settings
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
        )

        # Process documents in thread pool - exactly as original
        def process_document(doc, index):
            # Split document into chunks
            chunks = text_splitter.split_text(doc.page_content)
            # Add metadata to each chunk
            enriched_chunks = [
                {"content": chunk, "metadata": {"source": filename, "page": index + 1}}
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

        # Flatten the list of enriched chunks
        all_chunks = [chunk for result in results for chunk in result]
        self.logger.info(
            f"Initial chunking created {len(all_chunks)} chunks from {len(documents)} documents"
        )

        # Merge smaller chunks to meet token size requirements - exactly as original
        self.logger.info("Merging smaller chunks to meet token requirements...")
        merged_chunks = []
        payloads = []
        texts = []
        current_chunk = None

        for chunk in all_chunks:
            token_count = self.llm_client.count_tokens(chunk["content"])
            if current_chunk is None:
                current_chunk = chunk
                current_chunk["metadata"]["source"] = chunk["metadata"]["source"]
                current_chunk["metadata"]["page"] = chunk["metadata"]["page"]
            elif (
                token_count + self.llm_client.count_tokens(current_chunk["content"])
                <= self.config.chunk_size
            ):
                current_chunk["content"] += " " + chunk["content"]
            else:
                merged_chunks.append(current_chunk)
                payloads.append(
                    {
                        "tag": tag.lower(),
                        "filename": filename,
                        "page_content": current_chunk["content"],
                        "source": current_chunk["metadata"]["source"],
                        "page": current_chunk["metadata"]["page"],
                    }
                )
                texts.append(current_chunk["content"])
                current_chunk = chunk

        if current_chunk:
            merged_chunks.append(current_chunk)
            payloads.append(
                {
                    "tag": tag.lower(),
                    "filename": filename,
                    "page_content": current_chunk["content"],
                    "source": current_chunk["metadata"]["source"],
                    "page": current_chunk["metadata"]["page"],
                }
            )
            texts.append(current_chunk["content"])

        self.logger.info(
            f"Chunking complete: {len(texts)} final chunks from {len(all_chunks)} initial chunks"
        )
        return texts, payloads

    @staticmethod
    def build_file_path(
        attorney_id: str, applicant_id: str, bucket_name: str, file_path: str
    ) -> str:
        """Build file path exactly as original"""
        return os.path.join(
            "documents",
            "attorneys",
            attorney_id,
            "applicants",
            applicant_id,
            bucket_name,
            file_path,
        )

    @staticmethod
    def file_extension(file_path: str) -> str:
        """Get file extension exactly as original"""
        return os.path.splitext(file_path)[1]
