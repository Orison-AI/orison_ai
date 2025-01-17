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

# External

import asyncio
from request_handler import (
    RequestHandler,
    ErrorResponse,
    OKResponse,
)

# Internal

from or_store.models import GoogleScholarRequest
from or_store.db_interfaces import (
    GoogleScholarClient,
)
from or_retriever.google_scholar import (
    get_google_scholar_info,
)


class FetchScholar(RequestHandler):
    def __init__(self):
        super().__init__(str(self.__class__.__qualname__))

    async def fetch_scholar_helper_(self, user_request: GoogleScholarRequest):
        try:
            scholar_info = await get_google_scholar_info(
                attorney_id=user_request.attorney_id,
                applicant_id=user_request.applicant_id,
                scholar_link=user_request.scholar_link,
            )
        except Exception as e:
            self.logger.error(f"Failed to generate google scholar database. Error: {e}")
            raise e
        try:
            if scholar_info is not None:
                self.logger.info("Google scholar data class initialized")
                return scholar_info
        except Exception as e:
            self.logger.error(f"Failed to insert google scholar data. Error: {e}")
            raise e

    async def handle_request(self, request_json):
        # Convert JSON to UserRequest dataclass
        if request_json:
            user_request = GoogleScholarRequest(
                attorney_id=request_json["attorneyId"],
                applicant_id=request_json["applicantId"],
                scholar_link=request_json["scholarLink"],
            )
        else:
            return ErrorResponse("Could not parse input to JSON")

        # Attempt connection to the database
        try:
            client = GoogleScholarClient()
        except Exception as e:
            message = f"Failed to connect to the database. Error: {e}"
            self.logger.error(message)
            return ErrorResponse(f"Internal Server Error: {message}")

        # Download the Google Scholar page
        try:
            scholar_info = await self.fetch_scholar_helper_(user_request)
            id = await client.insert(
                attorney_id=user_request.attorney_id,
                applicant_id=user_request.applicant_id,
                doc=scholar_info,
            )
            return OKResponse(
                f"Scholar info:\n{scholar_info.to_json()} \nsaved with ID: {id}."
            )
        except Exception as e:
            message = f"Failed to download Google Scholar page. Error: {e}"
            self.logger.error(message)
            return ErrorResponse(f"Internal Server Error: {message}", 500)
