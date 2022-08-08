#!/usr/bin/env python
from dataclasses import asdict, fields

import simplejson as json  # type: ignore
from lib.dispatcher.data import LambdaProxySnsEvent

from .data import DynamodbItem, ScheduleItem, ScheduleStatus


class DataMapper:
    @classmethod
    def dynamodb_item_to_record(cls, dynamodb_item: DynamodbItem) -> dict:

        schedule_item_payload = asdict(dynamodb_item.schedule_item)
        dynamodb_item_payload = asdict(dynamodb_item)
        dynamodb_item_payload["status"] = dynamodb_item_payload["status"].value
        dynamodb_item_payload.update(schedule_item_payload)
        del dynamodb_item_payload["schedule_item"]

        return dynamodb_item_payload

    @classmethod
    def record_to_dynamodb_item(cls, record: dict) -> DynamodbItem:

        schedule_item_payload = {f.name: record[f.name] for f in fields(ScheduleItem)}
        schedule_item_payload["schedule_time"] = int(
            schedule_item_payload["schedule_time"]
        )
        schedule_item = ScheduleItem(**schedule_item_payload)

        dynamodb_item = DynamodbItem(
            time_period_hash=record["time_period_hash"],
            trigger_time=record["trigger_time"],
            status=ScheduleStatus(record["status"]),
            schedule_item=schedule_item,
        )

        return dynamodb_item

    @classmethod
    def dynamodb_item_to_sns_payload(cls, dynamodb_item: DynamodbItem) -> str:
        return json.dumps(cls.dynamodb_item_to_record(dynamodb_item))

    @classmethod
    def sns_payload_todynamodb_item(
        cls, sns_event: LambdaProxySnsEvent
    ) -> DynamodbItem:
        return DataMapper.record_to_dynamodb_item(json.loads(sns_event.payload))
