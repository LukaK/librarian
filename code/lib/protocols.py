#!/usr/bin/env python
from typing import Protocol

from .data import ScheduleItem, ScheduleRequest


class Scheduler(Protocol):
    def create_schedule_item(self, schedule_request: ScheduleRequest) -> ScheduleItem:
        ...

    def get_schedule_item(self, schedule_id: str) -> ScheduleItem:
        ...

    def add_to_schedule(self, schedule_item: ScheduleItem) -> None:
        ...

    def remove_from_schedule(self, schedule_id: str) -> None:
        ...
