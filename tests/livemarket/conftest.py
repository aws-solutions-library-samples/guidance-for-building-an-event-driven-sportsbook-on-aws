import os
import json
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for boto3."""
    with patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'testing',
        'AWS_SECRET_ACCESS_KEY': 'testing',
        'AWS_SECURITY_TOKEN': 'testing',
        'AWS_SESSION_TOKEN': 'testing',
        'AWS_DEFAULT_REGION': 'us-east-1'
    }):
        yield

@pytest.fixture
def events_client():
    """Mock EventBridge client."""
    mock_client = MagicMock()
    mock_client.put_events.return_value = {
        'FailedEntryCount': 0,
        'Entries': [{'EventId': '1234'}]
    }
    return mock_client

@pytest.fixture
def dynamodb_table():
    """Mock DynamoDB table."""
    mock_table = MagicMock()
    return mock_table

@pytest.fixture
def dynamodb_history_table():
    """Mock DynamoDB history table."""
    mock_table = MagicMock()
    return mock_table

@pytest.fixture
def mock_appsync_event():
    """Mock AppSync event."""
    return {
        'arguments': {},
        'identity': {
            'claims': {
                'sub': 'test-user-id',
                'email': 'user@example.com'
            }
        },
        'info': {
            'fieldName': 'testField',
            'parentTypeName': 'Query'
        },
        'request': {
            'headers': {
                'x-api-key': 'test-api-key'
            }
        },
        'source': {}
    }

@pytest.fixture
def mock_lambda_context():
    """Mock Lambda context."""
    context = MagicMock()
    context.function_name = "test-function"
    context.memory_limit_in_mb = 128
    context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
    context.aws_request_id = "test-request-id"
    return context

@pytest.fixture
def mock_gql_client():
    """Mock GraphQL client."""
    mock_client = MagicMock()
    return mock_client
