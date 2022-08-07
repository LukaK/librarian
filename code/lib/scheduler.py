#!/usr/bin/env python
import logging
from dataclasses import asdict

import boto3  # type: ignore
from boto3.dynamodb.conditions import Attr  # type: ignore

from .data import ScheduleItem, ScheduleRequest
from .ds_hash import DSPeriodHasher
from .environment import Environment
from .logging import request_context

# resources
logger = logging.getLogger(__name__)
dynamodb_resource = boto3.resource("dynamodb")


# TODO: Refactor this, too much responsibility, add handlers for hash and for item table
class DynamoScheduler:

    # resources
    environment = Environment.dynamodb_scheduler_env()
    table = dynamodb_resource.Table(environment.items_table_name)

    # constants
    time_period_hash_key = "time_period_hash"

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
