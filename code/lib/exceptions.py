#!/usr/bin/env python


class ValidationError(Exception):
    """Custom validation error"""

    def __init__(self, value: str, message: str) -> None:
        self.value = value
        self.message = message
        super().__init__(message)


class EnvironmentConfigError(Exception):
    """Custom environment initialization error"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFound(Exception):
    """Custom not found error"""

    def __init__(self, value: str, message: str) -> None:
        self.value = value
        self.message = message
        super().__init__(message)


class OperationsError(Exception):
    """Custom operations error"""

    def __init__(self, value: str, message: str) -> None:
        self.value = value
        self.message = message
        super().__init__(message)
