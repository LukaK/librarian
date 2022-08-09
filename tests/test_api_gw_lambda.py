#!/usr/bin/env python
import json
import time


def test__remove_item_lambda_not_exists(dynamo_tables):
    from api_gw.remove_schedule_item import lambda_handler

    lambda_event = {
        "httpMethod": "POST",
        "body": json.dumps({"schedule_id": "test_id"}),
    }
    response = lambda_handler(lambda_event, None)
    assert response["status_code"] != 200


def test__remove_item_lambda_exists(dynamo_tables):
    from api_gw.remove_schedule_item import lambda_handler
    from lib.requests_handler.data import ScheduleRequest
    from lib.scheduler.scheduler import DynamoScheduler

    schedule_time = int(time.time())
    schedule_request = ScheduleRequest(
        workflow_arn="test_arn", schedule_time=schedule_time
    )
    schedule_item = DynamoScheduler.add_to_schedule(schedule_request)

    lambda_event = {
        "httpMethod": "POST",
        "body": json.dumps({"schedule_id": schedule_item.schedule_id}),
    }
    response = lambda_handler(lambda_event, None)
    assert response["status_code"] == 200


def test__get_item_lambda_not_exists(dynamo_tables):
    from api_gw.get_schedule_item import lambda_handler

    lambda_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"schedule_id": "test_id"},
    }
    response = lambda_handler(lambda_event, None)
    assert response["status_code"] != 200


def test__get_item_lambda_exists(dynamo_tables):
    from api_gw.get_schedule_item import lambda_handler
    from lib.requests_handler.data import ScheduleRequest
    from lib.scheduler.scheduler import DynamoScheduler

    schedule_time = int(time.time())
    schedule_request = ScheduleRequest(
        workflow_arn="test_arn", schedule_time=schedule_time
    )
    schedule_item = DynamoScheduler.add_to_schedule(schedule_request)

    lambda_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"schedule_id": schedule_item.schedule_id},
    }

    response = lambda_handler(lambda_event, None)
    assert response["status_code"] == 200


def test__add_to_schedule_not_exists(dynamo_tables):
    from api_gw.schedule_item import lambda_handler

    lambda_event = {
        "httpMethod": "POST",
        "body": json.dumps({"schedule_time": int(time.time()), "workflow_arn": "test"}),
    }
    response = lambda_handler(lambda_event, None)
    assert response["status_code"] == 200


def test__update_schedule_item_not_exists(dynamo_tables):
    from api_gw.update_schedule_item import lambda_handler

    lambda_event = {
        "httpMethod": "POST",
        "body": json.dumps(
            {
                "schedule_time": int(time.time()),
                "workflow_arn": "test",
                "schedule_id": "test",
            }
        ),
    }
    response = lambda_handler(lambda_event, None)
    assert response["status_code"] == 400


def test__update_schedule_item_exists(dynamo_tables):
    from api_gw.update_schedule_item import lambda_handler
    from lib.requests_handler.data import ScheduleRequest
    from lib.scheduler.scheduler import DynamoScheduler

    schedule_time = int(time.time())
    schedule_request = ScheduleRequest(
        workflow_arn="test_arn", schedule_time=schedule_time
    )
    schedule_item = DynamoScheduler.add_to_schedule(schedule_request)

    lambda_event = {
        "httpMethod": "POST",
        "body": json.dumps(
            {
                "schedule_time": int(time.time()),
                "workflow_arn": "test",
                "schedule_id": schedule_item.schedule_id,
            }
        ),
    }
    response = lambda_handler(lambda_event, None)
    assert response["status_code"] == 200
