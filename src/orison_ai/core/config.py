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

from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class LLMConfig:
    """LLM configuration settings"""

    model: str = "gpt-4o"
    embedding_model: str = "text-embedding-ada-002"
    temperature: float = 0.2
    max_tokens: int = 4096
    max_retries: int = 5
    timeout: float = 90.0
    requests_per_second: float = 7.0
    max_bucket_size: int = 1


@dataclass
class VectorConfig:
    """Vector database configuration"""

    collection_name: str
    url: str
    api_key: str
    # Search settings
    retrieval_limit: int = 10
    # Vectorization settings
    chunk_size: int = 512
    chunk_overlap: int = 50
    min_token_size: int = 144
    # Qdrant settings
    port: int = 6333
    grpc_port: int = 6333
    https: bool = True
    timeout: int = 10


@dataclass
class AppConfig:
    """Application configuration with local/remote observability options"""

    project: str = "orison-ai"
    # Support for local LangSmith hosting
    endpoint: Optional[str] = None  # None = auto-detect, or set custom endpoint
    api_key: Optional[str] = None
    # Local observability options
    use_local_tracing: bool = False
    local_sqlite_path: Optional[str] = None
    local_web_port: int = 8000

    def __post_init__(self):
        if self.use_local_tracing:
            self._setup_local_tracing()
        else:
            self._setup_remote_tracing()

    def _setup_local_tracing(self):
        """Configure local tracing options"""
        # Option 1: Local SQLite tracing (lightweight)
        if self.local_sqlite_path:
            os.environ["LANGCHAIN_TRACING_V2"] = "false"
            os.environ["LANGCHAIN_CALLBACKS"] = "langchain.callbacks.sqlite"
            os.environ["LANGCHAIN_SQLITE_PATH"] = self.local_sqlite_path
        else:
            # Option 2: Use LangFuse (open-source alternative)
            os.environ["LANGCHAIN_TRACING_V2"] = "false"
            # Configure for local observation without external services
            os.environ.pop("LANGCHAIN_API_KEY", None)
            os.environ.pop("LANGCHAIN_ENDPOINT", None)

    def _setup_remote_tracing(self):
        """Configure remote LangSmith tracing"""
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = self.project

        # Use custom endpoint if provided, otherwise default to LangSmith
        endpoint = self.endpoint or "https://api.smith.langchain.com"
        os.environ["LANGCHAIN_ENDPOINT"] = endpoint

        if self.api_key:
            os.environ["LANGCHAIN_API_KEY"] = self.api_key

    @classmethod
    def for_local_development(cls, sqlite_path: str = "./traces.db"):
        """Factory method for local development setup"""
        return cls(
            project="orison-ai-local",
            use_local_tracing=True,
            local_sqlite_path=sqlite_path,
        )

    @classmethod
    def for_self_hosted_langsmith(cls, endpoint: str, api_key: Optional[str] = None):
        """Factory method for self-hosted LangSmith"""
        return cls(
            project="orison-ai",
            endpoint=endpoint,
            api_key=api_key,
            use_local_tracing=False,
        )
