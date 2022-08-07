#!/usr/bin/env python
from lib.requests_handler.data import LambdaProxyRequest
from lib.requests_handler.requests_handler import RequestsHandler
from lib.scheduler.scheduler import DynamoScheduler

# resources
request_handler = RequestsHandler()
scheduler = DynamoScheduler()


def lambda_handler(event, context):
    lambda_proxy_event = LambdaProxyRequest(lambda_event=event)
    return request_handler.get_schedule_item(lambda_proxy_event.payload, scheduler)
