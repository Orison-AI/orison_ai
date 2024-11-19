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
import json

# Internal

from request_handler import RequestHandler, OKResponse, ErrorResponse
from or_store.firebase import OrisonSecrets
from exceptions import OrisonMessenger_INITIALIZATION_FAILED
from or_llm.orison_messenger import OrisonMessenger
from or_store.db_interfaces import GoogleScholarClient, ScreeningClient, EvidenceClient
from or_store.models import EvidenceBuilder


class EvidenceGenerator(RequestHandler):
    def __init__(self):
        super().__init__(str(self.__class__.__qualname__))

    def initialize(self, secrets):
        try:
            self._orison_messenger = OrisonMessenger(secrets=secrets, max_tokens=16384)
        except Exception as e:
            raise OrisonMessenger_INITIALIZATION_FAILED(exception=e)

    async def _prompt(self, attorney_id, applicant_id):
        scholar_client = GoogleScholarClient()
        screening_client = ScreeningClient()

        # Read the file from the path
        with open(
            os.path.join(
                os.path.dirname(__file__), "templates/cover_letter_template.txt"
            ),
            "r",
        ) as file:
            prompt_message = file.read()
        try:
            screening_info, doc_id = await screening_client.find_top(
                attorney_id=attorney_id, applicant_id=applicant_id
            )
            for qna in screening_info.summary:
                prompt_message += f"\n\nQuestion asked to candidate:\n{qna.question}\nCandidate responded with:\n{qna.answer}"
        except Exception:
            pass
        prompt_message += "\n\n"
        try:
            prompt_message += "Google Scholar information for candidate:\n"
            scholar_info, doc_id = await scholar_client.find_top(
                attorney_id=attorney_id, applicant_id=applicant_id
            )
            scholar_info_str = json.dumps(scholar_info.to_json(), indent=4)
            prompt_message += scholar_info_str
        except Exception:
            pass
        return prompt_message

    async def handle_request(self, request_json):
        try:
            self.logger.info(f"Handling EvidenceGenerator request: {request_json}")
            attorney_id = request_json["attorneyId"]
            applicant_id = request_json["applicantId"]
            secrets = OrisonSecrets.from_attorney_applicant(attorney_id, applicant_id)
            self.logger.info("Initializing EvidenceGenerator secrets")
            self.initialize(secrets)
            self.logger.info("Generating EvidenceGenerator prompt")
            prompt_message = await self._prompt(attorney_id, applicant_id)
            chain_response = await self._orison_messenger._system_chain.ainvoke(
                {"text": prompt_message}
            )
            response = chain_response.get("text")
            evidence_client = EvidenceClient()
            evidence_letter = EvidenceBuilder(summary=response)
            await evidence_client.insert(
                attorney_id=attorney_id,
                applicant_id=applicant_id,
                doc=evidence_letter,
            )
            self.logger.info(f"Generated response from EvidenceGenerator: {response}")
        except Exception as e:
            message = f"Error generating response from EvidenceGenerator. Error code: {type(e).__name__}. Error message: {e}"
            self.logger.error(message, exc_info=True)
            return ErrorResponse(message)
        return OKResponse(response)


if __name__ == "__main__":
    import asyncio

    evidence_generator = EvidenceGenerator()
    asyncio.run(
        evidence_generator.handle_request(
            {
                "attorneyId": "xlMsyQpatdNCTvgRfW4TcysSDgX2",
                "applicantId": "tYdtBdc7lJHyVCxquubj",
            }
        )
    )
