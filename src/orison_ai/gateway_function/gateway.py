import dataclasses
from dataclasses import dataclass
from enum import Enum
from typing import Callable


def _str_to_enum(enum_class, string):
    try:
        return enum_class[string]
    except KeyError:
        raise ValueError(f"'{string}' is not a valid member of {enum_class}")


class GatewayRequestType(Enum):
    GOOGLE_SCHOLAR = "google_scholar"


@dataclass
class GatewayRequest:
    or_request_type: GatewayRequestType
    or_request_payload: dict

    def __post_init__(self):
        self.or_request_type = _str_to_enum(GatewayRequestType, self.or_request_type)


def router(routes: dict[GatewayRequestType, Callable[[dict], dict]], request) -> dict:
    # Parse the incoming JSON request data
    request_json = request.get_json()

    if not request_json:
        return {"message": "Could not parse input to JSON", "status": 400}
    try:
        gateway_request = GatewayRequest(**request_json)
    except Exception as e:
        return {
            "message": f"Could not parse input to GatewayRequest: {e}",
            "status": 400,
        }
    if not gateway_request.or_request_type in routes:
        return {"message": "Requested route not implemented", "status": 400}
    return routes[gateway_request.or_request_type](gateway_request.or_request_payload)
