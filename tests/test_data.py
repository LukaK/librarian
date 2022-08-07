#!/usr/bin/env python
import time

import pytest  # type: ignore
from lib.data import LambdaProxyRequest, ScheduleItem
from lib.exceptions import OperationsError


@pytest.mark.data
def test__schedule_item_random_id_and_trigger():
    schedule_time = int(time.time())
    schedule_item_1 = ScheduleItem(
        time_period_hash="test_hash",
        schedule_time=schedule_time,
        workflow_arn="test_arn",
    )
    schedule_item_2 = ScheduleItem(
        time_period_hash="test_hash",
        schedule_time=schedule_time,
        workflow_arn="test_arn",
    )

    assert schedule_item_1.trigger_time != schedule_item_2.trigger_time
    assert schedule_item_1.schedule_id != schedule_item_2.schedule_id


@pytest.mark.data
def test__schedule_item_set_id_and_trigger():
    schedule_time = int(time.time())
    schedule_item_1 = ScheduleItem(
        time_period_hash="test_hash",
        schedule_time=schedule_time,
        workflow_arn="test_arn",
        schedule_id="test_id",
        trigger_time=schedule_time,
    )
    schedule_item_2 = ScheduleItem(
        time_period_hash="test_hash",
        schedule_time=schedule_time,
        workflow_arn="test_arn",
        schedule_id="test_id",
        trigger_time=schedule_time,
    )

    assert schedule_item_1.trigger_time == schedule_item_2.trigger_time
    assert schedule_item_1.schedule_id == schedule_item_2.schedule_id


@pytest.mark.data
def test__lambda_proxy_request_invalid_event():
    with pytest.raises(OperationsError):
        LambdaProxyRequest(lambda_event={})


@pytest.mark.data
def test__lambda_proxy_request():
    lambda_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"schedle_id": "test_id"},
    }
    LambdaProxyRequest(lambda_event=lambda_event)
