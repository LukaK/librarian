#!/usr/bin/env python
import json
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


# data class for mapping of time period to a hash for dynamodb
@dataclass
class TimePeriodHash:
    time_period: str
    time_period_hash: str


# schedule item in dynamodb
@dataclass
class ScheduleItem:
    time_period_hash: str
    trigger_time: int
    schedule_id: str
    schedule_time: int
    schedule_time_formatted: str
    workflow_arn: str
    workflow_payload: Optional[dict]
