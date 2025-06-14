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
from typing import List

# Internal

from request_handler import RequestHandler, OKResponse, ErrorResponse
from or_store.models import ScreeningBuilder
from or_store.db_interfaces import ScreeningClient
from or_store.firebase import OrisonSecrets
from or_store.firebase import FireStoreDB
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
        Load prompts from Firestore using attorney ID.
        :param logger: Logger object
        """

        prompts = []

        try:
            # Initialize Firestore client
            client = FireStoreDB().client

            # Reference the document in Firestore
            doc_ref = client.collection("templates").document("eb1_a_questionnaire")
            doc = doc_ref.get()

            if doc.exists:
                # Extract data from Firestore document
                js = doc.to_dict()

                # Loop through the task array in the document to extract question, detail_level, and tag
                for task in js.get("task", []):
                    question = task.get("question")
                    detail_level = task.get("detail_level")
                    tag = task.get("tag")

                    # Create a Prompt object and append to the prompts list
                    prompts.append(
                        Prompt(question=question, detail_level=detail_level, tag=tag)
                    )
            else:
                logger.error(f"No questionnaire found for applicant.")

        except Exception as e:
            logger.error(f"Error fetching questionnaire for applicant. {e}")

        return prompts

    async def validate_response(self, prompt):
        response_verification_prompt = f"Here is a question: {prompt.question}.\nHere is the answer: {prompt.answer}.\nIs this answer even a little bit appropriate response to the question? Respond in true or false. no additional text."
        chat_response = await self._orison_messenger._system_chain.ainvoke(
            response_verification_prompt
        )
        response = chat_response.get("text")
        if "false" in response:
            prompt.answer = "Invalid response from AI. Either data is missing or question is not applicable to you."
            prompt.source = "N/A"
        return prompt

    async def summarize(self, prompts: List[Prompt]):
        self.logger.info("Generating screening")

        async def process_prompt(prompt):
            # First, send the request
            response = await self._orison_messenger.request(prompt)
            # Then, validate the response
            validated_response = await self.validate_response(response)
            return validated_response

        # Chain request and validation for each prompt
        tasks = [process_prompt(prompt) for prompt in prompts]
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
            if not prompts:
                message = f"No prompts found for attorney ID: {attorney_id}"
                self.logger.error(message)
                return ErrorResponse(message)
            screening = await self.summarize(prompts)
            screening.attorney_id = attorney_id
            screening.applicant_id = applicant_id
            self.logger.info("Storing screening in Firestore")
            id = await self._screening_client.insert(
                attorney_id=attorney_id, applicant_id=applicant_id, doc=screening
            )
            self.logger.info(f"Screening stored in Firestore with ID: {id}")
        except Exception as e:
            message = f"Error generating summary. Error code: {type(e).__name__}. Error message: {e}"
            self.logger.error(message, exc_info=True)
            return ErrorResponse(message)
        return OKResponse("Success!")


if __name__ == "__main__":
    request_json = {
        "attorneyId": "CHBgG1jdnRMPTt7v5drhMQV2sAU2",
        "applicantId": "3zJYpyzSOYHjrg2wKTf1",
    }
    summarize = Summarize()
    asyncio.run(summarize.handle_request(request_json))
