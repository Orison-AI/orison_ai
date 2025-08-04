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

import pytest
import logging
import tempfile
import os

# Internal

from storage.document_processor import DocumentProcessor
from storage.vector_store import VectorStore
from core.config import VectorConfig, LLMConfig, AppConfig
from core.environment import get_env
from database.secrets import OrisonSecrets
from core.client import LLMClient

logger = logging.getLogger(__name__)


class TestVectorization:
    """Test core vectorization functionality using underlying components"""

    def setup_method(self):
        """Setup test data and configuration"""
        self.attorney_id = "test_attorney_001"
        self.applicant_id = "test_applicant_001"
        self.file_id = "test_vectorize.txt"
        self.tag = "resume"

        # Test content from templates
        self.test_content = """The fog was as thick as pea soup. This was a problem. Gary was driving but couldn't see a thing in front of him. He knew he should stop, but the road was narrow so if he did, it would be right in the center of the road. He was sure that another car would end up rear-ending him, so he continued forward despite the lack of visibility. This was an unwise move. There was little doubt that the bridge was unsafe. All one had to do was look at it to know that with certainty. Yet Bob didn't see another option. He may have been able to work one out if he had a bit of time to think things through, but time was something he didn't have. A choice needed to be made, and it needed to be made quickly. Green vines attached to the trunk of the tree had wound themselves toward the top of the canopy. Ants used the vine as their private highway, avoiding all the creases and crags of the bark, to freely move at top speed from top to bottom or bottom to top depending on their current chore. At least this was the way it was supposed to be. Something had damaged the vine overnight halfway up the tree leaving a gap in the once pristine ant highway. It was a simple green chair. There was nothing extraordinary about it or so it seemed. It was the type of chair one would pass without even noticing it was there, let alone what the actual color of it was. It was due to this common and unassuming appearance that few people actually stopped to sit in it and discover its magical powers."""

    @pytest.mark.asyncio
    async def test_core_vectorization_functionality(self):
        """Test core vectorization: create file -> process -> vectorize -> search -> delete"""
        logger.info("Testing core vectorization functionality")

        # Create temporary test file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as temp_file:
            temp_file.write(self.test_content)
            temp_file_path = temp_file.name

        try:
            # Initialize components directly
            env = get_env()
            config = VectorConfig(
                collection_name="test_core_vectorization",
                url=env.qdrant_url,
                api_key=env.qdrant_api_key,
            )

            secrets = OrisonSecrets(
                openai_api_key=env.openai_api_key,
                qdrant_url=env.qdrant_url,
                qdrant_api_key=env.qdrant_api_key,
                collection_name=config.collection_name,
            )
            llm_config = LLMConfig()
            app_config = AppConfig()

            llm_client = LLMClient(secrets, llm_config, app_config)
            document_processor = DocumentProcessor(config, llm_client)
            vector_store = VectorStore(config, llm_client)

            # Process document directly
            documents = document_processor.load_document(temp_file_path, self.file_id)
            texts, payloads = await document_processor.chunk_documents(
                documents, self.tag, self.file_id
            )

            assert len(texts) > 0, "No text chunks generated"
            assert len(payloads) > 0, "No payloads generated"
            logger.info(f"Generated {len(texts)} chunks from document")

            # Store vectors directly
            await vector_store.store_vectors(texts, payloads, self.tag, self.file_id)
            logger.info(f"Stored {len(texts)} vectors")

            # Test search functionality
            search_results = await vector_store.search(
                query="fog driving visibility", limit=5
            )
            assert len(search_results) > 0, "No search results found"

            # Verify search results contain expected content
            found_fog = any(
                "fog" in result.content.lower() for result in search_results
            )
            found_driving = any(
                "driving" in result.content.lower() for result in search_results
            )
            assert found_fog, "Fog not found in search results"
            assert found_driving, "Driving not found in search results"

            # Test payload structure - verify all required fields exist
            for result in search_results:
                metadata = result.metadata
                assert (
                    "filename" in metadata
                ), f"Missing filename in metadata: {metadata}"
                assert "tag" in metadata, f"Missing tag in metadata: {metadata}"
                assert (
                    "page_content" in metadata
                ), f"Missing page_content in metadata: {metadata}"
                assert "source" in metadata, f"Missing source in metadata: {metadata}"
                assert "page" in metadata, f"Missing page in metadata: {metadata}"

                # Verify field values
                assert (
                    metadata["filename"] == self.file_id
                ), f"Filename mismatch: expected {self.file_id}, got {metadata['filename']}"
                assert (
                    metadata["tag"] == self.tag
                ), f"Tag mismatch: expected {self.tag}, got {metadata['tag']}"
                assert (
                    metadata["source"] == self.file_id
                ), f"Source mismatch: expected {self.file_id}, got {metadata['source']}"
                assert isinstance(
                    metadata["page"], (int, str)
                ), f"Page should be int or string, got {type(metadata['page'])}"

            logger.info(
                f"✅ Payload structure test passed: All fields present and correct"
            )

            # Test source formatting
            formatted_sources = vector_store.format_sources(search_results)
            logger.info(f"Formatted sources: {formatted_sources}")

            # Verify source formatting contains expected elements
            assert (
                self.file_id in formatted_sources
            ), f"Filename {self.file_id} not found in formatted sources: {formatted_sources}"
            assert (
                "Pages:" in formatted_sources or self.file_id in formatted_sources
            ), f"Page information missing in formatted sources: {formatted_sources}"

            logger.info(f"✅ Source formatting test passed: {formatted_sources}")

            logger.info(
                f"✅ Search test passed: Found {len(search_results)} results | Fog: {found_fog} | Driving: {found_driving}"
            )

            # Print detailed test results
            print("\n" + "=" * 60)
            print("VECTORIZATION TEST RESULTS")
            print("=" * 60)
            print(f"Collection: {config.collection_name}")
            print(f"File ID: {self.file_id}")
            print(f"Tag: {self.tag}")
            print(f"Chunks generated: {len(texts)}")
            print(f"Search results: {len(search_results)}")
            print(f"Formatted sources: {formatted_sources}")
            print("\nSample result metadata:")
            if search_results:
                sample_metadata = search_results[0].metadata
                for key, value in sample_metadata.items():
                    print(f"  {key}: {value}")
            print("=" * 60)

            # Test vector deletion - delete entire collection (as original test does)
            await vector_store.async_client.delete_collection(
                collection_name=config.collection_name
            )
            logger.info("Collection deleted successfully")

            logger.info("Core vectorization functionality test passed")

        finally:
            # Cleanup temporary file
            os.unlink(temp_file_path)

    @pytest.mark.asyncio
    async def test_batch_vectorization(self):
        """Test batch vectorization with multiple local files"""
        logger.info("Testing batch vectorization")

        # Create multiple test files
        test_files = [
            {
                "file_id": "resume.txt",
                "tag": "resume",
                "content": "Experienced software engineer with Python skills and machine learning expertise.",
            },
            {
                "file_id": "cover_letter.txt",
                "tag": "cover_letter",
                "content": "Motivated candidate interested in machine learning and artificial intelligence.",
            },
        ]

        temp_files = []

        try:
            # Create temporary files
            for test_file in test_files:
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".txt", delete=False
                ) as temp_file:
                    temp_file.write(test_file["content"])
                    temp_files.append(temp_file.name)

            # Initialize components directly
            env = get_env()
            config = VectorConfig(
                collection_name="test_batch_vectorization",
                url=env.qdrant_url,
                api_key=env.qdrant_api_key,
            )

            secrets = OrisonSecrets(
                openai_api_key=env.openai_api_key,
                qdrant_url=env.qdrant_url,
                qdrant_api_key=env.qdrant_api_key,
                collection_name=config.collection_name,
            )
            llm_config = LLMConfig()
            app_config = AppConfig()

            llm_client = LLMClient(secrets, llm_config, app_config)
            document_processor = DocumentProcessor(config, llm_client)
            vector_store = VectorStore(config, llm_client)

            # Process each file
            all_texts = []
            all_payloads = []

            for i, test_file in enumerate(test_files):
                documents = document_processor.load_document(
                    temp_files[i], test_file["file_id"]
                )
                texts, payloads = await document_processor.chunk_documents(
                    documents, test_file["tag"], test_file["file_id"]
                )
                all_texts.extend(texts)
                all_payloads.extend(payloads)

            # Store all vectors
            await vector_store.store_vectors(all_texts, all_payloads, "mixed", "batch")
            logger.info(f"Stored {len(all_texts)} vectors from batch processing")

            # Test search across both tags
            all_results = await vector_store.search("Python machine learning")
            assert len(all_results) > 0, "No results found in batch search"

            # Test search for specific content
            resume_results = await vector_store.search("software engineer")
            assert len(resume_results) > 0, "No resume results found"

            cover_letter_results = await vector_store.search("artificial intelligence")
            assert len(cover_letter_results) > 0, "No cover letter results found"

            # Test payload structure for batch results
            for result in all_results:
                metadata = result.metadata
                assert (
                    "filename" in metadata
                ), f"Missing filename in batch metadata: {metadata}"
                assert "tag" in metadata, f"Missing tag in batch metadata: {metadata}"
                assert (
                    "page_content" in metadata
                ), f"Missing page_content in batch metadata: {metadata}"
                assert (
                    "source" in metadata
                ), f"Missing source in batch metadata: {metadata}"
                assert "page" in metadata, f"Missing page in batch metadata: {metadata}"

            # Test source formatting for batch results
            batch_formatted_sources = vector_store.format_sources(all_results)
            logger.info(f"Batch formatted sources: {batch_formatted_sources}")

            # Verify batch source formatting contains both files
            assert (
                "resume.txt" in batch_formatted_sources
                or "cover_letter.txt" in batch_formatted_sources
            ), f"Expected filenames not found in batch sources: {batch_formatted_sources}"

            logger.info("Batch vectorization test passed")

            # Print detailed batch test results
            print("\n" + "=" * 60)
            print("BATCH VECTORIZATION TEST RESULTS")
            print("=" * 60)
            print(f"Collection: {config.collection_name}")
            print(f"Total chunks: {len(all_texts)}")
            print(f"Total search results: {len(all_results)}")
            print(f"Batch formatted sources: {batch_formatted_sources}")
            print("\nSample batch result metadata:")
            if all_results:
                sample_metadata = all_results[0].metadata
                for key, value in sample_metadata.items():
                    print(f"  {key}: {value}")
            print("=" * 60)

            # Clean up collection
            await vector_store.async_client.delete_collection(
                collection_name=config.collection_name
            )
            logger.info("Batch collection deleted successfully")

        finally:
            # Cleanup temporary files
            for temp_file in temp_files:
                os.unlink(temp_file)
