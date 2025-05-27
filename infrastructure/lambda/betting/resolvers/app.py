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
event_bus_name = getenv('EVENT_BUS')
events = session.client('events')


@app.resolver(type_name="Query", field_name="getBets")
@tracer.capture_method
def get_bets(startKey: str = "") -> dict:
    """
    Get bets for the current user.
    
    Args:
        startKey: Optional pagination token
        
    Returns:
        A BetList response containing the user's bets
    """
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
        logger.exception("ClientError when getting bets")
        return betting_error('UnknownError', 'An unknown error occurred.')
    except Exception as e:
        logger.exception("Unknown error when getting bets")
        return betting_error('UnknownError', 'An unknown error occurred.')


@app.resolver(type_name="Mutation", field_name="createBets")
@tracer.capture_method
def create_bets(input: dict) -> dict:
    """
    Create new bets for the current user.
    
    Args:
        input: Dictionary containing bet information
        
    Returns:
        A BetList response containing the created bets or an error
    """
    try:
        userId = get_user_id(app.current_event)
        processed_bets = []
        now = time.time()
        placement_time = scalar_types_utils.aws_datetime()
        total_stakes = 0.0
        
        for bet in input['bets']:
            event = get_live_market_event(bet['eventId'], now)

            # Check the event matches the request state
            if not event_matches_bet(event, bet):
                raise ValueError('Event does not match bet')

            bet['betId'] = scalar_types_utils.make_id()
            bet['event'] = event
            bet['placedAt'] = placement_time
            bet['amount'] = Decimal(bet['amount'])
            bet['betStatus'] = 'placed'
            total_stakes += float(bet['amount'])
            
            processed_bets.append(bet)
        
        # Deduct funds from wallet
        walletResponse = handle_funds(userId, amount=total_stakes)
        if 'InsufficientFundsError' in walletResponse['__typename']:
            return betting_error('InsufficientFundsError', 'The wallet does not have enough funds to cover the bet')
        elif 'Error' in walletResponse['__typename']:
            return betting_error('Error', 'There was a problem deducting funds when placing the bet')

        # Write validated bets to the db
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
        send_event(bet_list)
        return bet_list_response(bet_list)
    except ValueError as e:
        logger.exception("Validation error when creating bets")
        return betting_error('InputError', 'The requested bets could not be validated at this time.')
    except ClientError as e:
        logger.exception("ClientError when creating bets")
        return betting_error('UnknownError', 'An unknown error occurred.')
    except Exception as e:
        logger.exception("Unknown error when creating bets")
        return betting_error('UnknownError', 'An unknown error occurred.')


@app.resolver(type_name="Mutation", field_name="lockBetsForEvent")
@tracer.capture_method
def lock_bets_for_event(input: dict) -> dict:
    """
    Lock all bets for a specific event.
    
    Args:
        input: Dictionary containing eventId
        
    Returns:
        A BetList response containing the locked bets
    """
    try:
        bets = get_open_bets_by_event_id(input['eventId'])
        
        # Update all bets to "resulted" status
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
    except Exception as e:
        logger.exception("Error locking bets for event")
        return betting_error('UnknownError', 'An unknown error occurred.')


@tracer.capture_method
def get_open_bets_by_event_id(eventId: str = "") -> dict:
    """
    Get all open bets for a specific event.
    
    Args:
        eventId: The event ID to query
        
    Returns:
        A dictionary containing the open bets
    """
    try:
        args = {
            'KeyConditionExpression': 'eventId = :u AND betStatus = :s',
            'ExpressionAttributeValues': {':u': eventId, ':s': 'placed'},
            'IndexName': 'eventId-betStatus-index'
        }

        response = table.query(**args)
        result = {'items': response.get('Items', [])}
        if response.get('LastEvaluatedKey'):
            result['nextToken'] = response['LastEvaluatedKey']['betId']

        return bet_list_response(result)
    except ClientError as e:
        logger.exception("ClientError when getting open bets")
        return betting_error('UnknownError', 'An unknown error occurred.')
    except Exception as e:
        logger.exception("Unknown error when getting open bets")
        return betting_error('UnknownError', 'An unknown error occurred.')


def event_matches_bet(event, bet):
    """
    Check if an event matches a bet's odds.
    
    Args:
        event: Event data
        bet: Bet data
        
    Returns:
        True if the event matches the bet, False otherwise
    """
    try:
        outcome = bet['outcome']

        if outcome == OUTCOME_HOME_WIN:
            event_odds = event['homeOdds']
        elif outcome == OUTCOME_AWAY_WIN:
            event_odds = event['awayOdds']
        elif outcome == OUTCOME_DRAW:
            event_odds = event['drawOdds']
        else:
            raise ValueError(f'The specified outcome should be one of {OUTCOME_HOME_WIN}, {OUTCOME_AWAY_WIN}, {OUTCOME_DRAW}')

        # Convert both odds to Decimal before comparing
        return Decimal(event_odds) == Decimal(bet['odds'])
    except Exception as e:
        logger.exception("Error matching event to bet")
        return False


def get_live_market_event(eventId: str, timestamp: float = None) -> dict:
    """
    Get event data from the live market service.
    
    Args:
        eventId: The event ID to query
        timestamp: Optional timestamp
        
    Returns:
        Event data
    """
    try:
        gql_input = {'eventId': eventId}

        if timestamp is not None:
            gql_input['timestamp'] = timestamp

        response = gql_client.execute(gql(get_event), variable_values=gql_input)['getEvent']
        return response
    except Exception as e:
        logger.exception("Error getting live market event")
        raise


def handle_funds(userId: str, amount: float) -> dict:
    """
    Handle funds for a user (deduct funds from wallet).
    
    Args:
        userId: User ID
        amount: Amount to deduct
        
    Returns:
        Response from wallet service
    """
    try:
        gql_input = {'input': {'amount': amount, 'userId': userId}}
        response = gql_client.execute(gql(deduct_funds), variable_values=gql_input)['deductFunds']
        return response
    except Exception as e:
        logger.exception("Error handling funds")
        raise


def betting_error(errorType: str, error_msg: str) -> dict:
    """
    Create a betting error response.
    
    Args:
        errorType: Type of error
        error_msg: Error message
        
    Returns:
        Error response dictionary
    """
    return {'__typename': errorType, 'message': error_msg}


def bet_list_response(data: dict) -> dict:
    """
    Create a bet list response.
    
    Args:
        data: Bet data
        
    Returns:
        BetList response dictionary
    """
    return {**{'__typename': 'BetList'}, **data}


def get_user_id(event: AppSyncResolverEvent):
    """
    Get the user ID from the event.
    
    Args:
        event: AppSync resolver event
        
    Returns:
        User ID
    """
    return event.identity.sub


def form_event(bet):
    """
    Form an event for EventBridge.
    
    Args:
        bet: Bet data
        
    Returns:
        EventBridge event
    """
    return {
        'Source': 'com.betting',
        'DetailType': 'BetsPlaced',
        'Detail': json.dumps(bet, default=str),
        'EventBusName': event_bus_name
    }


def send_event(bet):
    """
    Send an event to EventBridge.
    
    Args:
        bet: Bet data
        
    Returns:
        EventBridge response
    """
    try:
        data = form_event(bet)
        response = events.put_events(Entries=[data])
        return response
    except Exception as e:
        logger.exception("Error sending event")
        raise


@logger.inject_lambda_context(correlation_id_path=correlation_paths.APPSYNC_RESOLVER, log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """
    Lambda handler function.
    
    Args:
        event: Lambda event
        context: Lambda context
        
    Returns:
        AppSync resolver response
    """
    return app.resolve(event, context)
