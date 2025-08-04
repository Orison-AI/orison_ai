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
import asyncio

# Internal

from core.environment import get_env
from core.config import LLMConfig, VectorConfig, AppConfig
from core.client import LLMClient
from database.secrets import OrisonSecrets
from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)


class TestConnections:
    """Test actual API connections and configuration"""

    def test_environment_loading(self):
        """Test that environment variables are loaded correctly"""
        logger.info("Testing environment configuration loading")

        env = get_env()

        # Verify required environment variables are loaded
        assert env.openai_api_key, "OpenAI API key not loaded"
        assert env.qdrant_url, "Qdrant URL not loaded"
        assert env.qdrant_api_key, "Qdrant API key not loaded"

        logger.info("Environment configuration loaded successfully")

    @pytest.mark.asyncio
    async def test_openai_connection(self):
        """Test actual OpenAI API connection"""
        logger.info("Testing OpenAI API connection")

        env = get_env()
        secrets = OrisonSecrets(
            openai_api_key=env.openai_api_key,
            qdrant_url=env.qdrant_url,
            qdrant_api_key=env.qdrant_api_key,
            collection_name="test_openai",
        )
        llm_config = LLMConfig()
        app_config = AppConfig()

        llm_client = LLMClient(secrets, llm_config, app_config)

        # Test actual API call
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "Respond with exactly 'Connection successful'.",
            },
        ]

        response = await llm_client.generate_response(messages)

        assert isinstance(response, str), "Response should be a string"
        assert len(response) > 0, "Response should not be empty"
        assert (
            "connection successful" in response.lower()
        ), "OpenAI API connection failed"

        logger.info("OpenAI API connection verified")

    def test_qdrant_connection(self):
        """Test actual Qdrant connection"""
        logger.info("Testing Qdrant connection")

        env = get_env()

        # Test Qdrant client connection
        client = QdrantClient(
            url=env.qdrant_url,
            api_key=env.qdrant_api_key,
            port=6333,
            grpc_port=6333,
            https=True,
            timeout=10,
        )

        # Test actual connection by getting collections
        collections = client.get_collections()
        assert isinstance(
            collections.collections, list
        ), "Should be able to get collections"

        logger.info(
            f"Qdrant connection verified: {len(collections.collections)} collections found"
        )

    def test_llm_config_defaults(self):
        """Test LLM configuration defaults"""
        logger.info("Testing LLM configuration defaults")

        config = LLMConfig()

        assert config.model == "gpt-4o", "Default model incorrect"
        assert (
            config.embedding_model == "text-embedding-ada-002"
        ), "Default embedding model incorrect"
        assert config.temperature == 0.2, "Default temperature incorrect"
        assert config.max_tokens == 4096, "Default max tokens incorrect"
        assert (
            config.requests_per_second == 7.0
        ), "Default requests per second incorrect"
        assert config.max_bucket_size == 1, "Default max bucket size incorrect"

        logger.info("LLM configuration defaults verified")

    def test_vector_config_creation(self):
        """Test vector configuration creation"""
        logger.info("Testing vector configuration creation")

        env = get_env()
        config = VectorConfig(
            collection_name="test_collection",
            url=env.qdrant_url,
            api_key=env.qdrant_api_key,
        )

        assert config.collection_name == "test_collection", "Collection name not set"
        assert config.url == env.qdrant_url, "URL not set correctly"
        assert config.api_key == env.qdrant_api_key, "API key not set correctly"
        assert config.chunk_size == 512, "Default chunk size incorrect"
        assert config.chunk_overlap == 50, "Default chunk overlap incorrect"
        assert config.retrieval_limit == 10, "Default retrieval limit incorrect"

        logger.info("Vector configuration creation verified")

    def test_app_config_factory_methods(self):
        """Test app configuration factory methods"""
        logger.info("Testing app configuration factory methods")

        # Test local development config
        local_config = AppConfig.for_local_development("./test_traces.db")
        assert local_config.project == "orison-ai-local", "Local project name incorrect"
        assert local_config.use_local_tracing is True, "Local tracing not enabled"
        assert (
            local_config.local_sqlite_path == "./test_traces.db"
        ), "SQLite path not set"

        # Test self-hosted config
        hosted_config = AppConfig.for_self_hosted_langsmith(
            "http://localhost:8000", "test_key"
        )
        assert hosted_config.project == "orison-ai", "Hosted project name incorrect"
        assert (
            hosted_config.use_local_tracing is False
        ), "Local tracing should be disabled"
        assert hosted_config.endpoint == "http://localhost:8000", "Endpoint not set"
        assert hosted_config.api_key == "test_key", "API key not set"

        logger.info("App configuration factory methods verified")
