import os
import pytest
import boto3
from moto import mock_dynamodb, mock_events, mock_sqs
from datetime import datetime, timezone, UTC

@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for boto3."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["EVENT_BUS"] = "test-event-bus"
    os.environ["DB_TABLE"] = "test-wallet-table"

@pytest.fixture(scope="function")
def dynamodb_client(aws_credentials):
    with mock_dynamodb():
        yield boto3.client("dynamodb", region_name="us-east-1")

@pytest.fixture(scope="function")
def dynamodb_resource(aws_credentials):
    with mock_dynamodb():
        yield boto3.resource("dynamodb", region_name="us-east-1")

@pytest.fixture(scope="function")
def events_client(aws_credentials):
    with mock_events():
        client = boto3.client("events", region_name="us-east-1")
        # Create the test event bus
        try:
            client.create_event_bus(Name="test-event-bus")
        except Exception as e:
            print(f"Error creating event bus: {e}")
        yield client
        
        # Clean up
        try:
            client.delete_event_bus(Name="test-event-bus")
        except Exception as e:
            print(f"Error deleting event bus: {e}")

@pytest.fixture(scope="function")
def wallet_table(dynamodb_resource):
    """Create a DynamoDB wallet table fixture."""
    table = dynamodb_resource.create_table(
        TableName="test-wallet-table",
        KeySchema=[{"AttributeName": "userId", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "userId", "AttributeType": "S"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    
    # Wait until the table exists
    table.meta.client.get_waiter("table_exists").wait(TableName="test-wallet-table")
    
    return table

@pytest.fixture(scope="function")
def event_bus(events_client):
    """Create an EventBridge event bus fixture."""
    events_client.create_event_bus(Name="test-event-bus")
    
    yield
    
    # Clean up
    events_client.delete_event_bus(Name="test-event-bus")

@pytest.fixture(scope="function")
def sqs_queue(sqs_resource):
    """Create an SQS queue fixture."""
    queue = sqs_resource.create_queue(QueueName="test-queue")
    yield queue
    queue.delete()

@pytest.fixture
def appsync_event_get_wallet():
    """Sample AppSync event for getWallet query."""
    return {
        "info": {
            "fieldName": "getWallet",
            "parentTypeName": "Query",
            "variables": {},
            "selectionSetList": ["userId", "balance"],
        },
        "identity": {
            "sub": "test-user-id",
            "issuer": "test-issuer",
            "username": "test-username",
            "claims": {},
            "sourceIp": ["127.0.0.1"],
            "defaultAuthStrategy": "ALLOW",
        },
        "source": None,
        "request": {
            "headers": {
                "x-forwarded-for": "127.0.0.1",
                "accept-encoding": "gzip, deflate, br",
                "content-type": "application/json",
            }
        },
        "prev": None,
        "stash": {},
        "arguments": {},
    }

@pytest.fixture
def appsync_event_deposit_funds():
    """Sample AppSync event for depositFunds mutation."""
    return {
        "info": {
            "fieldName": "depositFunds",
            "parentTypeName": "Mutation",
            "variables": {},
            "selectionSetList": ["userId", "balance"],
        },
        "identity": {
            "sub": "test-user-id",
            "issuer": "test-issuer",
            "username": "test-username",
            "claims": {},
            "sourceIp": ["127.0.0.1"],
            "defaultAuthStrategy": "ALLOW",
        },
        "source": None,
        "request": {
            "headers": {
                "x-forwarded-for": "127.0.0.1",
                "accept-encoding": "gzip, deflate, br",
                "content-type": "application/json",
            }
        },
        "prev": None,
        "stash": {},
        "arguments": {"input": {"amount": "100.00"}},
    }

@pytest.fixture
def appsync_event_withdraw_funds():
    """Sample AppSync event for withdrawFunds mutation."""
    return {
        "info": {
            "fieldName": "withdrawFunds",
            "parentTypeName": "Mutation",
            "variables": {},
            "selectionSetList": ["userId", "balance"],
        },
        "identity": {
            "sub": "test-user-id",
            "issuer": "test-issuer",
            "username": "test-username",
            "claims": {},
            "sourceIp": ["127.0.0.1"],
            "defaultAuthStrategy": "ALLOW",
        },
        "source": None,
        "request": {
            "headers": {
                "x-forwarded-for": "127.0.0.1",
                "accept-encoding": "gzip, deflate, br",
                "content-type": "application/json",
            }
        },
        "prev": None,
        "stash": {},
        "arguments": {"input": {"amount": "50.00"}},
    }

@pytest.fixture
def appsync_event_create_wallet():
    """Sample AppSync event for createWallet mutation."""
    return {
        "info": {
            "fieldName": "createWallet",
            "parentTypeName": "Mutation",
            "variables": {},
            "selectionSetList": ["userId", "balance"],
        },
        "identity": {
            "sub": "admin-user-id",
            "issuer": "test-issuer",
            "username": "admin-username",
            "claims": {},
            "sourceIp": ["127.0.0.1"],
            "defaultAuthStrategy": "ALLOW",
        },
        "source": None,
        "request": {
            "headers": {
                "x-forwarded-for": "127.0.0.1",
                "accept-encoding": "gzip, deflate, br",
                "content-type": "application/json",
            }
        },
        "prev": None,
        "stash": {},
        "arguments": {"input": {"userId": "new-user-id"}},
    }

@pytest.fixture
def appsync_event_deduct_funds():
    """Sample AppSync event for deductFunds mutation."""
    return {
        "info": {
            "fieldName": "deductFunds",
            "parentTypeName": "Mutation",
            "variables": {},
            "selectionSetList": ["userId", "balance"],
        },
        "identity": {
            "sub": "admin-user-id",
            "issuer": "test-issuer",
            "username": "admin-username",
            "claims": {},
            "sourceIp": ["127.0.0.1"],
            "defaultAuthStrategy": "ALLOW",
        },
        "source": None,
        "request": {
            "headers": {
                "x-forwarded-for": "127.0.0.1",
                "accept-encoding": "gzip, deflate, br",
                "content-type": "application/json",
            }
        },
        "prev": None,
        "stash": {},
        "arguments": {"input": {"userId": "test-user-id", "amount": "25.00"}},
    }

@pytest.fixture(scope="function")
def sqs_client(aws_credentials):
    with mock_sqs():
        yield boto3.client("sqs", region_name="us-east-1")

@pytest.fixture(scope="function")
def sqs_resource(aws_credentials):
    with mock_sqs():
        yield boto3.resource("sqs", region_name="us-east-1")

@pytest.fixture
def sqs_event_updated_odds():
    """Sample SQS event with UpdatedOdds message."""
    return {
        "Records": [
            {
                "messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
                "receiptHandle": "MessageReceiptHandle",
                "body": json.dumps({
                    'source': 'com.thirdparty',
                    'detail-type': 'UpdatedOdds',
                    'detail': {
                        'eventId': 'e46436a8-a916-4143-a05c-99d120eabfdb',
                        'homeOdds': '2/1',
                        'awayOdds': '3/1',
                        'drawOdds': '5/2'
                    }
                }),
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1523232000000",
                    "SenderId": "123456789012",
                    "ApproximateFirstReceiveTimestamp": "1523232000001"
                },
                "messageAttributes": {},
                "md5OfBody": "7b270e59b47ff90a553787216d55d91d",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:MyQueue",
                "awsRegion": "us-east-1"
            }
        ]
    }

@pytest.fixture(scope="function")
def event_bus(events_client):
    """Create an EventBridge event bus fixture."""
    events_client.create_event_bus(Name="test-event-bus")
    
    yield
    
    # Clean up
    events_client.delete_event_bus(Name="test-event-bus")

@pytest.fixture(scope="function")
def sqs_queue(sqs_resource):
    """Create an SQS queue fixture."""
    queue = sqs_resource.create_queue(QueueName="test-queue")
    yield queue
    queue.delete()
