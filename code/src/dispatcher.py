#!/usr/bin/env python
from lib.dispatcher.data import LambdaProxySnsEvent
from lib.dispatcher.dispatcher import Dispatcher
from lib.scheduler.data_mapper import DataMapper


def lambda_handler(event, context):
    sns_event = LambdaProxySnsEvent(lambda_event=event)
    dynamodb_item = DataMapper.sns_payload_todynamodb_item(sns_event)
    Dispatcher.trigger_lambda_workflow(dynamodb_item)
