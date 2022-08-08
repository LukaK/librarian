#!/usr/bin/env python
import io
import json
import os
import zipfile

import boto3  # type: ignore
import pytest  # type: ignore
from lib.environment import Environment
from moto import mock_dynamodb2, mock_iam, mock_lambda, mock_sns  # type: ignore
from pytest_mock import MockerFixture  # type: ignore

# TODO: Return dataclasses


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
    dispatcher_topic_name = "dispatcher_sns"

    mocker.patch.dict(
        os.environ,
        {
            Environment.hash_table_env_name: hash_table_name,
            Environment.items_table_env_name: items_table_name,
            Environment.schedule_id_index_env_name: index_name,
        },
    )
    return items_table_name, index_name, hash_table_name, dispatcher_topic_name


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


# TODO: Change env variable name and in cf, it is arn not topic name
@pytest.fixture
def sns(patch_environment, mocker: MockerFixture, aws_credentials):
    with mock_sns():
        sns_resource = boto3.resource("sns", region_name="us-east-1")
        workflow_topic = sns_resource.create_topic(Name=patch_environment[3])

        # patch environment with sns arn
        mocker.patch.dict(
            os.environ,
            {Environment.dispatch_sns_env_name: workflow_topic.arn},
        )

        yield workflow_topic


@pytest.fixture
def workflow_role(aws_credentials):
    with mock_iam():
        iam_resource = boto3.resource("iam", region_name="eu-west-1")

        assume_policy_document = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "*", "Resource": "*"},
        }

        role = iam_resource.create_role(
            RoleName="TestStepFunctionRole",
            AssumeRolePolicyDocument=json.dumps(assume_policy_document),
        )

        yield role


def zip_lambda_function_code():
    function_code = "def lambda_handler(event, context):\n" "    return event"

    zip_output = io.BytesIO()
    with zipfile.ZipFile(zip_output, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("lambda_function.py", function_code)
    zip_output.seek(0)
    return zip_output.read()


@pytest.fixture
def lambda_function(workflow_role):
    with mock_lambda():
        lambda_client = boto3.client("lambda")
        lambda_definition = {
            "FunctionName": "test_function",
            "Runtime": "python3.7",
            "Role": workflow_role.arn,
            "Handler": "lambda_function.lambda_handler",
            "Code": {
                "ZipFile": zip_lambda_function_code(),
            },
            "Description": "lambda function",
            "Timeout": 3,
            "MemorySize": 128,
            "Publish": True,
        }

        response = lambda_client.create_function(**lambda_definition)
        lambda_arn = response["FunctionArn"]
        yield lambda_client, lambda_arn
