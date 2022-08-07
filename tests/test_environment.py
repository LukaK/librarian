#!/usr/bin/env python
import pytest  # type: ignore


@pytest.mark.environment
def test__environment_no_patch():
    from lib.environment import Environment, EnvironmentConfigError

    with pytest.raises(EnvironmentConfigError):
        Environment.dynamodb_scheduler_env()


@pytest.mark.environment
def test__environment_patched(patch_environment):
    from lib.environment import DynamodbSchedulerEnvironment, Environment

    environment = Environment.dynamodb_scheduler_env()
    assert isinstance(environment, DynamodbSchedulerEnvironment)
