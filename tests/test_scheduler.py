#!/usr/bin/env python
import time

import pytest  # type: ignore
from moto.core import patch_resource  # type: ignore


def test__scheduler_get_item_not_exists(dynamo_tables):
    from lib.exceptions import NotFound
    from lib.scheduler.scheduler import DynamoScheduler

    with pytest.raises(NotFound):
        DynamoScheduler.get_schedule_item("test")


def test__scheduler_create_schedule_item(dynamo_tables):
    from lib.requests_handler.data import ScheduleRequest
    from lib.scheduler.data import DynamodbItem
    from lib.scheduler.scheduler import DynamoScheduler

    schedule_time = int(time.time())
    schedule_request = ScheduleRequest(
        workflow_arn="test_arn", schedule_time=schedule_time
    )
    dynamodb_item = DynamoScheduler._create_dynamodb_item(schedule_request)
    assert isinstance(dynamodb_item, DynamodbItem)


def test__scheduler_get_item_exists(dynamo_tables):
    from lib.requests_handler.data import ScheduleRequest
    from lib.scheduler.scheduler import DynamoScheduler

    schedule_time = int(time.time())
    schedule_request = ScheduleRequest(
        workflow_arn="test_arn", schedule_time=schedule_time
    )
    schedule_item = DynamoScheduler.add_to_schedule(schedule_request)
    schedule_item_2 = DynamoScheduler.get_schedule_item(schedule_item.schedule_id)
    assert schedule_item == schedule_item_2


def test__scheduler_remove_from_schedule_not_exists(dynamo_tables):
    from lib.exceptions import NotFound
    from lib.scheduler.scheduler import DynamoScheduler

    with pytest.raises(NotFound):
        DynamoScheduler.remove_from_schedule("test")


def test__scheduler_remove_from_schedule_exists(dynamo_tables):
    from lib.exceptions import NotFound
    from lib.requests_handler.data import ScheduleRequest
    from lib.scheduler.scheduler import DynamoScheduler

    schedule_time = int(time.time())
    schedule_request = ScheduleRequest(
        workflow_arn="test_arn", schedule_time=schedule_time
    )
    schedule_item = DynamoScheduler.add_to_schedule(schedule_request)
    DynamoScheduler.remove_from_schedule(schedule_item.schedule_id)

    with pytest.raises(NotFound):
        DynamoScheduler.get_schedule_item(schedule_item.schedule_id)


def test__scheduler_add_to_schedule_not_exists(dynamo_tables):
    from lib.requests_handler.data import ScheduleRequest
    from lib.scheduler.scheduler import DynamoScheduler

    schedule_time = int(time.time())
    schedule_request = ScheduleRequest(
        workflow_arn="test_arn", schedule_time=schedule_time
    )
    schedule_item = DynamoScheduler.add_to_schedule(schedule_request)
    schedule_item_2 = DynamoScheduler.get_schedule_item(schedule_item.schedule_id)
    assert schedule_item == schedule_item_2


def test__scheduler_get_schedule_items(dynamo_tables):
    from lib.requests_handler.data import ScheduleRequest
    from lib.scheduler.data import QueryRange, ScheduleStatus
    from lib.scheduler.scheduler import DynamoScheduler

    schedule_time = int(time.time())
    schedule_request = ScheduleRequest(
        workflow_arn="test_arn", schedule_time=schedule_time
    )
    schedule_item = DynamoScheduler.add_to_schedule(schedule_request)

    schedule_request = ScheduleRequest(
        workflow_arn="test_arn", schedule_time=schedule_time + 5 * 60
    )
    schedule_item = DynamoScheduler.add_to_schedule(schedule_request)

    schedule_request = ScheduleRequest(
        workflow_arn="test_arn", schedule_time=schedule_time + 6 * 60
    )
    schedule_item = DynamoScheduler.add_to_schedule(schedule_request)

    query_range = QueryRange(start_time=schedule_time, end_time=schedule_time + 6 * 60)
    schedule_items = DynamoScheduler.get_schedule_items(
        query_range, status=ScheduleStatus.NOT_STARTED
    )

    assert len(list(schedule_items)) == 2
