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

import pytest
import asyncio

# Internal

from core.environment import get_env
from core.config import LLMConfig
from database.secrets import OrisonSecrets
from core.client import LLMClient


class TestLangSmithIntegration:
    """Test LangSmith integration in Orison AI"""

    def test_langsmith_environment_loading(self):
        """Test that LangSmith environment variables are loaded correctly"""
        env = get_env()

        # Always test environment loading, regardless of configuration
        assert hasattr(env, "langchain_api_key")
        assert hasattr(env, "langchain_project")
        assert hasattr(env, "langchain_tracing")

    @pytest.mark.asyncio
    async def test_llm_client_with_langsmith(self):
        """Test LLMClient with LangSmith tracing - actual LLM call"""
        env = get_env()

        # Skip test if LangSmith is not configured
        if not env.langchain_api_key:
            pytest.skip("LangSmith not configured - skipping test")

        # Initialize components with minimal config
        secrets = OrisonSecrets(
            openai_api_key=env.openai_api_key,
            qdrant_url="https://test.qdrant.com",  # Dummy URL for test
            qdrant_api_key="test_key",  # Dummy key for test
            collection_name="test_collection",
        )

        llm_config = LLMConfig()
        # Initialize LLMClient - should configure LangSmith automatically
        client = LLMClient(secrets, llm_config)

        # Verify client was created successfully
        assert client is not None
        assert hasattr(client, "llm")
        assert hasattr(client, "embeddings")

        # Test actual LLM call with LangSmith tracing
        messages = [
            {
                "role": "user",
                "content": "Hello! This is a test of LangSmith integration.",
            }
        ]

        try:
            response = await client.generate_response(messages)
            assert response is not None
            assert len(response) > 0
            print(f"✅ LLM Response: {response[:100]}...")
        except Exception as e:
            pytest.fail(f"LLM call failed: {e}")

    @pytest.mark.asyncio
    async def test_embeddings_with_langsmith(self):
        """Test embeddings with LangSmith tracing"""
        env = get_env()

        # Skip test if LangSmith is not configured
        if not env.langchain_api_key:
            pytest.skip("LangSmith not configured - skipping test")

        # Initialize components
        secrets = OrisonSecrets(
            openai_api_key=env.openai_api_key,
            qdrant_url="https://test.qdrant.com",
            qdrant_api_key="test_key",
            collection_name="test_collection",
        )

        llm_config = LLMConfig()
        # Initialize LLMClient
        client = LLMClient(secrets, llm_config)

        # Test embedding generation with LangSmith tracing
        try:
            embedding = await client.embed_query("Test text for embedding")
            assert embedding is not None
            assert len(embedding) > 0
            print(f"✅ Embedding generated: {len(embedding)} dimensions")
        except Exception as e:
            pytest.fail(f"Embedding generation failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
