#!/usr/bin/env python
from typing import Generator, Protocol

from .requests_handler.data import ScheduleRequest
from .scheduler.data import QueryRange, ScheduleItem


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

    @classmethod
    def get_schedule_items(
        self, query_range: QueryRange
    ) -> Generator[ScheduleItem, None, None]:
        ...
