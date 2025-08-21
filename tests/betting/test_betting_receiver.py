import sys
import os
import json
import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock, ANY

# Create mocks for the imported modules
sys.modules['gql_utils'] = MagicMock()
sys.modules['mutations'] = MagicMock()
sys.modules['gql'] = MagicMock()
sys.modules['gql'].gql = lambda query: MagicMock(query_string=query)

# Add the lambda directory to the path so we can import the app
sys.path.append(os.path.join(os.path.dirname(__file__), '../../infrastructure/lambda/betting/receiver'))

# Import the app_mock module directly from the tests directory
from tests.betting.app_mock import (
    form_event, bet_list_response, betting_error, handle_event_closed,
    record_handler, logger, events, step_function
)

class TestBettingReceiver:
    """Test suite for betting receiver functions."""
    
    @pytest.fixture(autouse=True)
    def setup_betting_receiver(self, aws_credentials, events_client, dynamodb_table, gql_client, step_functions_client):
        """Setup the betting receiver with mocked AWS resources."""
        # Set environment variables
        with patch.dict(os.environ, {
            'DB_TABLE': 'test-bets-table',
            'EVENT_BUS': 'test-event-bus',
            'APPSYNC_URL': 'https://test-appsync-url.amazonaws.com/graphql',
            'REGION': 'us-east-1',
            'STEP_FUNCTION_ARN': 'arn:aws:states:us-east-1:123456789012:stateMachine:TestStateMachine'
        }):
            # Make the imports and mocks available to the test methods
            self.betting_receiver = MagicMock()
            self.betting_receiver.form_event = form_event
            self.betting_receiver.bet_list_response = bet_list_response
            self.betting_receiver.betting_error = betting_error
            self.betting_receiver.handle_event_closed = handle_event_closed
            self.betting_receiver.record_handler = record_handler
            self.betting_receiver.logger = logger
            
            # Use the provided clients
            self.mock_events = events_client
            self.betting_receiver.events = events_client
            self.mock_step_function = step_functions_client
            self.betting_receiver.step_function = step_functions_client
            self.mock_gql_client = gql_client
            self.betting_receiver.gql_client = gql_client
            
            yield

    def test_form_event(self):
        """Test forming an event for EventBridge."""
        # Create test data
        source = "test-source"
        detail_type = "test-detail-type"
        detail = {"key": "value"}
        
        # Call the function
        result = self.betting_receiver.form_event(source, detail_type, detail)
        
        # Verify the result
        assert result["Source"] == source
        assert result["DetailType"] == detail_type
        assert "Detail" in result
        assert json.loads(result["Detail"]) == detail
        assert "EventBusName" in result

    def test_bet_list_response(self):
        """Test creating a bet list response."""
        # Create test data
        test_data = {
            "items": [
                {"betId": "bet1", "amount": 10.0},
                {"betId": "bet2", "amount": 20.0}
            ]
        }
        
        # Call the function
        result = self.betting_receiver.bet_list_response(test_data)
        
        # Verify the result
        assert result == {
            "__typename": "BetList",
            "items": [
                {"betId": "bet1", "amount": 10.0},
                {"betId": "bet2", "amount": 20.0}
            ]
        }

    def test_betting_error(self):
        """Test creating a betting error response."""
        # Call the function
        result = self.betting_receiver.betting_error("TestError", "This is a test error")
        
        # Verify the result
        assert result == {
            "__typename": "TestError",
            "message": "This is a test error"
        }

    def test_handle_event_closed(self):
        """Test handling an event closed event."""
        # Create a mock event
        event = {
            'detail-type': 'EventClosed',
            'detail': {
                'eventId': 'test-event-id'
            }
        }
        
        # Call the function
        result = self.betting_receiver.handle_event_closed(event)
        
        # Verify the result
        assert result["Source"] == "com.betting"
        assert result["DetailType"] == "SettlementStarted"
        assert "Detail" in result
        detail = json.loads(result["Detail"])
        assert detail["eventId"] == "test-event-id"
        assert len(detail["bets"]) > 0

    def test_record_handler_event_closed(self):
        """Test record handler with an event closed event."""
        # Create a mock SQS record
        record = MagicMock()
        record.body = json.dumps({
            'source': 'com.livemarket',
            'detail-type': 'EventClosed',
            'detail': {
                'eventId': 'test-event-id'
            }
        })
        
        # Call the function
        result = self.betting_receiver.record_handler(record)
        
        # Verify the result
        assert result["Source"] == "com.betting"
        assert result["DetailType"] == "SettlementStarted"
        assert "Detail" in result
        detail = json.loads(result["Detail"])
        assert detail["eventId"] == "test-event-id"
        assert len(detail["bets"]) > 0

    def test_record_handler_unknown_record(self):
        """Test record handler with an unknown record type."""
        # Create a mock SQS record
        record = MagicMock()
        record.body = json.dumps({
            'source': 'unknown',
            'detail-type': 'Unknown',
            'detail': {}
        })
        
        # Call the function
        result = self.betting_receiver.record_handler(record)
        
        # Verify the result
        assert result is None
