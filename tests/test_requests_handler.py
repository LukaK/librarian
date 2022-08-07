#!/usr/bin/env python
import json
import time

import pytest  # type: ignore
from moto.core import patch_resource  # type: ignore


@pytest.mark.requests_handler
def test__requests_handler_add_schedule_item(dynamo_tables):
    from lib.api_gw.requests_handler import RequestsHandler
    from lib.scheduler.scheduler import DynamoScheduler, dynamodb_resource

    patch_resource(dynamodb_resource)

    scheduler = DynamoScheduler()
    schedule_time = int(time.time())
    payload = {"schedule_time": schedule_time, "workflow_arn": "test"}
    response = RequestsHandler.add_schedule_item(payload, scheduler)
    assert response["status_code"] == 200


@pytest.mark.requests_handler
def test__requests_handler_get_schedule_item(dynamo_tables):
    from lib.api_gw.requests_handler import RequestsHandler
    from lib.scheduler.scheduler import DynamoScheduler, dynamodb_resource

    patch_resource(dynamodb_resource)

    scheduler = DynamoScheduler()
    schedule_time = int(time.time())
    payload = {"schedule_time": schedule_time, "workflow_arn": "test"}
    response = RequestsHandler.add_schedule_item(payload, scheduler)

    schedule_id = json.loads(response["body"])["schedule_id"]
    payload = {"schedule_id": schedule_id}
    response = RequestsHandler.get_schedule_item(payload, scheduler)
    assert response["status_code"] == 200


@pytest.mark.requests_handler
def test__requests_handler_remove_schedule_item(dynamo_tables):
    from lib.api_gw.requests_handler import RequestsHandler
    from lib.scheduler.scheduler import DynamoScheduler, dynamodb_resource

    patch_resource(dynamodb_resource)

    scheduler = DynamoScheduler()
    schedule_time = int(time.time())
    payload = {"schedule_time": schedule_time, "workflow_arn": "test"}
    response = RequestsHandler.add_schedule_item(payload, scheduler)

    schedule_id = json.loads(response["body"])["schedule_id"]
    payload = {"schedule_id": schedule_id}
    response = RequestsHandler.remove_schedule_item(payload, scheduler)
    assert response["status_code"] == 200
