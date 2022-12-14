#!/usr/bin/env python
import logging
from dataclasses import asdict
from typing import Optional

import boto3  # type: ignore
from boto3.dynamodb.conditions import Attr  # type: ignore
from botocore.exceptions import ClientError  # type: ignore
from lib.environment import Environment
from lib.exceptions import OperationsError
from lib.logging import request_context
from lib.requests_handler.data import ScheduleRequest
from lib.scheduler.data_mapper import DataMapper

from .data import DynamodbItem, ScheduleItem, ScheduleStatus
from .ds_hash import DSPeriodHasher

# resources
logger = logging.getLogger(__name__)
dynamodb_resource = boto3.resource("dynamodb")
dynamodb_client = boto3.client("dynamodb")


class DynamoScheduleWriter:

    # resources
    environment = Environment.dynamodb_scheduler_env()
    table = dynamodb_resource.Table(environment.items_table_name)

    # constants
    time_period_hash_key = "time_period_hash"
    trigger_time_key = "trigger_time"

    @classmethod
    def _remove_dynamodb_item_from_schedule(cls, dynamodb_item: DynamodbItem) -> None:

        logger.info(
            f"Removing item from the schedule: {dynamodb_item}", extra=request_context
        )

        key_item = {
            cls.time_period_hash_key: dynamodb_item.time_period_hash,
            cls.trigger_time_key: dynamodb_item.trigger_time,
        }

        cls.table.delete_item(Key=key_item)
        logger.info("Item successfully deleted", extra=request_context)

    @classmethod
    def add_to_schedule(cls, schedule_request: ScheduleRequest) -> ScheduleItem:

        logger.info(
            f"Adding schedule item to the schedule: {schedule_request}",
            extra=request_context,
        )

        dynamodb_item = cls._create_dynamodb_item(schedule_request)
        dynamodb_item_payload = DataMapper.dynamodb_item_to_record(dynamodb_item)

        try:
            cls.table.put_item(
                Item=dynamodb_item_payload,
                ConditionExpression=(
                    Attr(cls.time_period_hash_key).not_exists()
                    & Attr(cls.trigger_time_key).not_exists()
                ),
            )
        except ClientError as e:
            raise OperationsError(value=str(asdict(dynamodb_item)), message=str(e))

        logger.info("Item added to the schedule successfully", extra=request_context)
        return dynamodb_item.schedule_item

    @classmethod
    def _create_dynamodb_item(
        cls, schedule_request: ScheduleRequest, schedule_id: Optional[str] = None
    ) -> DynamodbItem:
        logger.info(
            f"Creating dynamodb item from: {schedule_request}", extra=request_context
        )

        # get schedule period mapping
        time_period_map = DSPeriodHasher.get_time_period_hash(
            schedule_request.schedule_time
        )

        schedule_item = ScheduleItem(
            schedule_time=schedule_request.schedule_time,
            workflow_arn=schedule_request.workflow_arn,
            workflow_payload=schedule_request.workflow_payload,
            schedule_id=schedule_id,
        )

        dynamodb_item = DynamodbItem(
            time_period_hash=time_period_map.time_period_hash,
            schedule_item=schedule_item,
        )

        logger.info(
            f"Dynamodb item created successfully: {dynamodb_item}",
            extra=request_context,
        )
        return dynamodb_item

    @classmethod
    def update_dynamodb_item_status(
        cls, dynamodb_item: DynamodbItem, status: ScheduleStatus
    ) -> None:
        logger.info(
            f"Updating status of dynamodb item: {dynamodb_item}", extra=request_context
        )

        key_payload = {
            "time_period_hash": dynamodb_item.time_period_hash,
            "trigger_time": dynamodb_item.trigger_time,
        }

        cls.table.update_item(
            Key=key_payload,
            AttributeUpdates={"status": {"Value": status.value, "Action": "PUT"}},
        )
        logger.info("Update completed successfully")

    @classmethod
    def update_dynamodb_item(
        cls, dynamodb_item: DynamodbItem, schedule_request: ScheduleRequest
    ) -> DynamodbItem:
        logger.info(
            f"Updating dynamodb item: {dynamodb_item}: {schedule_request}",
            extra=request_context,
        )

        new_dynamodb_item = cls._create_dynamodb_item(
            schedule_request, dynamodb_item.schedule_item.schedule_id
        )

        # get transact payloads
        old_transact_record = DataMapper.dynamodb_item_to_transact_record(dynamodb_item)
        new_transact_record = DataMapper.dynamodb_item_to_transact_record(
            new_dynamodb_item
        )

        old_key_payload = {
            k: old_transact_record[k]
            for k in (cls.time_period_hash_key, cls.trigger_time_key)
        }

        dynamodb_client.transact_write_items(
            TransactItems=[
                {
                    "Delete": {
                        "TableName": cls.environment.items_table_name,
                        "Key": old_key_payload,
                    },
                },
                {
                    "Put": {
                        "TableName": cls.environment.items_table_name,
                        "Item": new_transact_record,
                    }
                },
            ]
        )

        logger.info("Item updated successfully", extra=request_context)
        return new_dynamodb_item
