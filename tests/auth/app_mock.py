"""
Mock implementation of the auth post confirmation app for testing.
"""
import json
from unittest.mock import MagicMock

# Mock objects
logger = MagicMock()
tracer = MagicMock()
events = MagicMock()
session = MagicMock()
event_bus_name = "test-event-bus"

# Mock decorator functions
def capture_lambda_handler(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def inject_lambda_context(correlation_id_path=None, log_event=True):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Mock the tracer object's methods
tracer.capture_lambda_handler = capture_lambda_handler

# Mock the logger object's methods
logger.inject_lambda_context = inject_lambda_context

def lambda_handler(event, context):
    """
    Lambda handler function for post confirmation.
    
    Args:
        event: Lambda event
        context: Lambda context
        
    Returns:
        The original event
    """
    try:
        detail = {'userId': event['userName']}

        events.put_events(
            Entries=[
                {
                    'Source': 'com.auth',
                    'DetailType': 'UserSignedUp',
                    'Detail': json.dumps(detail),
                    'EventBusName': event_bus_name
                },
            ]
        )
        return event
    except Exception as e:
        logger.exception("Error in post confirmation handler")
        raise
