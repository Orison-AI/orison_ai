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

import os
import asyncio
import json
from typing import List

# Internal

from request_handler import RequestHandler, OKResponse, ErrorResponse
from or_store.models import ScreeningBuilder
from or_store.story_client import ScreeningClient
from or_store.firebase import OrisonSecrets
from exceptions import OrisonMessenger_INITIALIZATION_FAILED
from or_llm.orison_messenger import (
    OrisonMessenger,
    Prompt,
)


class Summarize(RequestHandler):
    def __init__(self):
        super().__init__(str(self.__class__.__qualname__))

    def initialize(self, secrets):
        try:
            self._orison_messenger = OrisonMessenger(secrets=secrets)
        except Exception as e:
            raise OrisonMessenger_INITIALIZATION_FAILED(exception=e)
        self._screening_client = ScreeningClient()

    @staticmethod
    async def prompts(logger) -> List[Prompt]:
        """
        Load prompts from a JSON file
        :param logger: Logger object
        :return: List of prompts
        """

        local_path: str = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "templates",
            "eb1_a_questionnaire.json",
        )
        prompts = []
        with open(file=local_path, mode="r") as file:
            js = json.load(file)
            for question, detail_level in zip(
                js["question"],
                js["detail_level"],
            ):
                prompts.append(
                    Prompt(question=question, detail_level=detail_level, tag=js["tag"])
                )
            file.close()
        return prompts

    async def summarize(self, prompts: List[Prompt]):
        self.logger.info("Generating screening")
        tasks = [self._orison_messenger.request(prompt) for prompt in prompts]
        results = await asyncio.gather(*tasks)
        screening = ScreeningBuilder()
        for result in results:
            screening.summary.append(result)
        self.logger.info("Generating screening...DONE")
        return screening

    async def handle_request(self, request_json):
        try:
            self.logger.info(f"Handling summarize request: {request_json}")
            attorney_id = request_json["attorneyId"]
            applicant_id = request_json["applicantId"]
            secrets = OrisonSecrets.from_attorney_applicant(attorney_id, applicant_id)
            self.logger.info("Initializing summarizer with secrets")
            self.initialize(secrets)
            prompts = await self.prompts(logger=self.logger)
            self.logger.info("Initializing summarizer with secrets...done")
            screening = await self.summarize(prompts)
            screening.attorney_id = attorney_id
            screening.applicant_id = applicant_id
            self.logger.info("Storing screening in Firestore")
            id = await self._screening_client.insert(
                attorney_id=attorney_id, applicant_id=applicant_id, doc=screening
            )
            self.logger.info(f"Screening stored in Firestore with ID: {id}")
        except Exception as e:
            message = f"Error processing files. Error code: {type(e).__name__}. Error message: {e}"
            self.logger.error(message, exc_info=True)
            return ErrorResponse(message)
        return OKResponse("Success!")


if __name__ == "__main__":
    request_json = {
        "attorneyId": "xlMsyQpatdNCTvgRfW4TcysSDgX2",
        "applicantId": "tYdtBdc7lJHyVCxquubj",
    }
    summarize = Summarize()
    asyncio.run(summarize.handle_request(request_json))
