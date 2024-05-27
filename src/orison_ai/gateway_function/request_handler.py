import logging

logging.basicConfig(level=logging.INFO)


def OKResponse(message, status_code=200):
    return {"message": f"{message}", "status": status_code}


def ErrorResponse(message, status_code=400):
    return {"message": f"{message}", "status": status_code}


class RequestHandler:
    def __init__(self, request_type):
        self.logger = logging.getLogger(request_type)

    async def handle_request(self, request: dict):
        return ErrorResponse("Not implemented")
