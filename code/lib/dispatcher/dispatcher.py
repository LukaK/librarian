#!/usr/bin/env python
import json
import logging
import time

import boto3  # type: ignore
from lib.environment import Environment
from lib.logging import request_context
from lib.requests_handler.encoder import DecimalEncoder
from lib.scheduler.data import DynamodbItem, ScheduleStatus
from lib.scheduler.data_mapper import DataMapper
from lib.scheduler.scheduler import DynamoScheduler

from .data import LambdaProxySnsEvent

# resources
logger = logging.getLogger(__name__)
sns_resource = boto3.resource("sns")
lambda_client = boto3.client("lambda")


class Dispatcher:

    # resources
    environment = Environment.dispatcher_env()
    sns_topic = sns_resource.Topic(environment.dispatch_topic_name)

    @classmethod
    def dispatch_dynamodb_item(cls, dynamodb_item: DynamodbItem) -> None:
        logger.info(
            f"Dispatching for execution: {dynamodb_item}", extra=request_context
        )

        # send to sns
        sns_payload = json.dumps(
            DataMapper._dynamodb_item_to_record(dynamodb_item), cls=DecimalEncoder
        )
        cls.sns_topic.publish(Message=sns_payload)

        # update table entry
        DynamoScheduler.update_dynamodb_item_status(
            dynamodb_item, ScheduleStatus.PROCESSING
        )
        logger.info("Item dispatched successfully", extra=request_context)

    @classmethod
    def trigger_lambda_workflow(cls, sns_payload: LambdaProxySnsEvent) -> None:

        logger.info(f"Starting lambda workflow: {sns_payload}", extra=request_context)
        dynamodb_item = DataMapper._record_to_dynamodb_item(
            json.loads(sns_payload.payload)
        )
        schedule_item = dynamodb_item.schedule_item

        # waint untill its time
        wait_time = schedule_item.schedule_time - int(time.time())
        logger.info(f"Waiting: {wait_time}", extra=request_context)
        time.sleep(wait_time)

        # start lambda workflow
        logger.info(
            f"Starting lambda function workflow: {schedule_item.workflow_arn}",
            extra=request_context,
        )
        response = lambda_client.invoke(
            FunctionName=schedule_item.workflow_arn,
            InvocationType="Event",
            Payload=json.dumps(schedule_item.workflow_payload),
        )
        DynamoScheduler.update_dynamodb_item_status(
            dynamodb_item, ScheduleStatus.COMPLETED
        )
        logger.info(f"Lambda function started successfully: {response}")
