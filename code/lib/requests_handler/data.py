#!/usr/bin/env python
import json
import time
from dataclasses import dataclass
from typing import Optional

import pydantic  # type: ignore
from lib.exceptions import OperationsError, ValidationError


# data for schedule request
class ScheduleRequest(pydantic.BaseModel):
    schedule_time: int
    workflow_arn: str
    workflow_payload: dict = {}

    @pydantic.validator("schedule_time")
    @classmethod
    def validate_schedule_time(cls, value):
        current_time = int(time.time())
        if value <= current_time + 2 * 60:
            raise ValidationError(
                value=value, message=f"Schedule time too early: {value}"
            )
        return value

    @pydantic.validator("workflow_payload")
    @classmethod
    def validate_workflow_payload(cls, value):
        if value is not None:
            try:
                json.loads(value)
            except json.decoder.JSONDecodeError:
                raise ValidationError(
                    value=value, message=f"Unable to decode workflow payload: {value}"
                )
        return value

    class Config:
        frozen = True


# response data
@dataclass(frozen=True)
class Response:
    status_code: int
    body: str


# lambda proxy dataclsss
class LambdaProxyRequest(pydantic.BaseModel):
    lambda_event: dict
    context: Optional[object] = None

    @pydantic.validator("lambda_event")
    @classmethod
    def validate_lambda_event(cls, value: dict) -> dict:
        if "httpMethod" not in value:
            raise OperationsError(
                value=str(value), message="Lambda event not formatter correctly"
            )
        return value

    @property
    def http_method(self) -> str:
        return self.lambda_event["httpMethod"]

    @property
    def payload(self):
        if self.http_method == "GET":
            return self.query_string_parameters
        return self.body

    @property
    def query_string_parameters(self) -> Optional[dict]:
        return self.lambda_event.get("queryStringParameters")

    @property
    def body(self) -> Optional[dict]:
        body = self.lambda_event.get("body")
        return body if body is None else json.loads(body)
