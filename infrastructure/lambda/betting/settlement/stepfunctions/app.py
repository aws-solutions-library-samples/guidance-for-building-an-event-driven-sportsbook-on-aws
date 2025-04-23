from os import getenv
import json
import boto3
from decimal import Decimal

from queries import get_event 
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.batch import BatchProcessor, EventType
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from botocore.exceptions import ClientError
from gql_utils import get_client
from mutations import deduct_funds, deposit_funds
from gql import gql

tracer = Tracer()
logger = Logger()

event_bus_name = getenv('EVENT_BUS')
session = boto3.Session()
events = session.client('events')

table_name = getenv('DB_TABLE')
region = getenv("REGION")

session = boto3.Session()
dynamodb = session.resource('dynamodb')
table = dynamodb.Table(table_name)

appsync_url = getenv("APPSYNC_URL")
gql_client = get_client(region, appsync_url)

def form_event(detailType, detail):
    """
    Form an event for EventBridge.
    
    Args:
        detailType: Event detail type
        detail: Event details
        
    Returns:
        EventBridge event
    """
    return {
        'Source': 'com.betting.settlement',
        'DetailType': detailType,
        'Detail': json.dumps(detail),
        'EventBusName': event_bus_name
    }

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

        response = gql_client.execute(gql(get_event), variable_values=gql_input)[
            'getEvent']
        return response
    except Exception as e:
        logger.exception("Error getting live market event")
        raise

def get_event_outcome(eventId):
    """
    Get the outcome of an event.
    
    Args:
        eventId: Event ID
        
    Returns:
        Event outcome
    """
    try:
        livemarketevent = get_live_market_event(eventId)
        return livemarketevent['outcome']
    except Exception as e:
        logger.exception("Error getting event outcome")
        raise

def calculate_event_outcome(eventOutcome, betOutcome, odds, betAmount):
    """
    Calculate the outcome of a bet.
    
    Args:
        eventOutcome: Actual event outcome
        betOutcome: Bet outcome
        odds: Bet odds (decimal format as string)
        betAmount: Bet amount (float)
        
    Returns:
        Payout amount
    """
    try:
        # Convert odds string and betAmount to Decimal for precise calculation
        decimalOdds = Decimal(str(odds))
        decimalBetAmount = Decimal(str(betAmount))
        
        if eventOutcome == betOutcome:
            # For decimal odds, the formula is stake * odds
            # This includes the original stake
            return decimalOdds * decimalBetAmount
        else:
            return Decimal('0')
    except Exception as e:
        logger.exception("Error calculating event outcome")
        raise

def settle_bet(betId, userId):
    """
    Mark a bet as settled.
    
    Args:
        betId: Bet ID
        userId: User ID
    """
    try:
        table.update_item(
            Key={'userId': userId, 'betId': betId},
            UpdateExpression="set betStatus=:r",
            ExpressionAttributeValues={
                ':r': 'settled'
            },
            ReturnValues="UPDATED_NEW")
    except Exception as e:
        logger.exception("Error settling bet")
        raise

@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """
    Lambda handler function.
    
    Args:
        event: Lambda event
        context: Lambda context
        
    Returns:
        EventBridge event
    """
    try:
        odds = event['odds']
        betAmount = event['amount']
        if not betAmount:
            betAmount = 0.1
        eventOutcome = get_event_outcome(event['event']['eventId'])
        betOutcome = event['outcome']
        amount = calculate_event_outcome(eventOutcome, betOutcome, odds, betAmount)

        update_info = {
            'amount': round(amount*-1, 2),  # Required to use "deductfunds" function
            'userId': event['userId']
        }
        gql_input = {
            'input': update_info
        }

        logger.info("Settling bet. Event outcome: %s, bet outcome: %s, amount: %s", 
                   eventOutcome, betOutcome, amount)

        response = gql_client.execute(gql(deduct_funds), variable_values=gql_input)[
            'deductFunds']
        
        settle_bet(event['betId'], event['userId'])

        event_data = form_event('BetSettlementComplete', response)
        events.put_events(Entries=[event_data])

        return event_data
    except Exception as e:
        logger.exception("Error in lambda handler")
        raise
