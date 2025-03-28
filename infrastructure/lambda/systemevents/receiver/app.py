
from os import getenv
import json
import boto3
import uuid
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
    logger.debug( f'handle_system_event:{item}' )
    extended_detail = item['detail']
    extended_detail["systemEventId"] = str(uuid.uuid4())
    
    gql_input = { 
        'input': 
            {'source':item['source'],
             'detailType':item['detail-type'],
             'detail':extended_detail}
        }

    try:
        response = gql_client.execute(gql(add_system_event), variable_values=gql_input)[
        'addSystemEvent']
        logger.debug({"response": response}) 
        return {
            'Source': response['source'],
            'DetailType': response['detailType'],
            'Detail': response['detail'],
            'EventBusName': event_bus_name
        }
    except Exception as e:
        logger.error({"message": "Error adding system event", "error": e})
        raise ValueError(f"addSystemEvent failed: {e}")


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
    logger.info(event)
    batch = event["Records"]
    with processor(records=batch, handler=record_handler):
        processed_messages = processor.process()
        logger.debug(processed_messages)

    output_events = [x[1]
                    for x in processed_messages if x[0] == "success" and x[1] is not None]
                    
    logger.debug(processed_messages[0])
    if output_events:
        events.put_events(Entries=output_events)

    return processor.response()