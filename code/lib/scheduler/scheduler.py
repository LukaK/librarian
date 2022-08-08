#!/usr/bin/env python
import logging
from dataclasses import asdict
from typing import Generator

import boto3  # type: ignore
from boto3.dynamodb.conditions import Attr, Key  # type: ignore
from botocore.exceptions import ClientError  # type: ignore
from lib.environment import Environment
from lib.exceptions import NotFound, OperationsError
from lib.logging import request_context
from lib.requests_handler.data import ScheduleRequest

from .data import (
    DynamodbItem,
    DynamodbQueryRange,
    QueryRange,
    ScheduleItem,
    ScheduleStatus,
)
from .data_mapper import DataMapper
from .ds_hash import DSPeriodHasher

# resources
logger = logging.getLogger(__name__)
dynamodb_resource = boto3.resource("dynamodb")


# TODO: Refactor scheduler
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

    @classmethod
    def _get_schedule_items_for_ddb_query_range(
        cls, query_range: DynamodbQueryRange, status: ScheduleStatus
    ) -> Generator[ScheduleItem, None, None]:

        logger.info(
            f"Retrieving schedule items for ddb range: {query_range}",
            extra=request_context,
        )

        next_key = None
        query_arguments = {
            "KeyConditionExpression": Key(cls.time_period_hash_key).eq(
                query_range.time_period_hash
            )
            & Key(cls.trigger_time_key).between(
                query_range.start_trigger_time, query_range.end_trigger_time - 1
            )
            & Key("status").eq(status.value),
        }

        while True:

            if next_key is not None:
                query_arguments["ExclusiveStartKey"] = next_key

            response = cls.table.query(**query_arguments)
            schedule_items = response["Items"]
            next_key = response.get("LastEvaluatedKey")

            for schedule_item in schedule_items:
                yield schedule_item

            if next_key is None:
                break
        logger.info("Schedule items retrieved succesfully", extra=request_context)

    @classmethod
    def get_schedule_items(
        cls, query_range: QueryRange, status: ScheduleStatus
    ) -> Generator[ScheduleItem, None, None]:

        logger.info(
            f"Retrieving schedule items for range: {query_range}", extra=request_context
        )

        # get start query dynamodb range
        start_period_map = DSPeriodHasher.get_time_period_hash(query_range.start_time)
        start_dynamodb_query_range = DynamodbQueryRange(
            time_period_hash=start_period_map.time_period_hash, query_range=query_range
        )

        # get end query dynamodb range
        end_period_map = DSPeriodHasher.get_time_period_hash(query_range.end_time)
        end_dynamodb_query_range = DynamodbQueryRange(
            time_period_hash=end_period_map.time_period_hash, query_range=query_range
        )

        # retrieving items from the dynamodb
        for item in cls._get_schedule_items_for_ddb_query_range(
            start_dynamodb_query_range, status
        ):
            yield item

        if start_dynamodb_query_range == end_dynamodb_query_range:
            logger.info("Schedule items retrieved succesfully", extra=request_context)
            return

        # special case
        logger.info("Retrieving items for the next period", extra=request_context)
        for item in cls._get_schedule_items_for_ddb_query_range(
            end_dynamodb_query_range, status
        ):
            yield item

        logger.info(
            "Items for the next period retrieved successfully", extra=request_context
        )
