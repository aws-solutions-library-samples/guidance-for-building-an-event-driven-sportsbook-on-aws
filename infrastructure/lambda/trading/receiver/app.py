from os import getenv
import json
import boto3

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.batch import BatchProcessor, EventType
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord

processor = BatchProcessor(event_type=EventType.SQS)
tracer = Tracer()
logger = Logger()

event_bus_name = getenv('EVENT_BUS')
session = boto3.Session()
events = session.client('events')


@tracer.capture_method
def handle_thirdparty_event(event: dict, context: LambdaContext) -> dict:
    """
    Handle events from third-party sources.
    
    Args:
        event: The event to process
        context: Lambda context
        
    Returns:
        Processed event or None
    """
    try:
        if event['detail-type'] == 'UpdatedOdds':
            return handle_updated_odds(event)
        return None
    except Exception as e:
        logger.error(f"Error handling third party event: {str(e)}")
        return None


@tracer.capture_method
def handle_updated_odds(item: dict) -> dict:
    """
    Process updated odds events.
    
    In a real-world scenario, the odds would be assessed by this service
    to produce new odds. Currently, we just re-raise the event under
    the trading namespace.
    
    Args:
        item: Event containing updated odds
        
    Returns:
        Formatted event for EventBridge
    """
    try:
        return form_event('UpdatedOdds', item['detail'])
    except Exception as e:
        logger.error(f"Error handling updated odds: {str(e)}")
        return None


def form_event(detail_type: str, detail: dict) -> dict:
    """
    Create a properly formatted event for EventBridge.
    
    Args:
        detail_type: The type of event
        detail: The event payload
        
    Returns:
        Formatted event ready for EventBridge
    """
    try:
        return {
            'Source': 'com.trading',
            'DetailType': detail_type,
            'Detail': json.dumps(detail),
            'EventBusName': event_bus_name
        }
    except Exception as e:
        logger.error(f"Error forming event: {str(e)}")
        return None


@tracer.capture_method
def record_handler(record: SQSRecord) -> dict:
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
        
        # Check if this is a third-party updated odds event
        if (item.get('source') == 'com.thirdparty' and 
            item.get('detail-type') == 'UpdatedOdds'):
            return handle_updated_odds(item)
            
        return None
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
        # Process batch of records
        batch = event.get("Records", [])
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
