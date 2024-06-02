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
from request_handler import (
    RequestHandler,
    ErrorResponse,
    OKResponse,
)
import os

# Internal
from or_store.firebase_storage import FirebaseStorage


class VectorizeFiles(RequestHandler):
    def __init__(self):
        super().__init__(str(self.__class__.__qualname__))

    @staticmethod
    def _file_path_builder(attorney_id: str, applicant_id: str, file_path: str):
        return "/".join(["documents", "attorneys", attorney_id, "applicants", applicant_id, file_path])

    async def handle_request(self, request_json):
        attorney_id = request_json['attorneyId']
        applicant_id = request_json['applicantId']
        file_path = "research/test.md"

        def _local_path(filepath):
            return f"/tmp/{filepath}"

        await FirebaseStorage.download_file(
            remote_file_path=VectorizeFiles._file_path_builder(attorney_id, applicant_id, file_path),
            local_file_path=_local_path(file_path))
        if os.path.exists(_local_path(file_path)):
            self.logger.info(f"File written to {_local_path(file_path)}")
            with open(_local_path(file_path), "r") as file:
                data = file.read()
                self.logger.info(f"Readback: {data}")
        else:
            self.logger.error(f"File not found at {_local_path(file_path)}")
        self.logger.info(f"Handling vectorize files request: {request_json}")
        return OKResponse("Success!")
