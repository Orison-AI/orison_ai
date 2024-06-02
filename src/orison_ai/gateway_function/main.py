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
import logging
import asyncio
from flask import Request

# GCP
from functions_framework import create_app, http

# Firebase
from firebase_admin import auth

# Internal
from or_store.firebase import get_firebase_admin_app
from request_handler import RequestHandler
from fetch_scholar import FetchScholar
from summarize import Summarize
from vectorize_files import VectorizeFiles
from gateway import GatewayRequestType, router

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
get_firebase_admin_app()

# These are the routes that the gateway can handle. The router function will use the GatewayRequestType to determine
# which handler to use.
routes: dict[GatewayRequestType, RequestHandler] = {
    GatewayRequestType.GOOGLE_SCHOLAR: FetchScholar(),
    GatewayRequestType.VECTORIZE_FILES: VectorizeFiles(),
    GatewayRequestType.SUMMARIZE: Summarize(),
}


def verify_bearer_token(request: Request):
    """Verifies the Bearer token from the Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise ValueError("Authorization header missing")

    token = auth_header.split(" ")[1]
    decoded_token = auth.verify_id_token(token)
    return decoded_token


@http
def gateway_function(request: Request):
    logging.info(f"Received request: {request.method}")

    # Set CORS headers for the preflight request
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "3600",
        }
        return ("", 204, headers)

    # Set CORS headers for main request
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }

    try:
        verify_bearer_token(request)

        result = asyncio.run(router(routes, request))
        code = result["status"]

        return (
            {"data": {"requestId": "request-12345"} if code == 200 else {}},
            code,
            headers,
        )

    except ValueError as ve:
        # Handle token verification errors
        logger.error(f"Authentication error: {ve}")
        return ({"error": "Unauthorized"}, 401, headers)

    except Exception as e:
        # Make sure we add the CORS headers to any error messages too.
        logger.error(f"ERROR: {e}")
        return ({"error": str(e)}, 500, headers)


if __name__ == "__main__":
    app = create_app(gateway_function)
