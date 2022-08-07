#!/usr/bin/env python
from dataclasses import asdict, fields

from .data import DynamodbItem, ScheduleItem


class DataMapper:
    @classmethod
    def _dynamodb_item_to_record(cls, dynamodb_item: DynamodbItem) -> dict:

        schedule_item_payload = asdict(dynamodb_item.schedule_item)
        dynamodb_item_payload = asdict(dynamodb_item)
        dynamodb_item_payload.update(schedule_item_payload)
        del dynamodb_item_payload["schedule_item"]

        return dynamodb_item_payload

    @classmethod
    def _record_to_dynamodb_item(cls, record: dict) -> DynamodbItem:

        schedule_item_payload = {f.name: record[f.name] for f in fields(ScheduleItem)}
        schedule_item = ScheduleItem(**schedule_item_payload)

        dynamodb_item = DynamodbItem(
            time_period_hash=record["time_period_hash"],
            trigger_time=record["trigger_time"],
            status=record["status"],
            schedule_item=schedule_item,
        )

        return dynamodb_item
