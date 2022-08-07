#!/usr/bin/env python
import functools
import json
import logging
from dataclasses import asdict
from typing import Callable, Optional

from .data import Response, ScheduleItem, ScheduleRequest
from .exceptions import EnvironmentConfigError, ValidationError
from .logging import request_context
from .protocols import Scheduler

logger = logging.getLogger(__name__)


class RequestsHandler:
    @staticmethod
    def _handler_methods_wrapper(function: Callable[..., Response]):
        @functools.wraps(function)
        def wrapper(*args, **kwargs) -> dict:
            try:
                response = function(*args, **kwargs)
            except ValidationError as e:
                response = Response(status_code=400, body=e.message)
            except EnvironmentConfigError as e:
                response = Response(status_code=500, body=e.message)

            logger.info(f"Returning response: {response}", extra=request_context)
            return asdict(response)

        return wrapper

    @classmethod
    def _create_response(
        cls, schedule_item: Optional[ScheduleItem] = None, status_code: int = 200
    ) -> Response:

        body = json.dumps(schedule_item) if schedule_item else ""
        response = Response(status_code=200, body=body)
        return response

    @classmethod
    @_handler_methods_wrapper
    def add_schedule_item(cls, request_payload: dict, scheduler: Scheduler) -> Response:

        logger.info(f"Adding schedule item: {request_payload}", extra=request_context)

        # initialize schedule request
        schedule_request = ScheduleRequest(**request_payload)

        # create schedule item
        schedule_item = scheduler.create_schedule_item(schedule_request)
        scheduler.add_to_schedule(schedule_item)

        # create response
        return cls._create_response(schedule_item)

    @classmethod
    @_handler_methods_wrapper
    def get_schedule_item(cls, schedule_id: str, scheduler: Scheduler) -> Response:

        logger.info(f"Retrieving schedule item: {schedule_id}", extra=request_context)
        schedule_item = scheduler.get_schedule_item(schedule_id)
        return cls._create_response(schedule_item)

    @classmethod
    @_handler_methods_wrapper
    def remove_schedule_item(cls, schedule_id: str, scheduler: Scheduler) -> Response:

        logger.info(f"Removing schedule item: {schedule_id}", extra=request_context)
        scheduler.remove_from_schedule(schedule_id)
        return cls._create_response()
