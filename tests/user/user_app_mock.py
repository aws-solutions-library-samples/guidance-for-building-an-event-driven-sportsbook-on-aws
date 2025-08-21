"""
Mock implementation of the user app for testing.
"""
import json
from unittest.mock import MagicMock

# Mock objects
logger = MagicMock()
tracer = MagicMock()
app = MagicMock()
events = MagicMock()
session = MagicMock()
cognito = MagicMock()

# Mock decorator functions
def capture_lambda_handler(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def capture_method(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def inject_lambda_context(correlation_id_path=None, log_event=True):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

def resolver(type_name, field_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Mock the tracer object's methods
tracer.capture_lambda_handler = capture_lambda_handler
tracer.capture_method = capture_method

# Mock the logger object's methods
logger.inject_lambda_context = inject_lambda_context

# Mock the app object's methods
app.resolver = resolver
app.current_event = MagicMock()
app.current_event.identity = MagicMock()
app.current_event.identity.sub = "test-user-id"
app.resolve = MagicMock()

# Mock functions
def get_user_id(event):
    # For testing, we'll return the userId from the input instead of the identity
    if hasattr(event, 'arguments') and event.arguments.get('input', {}).get('userId'):
        return event.arguments['input']['userId']
    return event.identity.sub

def lock_user(input_data):
    try:
        userId = get_user_id(app.current_event)
        isLocked = input_data.get('isLocked', 'false')
        
        # Call Cognito to update user attributes
        cognito.admin_update_user_attributes(
            UserPoolId='test-user-pool-id',
            Username=userId,
            UserAttributes=[
                {
                    'Name': 'custom:isLocked',
                    'Value': isLocked
                }
            ]
        )
        
        # Create user response
        user_data = {
            'userId': userId,
            'isLocked': isLocked
        }
        
        response = user_response(user_data)
        
        # Send event
        send_event(response)
        
        return response
    except Exception as e:
        return wallet_error('Unknown error', str(e))

def form_event(user_data):
    return {
        'Source': 'com.pam',
        'DetailType': 'userLocked',
        'Detail': json.dumps(user_data),
        'EventBusName': 'test-event-bus'
    }

def send_event(user_data):
    event = form_event(user_data)
    response = events.put_events(Entries=[event])
    return response

def user_response(data):
    return {**{'__typename': 'User'}, **data}

def wallet_error(errorType, error_msg):
    return {'__typename': errorType, 'message': error_msg}

def lambda_handler(event, context):
    return app.resolve(event, context)
