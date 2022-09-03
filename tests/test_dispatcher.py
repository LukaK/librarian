#!/usr/bin/env python
import time

import pytest  # type: ignore


def test__dispatcher_dispatch_schedule_item(sns, dynamo_tables):
    from lib.dispatcher.dispatcher import Dispatcher
    from lib.requests_handler.data import ScheduleRequest
    from lib.scheduler.data import ScheduleStatus
    from lib.scheduler.scheduler import DynamoScheduler

    schedule_time = int(time.time()) + 3 * 60
    schedule_request = ScheduleRequest(
        workflow_arn="test_arn", schedule_time=schedule_time
    )
    schedule_item = DynamoScheduler.add_to_schedule(schedule_request)

    # dispatch dynamodb item
    dynamodb_item = DynamoScheduler.get_dynamodb_item(schedule_item.schedule_id)
    Dispatcher.dispatch_dynamodb_item(dynamodb_item)

    dynamodb_item_updated = DynamoScheduler.get_dynamodb_item(schedule_item.schedule_id)
    assert dynamodb_item_updated.status == ScheduleStatus.PROCESSING


@pytest.mark.slow
def test__dispatcher_trigger_lambda_workflow_exists(
    dynamo_tables, sns, lambda_function
):
    from lib.dispatcher.dispatcher import Dispatcher
    from lib.requests_handler.data import ScheduleRequest
    from lib.scheduler.data import ScheduleStatus
    from lib.scheduler.scheduler import DynamoScheduler

    schedule_time = int(time.time()) + 3 * 60
    schedule_request = ScheduleRequest(
        workflow_arn=lambda_function[1], schedule_time=schedule_time
    )
    schedule_item = DynamoScheduler.add_to_schedule(schedule_request)

    # dispatch dynamodb item
    dynamodb_item = DynamoScheduler.get_dynamodb_item(schedule_item.schedule_id)
    Dispatcher.trigger_lambda_workflow(dynamodb_item)

    dynamodb_item_updated = DynamoScheduler.get_dynamodb_item(schedule_item.schedule_id)
    assert dynamodb_item_updated.status == ScheduleStatus.COMPLETED


@pytest.mark.slow
def test__dispatcher_trigger_lambda_workflow_not_exists(
    dynamo_tables, sns, lambda_function
):
    from lib.dispatcher.dispatcher import Dispatcher
    from lib.requests_handler.data import ScheduleRequest
    from lib.scheduler.data import ScheduleStatus
    from lib.scheduler.scheduler import DynamoScheduler

    schedule_time = int(time.time()) + 3 * 60
    schedule_request = ScheduleRequest(workflow_arn="test", schedule_time=schedule_time)
    schedule_item = DynamoScheduler.add_to_schedule(schedule_request)

    # dispatch dynamodb item
    dynamodb_item = DynamoScheduler.get_dynamodb_item(schedule_item.schedule_id)
    Dispatcher.trigger_lambda_workflow(dynamodb_item)

    dynamodb_item_updated = DynamoScheduler.get_dynamodb_item(schedule_item.schedule_id)
    assert dynamodb_item_updated.status == ScheduleStatus.ERROR
