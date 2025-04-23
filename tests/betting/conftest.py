import os
import pytest
import json
from unittest.mock import MagicMock

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for boto3."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

@pytest.fixture
def dynamodb_table():
    """Create a mock DynamoDB table."""
    mock_table = MagicMock()
    mock_table.scan.return_value = {
        "Items": [
            {
                "userId": "user-1",
                "betId": "bet-1",
                "eventId": "event-1",
                "outcome": "homeWin",
                "amount": 10.0,
                "odds": "2/1",
                "betStatus": "placed"
            }
        ],
        "Count": 1,
        "ScannedCount": 1
    }
    mock_table.query.return_value = {
        "Items": [
            {
                "userId": "user-1",
                "betId": "bet-1",
                "eventId": "event-1",
                "outcome": "homeWin",
                "amount": 10.0,
                "odds": "2/1",
                "betStatus": "placed"
            }
        ],
        "Count": 1,
        "ScannedCount": 1
    }
    return mock_table

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
        ]
    }
    return mock_events

@pytest.fixture
def step_functions_client():
    """Create a mock Step Functions client."""
    mock_step_functions = MagicMock()
    mock_step_functions.start_execution.return_value = {
        "executionArn": "arn:aws:states:us-east-1:123456789012:execution:TestStateMachine:test-execution",
        "startDate": "2025-04-01T15:00:00Z"
    }
    return mock_step_functions

@pytest.fixture
def gql_client():
    """Create a mock GraphQL client."""
    mock_gql_client = MagicMock()
    mock_gql_client.execute.return_value = {
        "lockBetsForEvent": {
            "__typename": "BetList",
            "items": [
                {
                    "userId": "user-1",
                    "betId": "bet-1",
                    "eventId": "event-1",
                    "outcome": "homeWin",
                    "amount": 10.0,
                    "odds": "2/1",
                    "betStatus": "placed"
                }
            ]
        },
        "getEvent": {
            "eventId": "event-1",
            "homeTeam": "Home Team",
            "awayTeam": "Away Team",
            "homeOdds": "2/1",
            "awayOdds": "3/1",
            "draw": "5/2",
            "outcome": "homeWin"
        },
        "deductFunds": {
            "__typename": "Wallet",
            "userId": "user-1",
            "balance": 90.0
        }
    }
    return mock_gql_client

@pytest.fixture
def processor():
    """Create a mock processor."""
    mock_processor = MagicMock()
    mock_processor.process.return_value = [
        ("success", {
            'Source': 'com.betting',
            'DetailType': 'SettlementStarted',
            'Detail': json.dumps({
                'eventId': 'test-event-id',
                'bets': [
                    {
                        'userId': 'user-1',
                        'betId': 'bet-1',
                        'eventId': 'test-event-id',
                        'outcome': 'homeWin',
                        'amount': 10.0,
                        'odds': '2/1',
                        'betStatus': 'placed'
                    }
                ]
            }),
            'EventBusName': 'test-event-bus'
        })
    ]
    mock_processor.response.return_value = {"processed": True}
    return mock_processor
