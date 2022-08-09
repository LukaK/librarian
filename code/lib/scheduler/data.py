#!/usr/bin/env python
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from lib.exceptions import ValidationError


# data class for mapping of time period to a hash for dynamodb
@dataclass(frozen=True)
class TimePeriodMap:
    time_period: str
    time_period_hash: str


class ScheduleStatus(str, Enum):
    NOT_STARTED: str = "NOT_STARTED"
    PROCESSING: str = "PROCESSING"
    COMPLETED: str = "COMPLETED"
    ERROR: str = "ERROR"


@dataclass(frozen=True)
class ScheduleItem:
    schedule_time: int
    workflow_arn: str
    workflow_payload: Optional[dict] = field(default_factory=dict)
    schedule_id: Optional[str] = None

    def __post_init__(self):
        if self.schedule_id is None:
            object.__setattr__(self, "schedule_id", str(uuid.uuid4()))

    @property
    def schedule_time_formatted(self) -> str:
        return datetime.utcfromtimestamp(self.schedule_time).strftime("%Y-%m-%d %H:%M")


@dataclass(frozen=True)
class DynamodbItem:
    time_period_hash: str
    schedule_item: ScheduleItem
    trigger_time: Optional[int] = None
    status: str = ScheduleStatus.NOT_STARTED

    def __post_init__(self):
        if self.trigger_time is None:
            trigger_time = self.schedule_item.schedule_time * 10**6
            trigger_time += random.randint(0, 10**6 - 1)  # nosec
            object.__setattr__(self, "trigger_time", trigger_time)


@dataclass
class QueryRange:
    start_time: int
    end_time: int

    def __post_init__(self):
        time_diff = self.end_time - self.start_time

        if 0 > time_diff or time_diff > 600:
            raise ValidationError(value=time_diff, message="Query range not valid")


@dataclass
class DynamodbQueryRange:
    time_period_hash: str
    query_range: QueryRange

    @property
    def start_trigger_time(self):
        return self.query_range.start_time * 10**6

    @property
    def end_trigger_time(self):
        return self.query_range.end_time * 10**6
