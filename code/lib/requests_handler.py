#!/usr/bin/env python
import functools
import json
import logging
from dataclasses import asdict
from typing import Callable

from .data import Response, ScheduleItem, ScheduleRequest
from .exceptions import ValidationError
from .logging import request_context
from .protocols import Scheduler

logger = logging.getLogger(__name__)


class RequestsHandler:
    @staticmethod
    def handler_methods_wrapper(function: Callable[..., Response]):
        @functools.wraps(function)
        def wrapper(*args, **kwargs) -> dict:
            try:
                response = function(*args, **kwargs)
            except ValidationError as e:
                response = Response(status_code=400, body=e.message)

            logger.info(f"Returning response: {response}", extra=request_context)
            return asdict(response)

        return wrapper

    @classmethod
    def _create_response(
        cls, schedule_item: ScheduleItem, status_code: int = 200
    ) -> Response:
        response = Response(status_code=200, body=json.dumps(asdict(schedule_item)))
        return response

    @classmethod
    @handler_methods_wrapper
    def add_schedule_item(
        cls, schedule_request_payload: dict, scheduler: Scheduler
    ) -> Response:
        logger.info(
            f"Handling schedule request payload: {schedule_request_payload}",
            extra=request_context,
        )

        # initialize schedule request
        schedule_request = ScheduleRequest(**schedule_request_payload)

        # create schedule item
        schedule_item = scheduler.create_schedule_item(schedule_request)
        scheduler.add_to_schedule(schedule_item)

        # create response
        return cls._create_response(schedule_item)
