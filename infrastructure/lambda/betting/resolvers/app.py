import time
from datetime import datetime
from decimal import Decimal
from os import getenv
import json
import boto3
from gql_utils import get_client
from queries import get_event 
from mutations import deduct_funds
from gql import gql

from botocore.exceptions import ClientError

from aws_lambda_powertools.utilities.data_classes import AppSyncResolverEvent
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import AppSyncResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.data_classes.appsync import scalar_types_utils

OUTCOME_HOME_WIN = 'homeWin'
OUTCOME_AWAY_WIN = 'awayWin'
OUTCOME_DRAW = 'draw'

tracer = Tracer()
logger = Logger()
app = AppSyncResolver()

table_name = getenv('DB_TABLE')
appsync_url = getenv("APPSYNC_URL")
region = getenv("REGION")
session = boto3.Session()
dynamodb = session.resource('dynamodb')
table = dynamodb.Table(table_name)
gql_client = get_client(region, appsync_url)


@app.resolver(type_name="Query", field_name="getBets")
@tracer.capture_method
def get_bets(startKey: str = "") -> dict:
    userId = get_user_id(app.current_event)
    try:
        args = {}
        if startKey:
            args['ExclusiveStartKey'] = {'userId': userId, 'betId': startKey}
        args['KeyConditionExpression'] = 'userId = :u'
        args['ExpressionAttributeValues'] = {':u': userId}

        response = table.query(**args)
        result = {'items': response.get('Items', [])}
        if response.get('LastEvaluatedKey'):
            result['nextToken'] = response['LastEvaluatedKey']['betId']

        for item in result['items']:
            item['event'] = get_live_market_event(item['eventId'])

        return bet_list_response(result)
    except ClientError as e:
        logger.exception({'ClientError': e})
        return betting_error('UnknownError', 'An unknown error occured.')
    except Exception as e:
        logger.info({'UnknownError': e})
        return betting_error('Unknown error', 'An unknown error occured.')


@app.resolver(type_name="Mutation", field_name="createBets")
@tracer.capture_method
def create_bets(input: dict) -> dict:
    try:
        userId = get_user_id(app.current_event)
        processed_bets = []
        now = time.time()
        placement_time = scalar_types_utils.aws_datetime()
        total_stakes = 0.0
        
        for bet in input['bets']:
            event = get_live_market_event(bet['eventId'], now)

            # check the event matches the request state
            if not event_matches_bet(event, bet):
                raise ValueError('Event does not match bet')

            bet['betId'] = scalar_types_utils.make_id()
            bet['event'] = event
            bet['placedAt'] = placement_time
            bet['amount'] = Decimal(bet['amount'])
            bet['betStatus'] = 'placed'
            total_stakes += 10.0
            processed_bets.append(bet)

        # TODO - check market status (e.g., not Closed or Suspended)
        
        # TODO - call a handlePayments mutation to deduct the amounts from the wallet
        walletResponse = handle_funds(userId, amount = total_stakes)
        if 'InsufficientFundsError' in walletResponse['__typename']:
            return betting_error('InsufficientFundsError','The wallet does not have enough funds to cover the bet')
        elif 'Error' in walletResponse['__typename']:
            return betting_error('Error','There was a problem deducting funds when placing the bet')

        # TODO - In future we could do a fraud check here

        # write validated bets to the db
        with table.batch_writer() as batch:
            for bet in processed_bets:
                item = {
                    'userId': userId,
                    'betId': bet['betId'],
                    'eventId': bet['event']['eventId'],
                    'odds': bet['odds'],
                    'placedAt': bet['placedAt'],
                    'outcome': bet['outcome'],
                    'betStatus': bet['betStatus'],
                    'amount': bet['amount']
                }
                batch.put_item(Item=item)

        bet_list = {'items': processed_bets}
        return bet_list_response(bet_list)
    except ValueError as e:
        logger.exception({'ValueError': e})
        return betting_error('InputError', 'The requested bets could not be validated at this time.')
    except ClientError as e:
        logger.exception({'ClientError': e})
        return betting_error('UnknownError', 'An unknown error occured.')
    except Exception as e:
        logger.exception({'UnknownError': e})
        return betting_error('UnknownError', 'An unknown error occured.')

@app.resolver(type_name="Mutation", field_name="lockBetsForEvent")
@tracer.capture_method
def lock_bets_for_event(input: dict) -> dict:
    bets = get_bets_by_event_id(input['eventId'])
    #iterate through all bets and update the "status" field to "finalized"
    for bet in bets['items']:  
        bet['event'] = {'eventId': input['eventId']}
        table.update_item(
            Key={'userId': bet['userId'], 'betId': bet['betId']},
            UpdateExpression="set betStatus=:r",
            ExpressionAttributeValues={
                ':r': 'resulted'
            },
            ReturnValues="UPDATED_NEW")

    return bet_list_response(bets)


@tracer.capture_method
def get_bets_by_event_id(eventId: str = "") -> dict:
    try:
        args = {}
        
        args['KeyConditionExpression'] = 'eventId = :u'
        args['ExpressionAttributeValues'] = {':u': eventId}
        args['IndexName'] = 'eventId-userId-index'

        response = table.query(**args)
        result = {'items': response.get('Items', [])}
        if response.get('LastEvaluatedKey'):
            result['nextToken'] = response['LastEvaluatedKey']['betId']

        return bet_list_response(result)
    except ClientError as e:
        logger.exception({'ClientError': e})
        return betting_error('UnknownError', 'An unknown error occured.')
    except Exception as e:
        logger.info({'UnknownError': e})
        return betting_error('Unknown error', 'An unknown error occured.')


def event_matches_bet(event, bet):
    outcome = bet['outcome']

    if outcome == OUTCOME_HOME_WIN:
        event_odds = event['homeOdds']
    elif outcome == OUTCOME_AWAY_WIN:
        event_odds = event['awayOdds']
    elif outcome == OUTCOME_DRAW:
        event_odds = event['draw']
    else:
        raise ValueError(f'The specified outcome should be one of {OUTCOME_HOME_WIN}, {OUTCOME_AWAY_WIN}, {OUTCOME_DRAW}')

    if event_odds != bet['odds']:
        return False

    return True


def get_live_market_event(eventId: str, timestamp: float = None) -> dict:
    gql_input = {'eventId': eventId}

    if timestamp is not None:
        gql_input['timestamp'] = timestamp

    response = gql_client.execute(gql(get_event), variable_values=gql_input)[
        'getEvent']
    return response

def handle_funds(userId: str, amount: float) -> dict:
    gql_input = {'input':{'amount': amount, 'userId': userId}}
    response = gql_client.execute(gql(deduct_funds), variable_values=gql_input)[
        'deductFunds']
    return response


def betting_error(errorType: str, error_msg: str) -> dict:
    return {'__typename': errorType, 'message': error_msg}


def bet_list_response(data: dict) -> dict:
    return {**{'__typename': 'BetList'}, **data}


def get_user_id(event: AppSyncResolverEvent):
    return event.identity.sub


@logger.inject_lambda_context(correlation_id_path=correlation_paths.APPSYNC_RESOLVER, log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
