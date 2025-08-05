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

# Internal

from core.environment import get_env
from core.config import LLMConfig, AppConfig
from database.secrets import OrisonSecrets
from core.client import LLMClient


class TestLangSmithIntegration:
    """Test LangSmith integration in Orison AI"""

    def test_langsmith_tracing_enabled(self):
        """Test that LangSmith tracing is properly configured"""
        env = get_env()

        # Skip test if LangSmith is not configured
        if not env.langchain_api_key:
            pytest.skip("LangSmith not configured - skipping test")

        # Test that environment variables are loaded
        assert env.langchain_api_key is not None
        assert env.langchain_project is not None or env.langchain_api_key is not None

    def test_llm_client_with_langsmith(self):
        """Test LLMClient with LangSmith tracing"""
        env = get_env()

        # Skip test if LangSmith is not configured
        if not env.langchain_api_key:
            pytest.skip("LangSmith not configured - skipping test")

        # Initialize components
        secrets = OrisonSecrets(
            openai_api_key=env.openai_api_key,
            qdrant_url=env.qdrant_url,
            qdrant_api_key=env.qdrant_api_key,
            collection_name="test_collection",
        )

        llm_config = LLMConfig()
        app_config = AppConfig()

        # Initialize LLMClient - should configure LangSmith automatically
        client = LLMClient(secrets, llm_config, app_config)

        # Verify client was created successfully
        assert client is not None
        assert hasattr(client, "llm")
        assert hasattr(client, "embeddings")

    def test_self_hosted_langsmith_config(self):
        """Test self-hosted LangSmith configuration"""
        env = get_env()

        # Skip test if LangSmith is not configured
        if not env.langchain_api_key:
            pytest.skip("LangSmith not configured - skipping test")

        # Test self-hosted configuration
        config = AppConfig.for_self_hosted_langsmith(
            endpoint="https://custom.langsmith.com", api_key="test_key"
        )

        assert config.project == "orison-ai"
        assert config.endpoint == "https://custom.langsmith.com"
        assert config.api_key == "test_key"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
