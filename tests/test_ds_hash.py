#!/usr/bin/env python
import time

import pytest  # type: ignore
from boto3.dynamodb.conditions import Key  # type: ignore
from lib.exceptions import OperationsError
from moto.core import patch_resource  # type: ignore


def test__ds_hash_load_hash_not_exists(dynamo_tables):
    from lib.scheduler.ds_hash import DSPeriodHasher, dynamodb_resource

    patch_resource(dynamodb_resource)

    period_hash = DSPeriodHasher._load_period_hash("test_period")
    assert period_hash is None


def test__ds_hash_load_hash_exists(dynamo_tables):
    from lib.scheduler.ds_hash import DSPeriodHasher, dynamodb_resource

    patch_resource(dynamodb_resource)

    # get hash table
    hash_table = dynamo_tables[1]
    hash_table.put_item(
        Item={
            DSPeriodHasher.period_key_key: "test_period",
            DSPeriodHasher.hash_key: "test_hash",
        },
    )

    period_map = DSPeriodHasher._load_period_hash("test_period")
    assert period_map.time_period_hash == "test_hash"


def test__ds_hash_add_period_hash_not_exists(dynamo_tables):
    from lib.scheduler.ds_hash import DSPeriodHasher, dynamodb_resource

    patch_resource(dynamodb_resource)

    period_map = DSPeriodHasher._add_period_hash("test_period")

    hash_table = dynamo_tables[1]
    response = hash_table.query(
        KeyConditionExpression=Key(DSPeriodHasher.period_key_key).eq("test_period"),
    )
    assert len(response["Items"]) == 1
    item = response["Items"][0]
    assert item[DSPeriodHasher.period_key_key] == period_map.time_period
    assert item[DSPeriodHasher.hash_key] == period_map.time_period_hash


def test__ds_hash_add_period_hash_exists(dynamo_tables):
    from lib.scheduler.ds_hash import DSPeriodHasher, dynamodb_resource

    patch_resource(dynamodb_resource)

    hash_table = dynamo_tables[1]
    hash_table.put_item(
        Item={
            DSPeriodHasher.period_key_key: "test_period",
            DSPeriodHasher.hash_key: "test_hash",
        },
    )
    with pytest.raises(OperationsError):
        DSPeriodHasher._add_period_hash("test_period")


def test__ds_hash_get_time_period_hash_not_exists(dynamo_tables):
    from lib.scheduler.ds_hash import DSPeriodHasher, dynamodb_resource

    patch_resource(dynamodb_resource)

    schedule_time = int(time.time())
    period_map = DSPeriodHasher.get_time_period_hash(schedule_time)

    assert period_map is not None
