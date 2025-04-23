import os
import json
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for boto3."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

@pytest.fixture
def events_client():
    """Create a mock EventBridge client."""
    mock_events = MagicMock()
    mock_events.put_events.return_value = {
        "FailedEntryCount": 0,
        "Entries": [
            {
                "EventId": "11710aed-b79e-4468-a20b-bb3c0c3b4860"
            }
        ],
        "ResponseMetadata": {
            "RequestId": "1234"
        }
    }
    return mock_events
