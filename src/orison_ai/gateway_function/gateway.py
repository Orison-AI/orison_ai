from dataclasses import dataclass
from enum import Enum
from typing import Any, Coroutine

from request_handler import (
    RequestHandler,
    ErrorResponse,
    OKResponse,
)


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
    VECTORIZE_FILES = "vectorize-files"
    SUMMARIZE = "summarize"


@dataclass
class GatewayRequest:
    # Dataclass to represent the incoming request to the gateway
    or_request_type: GatewayRequestType
    or_request_payload: dict

    def __post_init__(self):
        self.or_request_type = _str_to_enum(GatewayRequestType, self.or_request_type)


def router(
    routes: dict[GatewayRequestType, RequestHandler], request
) -> Coroutine[Any, Any, Any]:
    # Function to route the incoming request to the appropriate handler based the given routes

    async def as_async(err):
        return err

    # Parse the incoming JSON request data
    request_json = request.get_json()

    if not request_json:
        return as_async(ErrorResponse("Could not parse input to JSON"))
    try:
        gateway_request = GatewayRequest(**(request_json["data"]))
    except Exception as e:
        return as_async(ErrorResponse(f"Could not parse input to GatewayRequest: {e}"))
    if gateway_request.or_request_type not in routes:
        return as_async(ErrorResponse("Requested route not implemented"))
    return routes[gateway_request.or_request_type].handle_request(
        gateway_request.or_request_payload
    )
