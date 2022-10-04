#!/usr/bin/env python
import functools
import logging
from dataclasses import asdict
from typing import Callable, Optional

import simplejson as json  # type: ignore
from lib.exceptions import (
    EnvironmentConfigError,
    NotFound,
    OperationsError,
    ValidationError,
)
from lib.logging import request_context
from lib.protocols import Scheduler

from .data import Response, ScheduleRequest

logger = logging.getLogger(__name__)


def create_response(data: Optional[dict] = None, status_code: int = 200) -> Response:
    body = json.dumps(data) if data else ""
    response = Response(status_code=status_code, body=body)
    return response


def handle_exceptions(function: Callable[..., Response]):
    @functools.wraps(function)
    def wrapper(*args, **kwargs) -> dict:
        try:
            response = function(*args, **kwargs)
        except ValidationError as e:
            response = create_response(status_code=400, data={"message": e.message})
        except EnvironmentConfigError as e:
            response = create_response(status_code=500, data={"message": e.message})
        except NotFound as e:
            response = create_response(status_code=400, data={"message": e.message})
        except OperationsError as e:
            response = create_response(status_code=501, data={"message": e.message})
        except Exception as e:
            response = create_response(status_code=502, data={"message": str(e)})

        logger.info(f"Returning response: {response}", extra=request_context)
        return asdict(response)

    return wrapper


class RequestsHandler:
    @classmethod
    @handle_exceptions
    def add_schedule_item(cls, request_payload: dict, scheduler: Scheduler) -> Response:

        logger.info(f"Adding schedule item: {request_payload}", extra=request_context)

        # initialize schedule request
        schedule_request = ScheduleRequest(**request_payload)

        # create schedule item
        schedule_item = scheduler.add_to_schedule(schedule_request)

        # create response
        return create_response(asdict(schedule_item))

    @classmethod
    @handle_exceptions
    def get_schedule_item(cls, request_payload: dict, scheduler: Scheduler) -> Response:

        logger.info(
            f"Retrieving schedule item: {request_payload}", extra=request_context
        )

        # validation
        if "schedule_id" not in request_payload:
            raise ValidationError(
                value=str(request_payload), message="Request not valid"
            )

        schedule_id = request_payload["schedule_id"]
        schedule_item = scheduler.get_schedule_item(schedule_id)
        return create_response(asdict(schedule_item))

    @classmethod
    @handle_exceptions
    def remove_schedule_item(
        cls, request_payload: dict, scheduler: Scheduler
    ) -> Response:

        logger.info(f"Removing schedule item: {request_payload}", extra=request_context)

        # validation
        if "schedule_id" not in request_payload:
            raise ValidationError(
                value=str(request_payload), message="Request not valid"
            )

        schedule_id = request_payload["schedule_id"]
        scheduler.remove_from_schedule(schedule_id)
        return create_response()

    @classmethod
    @handle_exceptions
    def update_schedule_item(
        cls, request_payload: dict, scheduler: Scheduler
    ) -> Response:

        logger.info(f"Updating schedule item: {request_payload}", extra=request_context)

        if "schedule_id" not in request_payload:
            raise ValidationError(
                value=str(request_payload), message="Request not valid"
            )

        schedule_id = request_payload["schedule_id"]
        del request_payload["schedule_id"]
        schedule_request = ScheduleRequest(**request_payload)

        # create schedule item
        schedule_item = scheduler.update_schedule_item(schedule_id, schedule_request)

        # create response
        return create_response(asdict(schedule_item))
