#!/usr/bin/env python
import time

import pytest
from moto.core import patch_client, patch_resource  # type: ignore


def test__workflow_starter_lambda(sns, dynamo_tables):
    from lib.requests_handler.data import ScheduleRequest
    from lib.scheduler.scheduler import DynamoScheduler
    from src.workflow_starter import lambda_handler

    schedule_time = int(time.time()) + 3 * 60
    schedule_request = ScheduleRequest(
        workflow_arn="test_arn", schedule_time=schedule_time
    )
    DynamoScheduler.add_to_schedule(schedule_request)
    lambda_handler({}, None)


@pytest.mark.slow
def test__dispatcher_lambda(sns, lambda_function, dynamo_tables):
    from lib.requests_handler.data import ScheduleRequest
    from lib.scheduler.data_mapper import DataMapper
    from lib.scheduler.scheduler import DynamoScheduler
    from src.dispatcher import lambda_handler

    schedule_time = int(time.time()) + 3 * 60
    schedule_request = ScheduleRequest(
        workflow_arn=lambda_function[1], schedule_time=schedule_time
    )
    schedule_item = DynamoScheduler.add_to_schedule(schedule_request)
    dynamodb_item = DynamoScheduler.get_dynamodb_item(schedule_item.schedule_id)

    lambda_event = {
        "Records": [
            {"Sns": {"Message": DataMapper.dynamodb_item_to_sns_payload(dynamodb_item)}}
        ]
    }
    lambda_handler(lambda_event, None)
