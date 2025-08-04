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

import logging
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from collections import defaultdict

from qdrant_client.async_qdrant_client import AsyncQdrantClient
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_qdrant import Qdrant
from langchain.retrievers.multi_query import MultiQueryRetriever

# Internal

from orison_ai.core.client import LLMClient
from orison_ai.core.config import VectorConfig


@dataclass
class SearchResult:
    """Result from vector search"""

    content: str
    metadata: Dict[str, Any]
    score: float


class VectorStore:
    """Vector store with exact original behavior preserved"""

    def __init__(self, config: VectorConfig, llm_client: LLMClient):
        self.config = config
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)

        # Qdrant clients - exactly as original setup
        self.client = QdrantClient(
            url=config.url,
            api_key=config.api_key,
            port=config.port,
            grpc_port=config.grpc_port,
            https=config.https,
            timeout=config.timeout,
        )

        self.async_client = AsyncQdrantClient(
            url=config.url,
            api_key=config.api_key,
            port=config.port,
            grpc_port=config.grpc_port,
            https=config.https,
            timeout=config.timeout,
        )

        # LangChain Qdrant wrapper - preserved from original
        self.vector_store = Qdrant(
            client=self.client,
            async_client=self.async_client,
            collection_name=config.collection_name,
            embeddings=llm_client.embeddings,
        )

        self.logger.info(
            f"VectorStore initialized with default collection: {config.collection_name}"
        )

    async def search(
        self, query: str, filters: Optional[Dict[str, Any]] = None, limit: int = None
    ) -> List[SearchResult]:
        """Search for relevant documents with proper filtering"""

        limit = limit or self.config.retrieval_limit
        self.logger.info(
            f"Searching for: '{query}' with limit: {limit} and filters: {filters}"
        )

        # Convert filters to Qdrant format if provided
        qdrant_filter = None
        if filters:
            must_conditions = []

            if "tag" in filters:
                tag_values = (
                    filters["tag"]
                    if isinstance(filters["tag"], list)
                    else [filters["tag"]]
                )
                must_conditions.append(
                    models.FieldCondition(
                        key="tag", match=models.MatchAny(any=tag_values)
                    )
                )

            if "filename" in filters:
                filename_values = (
                    filters["filename"]
                    if isinstance(filters["filename"], list)
                    else [filters["filename"]]
                )
                must_conditions.append(
                    models.FieldCondition(
                        key="filename", match=models.MatchAny(any=filename_values)
                    )
                )

            if must_conditions:
                qdrant_filter = models.Filter(must=must_conditions)

        # Use direct Qdrant client to get full payload data
        query_embedding = await self.llm_client.embed_query(query)

        search_result = await self.async_client.search(
            collection_name=self.config.collection_name,
            query_vector=query_embedding,
            limit=limit,
            query_filter=qdrant_filter,
            with_payload=True,
            with_vectors=False,
        )

        results = [
            SearchResult(
                content=point.payload.get("page_content", ""),
                metadata=point.payload,  # Use payload as metadata
                score=point.score,
            )
            for point in search_result
        ]

        self.logger.info(f"Found {len(results)} results for query: '{query}'")
        return results

    async def multi_query_search(
        self, query: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Multi-query retrieval with proper filtering"""

        try:
            # Convert filters to Qdrant format if provided
            qdrant_filter = None
            if filters:
                must_conditions = []

                if "tag" in filters:
                    tag_values = (
                        filters["tag"]
                        if isinstance(filters["tag"], list)
                        else [filters["tag"]]
                    )
                    must_conditions.append(
                        models.FieldCondition(
                            key="tag", match=models.MatchAny(any=tag_values)
                        )
                    )

                if "filename" in filters:
                    filename_values = (
                        filters["filename"]
                        if isinstance(filters["filename"], list)
                        else [filters["filename"]]
                    )
                    must_conditions.append(
                        models.FieldCondition(
                            key="filename", match=models.MatchAny(any=filename_values)
                        )
                    )

                if must_conditions:
                    qdrant_filter = models.Filter(must=must_conditions)

            # Use direct Qdrant client for multi-query search
            query_embedding = await self.llm_client.embed_query(query)

            search_result = await self.async_client.search(
                collection_name=self.config.collection_name,
                query_vector=query_embedding,
                limit=self.config.retrieval_limit,
                query_filter=qdrant_filter,
                with_payload=True,
                with_vectors=False,
            )

            return [
                SearchResult(
                    content=point.payload.get("page_content", ""),
                    metadata=point.payload,  # Use payload as metadata
                    score=point.score,
                )
                for point in search_result
            ]

        except Exception:
            # Fallback to single query
            return await self.search(query, filters)

    def format_context(self, results: List[SearchResult]) -> str:
        """Format search results into context - preserved from original"""
        return "\n".join([result.content for result in results])

    def format_sources(self, results: List[SearchResult]) -> str:
        """Format source information for Qdrant payload structure"""
        source_dict = defaultdict(list)

        for result in results:
            # Use the actual fields from your Qdrant payload
            filename = result.metadata.get("filename")
            page = result.metadata.get("page")

            # Use filename as the source identifier
            if filename:
                if page:
                    source_dict[filename].append(page)
                else:
                    source_dict[filename] = []  # No pages but still track the file

        # Format sources
        pairs = []
        for filename, pages in source_dict.items():
            if pages:
                # Sort and format pages
                page_list = ", ".join(map(str, sorted(set(pages))))
                pairs.append(f"{filename} (Pages: {page_list})")
            else:
                pairs.append(f"{filename}")

        return " and ".join(pairs) if pairs else "No sources available"

    async def store_vectors(
        self, texts: List[str], payloads: List[Dict[str, Any]], tag: str, filename: str
    ) -> None:
        """Store vectors in database - preserves original vectorization logic"""

        self.logger.info(
            f"Storing {len(texts)} vectors for file: {filename} with tag: {tag}"
        )

        # Ensure collection exists with proper configuration
        sample_embedding = await self.llm_client.embed_query("Sample for vector size")
        collection_exists = await self.async_client.collection_exists(
            collection_name=self.config.collection_name
        )

        if not collection_exists:
            self.logger.info(f"Creating collection: {self.config.collection_name}")
            await self.async_client.create_collection(
                collection_name=self.config.collection_name,
                vectors_config=models.VectorParams(
                    size=len(sample_embedding),
                    distance=models.Distance.COSINE,
                ),
            )

            # Create indexes for filtering (needed for deletion)
            await self.async_client.create_payload_index(
                collection_name=self.config.collection_name,
                field_name="tag",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )

            await self.async_client.create_payload_index(
                collection_name=self.config.collection_name,
                field_name="filename",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
            self.logger.info("Collection and indexes created successfully")
        else:
            # Check if collection has proper vector configuration
            collection_info = await self.async_client.get_collection(
                collection_name=self.config.collection_name
            )

            # If collection exists but doesn't have proper vector config, recreate it
            if not collection_info.config.params.vectors:
                self.logger.info(
                    f"Recreating collection {self.config.collection_name} with proper vector configuration"
                )
                await self.async_client.delete_collection(
                    collection_name=self.config.collection_name
                )
                await self.async_client.create_collection(
                    collection_name=self.config.collection_name,
                    vectors_config=models.VectorParams(
                        size=len(sample_embedding),
                        distance=models.Distance.COSINE,
                    ),
                )

                # Recreate indexes
                await self.async_client.create_payload_index(
                    collection_name=self.config.collection_name,
                    field_name="tag",
                    field_schema=models.PayloadSchemaType.KEYWORD,
                )
                await self.async_client.create_payload_index(
                    collection_name=self.config.collection_name,
                    field_name="filename",
                    field_schema=models.PayloadSchemaType.KEYWORD,
                )
                self.logger.info("Collection recreated with proper configuration")

        # Generate embeddings
        self.logger.info("Generating embeddings...")
        embeddings = await self.llm_client.embed_documents(texts)

        # Upload vectors - exactly as original
        self.logger.info("Uploading vectors to collection...")

        # Generate IDs for the vectors
        import uuid

        ids = [str(uuid.uuid4()) for _ in range(len(embeddings))]

        await self.async_client.upsert(
            collection_name=self.config.collection_name,
            points=models.Batch(
                ids=ids,
                vectors=np.array(embeddings),
                payloads=payloads,
            ),
        )

        self.logger.info(
            f"Successfully stored {len(texts)} vectors in collection: {self.config.collection_name}"
        )

    async def delete_file_vectors(
        self, collection_name: str, file_id: str, tag: str
    ) -> bool:
        """Delete vectors for a specific file"""
        try:
            self.logger.info(
                f"Attempting to delete vectors for file: {file_id} with tag: {tag}"
            )

            collection_exists = await self.async_client.collection_exists(
                collection_name=collection_name
            )

            if not collection_exists:
                self.logger.warning(f"Collection {collection_name} does not exist")
                return False

            points_selector = models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="tag",
                            match=models.MatchValue(value=tag.lower()),
                        ),
                        models.FieldCondition(
                            key="filename",
                            match=models.MatchValue(value=file_id),
                        ),
                    ],
                )
            )

            await self.async_client.delete(
                collection_name=collection_name, points_selector=points_selector
            )

            self.logger.info(f"Successfully deleted vectors for file: {file_id}")
            return True

        except Exception as e:
            self.logger.error(f"Deletion failed for file {file_id}: {e}")
            return False
