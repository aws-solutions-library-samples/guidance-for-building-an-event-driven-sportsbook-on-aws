import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock

# Add the lambda directory to the path so we can import the app
sys.path.append(os.path.join(os.path.dirname(__file__), '../../infrastructure/lambda/auth'))

# Import the app_mock module directly from the tests directory
from tests.auth.app_mock import lambda_handler, events, logger, tracer

class TestPostConfirmation:
    """Test suite for auth post confirmation function."""
    
    @pytest.fixture(autouse=True)
    def setup_auth_app(self, aws_credentials, events_client):
        """Setup the auth app with mocked AWS resources."""
        # Import the app module after setting up AWS credentials and mocks
        with patch.dict(os.environ, {
            'EVENT_BUS': 'test-event-bus'
        }):
            # Make the imports and mocks available to the test methods
            self.auth_app = MagicMock()
            self.auth_app.lambda_handler = lambda_handler
            self.auth_app.logger = logger
            self.auth_app.tracer = tracer
            
            # Use the provided clients
            self.mock_events = MagicMock()
            events.put_events = self.mock_events
            
            yield

    def test_lambda_handler_success(self):
        """Test successful lambda handler execution."""
        # Create a test event
        event = {
            'version': '1',
            'region': 'us-east-1',
            'userPoolId': 'us-east-1_example',
            'userName': 'test-user-id',
            'callerContext': {
                'awsSdkVersion': 'aws-sdk-js-2.6.4',
                'clientId': '1example23456789'
            },
            'triggerSource': 'PostConfirmation_ConfirmSignUp',
            'request': {
                'userAttributes': {
                    'sub': 'test-user-id',
                    'email_verified': 'true',
                    'cognito:user_status': 'CONFIRMED',
                    'email': 'test@example.com'
                }
            },
            'response': {}
        }
        
        # Create a mock context
        context = MagicMock()
        
        # Execute the function
        result = self.auth_app.lambda_handler(event, context)
        
        # Verify the result
        assert result == event
        
        # Verify the event was sent to EventBridge
        self.mock_events.assert_called_once()
        
        # Get the call arguments
        call_args = self.mock_events.call_args[1]
        entries = call_args['Entries']
        
        # Verify the event details
        assert len(entries) == 1
        assert entries[0]['Source'] == 'com.auth'
        assert entries[0]['DetailType'] == 'UserSignedUp'
        assert entries[0]['EventBusName'] == 'test-event-bus'
        
        # Verify the event detail
        detail = json.loads(entries[0]['Detail'])
        assert detail['userId'] == 'test-user-id'

    def test_lambda_handler_with_different_username(self):
        """Test lambda handler with a different username."""
        # Create a test event with a different username
        event = {
            'version': '1',
            'region': 'us-east-1',
            'userPoolId': 'us-east-1_example',
            'userName': 'another-user-id',
            'callerContext': {
                'awsSdkVersion': 'aws-sdk-js-2.6.4',
                'clientId': '1example23456789'
            },
            'triggerSource': 'PostConfirmation_ConfirmSignUp',
            'request': {
                'userAttributes': {
                    'sub': 'another-user-id',
                    'email_verified': 'true',
                    'cognito:user_status': 'CONFIRMED',
                    'email': 'another@example.com'
                }
            },
            'response': {}
        }
        
        # Create a mock context
        context = MagicMock()
        
        # Execute the function
        result = self.auth_app.lambda_handler(event, context)
        
        # Verify the result
        assert result == event
        
        # Verify the event was sent to EventBridge
        self.mock_events.assert_called_once()
        
        # Get the call arguments
        call_args = self.mock_events.call_args[1]
        entries = call_args['Entries']
        
        # Verify the event details
        assert len(entries) == 1
        assert entries[0]['Source'] == 'com.auth'
        assert entries[0]['DetailType'] == 'UserSignedUp'
        assert entries[0]['EventBusName'] == 'test-event-bus'
        
        # Verify the event detail
        detail = json.loads(entries[0]['Detail'])
        assert detail['userId'] == 'another-user-id'

    def test_lambda_handler_error_handling(self):
        """Test lambda handler error handling."""
        # Create a test event
        event = {
            'version': '1',
            'region': 'us-east-1',
            'userPoolId': 'us-east-1_example',
            'userName': 'test-user-id',
            'callerContext': {
                'awsSdkVersion': 'aws-sdk-js-2.6.4',
                'clientId': '1example23456789'
            },
            'triggerSource': 'PostConfirmation_ConfirmSignUp',
            'request': {
                'userAttributes': {
                    'sub': 'test-user-id',
                    'email_verified': 'true',
                    'cognito:user_status': 'CONFIRMED',
                    'email': 'test@example.com'
                }
            },
            'response': {}
        }
        
        # Create a mock context
        context = MagicMock()
        
        # Configure the mock to raise an exception
        self.mock_events.side_effect = Exception("Test exception")
        
        # Execute the function with exception handling
        with pytest.raises(Exception) as excinfo:
            self.auth_app.lambda_handler(event, context)
        
        # Verify the exception
        assert "Test exception" in str(excinfo.value)
