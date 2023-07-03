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
        return user_response(input)
    except KeyError:
        logger.info(f'Failed to get wallet for user {userId}')
        return wallet_error('NotFoundError', 'No wallet exists for user')
    except Exception as e:
        logger.info({'UnknownError': e})
        return wallet_error('Unknown error', 'An unknown error occured.')



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


@logger.inject_lambda_context(correlation_id_path=correlation_paths.APPSYNC_RESOLVER, log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
