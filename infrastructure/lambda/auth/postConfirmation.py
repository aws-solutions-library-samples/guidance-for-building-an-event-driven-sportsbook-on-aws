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

session = boto3.Session()
events = session.client('events')
event_bus_name = getenv('EVENT_BUS')

@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """
    Lambda handler for Cognito post confirmation.
    
    This function is triggered after a user confirms their registration.
    It sends a UserSignedUp event to EventBridge.
    
    Args:
        event: Cognito post confirmation event
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
    except KeyError as e:
        logger.error(f"Missing required field in event: {str(e)}")
        raise
    except Exception as e:
        logger.exception(f"Error in post confirmation handler: {str(e)}")
        raise
