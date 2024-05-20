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
import asyncio
from functions_framework import create_app, http

# Internal

from or_store.models import GoogleScholarRequest
from or_store.google_scholar_client import GoogleScholarClient
from or_retriever.google_scholar import get_google_scholar_info

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
            logger.info("Google scholar data class initialized")
            return scholar_info
    except Exception as e:
        logger.error(
            f"Failed to insert google scholar data. Error: {traceback.format_exc(e)}"
        )
        raise e


async def handle_request(request):
    # Parse the incoming JSON request data
    request_json = request.get_json()

    # Convert JSON to UserRequest dataclass
    if request_json:
        user_request = GoogleScholarRequest(**request_json)
    else:
        return {"message": "Bad Request", "status": 400}

    # Attempt connection to the database
    try:
        client = GoogleScholarClient()
    except Exception as e:
        message = f"Failed to connect to the database. Error: {traceback.format_exc(e)}"
        logger.error(message)
        return {"message": f"Internal Server Error: {message}", "status": 500}

    # Download the Google Scholar page
    try:
        scholar_info = await fetch_scholar_helper(user_request)
        id = await client.insert(scholar_info)
        return {
            "message": f"Scholar info:\n{scholar_info.to_json()} \nsaved with ID: {id}.",
            "status": 200,
        }
    except Exception as e:
        message = (
            f"Failed to download Google Scholar page. Error: {traceback.format_exc(e)}"
        )
        logger.error(message)
        return {"message": f"Internal Server Error: {message}", "status": 500}


@http
def fetch_scholar(request):
    return asyncio.run(handle_request(request))


if __name__ == "__main__":
    app = create_app(fetch_scholar)
