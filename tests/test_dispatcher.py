#!/usr/bin/env python
import time

import pytest
from moto.core import patch_client, patch_resource  # type: ignore


def test__dispatcher_dispatch_schedule_item(dynamo_tables, sns):
    from lib.dispatcher.dispatcher import Dispatcher, sns_resource
    from lib.requests_handler.data import ScheduleRequest
    from lib.scheduler.data import ScheduleStatus
    from lib.scheduler.scheduler import DynamoScheduler, dynamodb_resource

    # patch resources
    patch_resource(dynamodb_resource)
    patch_resource(sns_resource)

    schedule_time = int(time.time())
    schedule_request = ScheduleRequest(
        workflow_arn="test_arn", schedule_time=schedule_time
    )
    schedule_item = DynamoScheduler.add_to_schedule(schedule_request)

    # dispatch dynamodb item
    dynamodb_item = DynamoScheduler._get_dynamodb_item(schedule_item.schedule_id)
    Dispatcher.dispatch_dynamodb_item(dynamodb_item)

    dynamodb_item_updated = DynamoScheduler._get_dynamodb_item(
        schedule_item.schedule_id
    )
    assert dynamodb_item_updated.status == ScheduleStatus.PROCESSING


@pytest.mark.slow
def test__dispatcher_trigger_lambda_workflow(dynamo_tables, sns, lambda_function):
    from lib.dispatcher.dispatcher import Dispatcher, lambda_client, sns_resource
    from lib.requests_handler.data import ScheduleRequest
    from lib.scheduler.data import ScheduleStatus
    from lib.scheduler.scheduler import DynamoScheduler, dynamodb_resource

    # patch resources
    patch_resource(dynamodb_resource)
    patch_resource(sns_resource)
    patch_client(lambda_client)

    schedule_time = int(time.time())
    schedule_request = ScheduleRequest(
        workflow_arn=lambda_function[1], schedule_time=schedule_time
    )
    schedule_item = DynamoScheduler.add_to_schedule(schedule_request)

    # dispatch dynamodb item
    dynamodb_item = DynamoScheduler._get_dynamodb_item(schedule_item.schedule_id)
    Dispatcher.trigger_lambda_workflow(dynamodb_item)

    dynamodb_item_updated = DynamoScheduler._get_dynamodb_item(
        schedule_item.schedule_id
    )
    assert dynamodb_item_updated.status == ScheduleStatus.COMPLETED
