#!/usr/bin/env python
import json
import time


def test__requests_handler_add_schedule_item(dynamo_tables):
    from lib.requests_handler.requests_handler import RequestsHandler
    from lib.scheduler.scheduler import DynamoScheduler

    scheduler = DynamoScheduler()
    schedule_time = int(time.time())
    payload = {"schedule_time": schedule_time, "workflow_arn": "test"}
    response = RequestsHandler.add_schedule_item(payload, scheduler)
    assert response["status_code"] == 200


def test__requests_handler_get_schedule_item(dynamo_tables):
    from lib.requests_handler.requests_handler import RequestsHandler
    from lib.scheduler.scheduler import DynamoScheduler

    scheduler = DynamoScheduler()
    schedule_time = int(time.time())
    payload = {"schedule_time": schedule_time, "workflow_arn": "test"}
    response = RequestsHandler.add_schedule_item(payload, scheduler)

    schedule_id = json.loads(response["body"])["schedule_id"]
    payload = {"schedule_id": schedule_id}
    response = RequestsHandler.get_schedule_item(payload, scheduler)
    assert response["status_code"] == 200


def test__requests_handler_remove_schedule_item(dynamo_tables):
    from lib.requests_handler.requests_handler import RequestsHandler
    from lib.scheduler.scheduler import DynamoScheduler

    scheduler = DynamoScheduler()
    schedule_time = int(time.time())
    payload = {"schedule_time": schedule_time, "workflow_arn": "test"}
    response = RequestsHandler.add_schedule_item(payload, scheduler)

    schedule_id = json.loads(response["body"])["schedule_id"]
    payload = {"schedule_id": schedule_id}
    response = RequestsHandler.remove_schedule_item(payload, scheduler)
    assert response["status_code"] == 200


def test__requests_handler_update_schedule_item(dynamo_tables):
    from lib.requests_handler.requests_handler import RequestsHandler
    from lib.scheduler.scheduler import DynamoScheduler

    scheduler = DynamoScheduler()
    schedule_time = int(time.time())
    payload = {"schedule_time": schedule_time, "workflow_arn": "test"}
    response = RequestsHandler.add_schedule_item(payload, scheduler)

    schedule_id = json.loads(response["body"])["schedule_id"]
    payload = {"schedule_id": schedule_id, **payload}
    response = RequestsHandler.update_schedule_item(payload, scheduler)
    assert response["status_code"] == 200
