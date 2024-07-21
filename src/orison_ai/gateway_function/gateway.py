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
from dataclasses import dataclass
from enum import Enum
from typing import Any, Coroutine

# Internal

from request_handler import (
    RequestHandler,
    ErrorResponse,
)

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


def _str_to_enum(enum_class, string):
    # Helper function to convert a string to an enum member
    for i in enum_class:
        if i.value == string:
            return i
    raise ValueError(f"'{string}' is not a valid member of {enum_class}")


class GatewayRequestType(Enum):
    # Enum class for the different types of requests the gateway can handle
    # See api/orison_api.yaml for more information
    # TODO: Violating DRY principle. This enum is also defined in the OpenAPI spec.
    GOOGLE_SCHOLAR = "process-scholar-link"
    GOOGLE_SCHOLAR_NETWORK = "process-scholar-network"
    VECTORIZE_FILES = "vectorize-files"
    DELETE_FILE_VECTORS = "delete-file-vectors"
    SUMMARIZE = "summarize"


@dataclass
class GatewayRequest:
    # Dataclass to represent the incoming request to the gateway
    or_request_type: GatewayRequestType
    or_request_payload: dict

    def __post_init__(self):
        self.or_request_type = _str_to_enum(GatewayRequestType, self.or_request_type)


async def router(
    routes: dict[GatewayRequestType, RequestHandler], request
) -> Coroutine[Any, Any, Any]:
    # Function to route the incoming request to the appropriate handler based the given routes

    async def as_async(err):
        return err

    # Parse the incoming JSON request data
    request_json = request.get_json()
    _logger.info(f"Router received request: {request_json}")
    if not request_json:
        return await as_async(ErrorResponse("Could not parse input to JSON"))
    try:
        gateway_request = GatewayRequest(**(request_json["data"]))
        _logger.info(f"Parsed GatewayRequest type: {gateway_request}")
    except Exception as e:
        return await as_async(
            ErrorResponse(f"Could not parse input to GatewayRequest: {e}")
        )
    if gateway_request.or_request_type not in routes:
        return await as_async(ErrorResponse("Requested route not implemented"))
    return await routes[gateway_request.or_request_type].handle_request(
        gateway_request.or_request_payload
    )
