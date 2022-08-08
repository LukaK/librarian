#!/usr/bin/env python
import json
import logging
import time

import boto3  # type: ignore
from lib.environment import Environment
from lib.logging import request_context
from lib.scheduler.data import DynamodbItem, ScheduleStatus
from lib.scheduler.data_mapper import DataMapper
from lib.scheduler.scheduler import DynamoScheduler

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
        sns_payload = DataMapper.dynamodb_item_to_sns_payload(dynamodb_item)
        cls.sns_topic.publish(Message=sns_payload)

        # update table entry
        DynamoScheduler.update_dynamodb_item_status(
            dynamodb_item, ScheduleStatus.PROCESSING
        )
        logger.info("Item dispatched successfully", extra=request_context)

    @classmethod
    def trigger_lambda_workflow(cls, dynamodb_item: DynamodbItem) -> None:

        logger.info(f"Starting lambda workflow: {dynamodb_item}", extra=request_context)
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
