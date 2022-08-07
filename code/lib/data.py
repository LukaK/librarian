#!/usr/bin/env python
import json
import random
import uuid
from dataclasses import dataclass
from typing import Optional

import pydantic  # type: ignore

from .exceptions import ValidationError


# data for schedule request
class ScheduleRequest(pydantic.BaseModel):
    schedule_time: int
    workflow_arn: str
    workflow_payload: Optional[dict]

    @pydantic.validator("workflow_payload")
    @classmethod
    def validate_schedule_time(cls, value):
        if value is not None:
            try:
                json.loads(value)
            except json.decoder.JSONDecodeError:
                raise ValidationError(
                    value=value, message=f"Unable to decode workflow payload: {value}"
                )
        return value


# response data
@dataclass
class Response:
    status_code: int
    body: str


# data class for mapping of time period to a hash for dynamodb
@dataclass
class TimePeriodMap:
    time_period: str
    time_period_hash: str


# TODO: Too many variables in the schedule item, refactor this
# TODO: Add schedule time formatted as a property
# schedule item in dynamodb
@dataclass(frozen=True)
class ScheduleItem:
    time_period_hash: str
    trigger_time: Optional[int]
    schedule_id: Optional[str]
    schedule_time: int
    schedule_time_formatted: str
    workflow_arn: str
    workflow_payload: Optional[dict]

    def __post_init__(self):
        # set schedule id
        if self.schedule_id is None:
            object.__setattr__(self, "schedule_id", str(uuid.uuid4()))

        # set schedule time
        if self.trigger_time is None:
            trigger_time = self.schedule_time * 10**6
            trigger_time += random.randint(0, 10**6 - 1)  # nosec
            object.__setattr__(self, "trigger_time", trigger_time)
