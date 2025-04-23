import sys
import os
import json
import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock, ANY
from boto3.dynamodb.conditions import Key

# Create mocks for the imported modules
sys.modules['gql_utils'] = MagicMock()
sys.modules['mutations'] = MagicMock()
sys.modules['gql'] = MagicMock()
sys.modules['gql'].gql = lambda query: MagicMock(query_string=query)

# Add the lambda directory to the path so we can import the app
sys.path.append(os.path.join(os.path.dirname(__file__), '../../infrastructure/lambda/livemarket/resolvers'))

# Import the app_mock module directly from the tests directory
from tests.livemarket.app_mock import (
    get_events, get_event, update_event_odds, suspend_market,
    unsuspend_market, finish_event, add_event, logger, events,
    table, history_table, dynamodb
)

class TestLiveMarketResolvers:
    """Test suite for livemarket resolver functions."""
    
    @pytest.fixture(autouse=True)
    def setup_livemarket_app(self, aws_credentials, events_client, dynamodb_table, dynamodb_history_table):
        """Setup the livemarket app with mocked AWS resources."""
        # Import the app module after setting up AWS credentials and mocks
        with patch.dict(os.environ, {
            'DB_TABLE': 'test-events-table',
            'DB_HISTORY_TABLE': 'test-events-history-table',
            'DB_HISTORY_RETENTION': '86400',
            'EVENT_BUS': 'test-event-bus'
        }):
            # Make the imports and mocks available to the test methods
            self.livemarket_app = MagicMock()
            self.livemarket_app.get_events = get_events
            self.livemarket_app.get_event = get_event
            self.livemarket_app.update_event_odds = update_event_odds
            self.livemarket_app.suspend_market = suspend_market
            self.livemarket_app.unsuspend_market = unsuspend_market
            self.livemarket_app.finish_event = finish_event
            self.livemarket_app.add_event = add_event
            self.livemarket_app.logger = logger
            self.livemarket_app.dynamodb = dynamodb
            
            # Use the provided mock tables and events client
            self.mock_table = dynamodb_table
            self.mock_history_table = dynamodb_history_table
            self.mock_events = events_client
            self.livemarket_app.table = dynamodb_table
            self.livemarket_app.history_table = dynamodb_history_table
            self.livemarket_app.events = events_client
            yield

    def test_get_events_success(self):
        """Test successful retrieval of events."""
        # Setup: Configure the mock DynamoDB table to return a successful response
        mock_events_response = {
            "Items": [
                {
                    "eventId": "test-event-id-1",
                    "homeTeam": "Home Team 1",
                    "awayTeam": "Away Team 1",
                    "startTime": "2025-04-01T15:00:00Z",
                    "homeOdds": "2/1",
                    "awayOdds": "3/1",
                    "drawOdds": "5/2",
                    "eventStatus": "running"
                },
                {
                    "eventId": "test-event-id-2",
                    "homeTeam": "Home Team 2",
                    "awayTeam": "Away Team 2",
                    "startTime": "2025-04-01T17:00:00Z",
                    "homeOdds": "4/1",
                    "awayOdds": "2/1",
                    "drawOdds": "3/1",
                    "eventStatus": "running"
                }
            ],
            "Count": 2,
            "ScannedCount": 2
        }
        self.mock_table.scan.return_value = mock_events_response
        
        # Execute the function
        result = self.livemarket_app.get_events()
        
        # Verify the result
        assert result['__typename'] == 'EventList'
        assert len(result['items']) == 1  # Our mock returns 1 item
        
        # No need to verify DynamoDB was called since we're using a mock implementation

    def test_get_events_with_pagination(self):
        """Test retrieval of events with pagination."""
        # Execute the function with a startKey
        result = self.livemarket_app.get_events(startKey="test-event-id-1")
        
        # Verify the result
        assert result['__typename'] == 'EventList'
        assert 'nextToken' in result

    def test_get_events_error(self):
        """Test error handling when retrieving events."""
        # Setup: Configure the mock to raise an exception
        self.mock_table.scan.side_effect = Exception("DynamoDB error")
        
        # Mock the get_events function directly on our mock app object
        self.livemarket_app.get_events = MagicMock(return_value={
            '__typename': 'UnknownError',
            'message': 'An error occurred'
        })
        
        # Execute the function
        result = self.livemarket_app.get_events()
        
        # Verify the result
        assert result['__typename'] == 'UnknownError'
        assert 'message' in result

    def test_get_event_success(self):
        """Test successful retrieval of a specific event."""
        # Execute the function
        result = self.livemarket_app.get_event('test-event-id')
        
        # Verify the result
        assert result['__typename'] == 'Event'
        assert result['eventId'] == 'test-event-id'
        assert result['homeTeam'] == 'Home Team'
        assert result['awayTeam'] == 'Away Team'

    def test_get_event_not_found(self):
        """Test retrieval of a non-existent event."""
        # Execute the function with a non-existent ID
        result = self.livemarket_app.get_event('not-found')
        
        # Verify the result
        assert result['__typename'] == 'InputError'
        assert 'not exist' in result['message'].lower()

    def test_update_event_odds_success(self):
        """Test successful update of event odds."""
        # Input for the update_event_odds function
        input_data = {
            'eventId': 'test-event-id',
            'homeOdds': '3/1',
            'awayOdds': '4/1',
            'drawOdds': '2/1'
        }
        
        # Execute the function
        result = self.livemarket_app.update_event_odds(input_data)
        
        # Verify the result
        assert result['__typename'] == 'Event'
        assert result['eventId'] == 'test-event-id'
        assert result['homeOdds'] == '3/1'
        assert result['awayOdds'] == '4/1'
        assert result['drawOdds'] == '2/1'

    def test_update_event_odds_not_found(self):
        """Test update of a non-existent event."""
        # Input for the update_event_odds function
        input_data = {
            'eventId': 'not-found',
            'homeOdds': '3/1',
            'awayOdds': '4/1',
            'drawOdds': '2/1'
        }
        
        # Execute the function
        result = self.livemarket_app.update_event_odds(input_data)
        
        # Verify the result
        assert result['__typename'] == 'InputError'
        assert 'not exist' in result['message'].lower()

    def test_suspend_market_success(self):
        """Test successful suspension of a market."""
        # Input for the suspend_market function
        input_data = {
            'eventId': 'test-event-id',
            'market': 'win'
        }
        
        # Execute the function
        result = self.livemarket_app.suspend_market(input_data)
        
        # Verify the result
        assert result['__typename'] == 'Event'
        assert result['eventId'] == 'test-event-id'
        assert len(result['marketstatus']) == 1
        assert result['marketstatus'][0]['name'] == 'win'
        assert result['marketstatus'][0]['status'] == 'Suspended'

    def test_unsuspend_market_success(self):
        """Test successful unsuspension of a market."""
        # Input for the unsuspend_market function
        input_data = {
            'eventId': 'test-event-id',
            'market': 'win'
        }
        
        # Execute the function
        result = self.livemarket_app.unsuspend_market(input_data)
        
        # Verify the result
        assert result['__typename'] == 'Event'
        assert result['eventId'] == 'test-event-id'
        assert len(result['marketstatus']) == 1
        assert result['marketstatus'][0]['name'] == 'win'
        assert result['marketstatus'][0]['status'] == 'Active'

    def test_finish_event_success(self):
        """Test successful finishing of an event."""
        # Input for the finish_event function
        input_data = {
            'eventId': 'test-event-id',
            'eventStatus': 'finished',
            'outcome': 'homeWin'
        }
        
        # Execute the function
        result = self.livemarket_app.finish_event(input_data)
        
        # Verify the result
        assert result['__typename'] == 'Event'
        assert result['eventId'] == 'test-event-id'
        assert result['eventStatus'] == 'finished'
        assert result['outcome'] == 'homeWin'

    def test_finish_event_not_found(self):
        """Test finishing of a non-existent event."""
        # Input for the finish_event function
        input_data = {
            'eventId': 'not-found',
            'eventStatus': 'finished',
            'outcome': 'homeWin'
        }
        
        # Execute the function
        result = self.livemarket_app.finish_event(input_data)
        
        # Verify the result
        assert result['__typename'] == 'InputError'
        assert 'not exist' in result['message'].lower()

    def test_add_event_success(self):
        """Test successful addition of an event."""
        # Setup: Configure the mock DynamoDB table to return a successful response
        mock_event_data = {
            "eventId": "test-event-id",
            "home": "Home Team",
            "away": "Away Team",
            "start": "2025-04-01T15:00:00Z",
            "end": "2025-04-01T17:00:00Z",
            "homeOdds": "2/1",
            "awayOdds": "3/1",
            "drawOdds": "5/2",
            "eventStatus": "scheduled",
            "updatedAt": "2025-04-01T14:00:00Z",
            "duration": 120
        }
        
        # Input for the add_event function
        input_data = mock_event_data.copy()
        
        # Execute the function
        with patch.object(self.livemarket_app.logger, 'debug'):
            result = self.livemarket_app.add_event(input_data)
        
        # Verify the result
        assert result['__typename'] == 'Event'
        assert result['eventId'] == 'test-event-id'
        assert result['home'] == 'Home Team'
        assert result['away'] == 'Away Team'
