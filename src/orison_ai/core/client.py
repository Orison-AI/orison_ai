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
import logging
import tiktoken
from typing import AsyncIterator, Dict, List
from contextlib import asynccontextmanager
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.rate_limiters import InMemoryRateLimiter
from pydantic import SecretStr
import langsmith

# Internal

from core.config import LLMConfig, AppConfig
from database.secrets import OrisonSecrets


class LLMClient:
    """LLM client with streaming support - maintains exact original behavior"""

    # Original system role preserved exactly
    SYSTEM_ROLE = """
    You are a helpful, respectful and honest assistant.\
    Always answer as helpfully as possible and follow ALL given instructions.\
    Do not speculate or make up information.\
    Use bullet points to list multiple items using numbers.\
    Break your response into paragraphs for better readability.\
    """

    def __init__(
        self, secrets: OrisonSecrets, config: LLMConfig, app_config: AppConfig
    ):
        self.config = config
        self.app_config = app_config
        self.logger = logging.getLogger(__name__)

        # Configure LangSmith if available
        try:
            # Get environment for LangSmith config (includes Secret Manager)
            from core.environment import get_env

            env = get_env()

            # Check if LangSmith is configured via environment or Secret Manager
            if env.langchain_api_key or app_config.api_key or app_config.endpoint:
                # Set environment variables for LangSmith
                if env.langchain_api_key:
                    os.environ["LANGCHAIN_API_KEY"] = env.langchain_api_key
                elif app_config.api_key:
                    os.environ["LANGCHAIN_API_KEY"] = app_config.api_key

                if env.langsmith_endpoint or app_config.endpoint:
                    os.environ["LANGCHAIN_ENDPOINT"] = (
                        env.langsmith_endpoint or app_config.endpoint
                    )

                if env.langchain_project or app_config.project:
                    os.environ["LANGCHAIN_PROJECT"] = (
                        env.langchain_project or app_config.project or "orison-ai"
                    )

                self.logger.info("LangSmith tracing configured successfully")
                self.logger.info(
                    f"Project: {env.langchain_project or app_config.project or 'orison-ai'}"
                )
                self.logger.info(
                    f"Endpoint: {env.langsmith_endpoint or app_config.endpoint or 'Default'}"
                )
            else:
                self.logger.info("LangSmith not configured - skipping tracing setup")
        except Exception as e:
            self.logger.warning(f"Failed to configure LangSmith: {e}")

        # Rate limiter
        self._rate_limiter = InMemoryRateLimiter(
            requests_per_second=config.requests_per_second,
            check_every_n_seconds=0.1,
            max_bucket_size=config.max_bucket_size,
        )

        # LLM client
        self.llm = ChatOpenAI(
            api_key=SecretStr(secrets.openai_api_key),
            model=config.model,
            temperature=config.temperature,
            max_completion_tokens=config.max_tokens,
            timeout=config.timeout,
            rate_limiter=self._rate_limiter,
            streaming=True,
        )

        # Embeddings client - rate limiting handled via context manager
        self.embeddings = OpenAIEmbeddings(
            api_key=SecretStr(secrets.openai_api_key),
            model=config.embedding_model,
            max_retries=config.max_retries,
        )

        # Tokenizer
        self._tokenizer = tiktoken.encoding_for_model(config.model)

    async def stream_response(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncIterator[str]:
        """Stream LLM response"""
        self.logger.info(f"Streaming response for {len(messages)} messages")

        formatted_messages = [
            (
                SystemMessage(content=msg["content"])
                if msg["role"] == "system"
                else HumanMessage(content=msg["content"])
            )
            for msg in messages
        ]

        async for chunk in self.llm.astream(formatted_messages, **kwargs):
            if hasattr(chunk, "content") and chunk.content:
                yield chunk.content

    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate complete LLM response"""
        chunks = []
        async for chunk in self.stream_response(messages, **kwargs):
            chunks.append(chunk)
        return "".join(chunks)

    async def embed_query(self, text: str) -> List[float]:
        """Generate embeddings for a query with rate limiting"""
        self.logger.info(f"Embedding query: {len(text)} characters")
        async with self.rate_limited_context():
            return await self.embeddings.aembed_query(text)

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents with rate limiting"""
        self.logger.info(f"Embedding {len(texts)} documents")
        async with self.rate_limited_context():
            return await self.embeddings.aembed_documents(texts)

    @staticmethod
    def count_tokens(text: str, model: str = "gpt-4o") -> int:
        """Calculate tokens in text - preserved from original"""
        tokenizer = tiktoken.encoding_for_model(model)
        tokens = tokenizer.encode(text)
        return len(tokens)

    @staticmethod
    async def truncate_to_max_tokens(
        text: str, max_tokens: int = 120000, model: str = "gpt-4o"
    ) -> str:
        """Truncate text to max tokens - preserved from original"""
        tokenizer = tiktoken.encoding_for_model(model)
        tokens = tokenizer.encode(text)

        if len(tokens) > max_tokens:
            tokens_to_remove = len(tokens) - max_tokens
            truncated_tokens = tokens[:-tokens_to_remove]
            return tokenizer.decode(truncated_tokens)
        return text

    @asynccontextmanager
    async def rate_limited_context(self):
        """Context manager for rate limiting"""
        await self._rate_limiter.aacquire()
        try:
            yield
        finally:
            pass
