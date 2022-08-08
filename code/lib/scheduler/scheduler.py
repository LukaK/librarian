#!/usr/bin/env python
from .schedule_reader import DynamoScheduleReader
from .schedule_writer import DynamoScheduleWriter


class DynamoScheduler(DynamoScheduleWriter, DynamoScheduleReader):
    @classmethod
    def remove_from_schedule(cls, schedule_id: str) -> None:
        dynamodb_item = DynamoScheduleReader.get_dynamodb_item(schedule_id)
        DynamoScheduleWriter._remove_dynamodb_item_from_schedule(dynamodb_item)
