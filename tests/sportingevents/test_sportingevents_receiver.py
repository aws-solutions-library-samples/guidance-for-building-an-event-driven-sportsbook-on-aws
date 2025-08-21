import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the lambda directory to the path so we can import the app
sys.path.append(os.path.join(os.path.dirname(__file__), '../../infrastructure/lambda/sportingevents/receiver'))

class TestSportingEventsReceiver:
    """Test suite for sportingevents receiver functions."""
    
    @pytest.fixture(autouse=True)
    def setup_sportingevents_app(self, aws_credentials):
        """Setup the sportingevents app with mocked AWS resources."""
        # Import the app module after setting up AWS credentials and mocks
        with patch.dict(os.environ, {
            'EVENT_BUS': 'test-event-bus'
        }):
            # Import modules inside the test to ensure mocks are applied first
            import app as sportingevents_app
            
            # Patch the boto3 session and resources in the app module
            with patch.object(sportingevents_app, 'session') as mock_session, \
                 patch.object(sportingevents_app, 'eventsClient') as mock_events_client:
                
                # Configure the mock_events_client
                mock_events_client.put_events = MagicMock()
                
                # Make the imports and mocks available to the test methods
                self.sportingevents_app = sportingevents_app
                self.mock_events_client = mock_events_client
                yield

    def test_form_event(self):
        """Test the form_event function."""
        detail = {
            'eventId': 'test-event-id',
            'home': 'Home Team',
            'away': 'Away Team',
            'start': '2023-01-01T12:00:00Z',
            'end': '2023-01-01T14:00:00Z',
            'duration': '120',
            'homeOdds': '2/1',
            'awayOdds': '3/1',
            'drawOdds': '5/2',
            'eventStatus': 'SCHEDULED',
            'updatedAt': '2023-01-01T10:00:00Z'
        }
        
        result = self.sportingevents_app.form_event('EventAdded', detail)
        
        assert len(result) == 1
        assert result[0]['Source'] == 'com.thirdparty'
        assert result[0]['DetailType'] == 'EventAdded'
        assert json.loads(result[0]['Detail']) == detail
        assert result[0]['EventBusName'] == 'test-event-bus'

    def test_send_new_event(self):
        """Test the send_new_event function."""
        # Create a mock betting event
        current_timestamp = int(datetime.now().timestamp() * 1000)
        betting_event = {
            'eventId': 'test-event-id',
            'homeTeam': 'Home Team',
            'awayTeam': 'Away Team',
            'startTime': current_timestamp,
            'endTime': current_timestamp + 7200000,  # 2 hours later
            'duration': 120,
            'state': 'SCHEDULED',
            'homeOdds': '2/1',
            'awayOdds': '3/1',
            'drawOdds': '5/2',
            'updatedAt': current_timestamp - 3600000  # 1 hour before
        }
        
        # Call the function
        with patch.object(self.sportingevents_app.logger, 'debug'):
            self.sportingevents_app.send_new_event(betting_event, '%Y-%m-%dT%H:%M:%SZ')
        
        # Verify eventsClient.put_events was called
        self.mock_events_client.put_events.assert_called_once()
        
        # Get the call arguments
        call_args = self.mock_events_client.put_events.call_args[1]
        entries = call_args['Entries']
        
        # Verify the entries
        assert len(entries) == 1
        assert entries[0]['Source'] == 'com.thirdparty'
        assert entries[0]['DetailType'] == 'EventAdded'
        assert entries[0]['EventBusName'] == 'test-event-bus'
        
        # Parse the detail and verify its structure
        detail = json.loads(entries[0]['Detail'])
        assert detail['eventId'] == 'test-event-id'
        assert detail['home'] == 'Home Team'
        assert detail['away'] == 'Away Team'
        assert detail['duration'] == '120'
        assert detail['eventStatus'] == 'SCHEDULED'
        assert detail['homeOdds'] == '2/1'
        assert detail['awayOdds'] == '3/1'
        assert detail['drawOdds'] == '5/2'
        
    def test_send_new_event_missing_required_fields(self):
        """Test the send_new_event function with missing required fields."""
        # Create a mock betting event with missing fields
        current_timestamp = int(datetime.now().timestamp() * 1000)
        betting_event = {
            'eventId': 'test-event-id',
            'homeTeam': 'Home Team',
            'awayTeam': None,  # Missing away team
            'startTime': current_timestamp,
            'endTime': current_timestamp + 7200000,
            'duration': 120,
            'state': 'SCHEDULED',
            'homeOdds': '2/1',
            'awayOdds': '3/1',
            'drawOdds': '5/2',
            'updatedAt': current_timestamp - 3600000
        }
        
        # Call the function and expect an exception
        with pytest.raises(Exception):
            self.sportingevents_app.send_new_event(betting_event, '%Y-%m-%dT%H:%M:%SZ')
        
        # Verify eventsClient.put_events was not called
        self.mock_events_client.put_events.assert_not_called()
        
    def test_lambda_handler_success(self):
        """Test the lambda_handler function with successful event processing."""
        # Create a mock event
        current_timestamp = int(datetime.now().timestamp() * 1000)
        betting_events = [{
            'eventId': 'test-event-id',
            'homeTeam': 'Home Team',
            'awayTeam': 'Away Team',
            'startTime': current_timestamp,
            'endTime': current_timestamp + 7200000,
            'duration': 120,
            'state': 'SCHEDULED',
            'homeOdds': '2/1',
            'awayOdds': '3/1',
            'drawOdds': '5/2',
            'updatedAt': current_timestamp - 3600000
        }]
        
        event = {
            'body': json.dumps(betting_events)
        }
        
        # Mock the send_new_event function
        with patch.object(self.sportingevents_app, 'send_new_event') as mock_send_new_event, \
             patch.object(self.sportingevents_app.logger, 'info'):
            
            # Call the function
            result = self.sportingevents_app.lambda_handler(event, {})
            
            # Verify the result
            assert result['statusCode'] == 200
            assert result['body'] == 'Successfully inserted event!'
            
            # Verify send_new_event was called with the correct parameters
            mock_send_new_event.assert_called_once_with(betting_events[0], '%Y-%m-%dT%H:%M:%SZ')
            
    def test_lambda_handler_failure(self):
        """Test the lambda_handler function with failed event processing."""
        # Create a mock event
        current_timestamp = int(datetime.now().timestamp() * 1000)
        betting_events = [{
            'eventId': 'test-event-id',
            'homeTeam': 'Home Team',
            'awayTeam': 'Away Team',
            'startTime': current_timestamp,
            'endTime': current_timestamp + 7200000,
            'duration': 120,
            'state': 'SCHEDULED',
            'homeOdds': '2/1',
            'awayOdds': '3/1',
            'drawOdds': '5/2',
            'updatedAt': current_timestamp - 3600000
        }]
        
        event = {
            'body': json.dumps(betting_events)
        }
        
        # Mock the send_new_event function to raise an exception
        with patch.object(self.sportingevents_app, 'send_new_event', side_effect=Exception("Test error")), \
             patch.object(self.sportingevents_app.logger, 'info'):
            
            # Call the function
            result = self.sportingevents_app.lambda_handler(event, {})
            
            # Verify the result
            assert result['statusCode'] == 400
            assert result['body'] == 'Bad Request!'
