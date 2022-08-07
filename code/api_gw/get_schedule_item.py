#!/usr/bin/env python
from lib.requests_handler import RequestsHandler
from lib.scheduler import DynamoScheduler

# resources
request_handler = RequestsHandler()
scheduler = DynamoScheduler()


def lambda_handler(event, contenxt):
    # TODO: Parse event for schedule id
    schedule_id = ""
    request_handler.get_schedule_item(schedule_id, scheduler)
