#!/usr/bin/env python
import json
import logging
import os

from pythonjsonlogger import jsonlogger  # type: ignore


def _setup_logging(log_level: str = "INFO") -> None:
    logger = logging.getLogger()
    log_level = os.environ.get("LOGGING_LEVEL", log_level)

    logger.setLevel(log_level)
    json_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    json_handler.setFormatter(formatter)
    logger.addHandler(json_handler)
    logger.removeHandler(logger.handlers[0])


class RequestContext(dict):

    aws_request_id_key = "aws_request_id"
    frontend_request_id_key = "frontend_request_id"

    def __init__(self):
        self[self.aws_request_id_key] = ""
        self[self.frontend_request_id_key] = ""

    def populate(self, event: dict, context: object) -> None:

        # get aws request id
        aws_rid = event.get("requestContext", {}).get("requestId", "")

        # get frontend request id
        method = event.get("httpMethod", "GET")
        frontend_rid = (
            json.loads(event.get("body", "{}")).get("requestID", "")
            if method == "POST"
            else ""
        )

        # populate dictionary
        self[self.aws_request_id_key] = aws_rid
        self[self.frontend_request_id_key] = frontend_rid


# configure logging and initialize request context
_setup_logging()
request_context: RequestContext = RequestContext()
