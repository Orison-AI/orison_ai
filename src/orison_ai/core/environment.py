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
from dataclasses import dataclass
from typing import Optional

# Internal

from database.firebase_config import SecretManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Environment:
    """Centralized environment configuration - loaded once at startup"""

    # OpenAI
    openai_api_key: Optional[str] = None

    # Qdrant
    qdrant_url: Optional[str] = None
    qdrant_api_key: Optional[str] = None

    # Firebase
    firebase_credentials_json: Optional[str] = None

    # LangSmith (optional)
    langchain_api_key: Optional[str] = None
    langchain_project: Optional[str] = None
    langchain_tracing: Optional[str] = None
    langchain_tracing_v2: Optional[str] = None  # LangSmith v2

    # SerpAPI (optional)
    serpapi_key: Optional[str] = None

    # Google Scholar rate limiting
    scholar_requests_per_minute: int = 10
    scholar_max_depth: int = 3
    scholar_max_network_size: int = 20

    @classmethod
    def load(cls) -> "Environment":
        """Load environment variables once at startup with liberal validation"""

        # Try to import SecretManager for fallback
        secret_manager = None
        try:
            secret_manager = SecretManager()
            logger.info("SecretManager available for fallback")
        except ImportError:
            logger.warning(
                "SecretManager not available, using environment variables only"
            )
        except Exception as e:
            logger.warning(f"SecretManager initialization failed: {e}")

        def get_value(
            key: str, default: Optional[str] = None, skip_secret_manager: bool = False
        ) -> Optional[str]:
            """Get value with hierarchy: Secret Manager → Environment Variables → Default"""
            # Try environment variable first
            value = os.getenv(key)
            if value:
                logger.debug(f"Found {key} in environment variables")
                return value

            # Try Secret Manager if available and not skipped
            if secret_manager and not skip_secret_manager:
                try:
                    value = secret_manager.get_secret(key)
                    if value:
                        logger.debug(f"Found {key} in Secret Manager")
                        return value
                except Exception as e:
                    logger.debug(f"Secret Manager lookup failed for {key}: {e}")

            # Return default if provided
            if default is not None:
                logger.debug(f"Using default value for {key}")
                return default

            logger.warning(f"No value found for {key}")
            return None

        openai_key = get_value("OPENAI_API_KEY")
        qdrant_url_val = get_value("QDRANT_URL")
        qdrant_key = get_value("QDRANT_API_KEY")
        firebase_creds = get_value("FIREBASE_CREDENTIALS")

        if not openai_key:
            logger.warning("OPENAI_API_KEY not found - OpenAI services will not work")
        if not qdrant_url_val:
            logger.warning("QDRANT_URL not found - Vector search will not work")
        if not qdrant_key:
            logger.warning("QDRANT_API_KEY not found - Vector search will not work")
        if not firebase_creds:
            logger.warning(
                "FIREBASE_CREDENTIALS not found - Firebase services will not work"
            )

        return cls(
            openai_api_key=openai_key,
            qdrant_url=qdrant_url_val,
            qdrant_api_key=qdrant_key,
            firebase_credentials_json=firebase_creds,
            langchain_api_key=get_value("LANGCHAIN_API_KEY"),
            langchain_project=get_value(
                "LANGCHAIN_PROJECT", default="orison_ai", skip_secret_manager=True
            ),
            langchain_tracing=get_value(
                "LANGCHAIN_TRACING", default="true", skip_secret_manager=True
            ),
            langchain_tracing_v2=get_value(
                "LANGCHAIN_TRACING_V2", default="true", skip_secret_manager=True
            ),
            serpapi_key=get_value("SERPAPI_KEY"),
            scholar_requests_per_minute=int(
                get_value("SCHOLAR_REQUESTS_PER_MINUTE", "10", skip_secret_manager=True)
            ),
            scholar_max_depth=int(
                get_value("SCHOLAR_MAX_DEPTH", "3", skip_secret_manager=True)
            ),
            scholar_max_network_size=int(
                get_value("SCHOLAR_MAX_NETWORK_SIZE", "20", skip_secret_manager=True)
            ),
        )


# Global environment instance - loaded once
ENV: Optional[Environment] = None


def get_env() -> Environment:
    """Get the global environment instance"""
    global ENV
    if ENV is None:
        ENV = Environment.load()
        logger.info("Environment configuration loaded")
    os.environ["LANGCHAIN_PROJECT"] = ENV.langchain_project
    os.environ["LANGCHAIN_TRACING"] = ENV.langchain_tracing
    os.environ["LANGCHAIN_TRACING_V2"] = ENV.langchain_tracing_v2
    os.environ["LANGCHAIN_API_KEY"] = ENV.langchain_api_key
    return ENV
