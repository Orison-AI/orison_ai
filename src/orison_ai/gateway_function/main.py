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

from functions_framework import create_app, http

# Internal
from request_handler import RequestHandler
from fetch_scholar import FetchScholar
from vectorize_files import VectorizeFiles
from gateway import GatewayRequestType, router

# These are the routes that the gateway can handle. The router function will use the GatewayRequestType to determine
# which handler to use.
routes: dict[GatewayRequestType, RequestHandler] = {
    GatewayRequestType.GOOGLE_SCHOLAR: FetchScholar(),
    GatewayRequestType.VECTORIZE_FILES: VectorizeFiles(),
    GatewayRequestType.SUMMARIZE: RequestHandler("summarize"),
}


@http
def gateway_function(request):
    return asyncio.run(router(routes, request))


if __name__ == "__main__":
    app = create_app(gateway_function)
