
from os import getenv
import json
import boto3
from gql_utils import get_client
from mutations import add_system_event
from gql import gql

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.batch import BatchProcessor, EventType
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord

processor = BatchProcessor(event_type=EventType.SQS)
tracer = Tracer()
logger = Logger()

region = getenv("REGION")
appsync_url = getenv("APPSYNC_URL")
event_bus_name = getenv('EVENT_BUS')
gql_client = get_client(region, appsync_url)
session = boto3.Session()
events = session.client('events')

@tracer.capture_method
def handle_system_event(item: dict):
    logger.info( f'handle_system_event:{item}' )
    gql_input = { 
        'input': 
            {'source':item['source'],
             'detailType':item['detail-type'],
             'detail':item['detail']}
        } 
    response = gql_client.execute(gql(add_system_event), variable_values=gql_input)[
        'addSystemEvent']
    return response

@tracer.capture_method
def record_handler(record: SQSRecord):
    # This function processes a record from SQS
    # Optionally return a dict which will be raised as a new event
    payload = record.body
    if payload:
        item = json.loads(payload)
        return handle_system_event(item)

    logger.warning({"message": "Unknown record type", "record": item})
    return None

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