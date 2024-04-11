from os import getenv
import json
import boto3
from fractions import Fraction

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
    return {
        'Source': 'com.betting.settlement',
        'DetailType': detailType,
        'Detail': json.dumps(detail),
        'EventBusName': event_bus_name
    }

def get_live_market_event(eventId: str, timestamp: float = None) -> dict:
    gql_input = {'eventId': eventId}

    if timestamp is not None:
        gql_input['timestamp'] = timestamp

    response = gql_client.execute(gql(get_event), variable_values=gql_input)[
        'getEvent']
    return response

def get_event_outcome(eventId):
    livemarketevent = get_live_market_event(eventId)
    return livemarketevent['outcome']

def calculate_event_outcome(eventOutcome, betOutcome, odds, betAmount):
    fractionOdds = Fraction(odds)
    decimalOdds = float(fractionOdds.numerator) / float(fractionOdds.denominator)
    if eventOutcome == betOutcome:
        #We add amount that was bet. Since we might win less than we bet to begin with :)
        return betAmount+(decimalOdds * betAmount)
    else:
        return 0

def settle_bet(betId, userId):
    table.update_item(
            Key={'userId': userId, 'betId': betId},
            UpdateExpression="set betStatus=:r",
            ExpressionAttributeValues={
                ':r': 'settled'
            },
            ReturnValues="UPDATED_NEW")
    pass


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    print(event)
    
    odds = event['odds']
    betAmount = event['amount']
    if not betAmount:
        betAmount = 0.1
    eventOutcome = get_event_outcome(event['event']['eventId'])
    betOutcome = event['outcome']
    amount = calculate_event_outcome(eventOutcome, betOutcome, odds, betAmount)

    update_info = {
            'amount': round(amount*-1, 2), #required to use "deductfunds" function since it operates as a deduction. TODO: discuss wallet implementation
            'userId': event['userId']
    }
    gql_input = {
        'input': update_info
    }

    logger.info("The bet is settled. Event outcome is: %s, bet outcome: %s, amount: %s", eventOutcome, betOutcome, amount)

    response = gql_client.execute(gql(deduct_funds), variable_values=gql_input)[
        'deductFunds']
    
    settle_bet(event['betId'], event['userId'])

    event = form_event('BetSettlementComplete', response)
    events.put_events(Entries=[event])

    return event
