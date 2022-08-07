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
    mocker.patch.dict(
        os.environ,
        {Environment.hash_table_env_name: "", Environment.items_table_env_name: ""},
    )


@pytest.fixture(scope="function")
def mock_dynamodb(aws_credentials):
    @mock_dynamodb2
    def dynamo_table():

        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        # create items table
        dynamodb.create_table(
            TableName="items_table",
            KeySchema=[
                {"AttributeName": "time_period_hash", "KeyType": "HASH"},
                {"AttributeName": "trigger_time", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "time_period_hash", "AttributeType": "S"},
                {"AttributeName": "trigger_time", "AttributeType": "N"},
                {"AttributeName": "gsi_id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "gsi_id",
                    "KeySchema": [
                        {"AttributeName": "schedule_id", "KeyType": "HASH"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
        )

        dynamodb.create_table(
            TableName="period_hash_table",
            KeySchema=[
                {"AttributeName": "time_period", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "time_period", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        return dynamodb

    return mock_dynamodb
