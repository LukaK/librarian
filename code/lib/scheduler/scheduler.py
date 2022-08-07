#!/usr/bin/env python
import logging
from dataclasses import asdict

import boto3  # type: ignore
from boto3.dynamodb.conditions import Attr, Key  # type: ignore
from botocore.exceptions import ClientError  # type: ignore
from lib.environment import Environment
from lib.exceptions import NotFound, OperationsError
from lib.logging import request_context
from lib.requests_handler.data import ScheduleRequest

from .data import DynamodbItem, ScheduleItem
from .data_mapper import DataMapper
from .ds_hash import DSPeriodHasher

# resources
logger = logging.getLogger(__name__)
dynamodb_resource = boto3.resource("dynamodb")


class DynamoScheduler:

    # resources
    environment = Environment.dynamodb_scheduler_env()
    table = dynamodb_resource.Table(environment.items_table_name)

    # constants
    time_period_hash_key = "time_period_hash"
    trigger_time_key = "trigger_time"

    @classmethod
    def _get_dynamodb_item(cls, schedule_id: str) -> DynamodbItem:
        logger.info(f"Retrieving dynamodb item: {schedule_id}", extra=request_context)

        response = cls.table.query(
            IndexName=cls.environment.schedule_id_index_name,
            KeyConditionExpression=Key("schedule_id").eq(schedule_id),
        )
        try:
            item = response["Items"][0]
        except IndexError:
            raise NotFound(value=schedule_id, message="Schedule item not found")

        # construct dynamodb item from the record
        dynamodb_item = DataMapper._record_to_dynamodb_item(item)

        logger.info(
            f"Item successfully retrieved: {dynamodb_item}", extra=request_context
        )
        return dynamodb_item

    @classmethod
    def get_schedule_item(cls, schedule_id: str) -> ScheduleItem:
        logger.info(f"Retrieving schedule item: {schedule_id}", extra=request_context)

        dynamodb_item = cls._get_dynamodb_item(schedule_id)
        return dynamodb_item.schedule_item

    @classmethod
    def remove_from_schedule(cls, schedule_id: str) -> None:

        logger.info(
            f"Removing item from the schedule: {schedule_id}", extra=request_context
        )

        dynamodb_item = cls._get_dynamodb_item(schedule_id)
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
        dynamodb_item_payload = DataMapper._dynamodb_item_to_record(dynamodb_item)

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
    def _create_dynamodb_item(cls, schedule_request: ScheduleRequest) -> DynamodbItem:
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
