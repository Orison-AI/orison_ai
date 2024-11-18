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

# Internal

from request_handler import RequestHandler, OKResponse, ErrorResponse
from or_store.firebase import OrisonSecrets
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
            tag = request_json["tag"]  # List of tags
            filename = request_json["filename"]  # List of filenames
            secrets = OrisonSecrets.from_attorney_applicant(attorney_id, applicant_id)
            self.logger.info("Initializing docassist secrets")
            self.initialize(secrets)
            self.logger.info("Generating docassist prompt")
            prompt = Prompt(
                question=prompt_message,
                tag=tag,
                filename=filename,
                detail_level=DetailLevel.LIGHT,
                applicant_id=applicant_id,
                attorney_id=attorney_id,
            )
            response = await self._orison_messenger.request(prompt, use_memory=True)
            output_message = response.answer + f" (Source: {response.source})"
        except Exception as e:
            message = f"Error generating response from DocAssist. Error code: {type(e).__name__}. Error message: {e}"
            self.logger.error(message, exc_info=True)
            return ErrorResponse(message)
        return OKResponse(output_message)


if __name__ == "__main__":
    import asyncio

    docassist = DocAssist()
    asyncio.run(
        docassist.handle_request(
            {
                "attorneyId": "xlMsyQpatdNCTvgRfW4TcysSDgX2",
                "applicantId": "tYdtBdc7lJHyVCxquubj",
                "message": "Give me a summary of Rishi's skills",
                "tag": [],
                "filename": ["MalhanCV.pdf"],
            }
        )
    )
