from datetime import datetime
from decimal import Decimal
from os import getenv
import json
import boto3

from aws_lambda_powertools.utilities.data_classes import AppSyncResolverEvent
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import AppSyncResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

tracer = Tracer()
logger = Logger()
app = AppSyncResolver()

table_name = getenv('DB_TABLE')
session = boto3.Session()
cognito = boto3.client('cognito-idp')
event_bus_name = getenv('EVENT_BUS')
events = session.client('events')

# User pool resolvers
@app.resolver(type_name="Mutation", field_name="lockUser")
@tracer.capture_method
def lock_user(input: dict) -> dict:
    """
    Lock or unlock a user account.
    
    Updates the user's isLocked attribute in Cognito.
    
    Args:
        input: Contains isLocked flag to set user lock status
        
    Returns:
        dict: User response with updated lock status
        dict: Error response if operation fails
    """
    userId = get_user_id(app.current_event)

    try:
        cognito.admin_update_user_attributes(
            UserPoolId=getenv('USER_POOL_ID'),
            Username=userId,
            UserAttributes=[
                {
                    'Name': 'custom:isLocked',
                    'Value': input['isLocked']
                }
            ]
        )
        send_event(user_response(input))
        return user_response(input)
    except Exception as e:
        logger.error(f"Error locking user: {str(e)}")
        return wallet_error('Unknown error', 'An unknown error occurred.')
    
@app.resolver(type_name="Mutation", field_name="lockUserGenerateEvent")
@tracer.capture_method
def lock_user_generate_event(input: dict) -> dict:
    """
    Lock or unlock a user account and generate an event.
    
    Updates the user's isLocked attribute in Cognito and
    publishes an event to EventBridge.
    
    Args:
        input: Contains isLocked flag to set user lock status
        
    Returns:
        dict: User response with updated lock status
        dict: Error response if operation fails
    """
    userId = get_user_id(app.current_event)

    try:
        cognito.admin_update_user_attributes(
            UserPoolId=getenv('USER_POOL_ID'),
            Username=userId,
            UserAttributes=[
                {
                    'Name': 'custom:isLocked',
                    'Value': input['isLocked']
                }
            ]
        )
        send_event(user_response(input))
        return user_response(input)
    except Exception as e:
        logger.error(f"Error locking user with event generation: {str(e)}")
        return wallet_error('Unknown error', 'An unknown error occurred.')

def send_event(userResponse):
    """
    Send a user event to EventBridge.
    
    Args:
        userResponse: User data to include in the event
        
    Returns:
        dict: EventBridge put_events response or None if error occurs
    """
    try:
        data = form_event(userResponse)
        response = events.put_events(Entries=[data])
        return response
    except Exception as e:
        logger.error(f"Error sending event: {str(e)}")
        return None

def _try_get_user(userId: str):
    """
    Get a user from Cognito user pool.
    
    Args:
        userId: ID of the user to retrieve
        
    Returns:
        dict: Cognito user object
        
    Raises:
        Exception: If user retrieval fails
    """
    try:
        # Get Cognito user from user pool by id and return it
        cognitouserpool = cognito.UserPool(getenv('USER_POOL_ID'))
        cognitouser = cognitouserpool.get_user(Username=userId)
        return cognitouser
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        raise

def get_user_id(event: AppSyncResolverEvent):
    """
    Extract user ID from AppSync event.
    
    Args:
        event: AppSync resolver event
        
    Returns:
        str: User ID from the event identity
    """
    return event.identity.sub

def wallet_error(errorType: str, error_msg: str) -> dict:
    """
    Create an error response.
    
    Args:
        errorType: Type of error
        error_msg: Error message
        
    Returns:
        dict: Formatted error response
    """
    return {'__typename': errorType, 'message': error_msg}

def user_response(data: dict) -> dict:
    """
    Create a user response.
    
    Args:
        data: User data
        
    Returns:
        dict: Formatted user response
    """
    return {**{'__typename': 'User'}, **data}

def form_event(userResponse):
    """
    Create a properly formatted event for EventBridge.
    
    Args:
        userResponse: User data to include in the event
        
    Returns:
        dict: Formatted event ready for EventBridge
    """
    return {
        'Source': 'com.pam',
        'DetailType': 'userLocked',
        'Detail': json.dumps(userResponse),
        'EventBusName': event_bus_name
    }

@logger.inject_lambda_context(correlation_id_path=correlation_paths.APPSYNC_RESOLVER, log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """
    Main Lambda handler function.
    
    Args:
        event: Lambda event
        context: Lambda context
        
    Returns:
        dict: AppSync resolver response
    """
    return app.resolve(event, context)
