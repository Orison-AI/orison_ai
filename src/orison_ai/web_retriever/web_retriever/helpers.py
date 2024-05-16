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

import traceback
import logging

# Internal

from web_retriever.google_scholar import get_google_scholar_info
from web_retriever.models import GoogleScholarRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fetch_scholar_helper(user_request: GoogleScholarRequest):
    try:
        scholar_info = await get_google_scholar_info(
            attorney_id=user_request.attorney_id,
            applicant_id=user_request.applicant_id,
            scholar_link=user_request.scholar_link,
        )
    except Exception as e:
        logger.error(
            f"Failed to generate google scholar database. Error: {traceback.format_exc(e)}"
        )
        raise e
    try:
        if scholar_info is not None:
            logger.info("Google scholar data saved to json file")
            return scholar_info.to_json()
    except Exception as e:
        logger.error(
            f"Failed to insert google scholar data. Error: {traceback.format_exc(e)}"
        )
        raise e
