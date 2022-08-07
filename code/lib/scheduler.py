#!/usr/bin/env python
import logging
from dataclasses import asdict

import boto3  # type: ignore
from boto3.dynamodb.conditions import Attr, Key  # type: ignore

from .data import ScheduleItem, ScheduleRequest
from .ds_hash import DSPeriodHasher
from .environment import Environment
from .exceptions import NotFound
from .logging import request_context

# resources
logger = logging.getLogger(__name__)
dynamodb_resource = boto3.resource("dynamodb")


class DynamoScheduler:

    # resources
    environment = Environment.dynamodb_scheduler_env()
    table = dynamodb_resource.Table(environment.items_table_name)

    # constants
    index_name = "gsi_id"
    time_period_hash_key = "time_period_hash"
    trigger_time_key = "trigger_time"

    @classmethod
    def get_schedule_item(cls, schedule_id: str) -> ScheduleItem:
        logger.info(f"Retrieving schedule item: {schedule_id}", extra=request_context)

        response = cls.table.query(
            IndexName=cls.index_name,
            KeyConditionExpression=Key("schedule_id").eq(schedule_id),
        )
        try:
            item = response["Items"][0]
        except IndexError:
            raise NotFound(value=schedule_id, message="Schedule item not found")
        schedule_item = ScheduleItem(**item)

        logger.info(
            f"Item successfully retrieved: {schedule_item}", extra=request_context
        )
        return schedule_item

    @classmethod
    def remove_from_schedule(cls, schedule_id: str) -> None:

        logger.info(
            f"Removing item from the schedule: {schedule_id}", extra=request_context
        )
        schedule_item = cls.get_schedule_item(schedule_id)
        key_item = {
            cls.time_period_hash_key: schedule_item.time_period_hash,
            cls.trigger_time_key: schedule_item.trigger_time,
        }

        cls.table.delete_item(Key=key_item)
        logger.info("Schedule item successfully deleted", extra=request_context)

    @classmethod
    def add_to_schedule(cls, schedule_item: ScheduleItem) -> None:

        logger.info(
            f"Writing item to the schedule: {schedule_item}", extra=request_context
        )
        cls.table.put_item(
            Item=asdict(schedule_item),
            ConditionExpression=(Attr(cls.time_period_hash_key).not_exists()),
        )
        logger.info("Item added to the schedule successfully", extra=request_context)

    @classmethod
    def create_schedule_item(cls, schedule_request: ScheduleRequest) -> ScheduleItem:
        logger.info(
            f"Creating schedule item from: {schedule_request}", extra=request_context
        )

        # get schedule period mapping
        time_period_map = DSPeriodHasher.get_time_period_hash(
            schedule_request.schedule_time
        )

        # create schedule item
        schedule_item = ScheduleItem(
            time_period_hash=time_period_map.time_period_hash, **schedule_request
        )

        logger.info(
            f"Schedule item created successfully: {schedule_item}",
            extra=request_context,
        )
        return schedule_item
