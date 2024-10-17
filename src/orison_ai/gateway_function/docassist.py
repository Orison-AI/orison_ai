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
from typing import List

# Internal

from request_handler import RequestHandler, OKResponse, ErrorResponse
from or_store.firebase import OrisonSecrets
from or_store.firebase import FireStoreDB
from exceptions import OrisonMessenger_INITIALIZATION_FAILED
from or_llm.orison_messenger import OrisonMessenger, Prompt, DetailLevel


class DocAssist(RequestHandler):
    def __init__(self):
        super().__init__(str(self.__class__.__qualname__))

    def initialize(self, secrets):
        try:
            self._orison_messenger = OrisonMessenger(secrets=secrets)
        except Exception as e:
            raise OrisonMessenger_INITIALIZATION_FAILED(exception=e)

    async def handle_request(self, request_json):
        try:
            self.logger.info(f"Handling docassist request: {request_json}")
            attorney_id = request_json["attorneyId"]
            applicant_id = request_json["applicantId"]
            prompt_message = request_json["message"]
            tag = request_json["bucket"]
            secrets = OrisonSecrets.from_attorney_applicant(attorney_id, applicant_id)
            self.logger.info("Initializing docassist with secrets")
            self.initialize(secrets)
            prompt = Prompt(
                question=prompt_message, tag=tag, detail_level=DetailLevel.MODERATE
            )
            response = await self._orison_messenger.request(prompt)
            output_message = response.answer + f"\t(Source: {response.source})"
        except Exception as e:
            message = f"Error generating response from DocAssist. Error code: {type(e).__name__}. Error message: {e}"
            self.logger.error(message, exc_info=True)
            return ErrorResponse(message)
        return OKResponse(output_message)
