#!/usr/bin/env python
import json
import logging
import time
from dataclasses import asdict

import boto3  # type: ignore
from lib.environment import Environment
from lib.logging import request_context
from lib.scheduler.data import ScheduleItem

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
    def dispatch_schedule_item(cls, schedule_item: ScheduleItem) -> None:
        logger.info(
            f"Dispatching for execution: {schedule_item}", extra=request_context
        )
        sns_payload = json.dumps(asdict(schedule_item))
        cls.sns_topic.publish(Message=sns_payload)
        logger.info("Item dispatched successfully", extra=request_context)

    @classmethod
    def trigger_lambda_workflow(cls, sns_payload: LambdaProxySnsEvent) -> None:

        logger.info(f"Starting lambda workflow: {sns_payload}", extra=request_context)
        schedule_item = ScheduleItem(**json.loads(sns_payload.payload))

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
        logger.info(f"Lambda function started successfully: {response}")
