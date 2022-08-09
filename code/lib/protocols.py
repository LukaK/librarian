#!/usr/bin/env python
from typing import Generator, Protocol

from .requests_handler.data import ScheduleRequest
from .scheduler import DynamodbItem, QueryRange, ScheduleItem, ScheduleStatus


class Scheduler(Protocol):
    @classmethod
    def get_schedule_item(self, schedule_id: str) -> ScheduleItem:
        ...

    @classmethod
    def get_dynamodb_item(self, schedule_id: str) -> ScheduleItem:
        ...

    @classmethod
    def add_to_schedule(self, schedule_item: ScheduleRequest) -> ScheduleItem:
        ...

    @classmethod
    def remove_from_schedule(self, schedule_id: str) -> None:
        ...

    @classmethod
    def update_schedule_item(
        self, schedule_id: str, schedule_item: ScheduleRequest
    ) -> ScheduleItem:
        ...

    @classmethod
    def update_dynamodb_item_status(
        cls, dynamodb_item: DynamodbItem, status: ScheduleStatus
    ) -> None:
        ...

    @classmethod
    def get_schedule_items(
        self, query_range: QueryRange, status: ScheduleStatus
    ) -> Generator[ScheduleItem, None, None]:
        ...

    @classmethod
    def get_dynamodb_items(
        self, query_range: QueryRange, status: ScheduleStatus
    ) -> Generator[DynamodbItem, None, None]:
        ...
