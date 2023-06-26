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
dynamodb = session.resource('dynamodb')
table = dynamodb.Table(table_name)

# User pool resolvers


@app.resolver(type_name="Query", field_name="getWallet")
@tracer.capture_method
def get_wallet() -> dict:
    userId = get_user_id(app.current_event)
    logger.debug(app.current_event)
    try:
        item = _try_get_wallet(userId)
        return wallet_response(item)
    except KeyError:
        logger.info(f'Failed to get wallet for user {userId}')
        return wallet_error('NotFoundError', 'No wallet exists for user')
    except Exception as e:
        logger.info({'UnknownError': e})
        return wallet_error('Unknown error', 'An unknown error occured.')


@app.resolver(type_name="Mutation", field_name="withdrawFunds")
@tracer.capture_method
def withdraw_funds(input: dict) -> dict:
    logger.debug(app.current_event)
    logger.debug(input)
    userId = get_user_id(app.current_event)

    try:
        item = _try_get_wallet(userId)
        withdrawAmount = Decimal(input['amount'])
        logger.info(f'withdraw amount: {withdrawAmount}, wallet balance: {item["balance"]}')
        if ((item['balance'] - withdrawAmount) >= 0):
            item['balance'] -= withdrawAmount
        else:
            logger.info(f'Insufficient funds for withdrawal request')
            return wallet_error('InsufficientFunds', 'Wallet contains insufficuient funds to withdraw') 

        table.update_item(
            Key={'userId': userId},
            UpdateExpression="set balance=:r",
            ExpressionAttributeValues={
                ':r': item['balance']
            },
            ReturnValues="UPDATED_NEW")

        return wallet_response(item)
    except KeyError:
        logger.info(f'Failed to get wallet for user {userId}')
        return wallet_error('NotFoundError', 'No wallet exists for user')
    except Exception as e:
        logger.info({'UnknownError': e})
        return wallet_error('Unknown error', 'An unknown error occured.')


@app.resolver(type_name="Mutation", field_name="depositFunds")
@tracer.capture_method
def deposit_funds(input: dict) -> dict:
    logger.debug(app.current_event)
    logger.debug(input)
    userId = get_user_id(app.current_event)

    try:
        item = _try_get_wallet(userId)
        item['balance'] += Decimal(input['amount'])

        table.update_item(
            Key={'userId': userId},
            UpdateExpression="set balance=:r",
            ExpressionAttributeValues={
                ':r': item['balance']
            },
            ReturnValues="UPDATED_NEW")

        return wallet_response(item)
    except KeyError:
        logger.info(f'Failed to get wallet for user {userId}')
        return wallet_error('NotFoundError', 'No wallet exists for user')
    except Exception as e:
        logger.info({'UnknownError': e})
        return wallet_error('Unknown error', 'An unknown error occured.')


# IAM resolvers


@app.resolver(type_name="Query", field_name="getWalletByUserId")
@tracer.capture_method
def get_wallet_by_user_id(userId: str) -> dict:
    if not userId:
        return wallet_error('InputError', 'You must provide a valid userId')

    try:
        item = _try_get_wallet(userId)
        return wallet_response(item)
    except KeyError:
        logger.info(f'Failed to get wallet for user {userId}')
        return wallet_error('NotFoundError', 'No wallet exists for user')
    except Exception as e:
        logger.info({'UnknownError': e})
        return wallet_error('UnknownError', 'An unknown error occured.')


@app.resolver(type_name="Mutation", field_name="createWallet")
@tracer.capture_method
def create_wallet(input: dict) -> dict:
    logger.debug(app.current_event)
    logger.debug(input)
    item = {
        'userId': input['userId'],
        'balance': Decimal(0),
    }
    table.put_item(Item=item)
    return wallet_response(item)


def _try_get_wallet(userId: str):
    return table.get_item(
        Key={"userId": userId}
    )["Item"]


def get_user_id(event: AppSyncResolverEvent):
    return event.identity.sub


def wallet_error(errorType: str, error_msg: str) -> dict:
    return {'__typename': errorType, 'message': error_msg}


def wallet_response(data: dict) -> dict:
    return {**{'__typename': 'Wallet'}, **data}


@logger.inject_lambda_context(correlation_id_path=correlation_paths.APPSYNC_RESOLVER, log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
