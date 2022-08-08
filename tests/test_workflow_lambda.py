#!/usr/bin/env python
import time

import pytest
from moto.core import patch_client, patch_resource  # type: ignore


def test__workflow_starter_lambda(dynamo_tables, sns):
    from lib.dispatcher.dispatcher import sns_resource
    from lib.requests_handler.data import ScheduleRequest
    from lib.scheduler.scheduler import DynamoScheduler, dynamodb_resource
    from src.workflow_starter import lambda_handler

    patch_resource(dynamodb_resource)
    patch_resource(sns_resource)

    schedule_time = int(time.time())
    schedule_request = ScheduleRequest(
        workflow_arn="test_arn", schedule_time=schedule_time
    )
    DynamoScheduler.add_to_schedule(schedule_request)
    lambda_handler({}, None)


@pytest.mark.slow
def test__dispatcher_lambda(dynamo_tables, sns, lambda_function):
    from lib.dispatcher.dispatcher import lambda_client, sns_resource
    from lib.requests_handler.data import ScheduleRequest
    from lib.scheduler.data_mapper import DataMapper
    from lib.scheduler.scheduler import DynamoScheduler, dynamodb_resource
    from src.dispatcher import lambda_handler

    patch_resource(dynamodb_resource)
    patch_resource(sns_resource)
    patch_client(lambda_client)

    schedule_time = int(time.time())
    schedule_request = ScheduleRequest(
        workflow_arn=lambda_function[1], schedule_time=schedule_time
    )
    schedule_item = DynamoScheduler.add_to_schedule(schedule_request)
    dynamodb_item = DynamoScheduler._get_dynamodb_item(schedule_item.schedule_id)

    lambda_event = {
        "Records": [
            {"Sns": {"Message": DataMapper.dynamodb_item_to_sns_payload(dynamodb_item)}}
        ]
    }
    lambda_handler(lambda_event, None)
