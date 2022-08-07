#!/usr/bin/env python
import json
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    """Json encoder that handles conversions in dynamodb from int to decimal"""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj)
        return json.JSONEncoder.default(self, obj)
