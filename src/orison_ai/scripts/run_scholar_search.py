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
from orison_ai.services.scholar.scholar_service import ScholarService
from orison_ai.services.scholar.config import ScholarServiceConfig
from orison_ai.database.firebase_config import FirestoreClient
from orison_ai.database.firestore_clients import (
    GoogleScholarClient,
    GoogleScholarNetworkClient,
)

logger = logging.getLogger(__name__)


async def search_and_save_scholar_data():
    """Search Google Scholar, build network, and save to Firestore"""

    # Test attorney and applicant IDs
    attorney_id = "test_orison_attorney"
    applicant_id = "test_orison_applicant"

    logger.info(
        f"Starting Google Scholar search for attorney: {attorney_id}, applicant: {applicant_id}"
    )

    # Initialize configuration
    config = ScholarServiceConfig.from_env()

    # Initialize services
    scholar_service = ScholarService(config)
    scholar_client = GoogleScholarClient()
    network_client = GoogleScholarNetworkClient()

    try:
        # Search for scholar info (using a test name)
        author_name = "Rishi Malhan"  # Test author name
        TEST_SCHOLAR_ID = "QW93AM0AAAAJ"
        scholar_link = f"https://scholar.google.com/citations?user={TEST_SCHOLAR_ID}"
        logger.info(f"Searching for scholar: {author_name}")

        scholar_info = await scholar_service.get_scholar_info(
            attorney_id=attorney_id,
            applicant_id=applicant_id,
            scholar_link=scholar_link,
            author_name=author_name,
        )

        if not scholar_info:
            logger.error(f"No scholar info found for: {author_name}")
            return

        logger.info(
            f"Found scholar info: {scholar_info.author.name} (ID: {scholar_info.author.scholar_id})"
        )
        logger.info(f"Scholar summary: {scholar_info.to_json()}")

        # Build network database object
        logger.info("Building network database object...")
        network_db = await scholar_service.build_network_database(
            root_scholar_id=TEST_SCHOLAR_ID,
            author_name=author_name,
            max_depth=5,
            max_size=10,
        )

        if not network_db:
            logger.error("Failed to build network database object")
            return

        logger.info(f"Network DB summary: {network_db.to_json()}")

        # Save to Firestore using proper clients
        logger.info("Saving data to Firestore...")

        # Save scholar info using GoogleScholarClient
        scholar_doc_id = await scholar_client.insert(
            attorney_id=attorney_id, applicant_id=applicant_id, doc=scholar_info
        )
        logger.info(f"Saved scholar info with ID: {scholar_doc_id}")

        # Save network data using GoogleScholarNetworkClient
        network_doc_id = await network_client.insert(
            attorney_id=attorney_id, applicant_id=applicant_id, doc=network_db
        )
        logger.info(f"Saved network data with ID: {network_doc_id}")

        logger.info("Google Scholar search and save completed successfully!")
        logger.info(
            f"Data saved under attorney: {attorney_id}, applicant: {applicant_id}"
        )

    except Exception as e:
        logger.error(f"Error in scholar search and save: {e}")
        import traceback

        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise


async def main():
    """Main function to run scholar search and retrieval"""

    logger.info("Starting Google Scholar search and save script")

    # Search and save data
    await search_and_save_scholar_data()

    logger.info("Script completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
