#!/usr/bin/env python
import logging
import uuid
from dataclasses import asdict
from datetime import datetime
from typing import Optional

import boto3  # type: ignore
from boto3.dynamodb.conditions import Attr, Key  # type: ignore

from .data import TimePeriodMap
from .environment import Environment
from .logging import request_context

# resources
logger = logging.getLogger(__name__)
dynamodb_resource = boto3.resource("dynamodb")


class DSPeriodHasher:

    # resources
    environment = Environment.dynamodb_scheduler_env()
    table = dynamodb_resource.Table(environment.hash_table_name)

    # constants
    period_key_key = "time_period"
    hash_key = "time_period_hash"

    @classmethod
    def _load_period_hash(cls, period_key: str) -> Optional[TimePeriodMap]:

        logger.info(f"Loading period key for: {period_key}", extra=request_context)
        response = cls.table.query(
            KeyConditionExpression=Key(cls.period_key_key).eq(period_key)
        )

        try:
            return TimePeriodMap(**response["Items"][0])
        except IndexError:
            pass
        return None

    # and handle those
    @classmethod
    def _add_period_hash(cls, period_key: str) -> TimePeriodMap:

        time_period_hash = TimePeriodMap(
            time_period=period_key, time_period_hash=str(uuid.uuid4())
        )

        logger.info(f"Writing new period hash to the table: {time_period_hash}")
        cls.table.put_item(
            Item=asdict(time_period_hash),
            ConditionExpression=(Attr(cls.period_key_key).not_exists()),
        )
        return time_period_hash

    @classmethod
    def get_time_period_hash(cls, schedule_time: int) -> TimePeriodMap:
        logger.info(
            f"Retrieving time period map for: {schedule_time}", extra=request_context
        )

        date = datetime.fromtimestamp(schedule_time)
        period_key = f"{date.year}-{str(int((date.month - 1) / 3))}"

        # load period key
        time_period_map = cls._load_period_hash(period_key)
        if time_period_map is None:
            time_period_map = cls._add_period_hash(period_key)

        logger.info(
            f"Time period map retrieved: {time_period_map}", extra=request_context
        )
        return time_period_map
