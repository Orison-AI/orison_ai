import logging


class RequestHandler:
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def handle_request(self, request):
        return {"message": f"Internal Server Error: {message}", "status": 500}
