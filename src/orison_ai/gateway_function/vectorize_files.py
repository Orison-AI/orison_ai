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

# Internal


class VectorizeFiles(RequestHandler):
    def __init__(self):
        super().__init__(str(self.__class__.__qualname__))

    async def handle_request(self, request_json):
        self.logger.info(f"Handling vectorize files request: {request_json}")
        return OKResponse("Success!")


if __name__ == "__main__":
    import asyncio

    xx = VectorizeFiles()
    asyncio.run(xx.handle_request("test"))
