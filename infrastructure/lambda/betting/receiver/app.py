from os import getenv
import json
import boto3

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.batch import BatchProcessor, EventType
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from botocore.exceptions import ClientError
from gql_utils import get_client
from mutations import lock_bets_for_event
from gql import gql

processor = BatchProcessor(event_type=EventType.SQS)
tracer = Tracer()
logger = Logger()

event_bus_name = getenv('EVENT_BUS')
session = boto3.Session()
events = session.client('events')

table_name = getenv('DB_TABLE')
region = getenv("REGION")
step_function = boto3.client('stepfunctions')

session = boto3.Session()
dynamodb = session.resource('dynamodb')
table = dynamodb.Table(table_name)

appsync_url = getenv("APPSYNC_URL")
gql_client = get_client(region, appsync_url)

def form_event(source, detailType, detail):
    return {
        'Source': source,
        'DetailType': detailType,
        'Detail': json.dumps(detail, default=str),
        'EventBusName': event_bus_name
    }

@tracer.capture_method
def record_handler(record: SQSRecord):
    # This function processes a record from SQS
    # Optionally return a dict which will be raised as a new event
    payload = record.body
    if payload:
        item = json.loads(payload)
        if item['source'] == 'com.livemarket':
            if item['detail-type'] == 'EventClosed':
                return handle_event_closed(item)

    logger.info({"message": "Unknown record type", "record": item})
    return None

@tracer.capture_method
def handle_event_closed(item: dict) -> dict:
    update_info = {
        'eventId': item['detail']['eventId']
    }
    gql_input = {
        'input': update_info
    }
    response = gql_client.execute(gql(lock_bets_for_event), variable_values=gql_input)[
        'lockBetsForEvent']

    update_info['bets'] = response['items']

    #iterate through all response['items'] form an event
    for bet in update_info['bets']:
        logger.info(f"Starting step function for bet")
        result = step_function.start_execution(
            stateMachineArn=getenv('STEP_FUNCTION_ARN'),
            input=json.dumps(bet, default=str)
            )
        bet['result'] = result

    if response['__typename'] == 'BetList':
        logger.info("Bets are closed. Beginning to settle the bets")
        return form_event('com.betting', 'SettlementStarted', update_info)
    elif 'Error' in response['__typename']:
        logger.exception("Failed to update odds")
        raise ValueError(
            f"updateEventOdds failed: {response['message']}")
    
def raise_bet_event(formevent) -> dict:
    return events.put_events(
        Entries=[
            formevent
        ]
    )

def bet_list_response(data: dict) -> dict:
    return {**{'__typename': 'BetList'}, **data}

def betting_error(errorType: str, error_msg: str) -> dict:
    return {'__typename': errorType, 'message': error_msg}

@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    batch = event["Records"]
    with processor(records=batch, handler=record_handler):
        processed_messages = processor.process()
        logger.info(processed_messages)

    output_events = [x[1]
                     for x in processed_messages if x[0] == "success" and x[1] is not None]
    if output_events:
        events.put_events(Entries=output_events)

    return processor.response()
