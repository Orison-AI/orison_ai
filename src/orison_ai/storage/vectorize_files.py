#!/usr/bin/env python3.11

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
from qdrant_client.http import models

# Internal
from storage.vector_store import VectorStore
from storage.document_processor import DocumentProcessor
from core.config import VectorConfig
from core.client import LLMClient
from core.environment import get_env
from database.secrets import OrisonSecrets
from core.config import LLMConfig


class VectorizeFiles:
    """Efficient file vectorization for structured/unstructured documents"""

    def __init__(self):
        """Initialize VectorizeFiles - actual initialization happens when needed"""
        self.config = None
        self.logger = logging.getLogger(__name__)
        self.llm_client = None
        self.vector_store = None
        self.document_processor = None

    def _initialize(self, collection_name: str = None):
        """Initialize all components with proper collection name"""
        env = get_env()
        target_collection = collection_name or "orison_default"

        secrets = OrisonSecrets(
            openai_api_key=env.openai_api_key,
            qdrant_url=env.qdrant_url,
            qdrant_api_key=env.qdrant_api_key,
            collection_name=target_collection,
        )
        llm_config = LLMConfig()
        self.llm_client = LLMClient(secrets, llm_config)

        # Create config with proper collection name
        self.config = VectorConfig(
            collection_name=target_collection,
            url=env.qdrant_url,
            api_key=env.qdrant_api_key,
        )

        self.vector_store = VectorStore(self.config, self.llm_client)
        self.document_processor = DocumentProcessor(self.config, self.llm_client)

        self.logger.info(
            f"VectorizeFiles initialized with collection: {target_collection}"
        )

    async def vectorize_file(
        self,
        attorney_id: str,
        applicant_id: str,
        file_id: str,
        tag,
    ) -> bool:
        """Vectorize a single file efficiently"""
        try:
            collection_name = f"{attorney_id}_{applicant_id}"
            tag_value = tag[0] if isinstance(tag, list) else tag
            self._initialize(collection_name)
            self.logger.info(
                f"Starting vectorization: {file_id} | Attorney: {attorney_id} | Applicant: {applicant_id} | Tag: {tag_value}"
            )
            # Build paths
            bucket_path = self.document_processor.build_file_path(
                attorney_id, applicant_id, tag_value, file_id
            )
            local_path = f"/tmp/vectorize_{file_id}{self.document_processor.file_extension(bucket_path)}"

            # Download and process
            self.logger.info(f"Downloading file from: {bucket_path}")
            await self.document_processor.download_file(bucket_path, local_path)

            self.logger.info("Processing document...")
            documents = self.document_processor.load_document(local_path, file_id)
            texts, payloads = await self.document_processor.chunk_documents(
                documents, tag_value, file_id
            )
            self.logger.info(f"Storing vectors in collection: {collection_name}")
            await self.vector_store.store_vectors(texts, payloads, tag_value, file_id)
            self.logger.info(
                f"✅ Vectorization complete: {file_id} | {len(texts)} chunks stored"
            )
            return True

        except Exception as e:
            self.logger.error(f"❌ Vectorization failed: {file_id} | Error: {e}")
            return False

    async def vectorize_batch(self, files: list, max_concurrent: int = 3) -> dict:
        """Vectorize multiple files concurrently"""
        import asyncio

        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_file(file_data):
            async with semaphore:
                return await self.vectorize_file(**file_data)

        tasks = [process_file(file) for file in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            "total": len(files),
            "successful": sum(1 for r in results if r is True),
            "failed": sum(1 for r in results if r is False or isinstance(r, Exception)),
        }

    async def search_documents(
        self, query: str, filters: dict = None, limit: int = 10
    ) -> list:
        """Search vectorized documents"""
        return await self.vector_store.search(query, filters, limit)


class DeleteFileVectors:
    """Delete file vectors efficiently"""

    def __init__(self):
        """Initialize DeleteFileVectors - actual initialization happens when needed"""
        self.config = None
        self.llm_client = None
        self.vector_store = None
        self.logger = logging.getLogger(__name__)

    def _initialize(self, collection_name: str = None):
        """Initialize all components with proper collection name"""
        env = get_env()
        target_collection = collection_name or "orison_default"
        secrets = OrisonSecrets(
            openai_api_key=env.openai_api_key,
            qdrant_url=env.qdrant_url,
            qdrant_api_key=env.qdrant_api_key,
            collection_name=target_collection,
        )
        llm_config = LLMConfig()
        self.llm_client = LLMClient(secrets, llm_config)

        # Create config with proper collection name
        self.config = VectorConfig(
            collection_name=target_collection,
            url=env.qdrant_url,
            api_key=env.qdrant_api_key,
        )

        self.vector_store = VectorStore(self.config, self.llm_client)

    async def delete_vectors(
        self, attorney_id: str, applicant_id: str, file_id: str, tag
    ) -> bool:
        """Delete vectors for specific file and tag"""
        try:
            collection_name = f"{attorney_id}_{applicant_id}"
            tag_value = tag[0] if isinstance(tag, list) else tag
            self._initialize(collection_name)

            collection_exists = await self.vector_store.async_client.collection_exists(
                collection_name=collection_name
            )
            if not collection_exists:
                self.logger.warning(
                    f"Collection {collection_name} does not exist when deleting vectors"
                )
                return False

            points_selector = models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="tag",
                            match=models.MatchValue(value=tag_value.lower()),
                        ),
                        models.FieldCondition(
                            key="filename",
                            match=models.MatchValue(value=file_id),
                        ),
                    ],
                )
            )

            await self.vector_store.async_client.delete(
                collection_name=collection_name, points_selector=points_selector
            )

            self.logger.info(f"Deleted vectors for file {file_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete vectors: {e}")
            return False


# Simple usage examples
if __name__ == "__main__":
    import asyncio

    async def test_vectorization():
        # Single file
        vectorizer = VectorizeFiles()
        success = await vectorizer.vectorize_file(
            attorney_id="test_attorney",
            applicant_id="test_applicant",
            file_id="document.pdf",
            tag="resume",
        )
        print(f"Single file vectorization: {'Success' if success else 'Failed'}")

        # Batch processing
        files = [
            {
                "attorney_id": "test_attorney",
                "applicant_id": "test_applicant",
                "file_id": "doc1.pdf",
                "tag": "resume",
            },
            {
                "attorney_id": "test_attorney",
                "applicant_id": "test_applicant",
                "file_id": "doc2.pdf",
                "tag": "cover_letter",
            },
        ]
        result = await vectorizer.vectorize_batch(files, max_concurrent=2)
        print(f"Batch result: {result}")

        # Search
        results = await vectorizer.search_documents(
            "experience", filters={"tag": "resume"}
        )
        print(f"Search results: {len(results)} found")

        # Delete
        deleter = DeleteFileVectors()
        deleted = await deleter.delete_vectors("test_collection", "doc1.pdf", "resume")
        print(f"Deletion: {'Success' if deleted else 'Failed'}")

    asyncio.run(test_vectorization())
