#! /usr/bin/env python3.11

# ==========================================================================
#  Copyright (c) Orison AI, 2024.
# ==========================================================================

import os
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Environment:
    """Centralized environment configuration - loaded once at startup"""

    # OpenAI
    openai_api_key: str

    # Qdrant
    qdrant_url: str
    qdrant_api_key: str

    # Firebase
    firebase_credentials_json: Optional[str]

    # LangSmith (optional)
    langchain_api_key: Optional[str] = None
    langsmith_endpoint: Optional[str] = None

    # Google Scholar rate limiting
    scholar_requests_per_minute: int = 60
    scholar_max_depth: int = 1
    scholar_max_network_size: int = 10

    @classmethod
    def load(cls) -> "Environment":
        """Load environment variables once at startup"""

        # Required variables
        required_vars = ["OPENAI_API_KEY", "QDRANT_URL", "QDRANT_API_KEY"]
        missing = [var for var in required_vars if not os.getenv(var)]

        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")

        return cls(
            openai_api_key=os.environ["OPENAI_API_KEY"],
            qdrant_url=os.environ["QDRANT_URL"],
            qdrant_api_key=os.environ["QDRANT_API_KEY"],
            firebase_credentials_json=os.getenv("FIREBASE_CREDENTIALS_JSON"),
            langchain_api_key=os.getenv("LANGCHAIN_API_KEY"),
            langsmith_endpoint=os.getenv("LANGSMITH_ENDPOINT"),
            scholar_requests_per_minute=int(
                os.getenv("SCHOLAR_REQUESTS_PER_MINUTE", "5")
            ),
            scholar_max_depth=int(os.getenv("SCHOLAR_MAX_DEPTH", "1")),
            scholar_max_network_size=int(os.getenv("SCHOLAR_MAX_NETWORK_SIZE", "20")),
        )


# Global environment instance - loaded once
ENV: Optional[Environment] = None


def get_env() -> Environment:
    """Get the global environment instance"""
    global ENV
    if ENV is None:
        ENV = Environment.load()
        logger.info("Environment configuration loaded")
    return ENV
