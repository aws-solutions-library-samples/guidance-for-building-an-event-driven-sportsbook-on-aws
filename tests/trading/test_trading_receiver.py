import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock

# Add the lambda directory to the path so we can import the app
sys.path.append(os.path.join(os.path.dirname(__file__), '../../infrastructure/lambda/trading/receiver'))

class TestTradingReceiver:
    """Test suite for trading receiver functions."""
    
    @pytest.fixture(autouse=True)
    def setup_trading_app(self, aws_credentials, events_client):
        """Setup the trading app with mocked AWS resources."""
        # Import the app module after setting up AWS credentials and mocks
        with patch.dict(os.environ, {
            'EVENT_BUS': 'test-event-bus'
        }):
            # Import modules inside the test to ensure mocks are applied first
            import app as trading_app
            
            # Patch the boto3 session and resources in the app module
            with patch.object(trading_app, 'session') as mock_session, \
                 patch.object(trading_app, 'events') as mock_events:  # Use a mock instead of events_client
                
                # Make the imports and mocks available to the test methods
                self.trading_app = trading_app
                self.mock_events = mock_events  # Store the mock for assertions
                yield

    def test_form_event(self):
        """Test the form_event function."""
        detail = {"eventId": "123", "homeOdds": "2/1", "awayOdds": "3/1", "drawOdds": "5/2"}
        result = self.trading_app.form_event('UpdatedOdds', detail)
        
        assert result['Source'] == 'com.trading'
        assert result['DetailType'] == 'UpdatedOdds'
        assert json.loads(result['Detail']) == detail
        assert result['EventBusName'] == 'test-event-bus'

    def test_handle_updated_odds(self):
        """Test the handle_updated_odds function."""
        item = {
            'source': 'com.thirdparty',
            'detail-type': 'UpdatedOdds',
            'detail': {
                'eventId': '123',
                'homeOdds': '2/1',
                'awayOdds': '3/1',
                'drawOdds': '5/2'
            }
        }
        
        result = self.trading_app.handle_updated_odds(item)
        
        assert result['Source'] == 'com.trading'
        assert result['DetailType'] == 'UpdatedOdds'
        assert json.loads(result['Detail']) == item['detail']
        assert result['EventBusName'] == 'test-event-bus'

    def test_record_handler_with_updated_odds(self):
        """Test the record_handler function with UpdatedOdds event."""
        # Create a mock SQSRecord
        mock_record = MagicMock()
        mock_record.body = json.dumps({
            'source': 'com.thirdparty',
            'detail-type': 'UpdatedOdds',
            'detail': {
                'eventId': '123',
                'homeOdds': '2/1',
                'awayOdds': '3/1',
                'drawOdds': '5/2'
            }
        })
        
        result = self.trading_app.record_handler(mock_record)
        
        assert result['Source'] == 'com.trading'
        assert result['DetailType'] == 'UpdatedOdds'
        assert 'eventId' in json.loads(result['Detail'])
        assert result['EventBusName'] == 'test-event-bus'

    def test_record_handler_with_unknown_event(self):
        """Test the record_handler function with unknown event."""
        # Create a mock SQSRecord
        mock_record = MagicMock()
        mock_record.body = json.dumps({
            'source': 'com.thirdparty',
            'detail-type': 'UnknownEvent',
            'detail': {
                'someData': 'value'
            }
        })
        
        # Patch the logger to avoid the debug call
        with patch.object(self.trading_app.logger, 'debug'):
            result = self.trading_app.record_handler(mock_record)
            assert result is None

    def test_record_handler_with_empty_payload(self):
        """Test the record_handler function with empty payload."""
        # Create a mock SQSRecord
        mock_record = MagicMock()
        mock_record.body = None
        
        # With the improved implementation, we expect the function to handle
        # the empty payload gracefully and return None
        result = self.trading_app.record_handler(mock_record)
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
                        'source': 'com.thirdparty',
                        'detail-type': 'UpdatedOdds',
                        'detail': {
                            'eventId': '123',
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
        
        # Create a mock Lambda context
        mock_context = MagicMock()
        mock_context.function_name = "test-function"
        mock_context.memory_limit_in_mb = 128
        mock_context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
        mock_context.aws_request_id = "test-request-id"
        
        # Mock the processor.process method to return a list of tuples
        with patch.object(self.trading_app.processor, 'process', return_value=[
            ('success', {
                'Source': 'com.trading',
                'DetailType': 'UpdatedOdds',
                'Detail': json.dumps({
                    'eventId': '123',
                    'homeOdds': '2/1',
                    'awayOdds': '3/1',
                    'drawOdds': '5/2'
                }),
                'EventBusName': 'test-event-bus'
            })
        ]), \
        patch.object(self.trading_app.processor, 'response', return_value={'batchItemFailures': []}), \
        patch.object(self.trading_app.logger, 'info'), \
        patch.object(self.trading_app.logger, 'debug'):
            
            result = self.trading_app.lambda_handler(event, mock_context)
            
            # Verify events.put_events was called
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
                        'source': 'com.thirdparty',
                        'detail-type': 'UnknownEvent',
                        'detail': {
                            'someData': 'value'
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
        with patch.object(self.trading_app.processor, 'process', return_value=[
            ('success', None)
        ]), \
        patch.object(self.trading_app.processor, 'response', return_value={'batchItemFailures': []}), \
        patch.object(self.trading_app.logger, 'info'), \
        patch.object(self.trading_app.logger, 'debug'):
            
            result = self.trading_app.lambda_handler(event, mock_context)
            
            # Verify events.put_events was not called
            self.mock_events.put_events.assert_not_called()
            assert result == {'batchItemFailures': []}
