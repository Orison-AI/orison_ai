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

import logging

logging.basicConfig(level=logging.DEBUG)


def OKResponse(message, status_code=200):
    return {"message": f"{message}", "status": status_code}


def ErrorResponse(message, status_code=400):
    return {"message": f"{message}", "status": status_code}


class RequestHandler:
    def __init__(self, request_type):
        self.logger = logging.getLogger(request_type)

    async def handle_request(self, request: dict):
        return ErrorResponse("Not implemented")
