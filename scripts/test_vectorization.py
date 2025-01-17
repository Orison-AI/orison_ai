#! /usr/bin/env python3.11

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

"""
Setup these env vars before use
OPENAI_API_KEY
QDRANT_URL
QDRANT_API_KEY
"""

# Standard Imports

import logging
import os
from IPython import embed
import numpy as np
from openai import OpenAI

# File Loader and Embeddings Imports

from langchain_community.document_loaders import (
    PyPDFLoader,
    CSVLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    JSONLoader,
)
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings


# Vectorization Imports

from qdrant_client import QdrantClient
from qdrant_client.http import models

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Initialize Qdrant client
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)
# Define the name of the collection
collection_name = "orison_vdb"


# Chunking
MIN_CHUNK_SIZE = 256

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


def load_file(file_path):
    # Identify the file format based on the file extension
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension in [".txt"]:
        # Use TextLoader for text-based files
        loader = TextLoader(file_path)
    elif file_extension in [".json"]:
        # Use JSONLoader for JSON files
        loader = JSONLoader(file_path)
    elif file_extension in [".md"]:
        # Use UnstructuredMarkdownLoader for text-based files
        loader = UnstructuredMarkdownLoader(file_path)
    elif file_extension in ".csv":
        # Use CSVLoader for CSV files
        loader = CSVLoader(file_path)
    elif file_extension == ".pdf":
        # Use PyPDFLoader for PDF files
        loader = PyPDFLoader(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

    # Load the file and return the documents
    # Each document is a dictionary with the keys "page_content" and "metadata"
    # Each document page_content is literally whatever is on that page
    documents = loader.load()
    return documents


def apply_semantic_splitter(documents):
    # Initialize the text splitter
    # text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    text_splitter = SemanticChunker(
        OpenAIEmbeddings(model="text-embedding-ada-002"),
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=75,
        buffer_size=10,
    )
    # Apply the splitter to the document. It will internally call create_documents
    # which will internally call split_text
    # Returns a List[Document]
    _logger.info("Splitting documents")
    chunks = text_splitter.split_documents(documents)
    _logger.info("Splitting documents....done")
    filtered_chunks = []
    for chunk in chunks:
        if len(chunk.page_content) >= MIN_CHUNK_SIZE:
            filtered_chunks.append(chunk)
    return filtered_chunks


documents = load_file("/app/data/dissertation.pdf")
chunks = apply_semantic_splitter(documents)

# Vectorization
# ToDo: Add source and other information from chunk to vector


# Function to get embeddings from OpenAI
def get_openai_embedding(text):
    response = client.embeddings.create(
        input=[text], model="text-embedding-ada-002"
    )  # Use the appropriate OpenAI model)
    return response.data[0].embedding


# Function to store chunks to Qdrant
def store_chunks_to_qdrant(chunks):
    embeddings = []
    payloads = []
    for chunk in chunks:
        embedding = get_openai_embedding(chunk.page_content)
        embeddings.append(embedding)
        payloads.append(
            {"page_content": chunk.page_content, "metadata": chunk.metadata}
        )

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


store_chunks_to_qdrant(chunks)

embed()
