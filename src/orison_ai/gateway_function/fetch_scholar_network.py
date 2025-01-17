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

from or_store.models import SimplifiedScholarSummary, GoogleScholarNetworkDB
from or_store.db_interfaces import (
    GoogleScholarNetworkClient,
)
from or_retriever.google_scholar import gather_network, extract_user


class FetchScholarNetwork(RequestHandler):
    def __init__(self):
        super().__init__(str(self.__class__.__qualname__))

    async def handle_request(self, request_json):
        # Convert JSON to UserRequest dataclass
        if request_json:
            attorney_id = request_json["attorneyId"]
            applicant_id = request_json["applicantId"]
            scholar_link = request_json["scholarLink"]

            scholar_id = extract_user(scholar_link)
            seen_scholar_ids = set()
            scholar_summaries_tmp = await gather_network(
                scholar_id, depth=1, seen_scholar_ids=seen_scholar_ids
            )
            simplified_scholar_summaries = list(
                map(
                    lambda summary: SimplifiedScholarSummary(
                        name=summary.name,
                        scholar_id=summary.scholar_id,
                        hindex=summary.hindex,
                        citations=summary.citedby,
                        publication_count=summary.publication_count,
                    ),
                    scholar_summaries_tmp,
                )
            )
            # scholar_summaries = list(map(simplified_scholar_summary, scholar_summaries_tmp))
            scholar_network_entry = GoogleScholarNetworkDB(
                network=simplified_scholar_summaries
            )
        else:
            return ErrorResponse("Could not parse input to JSON")

        # Attempt connection to the database
        try:
            client = GoogleScholarNetworkClient()
        except Exception as e:
            message = f"Failed to connect to the database. Error: {e}"
            self.logger.error(message)
            return ErrorResponse(f"Internal Server Error: {message}")

        # Insert data into scholar network database
        try:
            scholar_network_entry.attorney_id = attorney_id
            scholar_network_entry.applicant_id = applicant_id
            id = await client.insert(
                attorney_id=attorney_id,
                applicant_id=applicant_id,
                doc=scholar_network_entry,
            )
            return OKResponse(
                f"Scholar info:\n{scholar_network_entry.to_json()} \nsaved with ID: {id}."
            )
        except Exception as e:
            message = f"Failed to write Google Scholar network. Error: {e}"
            self.logger.error(message)
            return ErrorResponse(f"Internal Server Error: {message}", 500)
