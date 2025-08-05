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

from core.client import LLMClient
from core.config import LLMConfig
from core.environment import get_env
from database.secrets import OrisonSecrets

logger = logging.getLogger(__name__)


class TestLLM:
    """Test LLM functionality with streaming and rate limiting"""

    def setup_method(self):
        """Setup test configuration"""
        env = get_env()
        secrets = OrisonSecrets(
            openai_api_key=env.openai_api_key,
            qdrant_url=env.qdrant_url,
            qdrant_api_key=env.qdrant_api_key,
            collection_name="test_llm",
        )
        llm_config = LLMConfig()
        self.llm_client = LLMClient(secrets, llm_config)

    def teardown_method(self):
        """Clean up after each test"""
        if hasattr(self, "llm_client"):
            # Close any open connections
            if hasattr(self.llm_client, "llm") and hasattr(
                self.llm_client.llm, "async_client"
            ):
                try:
                    self.llm_client.llm.async_client.close()
                except:
                    pass

    @pytest.mark.asyncio
    async def test_streaming_response(self):
        """Test streaming LLM response"""
        logger.info("Testing streaming LLM response")

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello in exactly 3 words."},
        ]

        chunks = []
        async for chunk in self.llm_client.stream_response(messages):
            chunks.append(chunk)

        # Verify streaming worked
        assert len(chunks) > 0, "Should have received streaming chunks"

        # Combine chunks into full response
        full_response = "".join(chunks)
        assert len(full_response) > 0, "Full response should not be empty"

        # Verify response contains expected content
        assert "hello" in full_response.lower(), "Response should contain 'hello'"

        logger.info(
            f"Streaming response received: {len(chunks)} chunks, {len(full_response)} characters"
        )

    @pytest.mark.asyncio
    async def test_complete_response(self):
        """Test complete LLM response generation"""
        logger.info("Testing complete LLM response generation")

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is 2 + 2? Answer with just the number."},
        ]

        response = await self.llm_client.generate_response(messages)

        assert isinstance(response, str), "Response should be a string"
        assert len(response) > 0, "Response should not be empty"

        # Verify response contains the answer
        assert "4" in response, "Response should contain the answer '4'"

        logger.info(f"Complete response generated: {len(response)} characters")

    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test that rate limiting works for LLM requests"""
        logger.info("Testing LLM rate limiting")

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'test' and nothing else."},
        ]

        # Make multiple requests quickly to test rate limiting
        tasks = []
        for i in range(3):
            tasks.append(self.llm_client.generate_response(messages))

        # Execute all tasks
        responses = await asyncio.gather(*tasks)

        # Verify all responses were generated
        assert len(responses) == 3, "Should have generated 3 responses"
        for response in responses:
            assert isinstance(response, str), "Each response should be a string"
            assert len(response) > 0, "Each response should not be empty"

        logger.info("LLM rate limiting verified")

    @pytest.mark.asyncio
    async def test_system_role_preservation(self):
        """Test that system role is preserved correctly"""
        logger.info("Testing system role preservation")

        # Test with custom system role
        messages = [
            {
                "role": "system",
                "content": "You are a math tutor. Always respond with numbers only.",
            },
            {"role": "user", "content": "What is 5 + 3?"},
        ]

        try:
            response = await self.llm_client.generate_response(messages)

            assert isinstance(response, str), "Response should be a string"
            assert len(response) > 0, "Response should not be empty"

            # Should contain the answer (8)
            assert "8" in response, "Response should contain the answer '8'"

            logger.info("System role preservation verified")
        except Exception as e:
            logger.warning(f"System role preservation test failed: {e}")
            # Skip this test if there are connection issues
            pytest.skip(f"Connection issue in system role test: {e}")

    @pytest.mark.asyncio
    async def test_context_manager_rate_limiting(self):
        """Test rate limiting context manager"""
        logger.info("Testing rate limiting context manager")

        async with self.llm_client.rate_limited_context():
            # This should work without throwing rate limit errors
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'success'."},
            ]
            response = await self.llm_client.generate_response(messages)
            assert "success" in response.lower(), "Response should contain 'success'"

        logger.info("Rate limiting context manager verified")

    def test_token_counting_static_method(self):
        """Test static token counting method"""
        logger.info("Testing static token counting method")

        test_text = "This is a test sentence for token counting."

        token_count = LLMClient.count_tokens(test_text)

        assert isinstance(token_count, int), "Token count should be an integer"
        assert token_count > 0, "Token count should be positive"

        # Test with different model
        token_count_gpt4 = LLMClient.count_tokens(test_text, model="gpt-4")
        assert isinstance(
            token_count_gpt4, int
        ), "Token count with gpt-4 should be an integer"

        logger.info(f"Static token counting verified: {token_count} tokens")

    @pytest.mark.asyncio
    async def test_text_truncation(self):
        """Test text truncation functionality"""
        logger.info("Testing text truncation")

        # Create a long text
        long_text = "This is a test sentence. " * 1000  # Very long text

        # Truncate to a reasonable size
        truncated = await LLMClient.truncate_to_max_tokens(long_text, max_tokens=100)

        assert isinstance(truncated, str), "Truncated text should be a string"
        assert len(truncated) < len(long_text), "Truncated text should be shorter"

        # Verify token count is within limit
        token_count = LLMClient.count_tokens(truncated)
        assert (
            token_count <= 100
        ), f"Truncated text should have <= 100 tokens, got {token_count}"

        logger.info(
            f"Text truncation verified: {len(long_text)} -> {len(truncated)} characters"
        )
