#!/usr/bin/env python
import json
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

import pydantic  # type: ignore

from .exceptions import OperationsError, ValidationError


# TODO: Add validator for scheduler arn ( check if function exists )
# data for schedule request
class ScheduleRequest(pydantic.BaseModel):
    schedule_time: int
    workflow_arn: str
    workflow_payload: Optional[dict] = None

    @pydantic.validator("workflow_payload")
    @classmethod
    def validate_workflow_payload(cls, value):
        if value is not None:
            try:
                json.loads(value)
            except json.decoder.JSONDecodeError:
                raise ValidationError(
                    value=value, message=f"Unable to decode workflow payload: {value}"
                )
        return value

    class Config:
        frozen = True


# response data
@dataclass(frozen=True)
class Response:
    status_code: int
    body: str


# data class for mapping of time period to a hash for dynamodb
@dataclass(frozen=True)
class TimePeriodMap:
    time_period: str
    time_period_hash: str


class ScheduleStatus(str, Enum):
    NOT_STARTED: str = "NOT_STARTED"
    PROCESSING: str = "PROCESSING"
    COMPLETED: str = "COMPLETED"


@dataclass(frozen=True)
class ScheduleItem:
    schedule_time: int
    workflow_arn: str
    workflow_payload: Optional[dict] = field(default_factory=dict)
    schedule_id: Optional[str] = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def schedule_time_formatted(self) -> str:
        return datetime.utcfromtimestamp(self.schedule_time).strftime("%Y-%m-%d %H:%M")


@dataclass(frozen=True)
class DynamodbItem:
    time_period_hash: str
    schedule_item: ScheduleItem
    trigger_time: Optional[int] = None
    status: Optional[str] = ScheduleStatus.NOT_STARTED.value

    def __post_init__(self):
        if self.trigger_time is None:
            trigger_time = self.schedule_item.schedule_time * 10**6
            trigger_time += random.randint(0, 10**6 - 1)  # nosec
            object.__setattr__(self, "trigger_time", trigger_time)


class LambdaProxyRequest(pydantic.BaseModel):
    lambda_event: dict
    context: Optional[object] = None

    @pydantic.validator("lambda_event")
    @classmethod
    def validate_lambda_event(cls, value: dict) -> dict:
        if "httpMethod" not in value:
            raise OperationsError(
                value=str(value), message="Lambda event not formatter correctly"
            )
        return value

    @property
    def http_method(self) -> str:
        return self.lambda_event["httpMethod"]

    @property
    def payload(self):
        if self.http_method == "GET":
            return self.query_string_parameters
        return self.body

    @property
    def query_string_parameters(self) -> Optional[dict]:
        return self.lambda_event.get("queryStringParameters")

    @property
    def body(self) -> Optional[dict]:
        body = self.lambda_event.get("body")
        return body if body is None else json.loads(body)
