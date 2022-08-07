#!/usr/bin/env python
import time

import pytest  # type: ignore
from moto.core import patch_resource  # type: ignore


@pytest.mark.scheduler
def test__scheduler_get_item_not_exists(dynamo_tables):
    from lib.exceptions import NotFound
    from lib.scheduler import DynamoScheduler, dynamodb_resource

    patch_resource(dynamodb_resource)
    with pytest.raises(NotFound):
        DynamoScheduler.get_schedule_item("test")


@pytest.mark.scheduler
def test__scheduler_create_schedule_item(dynamo_tables):
    from lib.data import ScheduleItem, ScheduleRequest
    from lib.scheduler import DynamoScheduler, dynamodb_resource

    patch_resource(dynamodb_resource)
    schedule_time = int(time.time())
    schedule_request = ScheduleRequest(
        workflow_arn="test_arn", schedule_time=schedule_time
    )
    schedule_item = DynamoScheduler.create_schedule_item(schedule_request)

    assert isinstance(schedule_item, ScheduleItem)


@pytest.mark.scheduler
def test__scheduler_get_item_exists(dynamo_tables):
    from lib.data import ScheduleItem, ScheduleRequest
    from lib.scheduler import DynamoScheduler, dynamodb_resource

    patch_resource(dynamodb_resource)
    schedule_time = int(time.time())
    schedule_request = ScheduleRequest(
        workflow_arn="test_arn", schedule_time=schedule_time
    )
    schedule_item = DynamoScheduler.create_schedule_item(schedule_request)
    DynamoScheduler.add_to_schedule(schedule_item)

    schedule_item_2 = DynamoScheduler.get_schedule_item(schedule_item.schedule_id)
    assert schedule_item == schedule_item_2


@pytest.mark.scheduler
def test__scheduler_remove_from_schedule_not_exists(dynamo_tables):
    from lib.exceptions import NotFound
    from lib.scheduler import DynamoScheduler, dynamodb_resource

    patch_resource(dynamodb_resource)
    with pytest.raises(NotFound):
        DynamoScheduler.remove_from_schedule("test")


@pytest.mark.scheduler
def test__scheduler_remove_from_schedule_exists(dynamo_tables):
    from lib.data import ScheduleItem, ScheduleRequest
    from lib.exceptions import NotFound
    from lib.scheduler import DynamoScheduler, dynamodb_resource

    patch_resource(dynamodb_resource)
    schedule_time = int(time.time())
    schedule_request = ScheduleRequest(
        workflow_arn="test_arn", schedule_time=schedule_time
    )
    schedule_item = DynamoScheduler.create_schedule_item(schedule_request)
    DynamoScheduler.add_to_schedule(schedule_item)
    DynamoScheduler.remove_from_schedule(schedule_item.schedule_id)

    with pytest.raises(NotFound):
        DynamoScheduler.get_schedule_item(schedule_item.schedule_id)


@pytest.mark.scheduler
def test__scheduler_add_to_schedule_exists(dynamo_tables):

    from lib.data import ScheduleItem, ScheduleRequest
    from lib.exceptions import OperationsError
    from lib.scheduler import DynamoScheduler, dynamodb_resource

    patch_resource(dynamodb_resource)
    schedule_time = int(time.time())
    schedule_request = ScheduleRequest(
        workflow_arn="test_arn", schedule_time=schedule_time
    )
    schedule_item = DynamoScheduler.create_schedule_item(schedule_request)
    DynamoScheduler.add_to_schedule(schedule_item)

    with pytest.raises(OperationsError):
        DynamoScheduler.add_to_schedule(schedule_item)


@pytest.mark.scheduler
def test__scheduler_add_to_schedule_not_exists(dynamo_tables):
    from lib.data import ScheduleItem, ScheduleRequest
    from lib.scheduler import DynamoScheduler, dynamodb_resource

    patch_resource(dynamodb_resource)

    schedule_time = int(time.time())
    schedule_request = ScheduleRequest(
        workflow_arn="test_arn", schedule_time=schedule_time
    )
    schedule_item = DynamoScheduler.create_schedule_item(schedule_request)

    DynamoScheduler.add_to_schedule(schedule_item)
    schedule_item_2 = DynamoScheduler.get_schedule_item(schedule_item.schedule_id)
    assert schedule_item == schedule_item_2