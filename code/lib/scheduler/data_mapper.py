#!/usr/bin/env python
import logging
from dataclasses import asdict, fields

import simplejson as json  # type: ignore
from lib.dispatcher import LambdaProxySnsEvent
from lib.logging import request_context

from .data import DynamodbItem, ScheduleItem, ScheduleStatus

logger = logging.getLogger(__name__)


class DataMapper:
    @classmethod
    def dynamodb_item_to_record(cls, dynamodb_item: DynamodbItem) -> dict:

        logger.debug(
            f"Converting dynamodb item to record: {dynamodb_item}",
            extra=request_context,
        )

        schedule_item_payload = asdict(dynamodb_item.schedule_item)
        dynamodb_item_payload = asdict(dynamodb_item)

        schedule_item_payload["workflow_payload"] = json.dumps(
            schedule_item_payload["workflow_payload"]
        )
        dynamodb_item_payload["status"] = dynamodb_item_payload["status"].value
        dynamodb_item_payload["trigger_time"] = int(
            dynamodb_item_payload["trigger_time"]
        )
        dynamodb_item_payload.update(schedule_item_payload)
        del dynamodb_item_payload["schedule_item"]

        logger.debug(
            f"Conversion successfull: {dynamodb_item_payload}", extra=request_context
        )
        return dynamodb_item_payload

    @classmethod
    def record_to_dynamodb_item(cls, record: dict) -> DynamodbItem:
        logger.debug(
            f"Converting record to dynamodb item: {record}", extra=request_context
        )

        schedule_item_payload = {f.name: record[f.name] for f in fields(ScheduleItem)}
        schedule_item_payload["schedule_time"] = int(
            schedule_item_payload["schedule_time"]
        )
        schedule_item_payload["workflow_payload"] = json.loads(
            schedule_item_payload["workflow_payload"]
        )
        schedule_item = ScheduleItem(**schedule_item_payload)

        record["trigger_time"] = int(record["trigger_time"])
        dynamodb_item = DynamodbItem(
            time_period_hash=record["time_period_hash"],
            trigger_time=record["trigger_time"],
            status=ScheduleStatus(record["status"]),
            schedule_item=schedule_item,
        )

        logger.debug(f"Conversion successfull: {dynamodb_item}", extra=request_context)
        return dynamodb_item

    @classmethod
    def dynamodb_item_to_sns_payload(cls, dynamodb_item: DynamodbItem) -> str:
        logger.debug(
            f"Converting dynamodb item to sns payload: {dynamodb_item}",
            extra=request_context,
        )
        payload = json.dumps(cls.dynamodb_item_to_record(dynamodb_item))

        logger.debug(f"Conversion successfull: {payload}", extra=request_context)
        return payload

    @classmethod
    def sns_payload_todynamodb_item(
        cls, sns_event: LambdaProxySnsEvent
    ) -> DynamodbItem:
        logger.debug(
            f"Converting sns event to dynamodb item: {sns_event}", extra=request_context
        )
        dynamodb_item = DataMapper.record_to_dynamodb_item(
            json.loads(sns_event.payload)
        )

        logger.debug(f"Conversion successfull: {dynamodb_item}", extra=request_context)
        return dynamodb_item

    @classmethod
    def dynamodb_item_to_transact_record(cls, dynamodb_item: DynamodbItem) -> dict:
        logger.debug(
            f"Converting dynamodb item to transact record: {dynamodb_item}",
            extra=request_context,
        )

        dynamodb_record = cls.dynamodb_item_to_record(dynamodb_item)
        tr_record = cls._dynamodb_record_to_transact_record(dynamodb_record)

        logger.debug(f"Conversion successfull: {tr_record}", extra=request_context)
        return tr_record

    @classmethod
    def _dynamodb_record_to_transact_record(cls, dynamodb_record: dict) -> dict:
        field_map = {str(int): "N", str(str): "S"}
        tr_record = {
            k: {field_map[str(type(v))]: str(v)} for k, v in dynamodb_record.items()
        }
        return tr_record
