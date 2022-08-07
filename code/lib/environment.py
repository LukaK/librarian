#!/usr/bin/env python
import os
from dataclasses import dataclass

from .exceptions import EnvironmentConfigError


@dataclass
class DynamodbSchedulerEnvironment:
    hash_table_name: str
    items_table_name: str


class Environment:

    hash_table_env_name = "HASH_TABLE_NAME"
    items_table_env_name = "SCHEDULE_ITEMS_TABLE_NAME"

    @classmethod
    def dynamodb_scheduler_env(cls) -> DynamodbSchedulerEnvironment:
        try:
            return DynamodbSchedulerEnvironment(
                hash_table_name=os.environ[cls.hash_table_env_name],
                items_table_name=os.environ[cls.items_table_env_name],
            )
        except KeyError as e:
            raise EnvironmentConfigError(message=str(e))
