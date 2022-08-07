#!/usr/bin/env python
import os

import boto3  # type: ignore
import pytest  # type: ignore
from lib.environment import Environment
from moto import mock_dynamodb2  # type: ignore
from pytest_mock import MockerFixture  # type: ignore


@pytest.fixture(scope="function")
def aws_credentials(mocker: MockerFixture):
    """Mocked AWS Credentials for moto."""
    mocker.patch.dict(
        os.environ,
        {
            "AWS_ACCESS_KEY_ID": "testing",
            "AWS_SECRET_ACCESS_KEY": "testing",
            "AWS_SECURITY_TOKEN": "testing",
            "AWS_SESSION_TOKEN": "testing",
            "AWS_DEFAULT_REGION": "us-east-1",
        },
    )


@pytest.fixture(scope="function")
def patch_environment(mocker: MockerFixture, aws_credentials):
    items_table_name = "schedule_items"
    hash_table_name = "period_hashes"
    index_name = "gsi_id"

    mocker.patch.dict(
        os.environ,
        {
            Environment.hash_table_env_name: hash_table_name,
            Environment.items_table_env_name: items_table_name,
        },
    )
    return items_table_name, index_name, hash_table_name


@pytest.fixture(scope="function")
def dynamo_tables(aws_credentials, patch_environment):
    with mock_dynamodb2():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        # Create items table
        dynamodb.create_table(
            TableName=patch_environment[0],
            KeySchema=[
                {"AttributeName": "time_period_hash", "KeyType": "HASH"},
                {"AttributeName": "trigger_time", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "time_period_hash", "AttributeType": "S"},
                {"AttributeName": "trigger_time", "AttributeType": "N"},
                {"AttributeName": "schedule_id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
            SSESpecification={
                "Enabled": True,
            },
            GlobalSecondaryIndexes=[
                {
                    "IndexName": patch_environment[1],
                    "KeySchema": [
                        {"AttributeName": "schedule_id", "KeyType": "HASH"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
        )

        # create hash table
        dynamodb.create_table(
            TableName=patch_environment[2],
            KeySchema=[
                {"AttributeName": "time_period", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "time_period", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
            SSESpecification={
                "Enabled": True,
            },
        )
        items_table = dynamodb.Table(patch_environment[0])
        hash_table = dynamodb.Table(patch_environment[2])
        yield items_table, hash_table
