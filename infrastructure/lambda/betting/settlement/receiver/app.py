from os import getenv
import json
import boto3

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.batch import BatchProcessor, EventType
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from botocore.exceptions import ClientError
from gql_utils import get_client

processor = BatchProcessor(event_type=EventType.SQS)
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


@tracer.capture_method
def handle_thirdparty_event(event: dict, context: LambdaContext) -> dict:
    if event['detail-type'] == 'UpdatedOdds':
        handle_updated_odds(event)


@tracer.capture_method
def handle_updated_odds(item: dict) -> dict:
    # Here we effectively just re-raise the event under the trading namespace
    # In a real world scenario the odds would be assessed by this service to produce new odds
    return form_event('UpdatedOdds', item['detail'])


def form_event(detailType, detail):
    return {
        'Source': 'com.trading',
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
        if item['source'] == 'com.betting':
            if item['detail-type'] == 'BetLocked':
                return handle_bet_settlement(item)

    logger.info({"message": "Unknown record type", "record": item})
    return None

def handle_bet_settlement(item: dict) -> dict:
    bet = item['detail']
    logger.info(f"Starting step function for bet")
    step_function = boto3.client('stepfunctions')
    result = step_function.start_execution(
        stateMachineArn=getenv('STEP_FUNCTION_ARN'),
        input=json.dumps(item['detail'], default=str)
        )
    print(result)
    bet['result'] = result

    return form_event('SettlementProcessBegan', bet)


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
