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
    logger.debug(app.current_event)
    logger.debug(input)
    userId = get_user_id(app.current_event)

    try:
        #get user from cognito user pool
        
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
        eventresponse = send_event(user_response(input))
        logger.debug({'EventResponse:': eventresponse})
        return user_response(input)
    except Exception as e:
        logger.error({'UnknownError': e})
        return wallet_error('Unknown error', 'An unknown error occured.')
    
@app.resolver(type_name="Mutation", field_name="lockUserGenerateEvent")
@tracer.capture_method
def lock_user(input: dict) -> dict:
    logger.debug(app.current_event)
    logger.debug(input)
    userId = get_user_id(app.current_event)

    try:
        #get user from cognito user pool
        
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
        eventresponse = send_event(user_response(input))
        logger.debug({'EventResponse:': eventresponse})
        return user_response(input)
    except Exception as e:
        logger.error({'UnknownError': e})
        return wallet_error('Unknown error', 'An unknown error occured.')

def send_event(userResponse):
    data = form_event(userResponse)
    response = events.put_events(Entries=[data])
    return response

# IAM resolvers


def _try_get_user(userId: str):
    # Get Cognito user from user pool by id and return it
    cognitouserpool = cognito.UserPool(
        getenv('USER_POOL_ID'))
    
    cognitouser = cognitouserpool.get_user(
        Username=userId)
    
    return cognitouser


def get_user_id(event: AppSyncResolverEvent):
    return event.identity.sub


def wallet_error(errorType: str, error_msg: str) -> dict:
    return {'__typename': errorType, 'message': error_msg}


def user_response(data: dict) -> dict:
    return {**{'__typename': 'User'}, **data}

def form_event(userResponse):
    return {
        'Source': 'com.pam',
        'DetailType': 'userLocked',
        'Detail': json.dumps(userResponse),
        'EventBusName': event_bus_name
    }


@logger.inject_lambda_context(correlation_id_path=correlation_paths.APPSYNC_RESOLVER, log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    logger.info(event)
    return app.resolve(event, context)
