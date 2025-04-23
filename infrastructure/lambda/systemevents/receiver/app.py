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
    """
    Handle a system event by adding it to the system events database via GraphQL.
    
    Args:
        item: The event item to process
        
    Returns:
        Formatted event for EventBridge or None if error
    """
    try:
        extended_detail = item['detail']
        extended_detail["systemEventId"] = str(uuid.uuid4())
        
        gql_input = { 
            'input': 
                {'source': item['source'],
                'detailType': item['detail-type'],
                'detail': extended_detail}
            }

        response = gql_client.execute(gql(add_system_event), variable_values=gql_input)[
            'addSystemEvent']
            
        return {
            'Source': response['source'],
            'DetailType': response['detailType'],
            'Detail': response['detail'],
            'EventBusName': event_bus_name
        }
    except Exception as e:
        logger.error(f"Error adding system event: {str(e)}")
        return None


@tracer.capture_method
def record_handler(record: SQSRecord):
    """
    Process a single record from SQS.
    
    Args:
        record: SQS record to process
        
    Returns:
        Event to be raised or None
    """
    try:
        payload = record.body
        if not payload:
            return None
            
        item = json.loads(payload)
        return handle_system_event(item)
    except Exception as e:
        logger.error(f"Error processing record: {str(e)}")
        return None


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """
    Main Lambda handler function.
    
    Args:
        event: Lambda event
        context: Lambda context
        
    Returns:
        Batch processing response
    """
    try:
        batch = event["Records"]
        with processor(records=batch, handler=record_handler):
            processed_messages = processor.process()

        # Extract successful events that returned a value
        output_events = [
            result[1] for result in processed_messages 
            if result[0] == "success" and result[1] is not None
        ]
        
        # Send events to EventBridge if any exist
        if output_events:
            events.put_events(Entries=output_events)

        return processor.response()
    except Exception as e:
        logger.error(f"Error in lambda handler: {str(e)}")
        return {"batchItemFailures": []}
