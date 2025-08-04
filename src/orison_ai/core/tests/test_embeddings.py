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

import pytest
import logging
import time
import asyncio

from core.client import LLMClient
from core.config import LLMConfig, AppConfig
from core.environment import get_env
from database.secrets import OrisonSecrets

logger = logging.getLogger(__name__)


class TestEmbeddings:
    """Test embeddings functionality with rate limiting"""

    def setup_method(self):
        """Setup test configuration"""
        env = get_env()
        secrets = OrisonSecrets(
            openai_api_key=env.openai_api_key,
            qdrant_url=env.qdrant_url,
            qdrant_api_key=env.qdrant_api_key,
            collection_name="test_embeddings",
        )
        llm_config = LLMConfig()
        app_config = AppConfig()

        self.llm_client = LLMClient(secrets, llm_config, app_config)

    @pytest.mark.asyncio
    async def test_single_embedding(self):
        """Test single text embedding"""
        logger.info("Testing single text embedding")

        test_text = "This is a test sentence for embedding generation."

        embedding = await self.llm_client.embed_query(test_text)

        assert isinstance(embedding, list), "Embedding should be a list"
        assert len(embedding) > 0, "Embedding should not be empty"
        assert all(
            isinstance(x, float) for x in embedding
        ), "All embedding values should be floats"

        # Check embedding dimension (text-embedding-ada-002 produces 1536-dimensional vectors)
        assert len(embedding) == 1536, f"Expected 1536 dimensions, got {len(embedding)}"

        logger.info(
            f"Single embedding generated successfully: {len(embedding)} dimensions"
        )

    @pytest.mark.asyncio
    async def test_batch_embeddings(self):
        """Test batch text embeddings"""
        logger.info("Testing batch text embeddings")

        test_texts = [
            "First test sentence for batch embedding.",
            "Second test sentence with different content.",
            "Third test sentence to verify batch processing.",
        ]

        embeddings = await self.llm_client.embed_documents(test_texts)

        assert isinstance(embeddings, list), "Embeddings should be a list"
        assert len(embeddings) == len(
            test_texts
        ), "Number of embeddings should match number of texts"

        for i, embedding in enumerate(embeddings):
            assert isinstance(embedding, list), f"Embedding {i} should be a list"
            assert len(embedding) == 1536, f"Embedding {i} should have 1536 dimensions"
            assert all(
                isinstance(x, float) for x in embedding
            ), f"All values in embedding {i} should be floats"

        logger.info(
            f"Batch embeddings generated successfully: {len(embeddings)} embeddings"
        )

    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test that rate limiting works correctly"""
        logger.info("Testing rate limiting functionality")

        test_text = "Rate limiting test sentence."
        start_time = time.time()

        # Make multiple requests quickly to test rate limiting
        tasks = []
        for i in range(3):
            tasks.append(self.llm_client.embed_query(f"{test_text} {i}"))

        # Execute all tasks
        embeddings = await asyncio.gather(*tasks)
        end_time = time.time()

        # Verify all embeddings were generated
        assert len(embeddings) == 3, "Should have generated 3 embeddings"
        for embedding in embeddings:
            assert len(embedding) == 1536, "Each embedding should have 1536 dimensions"

        # Rate limiting should cause some delay (requests_per_second = 7.0)
        # With 3 requests, it should take at least some time
        elapsed_time = end_time - start_time
        logger.info(f"Rate limiting test completed in {elapsed_time:.3f}s")

        # Verify rate limiting is working (should take some time)
        assert elapsed_time > 0.1, "Rate limiting should cause some delay"

        logger.info("Rate limiting functionality verified")

    @pytest.mark.asyncio
    async def test_embedding_consistency(self):
        """Test that same text produces consistent embeddings"""
        logger.info("Testing embedding consistency")

        test_text = "Consistency test sentence for embedding verification."

        # Generate embeddings for the same text multiple times
        embedding1 = await self.llm_client.embed_query(test_text)
        embedding2 = await self.llm_client.embed_query(test_text)

        assert len(embedding1) == len(
            embedding2
        ), "Embeddings should have same dimensions"
        assert len(embedding1) == 1536, "Embeddings should have 1536 dimensions"

        # Embeddings should be very similar for the same text (but may not be identical)
        # Calculate cosine similarity to verify they're similar
        import numpy as np

        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        similarity = cosine_similarity(embedding1, embedding2)
        assert (
            similarity > 0.99
        ), f"Embeddings should be very similar, got similarity: {similarity}"

        logger.info("Embedding consistency verified")

    def test_token_counting(self):
        """Test token counting functionality"""
        logger.info("Testing token counting")

        test_text = "This is a test sentence for token counting."

        token_count = self.llm_client.count_tokens(test_text)

        assert isinstance(token_count, int), "Token count should be an integer"
        assert token_count > 0, "Token count should be positive"

        # Verify token count is reasonable for the text
        # Tokens can be subwords, so count should be reasonable but may exceed word count
        assert token_count >= len(test_text.split()) * 0.5, "Token count seems too low"
        assert token_count <= len(test_text.split()) * 2, "Token count seems too high"

        logger.info(f"Token counting verified: {token_count} tokens for '{test_text}'")
