#!/usr/bin/env python


class ValidationError(Exception):
    """Custom validation error"""

    def __init__(self, value: str, message: str) -> None:
        self.value = value
        self.message = message
        super().__init__(message)
