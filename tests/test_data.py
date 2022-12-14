#!/usr/bin/env python
import time

import pytest  # type: ignore
from lib.exceptions import OperationsError, ValidationError
from lib.requests_handler.data import LambdaProxyRequest
from lib.scheduler.data import DynamodbItem, QueryRange, ScheduleItem


def test__schedule_item_random_id():
    schedule_time = int(time.time()) + 3 * 60
    schedule_item_1 = ScheduleItem(
        schedule_time=schedule_time,
        workflow_arn="test_arn",
    )
    schedule_item_2 = ScheduleItem(
        schedule_time=schedule_time,
        workflow_arn="test_arn",
    )

    assert schedule_item_1.schedule_id != schedule_item_2.schedule_id


def test__schedule_item_set_id():
    schedule_time = int(time.time()) + 3 * 60
    schedule_item_1 = ScheduleItem(
        schedule_time=schedule_time,
        workflow_arn="test_arn",
        schedule_id="test_id",
    )
    schedule_item_2 = ScheduleItem(
        schedule_time=schedule_time,
        workflow_arn="test_arn",
        schedule_id="test_id",
    )

    assert schedule_item_1.schedule_id == schedule_item_2.schedule_id


def test__dynamodb_item_random_trigger_time():
    schedule_time = int(time.time()) + 3 * 60
    schedule_item = ScheduleItem(
        schedule_time=schedule_time,
        workflow_arn="test_arn",
    )
    dynamodb_item1 = DynamodbItem(time_period_hash="test", schedule_item=schedule_item)
    dynamodb_item2 = DynamodbItem(time_period_hash="test", schedule_item=schedule_item)

    assert dynamodb_item1.trigger_time != dynamodb_item2.trigger_time


def test__dynamodb_item_set_trigger_time():
    schedule_time = int(time.time()) + 3 * 60
    schedule_item = ScheduleItem(
        schedule_time=schedule_time,
        workflow_arn="test_arn",
    )
    dynamodb_item1 = DynamodbItem(
        time_period_hash="test", schedule_item=schedule_item, trigger_time=schedule_time
    )
    dynamodb_item2 = DynamodbItem(
        time_period_hash="test", schedule_item=schedule_item, trigger_time=schedule_time
    )

    assert dynamodb_item1.trigger_time == dynamodb_item2.trigger_time


def test__lambda_proxy_request_invalid_event():
    with pytest.raises(OperationsError):
        LambdaProxyRequest(lambda_event={})


def test__lambda_proxy_request():
    lambda_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"schedle_id": "test_id"},
    }
    LambdaProxyRequest(lambda_event=lambda_event)


def test__query_range_negative_diff():
    with pytest.raises(ValidationError):
        QueryRange(start_time=1, end_time=0)


def test__query_range_too_big_range():
    with pytest.raises(ValidationError):
        QueryRange(start_time=0, end_time=11 * 60)
