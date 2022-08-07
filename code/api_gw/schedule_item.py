#!/usr/bin/env python
from lib.data import LambdaProxyRequest
from lib.requests_handler import RequestsHandler
from lib.scheduler import DynamoScheduler

# resources
request_handler = RequestsHandler()
scheduler = DynamoScheduler()


def lambda_handler(event, context):
    lambda_proxy_event = LambdaProxyRequest(event, context)
    request_handler.remove_schedule_item(lambda_proxy_event.payload, scheduler)
