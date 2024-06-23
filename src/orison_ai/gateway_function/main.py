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
import logging
import asyncio
from flask import Request

# GCP
from functions_framework import create_app, http

# Firebase
from firebase_admin import auth

# Internal
from or_store.firebase import get_firebase_admin_app
from fetch_scholar import FetchScholar

from summarize import Summarize
from vectorize_files import VectorizeFiles
from gateway import GatewayRequestType, router


logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

firebase_app = None
routes = None


def init_firebase():
    global firebase_app

    if firebase_app:
        _logger.info("Firebase admin app already created")
    else:
        _logger.info("Getting firebase admin app.")
        firebase_app = get_firebase_admin_app()
    _logger.info("Getting firebase admin app....DONE")


def init_routes():
    global routes

    if routes:
        _logger.info("Routes already created")
    else:
        _logger.info("Initializing routes")
        routes = {
            GatewayRequestType.GOOGLE_SCHOLAR: FetchScholar(),
            GatewayRequestType.VECTORIZE_FILES: VectorizeFiles(),
            GatewayRequestType.SUMMARIZE: Summarize(),
        }
        _logger.info("Initializing routes....DONE")


def verify_bearer_token(request: Request):
    """Verifies the Bearer token from the Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise ValueError("Authorization header missing")

    token = auth_header.split(" ")[1]
    decoded_token = auth.verify_id_token(token)
    return decoded_token


@http
def gateway_function_staging(request: Request):
    _logger.info(f"Gateway received request: {request.json}")

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
        init_firebase()
        verify_bearer_token(request)
        init_routes()

        _logger.info("Token verified. Sending request to router.")
        result = asyncio.run(router(routes, request))
        code = result["status"]

        return (
            {
                "data": (
                    {"requestId": "request-12345"}
                    if code == 200
                    else {"Internal Server Error": result["message"]}
                )
            },
            code,
            headers,
        )

    except ValueError as ve:
        # Handle token verification errors
        _logger.error(f"Authentication error: {ve}")
        return ({"error": "Unauthorized"}, 401, headers)

    except Exception as e:
        # Make sure we add the CORS headers to any error messages too.
        _logger.error(f"ERROR: {e}")
        return ({"error": str(e)}, 500, headers)


if __name__ == "__main__":
    app = create_app(gateway_function_staging)
    app.run(port=int(os.environ.get("PORT", 8080)), host="0.0.0.0", debug=True)
