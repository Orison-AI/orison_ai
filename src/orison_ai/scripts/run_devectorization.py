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

import sys
import asyncio
import logging
from pathlib import Path

# Add the parent directory to the path to import orison_ai modules
sys.path.append(str(Path(__file__).parent.parent))

# Internal

from orison_ai.core.environment import get_env
from orison_ai.core.config import VectorConfig, LLMConfig, AppConfig
from orison_ai.database.secrets import OrisonSecrets
from orison_ai.core.client import LLMClient
from orison_ai.storage.vector_store import VectorStore

logger = logging.getLogger(__name__)


async def delete_collection():
    """Delete the test_orison collection and all its vectors"""

    logger.info("Starting collection deletion process")

    # Initialize configuration
    env = get_env()
    config = VectorConfig(
        collection_name="test_orison",
        url=env.qdrant_url,
        api_key=env.qdrant_api_key,
    )

    secrets = OrisonSecrets(
        openai_api_key=env.openai_api_key,
        qdrant_url=env.qdrant_url,
        qdrant_api_key=env.qdrant_api_key,
        collection_name=config.collection_name,
    )

    # Initialize components
    llm_config = LLMConfig()
    app_config = AppConfig()
    llm_client = LLMClient(secrets, llm_config, app_config)
    vector_store = VectorStore(config, llm_client)

    try:
        # Check if collection exists
        collection_exists = await vector_store.async_client.get_collection(
            config.collection_name
        )

        if collection_exists:
            logger.info(
                f"Collection '{config.collection_name}' exists, proceeding with deletion"
            )

            # Delete the entire collection
            await vector_store.async_client.delete_collection(config.collection_name)
            logger.info(
                f"Successfully deleted collection '{config.collection_name}' and all vectors"
            )
        else:
            logger.warning(f"Collection '{config.collection_name}' does not exist")

    except Exception as e:
        logger.error(f"Error deleting collection: {e}")
        raise


async def main():
    """Main function to delete collection and vectors"""

    logger.info("Starting devectorization script")

    # Delete collection
    await delete_collection()

    logger.info("Devectorization completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
