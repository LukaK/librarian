#!/usr/bin/env python
import time

from lib.dispatcher.dispatcher import Dispatcher
from lib.scheduler.data import QueryRange, ScheduleStatus
from lib.scheduler.scheduler import DynamoScheduler


def lambda_handler(event, context):
    current_time = int(time.time())
    start_time = current_time - 60
    end_time = current_time + 60
    query_range = QueryRange(start_time=start_time, end_time=end_time)

    for dynamodb_item in DynamoScheduler.get_dynamodb_items(
        query_range, ScheduleStatus.NOT_STARTED
    ):
        Dispatcher.dispatch_dynamodb_item(dynamodb_item)
