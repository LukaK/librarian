#!/usr/bin/env python
import logging
import os
from dataclasses import dataclass

from .exceptions import EnvironmentConfigError
from .logging import request_context

logger = logging.getLogger(__name__)


@dataclass
class DynamodbSchedulerEnvironment:
    hash_table_name: str
    items_table_name: str
    schedule_id_index_name: str


@dataclass
class DispatcherEnvironment:
    dispatch_topic_name: str


class Environment:

    hash_table_env_name = "HASH_TABLE_NAME"
    items_table_env_name = "SCHEDULE_ITEMS_TABLE_NAME"
    schedule_id_index_env_name = "SCHEDULE_ID_INDEX_NAME"
    dispatch_sns_env_name = "DISPATCHER_SNS_ARN"

    @classmethod
    def dynamodb_scheduler_env(cls) -> DynamodbSchedulerEnvironment:
        logger.info("Retrieving environment for the scheduler", extra=request_context)
        try:
            env = DynamodbSchedulerEnvironment(
                hash_table_name=os.environ[cls.hash_table_env_name],
                items_table_name=os.environ[cls.items_table_env_name],
                schedule_id_index_name=os.environ[cls.schedule_id_index_env_name],
            )
            logger.info(f"Environment retrieved: {env}", extra=request_context)
            return env
        except KeyError as e:
            raise EnvironmentConfigError(message=str(e))

    @classmethod
    def dispatcher_env(cls):
        logger.info("Retrieving environment for the dispatcher", extra=request_context)
        try:
            env = DispatcherEnvironment(
                dispatch_topic_name=os.environ[cls.dispatch_sns_env_name],
            )
            logger.info(f"Environment retrieved: {env}", extra=request_context)
            return env
        except KeyError as e:
            raise EnvironmentConfigError(message=str(e))
