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

from or_retriever.helpers import fetch_scholar_helper
from or_store.models import GoogleScholarRequest
from or_store.google_scholar_client import GoogleScholarClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def handle_request(request):
    # Parse the incoming JSON request data
    request_json = request.get_json()

    # Convert JSON to UserRequest dataclass
    if request_json:
        user_request = GoogleScholarRequest(**request_json)
    else:
        return {"message": "Bad Request", "status": 400}

    # Download the Google Scholar page
    try:
        scholar_info = await fetch_scholar_helper(user_request)
        client = GoogleScholarClient()
        id = await client.insert(scholar_info)
        return {
            "message": f"Scholar info:\n{scholar_info.to_json()} \nsaved with ID: {id}.",
            "status": "200",
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
