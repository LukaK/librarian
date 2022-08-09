#!/usr/bin/env python
from lib.requests_handler import ScheduleRequest

from .data import ScheduleItem
from .schedule_reader import DynamoScheduleReader
from .schedule_writer import DynamoScheduleWriter


class DynamoScheduler(DynamoScheduleWriter, DynamoScheduleReader):
    @classmethod
    def remove_from_schedule(cls, schedule_id: str) -> None:
        dynamodb_item = DynamoScheduleReader.get_dynamodb_item(schedule_id)
        DynamoScheduleWriter._remove_dynamodb_item_from_schedule(dynamodb_item)

    @classmethod
    def update_schedule_item(
        cls, schedule_id: str, schedule_request: ScheduleRequest
    ) -> ScheduleItem:
        dynamodb_item = DynamoScheduleReader.get_dynamodb_item(schedule_id)
        dynamodb_item_updated = DynamoScheduleWriter.update_dynamodb_item(
            dynamodb_item, schedule_request
        )
        return dynamodb_item_updated.schedule_item
