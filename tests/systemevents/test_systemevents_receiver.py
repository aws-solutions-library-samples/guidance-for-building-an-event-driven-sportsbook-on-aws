import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock

# Add the lambda directory to the path so we can import the app
sys.path.append(os.path.join(os.path.dirname(__file__), '../../infrastructure/lambda/systemevents/receiver'))
# Add the gql directory to the path to find gql_utils
sys.path.append(os.path.join(os.path.dirname(__file__), '../../infrastructure/lambda/gql'))

# Create a fixture for aws_credentials
@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for boto3."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

class TestSystemEventsReceiver:
    """Test suite for systemevents receiver functions."""
    
    @pytest.fixture(autouse=True)
    def setup_systemevents_app(self, aws_credentials):
        """Setup the systemevents app with mocked AWS resources."""
        # Mock the modules before importing app
        with patch.dict('sys.modules', {
            'gql_utils': MagicMock(),
            'gql': MagicMock(),
        }):
            # Set up environment variables
            with patch.dict(os.environ, {
                'EVENT_BUS': 'test-event-bus',
                'REGION': 'us-east-1',
                'APPSYNC_URL': 'https://test-appsync-url.amazonaws.com/graphql'
            }):
                # Import the app module
                import app as systemevents_app
                
                # Mock the boto3 session and resources
                with patch.object(systemevents_app, 'session') as mock_session, \
                     patch.object(systemevents_app, 'events') as mock_events, \
                     patch.object(systemevents_app, 'get_client') as mock_get_client, \
                     patch.object(systemevents_app, 'gql') as mock_gql:
                    
                    # Configure the mock_events
                    mock_events.put_events = MagicMock()
                    
                    # Configure the mock_gql
                    mock_gql.return_value = "mocked_gql_query"
                    
                    # Configure the mock_get_client
                    mock_gql_client = MagicMock()
                    mock_get_client.return_value = mock_gql_client
                    
                    # Make the imports and mocks available to the test methods
                    self.systemevents_app = systemevents_app
                    self.mock_events = mock_events
                    self.mock_gql_client = mock_gql_client
                    self.mock_gql = mock_gql
                    yield

    def test_handle_system_event(self):
        """Test the handle_system_event function."""
        # Create a mock event
        item = {
            'source': 'com.test',
            'detail-type': 'TestEvent',
            'detail': {
                'testData': 'value'
            }
        }
        
        # Set up the mock response
        mock_response = {
            'source': 'com.test',
            'detailType': 'TestEvent',
            'detail': {
                'testData': 'value',
                'systemEventId': '12345678-1234-1234-1234-123456789012'
            }
        }
        
        # Configure the mock to return the expected response
        self.mock_gql_client.execute.return_value = {'addSystemEvent': mock_response}
        
        # Mock uuid.uuid4
        with patch('uuid.uuid4', return_value='12345678-1234-1234-1234-123456789012'):
            # Call the function under test
            with patch.object(self.systemevents_app, 'gql_client', self.mock_gql_client):
                result = self.systemevents_app.handle_system_event(item)
            
            # Verify the result
            assert result['Source'] == 'com.test'
            assert result['DetailType'] == 'TestEvent'
            assert result['Detail']['testData'] == 'value'
            assert result['Detail']['systemEventId'] == '12345678-1234-1234-1234-123456789012'
            assert result['EventBusName'] == 'test-event-bus'
        
    def test_handle_system_event_error(self):
        """Test the handle_system_event function with an error."""
        # Create a mock event
        item = {
            'source': 'com.test',
            'detail-type': 'TestEvent',
            'detail': {
                'testData': 'value'
            }
        }
        
        # Configure the mock to raise an exception
        self.mock_gql_client.execute.side_effect = Exception("GraphQL error")
        
        # Call the function and expect None as return value
        with patch.object(self.systemevents_app, 'gql_client', self.mock_gql_client):
            result = self.systemevents_app.handle_system_event(item)
            assert result is None
        
    def test_record_handler(self):
        """Test the record_handler function."""
        # Create a mock SQSRecord
        mock_record = MagicMock()
        mock_record.body = json.dumps({
            'source': 'com.test',
            'detail-type': 'TestEvent',
            'detail': {
                'testData': 'value'
            }
        })
        
        # Mock the handle_system_event function
        with patch.object(self.systemevents_app, 'handle_system_event') as mock_handle_system_event:
            mock_handle_system_event.return_value = {
                'Source': 'com.test',
                'DetailType': 'TestEvent',
                'Detail': {
                    'testData': 'value',
                    'systemEventId': '12345678-1234-1234-1234-123456789012'
                },
                'EventBusName': 'test-event-bus'
            }
            
            # Call the function
            result = self.systemevents_app.record_handler(mock_record)
            
            # Verify the result
            assert result['Source'] == 'com.test'
            assert result['DetailType'] == 'TestEvent'
            assert result['Detail']['testData'] == 'value'
            assert result['Detail']['systemEventId'] == '12345678-1234-1234-1234-123456789012'
            assert result['EventBusName'] == 'test-event-bus'
            
            # Verify handle_system_event was called with the correct parameters
            mock_handle_system_event.assert_called_once_with({
                'source': 'com.test',
                'detail-type': 'TestEvent',
                'detail': {
                    'testData': 'value'
                }
            })
    
    def test_record_handler_empty_payload(self):
        """Test the record_handler function with empty payload."""
        # Create a mock SQSRecord
        mock_record = MagicMock()
        mock_record.body = None
        
        # With the improved implementation, we expect the function to handle
        # the empty payload gracefully and return None
        result = self.systemevents_app.record_handler(mock_record)
        assert result is None
    
    def test_lambda_handler(self):
        """Test the lambda_handler function."""
        # Create a mock event with SQS records
        event = {
            "Records": [
                {
                    "messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
                    "receiptHandle": "MessageReceiptHandle",
                    "body": json.dumps({
                        'source': 'com.test',
                        'detail-type': 'TestEvent',
                        'detail': {
                            'testData': 'value'
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
        
        # Create a mock Lambda context
        mock_context = MagicMock()
        mock_context.function_name = "test-function"
        mock_context.memory_limit_in_mb = 128
        mock_context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
        mock_context.aws_request_id = "test-request-id"
        
        # Mock the processor.process method to return a list of tuples
        with patch.object(self.systemevents_app.processor, 'process', return_value=[
            ('success', {
                'Source': 'com.test',
                'DetailType': 'TestEvent',
                'Detail': {
                    'testData': 'value',
                    'systemEventId': '12345678-1234-1234-1234-123456789012'
                },
                'EventBusName': 'test-event-bus'
            })
        ]), \
        patch.object(self.systemevents_app.processor, 'response', return_value={'batchItemFailures': []}), \
        patch.object(self.systemevents_app.logger, 'info'), \
        patch.object(self.systemevents_app.logger, 'debug'):
            
            # Call the function
            result = self.systemevents_app.lambda_handler(event, mock_context)
            
            # Verify events.put_events was called with the correct parameters
            self.mock_events.put_events.assert_called_once()
            assert result == {'batchItemFailures': []}
    
    def test_lambda_handler_no_output_events(self):
        """Test the lambda_handler function with no output events."""
        # Create a mock event with SQS records
        event = {
            "Records": [
                {
                    "messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
                    "receiptHandle": "MessageReceiptHandle",
                    "body": json.dumps({
                        'source': 'com.test',
                        'detail-type': 'TestEvent',
                        'detail': {
                            'testData': 'value'
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
        
        # Create a mock Lambda context
        mock_context = MagicMock()
        mock_context.function_name = "test-function"
        mock_context.memory_limit_in_mb = 128
        mock_context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
        mock_context.aws_request_id = "test-request-id"
        
        # Mock the processor.process method to return a list of tuples with None
        with patch.object(self.systemevents_app.processor, 'process', return_value=[
            ('success', None)
        ]), \
        patch.object(self.systemevents_app.processor, 'response', return_value={'batchItemFailures': []}), \
        patch.object(self.systemevents_app.logger, 'info'), \
        patch.object(self.systemevents_app.logger, 'debug'):
            
            # Call the function
            result = self.systemevents_app.lambda_handler(event, mock_context)
            
            # Verify events.put_events was not called
            self.mock_events.put_events.assert_not_called()
            assert result == {'batchItemFailures': []}
