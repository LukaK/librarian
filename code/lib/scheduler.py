#!/usr/bin/env python
import logging
from typing import Optional

import boto3  # type: ignore

from .data import ScheduleItem, ScheduleRequest
from .environment import Environment
from .logging import request_context

# resources
logger = logging.getLogger(__name__)
dynamodb_resource = boto3.resource("dynamodb")


# TODO: Refactor this, too much responsibility, add handlers for hash and for item table
class DynamoScheduler:

    # resources
    environment = Environment.dynamodb_scheduler_env()
    hash_table = dynamodb_resource.Table(environment.hash_table_name)
    items_table = dynamodb_resource.Table(environment.items_table_name)

    # TODO: implement
    @classmethod
    def _get_time_period_hans(cls, trigger_time: int) -> Optional[str]:
        pass

    # TODO: Implement
    @classmethod
    def _create_time_period_hash(cls, trigger_time: int) -> str:
        pass

    # TODO: Implement
    @classmethod
    def add_to_schedule(cls, schedule_item: ScheduleItem) -> None:
        pass

    @classmethod
    def create_schedule_item(cls, schedule_request: ScheduleRequest) -> ScheduleItem:
        logger.info(
            f"Creating schedule item from: {schedule_request}", extra=request_context
        )

        # get schedule period mapping
        time_period_hash = cls._get_time_period_hans(schedule_request.schedule_time)
        if time_period_hash is None:
            time_period_hash = cls._create_time_period_hash(
                schedule_request.schedule_time
            )

        # create schedule item
        schedule_item = ScheduleItem(
            time_period_hash=time_period_hash, **schedule_request
        )

        logger.info(
            f"Schedule item created successfully: {schedule_item}",
            extra=request_context,
        )
        return schedule_item
