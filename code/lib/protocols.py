#!/usr/bin/env python
from typing import Protocol

from .data import ScheduleItem, ScheduleRequest


class Scheduler(Protocol):
    @classmethod
    def create_schedule_item(self, schedule_request: ScheduleRequest) -> ScheduleItem:
        ...

    @classmethod
    def get_schedule_item(self, schedule_id: str) -> ScheduleItem:
        ...

    @classmethod
    def add_to_schedule(self, schedule_item: ScheduleItem) -> None:
        ...

    @classmethod
    def remove_from_schedule(self, schedule_id: str) -> None:
        ...
