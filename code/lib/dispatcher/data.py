#!/usr/bin/env python
import json
from typing import Optional

import pydantic
from lib.exceptions import ValidationError


class LambdaProxySnsEvent(pydantic.BaseModel):
    lambda_event: dict
    context: Optional[object] = None

    @pydantic.validator("lambda_event")
    @classmethod
    def validate_lambda_event(cls, value: dict) -> dict:
        try:
            message = value["Records"][0]["Sns"]["Message"]
            payload = json.loads(message)
        except (json.decoder.JSONDecodeError, KeyError):
            raise ValidationError(
                value=str(value), message=f"Invalid lambda event: {str(value)}"
            )
        return value

    @property
    def payload(self) -> str:
        return self.lambda_event["Records"][0]["Sns"]["Message"]

    # configuration
    class Config:
        frozen = True
