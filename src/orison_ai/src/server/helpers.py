#! /usr/bin/env python3.10

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

# External

import asyncio
import traceback
import json
import logging
import os
from pathlib import Path

# Internal

from orison_ai.src.utils.constants import VAULT_PATH
from orison_ai.src.core.google_scholar import get_google_scholar_info
from orison_ai.src.core.storybuilder import ingest_documents, analyze_documents
from orison_ai.src.database.google_scholar_client import GoogleScholarClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def download_scholar_helper(
    attorney_id: str, user_id: str, database: str, category: str, parameters: dict
):
    client = GoogleScholarClient()
    scholar_link = parameters.get("scholar_link")
    folder_path = os.path.join(VAULT_PATH, category)  # Where would we fetch this from?
    if scholar_link != "":
        try:
            scholar_info = await get_google_scholar_info(
                attorney_id=attorney_id, user_id=user_id, scholar_link=scholar_link
            )
        except Exception as e:
            logger.error(
                f"Failed to generate google scholar database. Error: {traceback.format_exc(e)}"
            )
            raise e
        try:
            if scholar_info is not None:
                await client.insert(scholar_info)
                with open(
                    os.path.join(folder_path, parameters.get("file_name") + ".json"),
                    "w",
                ) as scholar_file:
                    json.dump(scholar_info.to_json(), indent=2, fp=scholar_file)
                    logger.info("Google scholar data saved to json file")
        except Exception as e:
            logger.error(
                f"Failed to insert google scholar data. Error: {traceback.format_exc(e)}"
            )
            raise e


async def ingest_helper(category: str):
    folder_path = os.path.join(VAULT_PATH, category)  # Where would we fetch this from?
    try:
        await asyncio.to_thread(ingest_documents, Path(folder_path))
    except Exception as e:
        logger.error(f"Failed to ingest documents. Error: {traceback.format_exc(e)}")
        raise e


async def analysis_helper(attorney_id: str, user_id: str, type_of_story: str):
    try:
        await analyze_documents(
            attorney_id=attorney_id, user_id=user_id, type_of_story=type_of_story
        )
    except Exception as e:
        logger.error(f"Failed to analyze documents. Error: {traceback.format_exc(e)}")
        raise e
