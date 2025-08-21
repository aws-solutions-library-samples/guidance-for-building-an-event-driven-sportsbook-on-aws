from os import getenv
import json
import boto3
from gql_utils import get_client
from mutations import update_event_odds, add_event, finish_event, suspend_market, unsuspend_market
from gql import gql

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.batch import BatchProcessor, EventType
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord

processor = BatchProcessor(event_type=EventType.SQS)
tracer = Tracer()
logger = Logger()

appsync_url = getenv("APPSYNC_URL")
region = getenv("REGION")
event_bus_name = getenv('EVENT_BUS')
gql_client = get_client(region, appsync_url)
session = boto3.Session()
events = session.client('events')
sqsqueue = session.client('sqs')
queue_url = getenv('QUEUE')


@tracer.capture_method
def handle_updated_odds(item: dict) -> dict:
    """
    Handle updated odds event.
    
    Args:
        item: Event containing updated odds
        
    Returns:
        Formatted event for EventBridge or None if error
    """
    try:
        update_info = {
            'eventId': item['detail']['eventId'],
            'homeOdds': item['detail']['homeOdds'],
            'awayOdds': item['detail']['awayOdds'],
            'drawOdds': item['detail']['drawOdds']
        }
        gql_input = {
            'input': update_info
        }
        response = gql_client.execute(gql(update_event_odds), variable_values=gql_input)[
            'updateEventOdds']

        if response['__typename'] == 'Event':
            return form_event('com.livemarket', 'UpdatedOdds', update_info)
        elif 'Error' in response['__typename']:
            logger.error(f"Failed to update odds: {response['message']}")
            return None
    except Exception as e:
        logger.error(f"Error handling updated odds: {str(e)}")
        return None


@tracer.capture_method
def handle_event_finished(item: dict) -> dict:
    """
    Handle event finished notification.
    
    Args:
        item: Event containing finished event data
        
    Returns:
        Formatted event for EventBridge or None if error
    """
    try:
        update_info = {
            'eventId': item['detail']['eventId'],
            'eventStatus': 'finished',
            'outcome': item['detail']['outcome']
        }
        gql_input = {
            'input': update_info
        }

        response = gql_client.execute(gql(finish_event), variable_values=gql_input)[
            'finishEvent']

        if response['__typename'] == 'Event':
            return form_event('com.livemarket', 'EventClosed', update_info)
        elif 'Error' in response['__typename']:
            logger.error(f"Failed to finish event: {response['message']}")
            return None
    except Exception as e:
        logger.error(f"Error handling event finished: {str(e)}")
        return None


@tracer.capture_method
def handle_add_event(item: dict) -> dict:
    """
    Handle add event notification.
    
    Args:
        item: Event containing new event data
        
    Returns:
        Formatted event for EventBridge or None if error
    """
    try:
        add_event_info = {
            'eventId': item['detail']['eventId'],
            'home': item['detail']['home'],
            'away': item['detail']['away'],
            'homeOdds': item['detail']['homeOdds'],
            'awayOdds': item['detail']['awayOdds'],
            'drawOdds': item['detail']['drawOdds'],
            'start': item['detail']['start'],
            'end': item['detail']['end'],
            'updatedAt': item['detail']['updatedAt'],
            'duration': item['detail']['duration'],
            'eventStatus': item['detail']['eventStatus']
        }

        gql_input = {
            'input': add_event_info
        }

        response = gql_client.execute(gql(add_event), variable_values=gql_input)[
            'addEvent']

        if response['__typename'] == 'Event':
            return form_event('com.livemarket', 'EventAdded', add_event_info)
        elif 'Error' in response['__typename']:
            logger.error(f"Failed to add event: {response['message']}")
            return None
    except Exception as e:
        logger.error(f"Error handling add event: {str(e)}")
        return None


def form_event(source, detail_type, detail):
    """
    Create a properly formatted event for EventBridge.
    
    Args:
        source: Event source
        detail_type: The type of event
        detail: The event payload
        
    Returns:
        Formatted event for EventBridge
    """
    try:
        return {
            'Source': source,
            'DetailType': detail_type,
            'Detail': json.dumps(detail),
            'EventBusName': event_bus_name
        }
    except Exception as e:
        logger.error(f"Error forming event: {str(e)}")
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
        
        if item['source'] == 'com.trading' and item['detail-type'] == 'UpdatedOdds':
            return handle_updated_odds(item)
            
        if item['source'] == 'com.thirdparty':
            if item['detail-type'] == 'EventClosed':
                return handle_event_finished(item)
            elif item['detail-type'] == 'MarketSuspended':
                return handle_market_suspended(item)
            elif item['detail-type'] == 'MarketUnsuspended':
                return handle_market_unsuspended(item)
            elif item['detail-type'] == 'EventAdded':
                return handle_add_event(item)
                
        return None
    except Exception as e:
        logger.error(f"Error processing record: {str(e)}")
        return None


@tracer.capture_method
def handle_market_suspended(item: dict) -> dict:
    """
    Handle market suspended notification.
    
    Args:
        item: Event containing market suspension data
        
    Returns:
        Formatted event for EventBridge or None if error
    """
    try:
        update_info = {
            'eventId': item['detail']['eventId'],
            'market': item['detail']['market'],
        }
        gql_input = {
            'input': update_info
        }
        response = gql_client.execute(gql(suspend_market), variable_values=gql_input)[
            'suspendMarket']

        if response['__typename'] == 'Event':
            return form_event('com.livemarket', 'MarketSuspended', update_info)
        elif 'Error' in response['__typename']:
            logger.error(f"Failed to suspend market: {response['message']}")
            return None
    except Exception as e:
        logger.error(f"Error handling market suspended: {str(e)}")
        return None


@tracer.capture_method
def handle_market_unsuspended(item: dict) -> dict:
    """
    Handle market unsuspended notification.
    
    Args:
        item: Event containing market unsuspension data
        
    Returns:
        Formatted event for EventBridge or None if error
    """
    try:
        update_info = {
            'eventId': item['detail']['eventId'],
            'market': item['detail']['market'],
        }
        gql_input = {
            'input': update_info
        }
        response = gql_client.execute(gql(unsuspend_market), variable_values=gql_input)[
            'unsuspendMarket']

        if response['__typename'] == 'Event':
            return form_event('com.livemarket', 'MarketUnsuspended', update_info)
        elif 'Error' in response['__typename']:
            logger.error(f"Failed to unsuspend market: {response['message']}")
            return None
    except Exception as e:
        logger.error(f"Error handling market unsuspended: {str(e)}")
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
