#!/usr/bin/env python
from typing import Protocol

from .requests_handler.data import ScheduleRequest
from .scheduler.data import ScheduleItem


class Scheduler(Protocol):
    @classmethod
    def get_schedule_item(self, schedule_id: str) -> ScheduleItem:
        ...

    @classmethod
    def add_to_schedule(self, schedule_item: ScheduleRequest) -> ScheduleItem:
        ...

    @classmethod
    def remove_from_schedule(self, schedule_id: str) -> None:
        ...
