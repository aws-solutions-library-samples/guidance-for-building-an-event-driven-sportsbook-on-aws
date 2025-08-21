import time
from datetime import datetime
from decimal import Decimal
from os import getenv
import json
import boto3

from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

from aws_lambda_powertools.utilities.data_classes import AppSyncResolverEvent
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import AppSyncResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.data_classes.appsync import scalar_types_utils

tracer = Tracer()
logger = Logger()
app = AppSyncResolver()

table_name = getenv('DB_TABLE')
history_table_name = getenv('DB_HISTORY_TABLE')
history_retention_seconds = int(getenv('DB_HISTORY_RETENTION'))
session = boto3.Session()
dynamodb = session.resource('dynamodb')
table = dynamodb.Table(table_name)
history_table = dynamodb.Table(history_table_name)
event_bus_name = getenv('EVENT_BUS')
events = session.client('events')


@app.resolver(type_name="Query", field_name="getEvents")
@tracer.capture_method
def get_events(startKey: str = "") -> dict:
    """
    Get all running events.
    
    Args:
        startKey: Optional pagination token
        
    Returns:
        List of events or error response
    """
    try:
        args = {
            'FilterExpression': Key('eventStatus').eq('running')
        }
        if startKey:
            args['ExclusiveStartKey'] = {'eventId': startKey}
                
        response = table.scan(**args)
        result = {
            'items': response.get('Items', [])
        }
        if response.get('LastEvaluatedKey'):
            result['nextToken'] = response['LastEvaluatedKey']['eventId']

        return event_list_response(result)

    except ClientError as e:
        logger.error(f"DynamoDB client error in get_events: {str(e)}")
        return events_error('UnknownError', 'An unknown error occurred.')
    except Exception as e:
        logger.error(f"Error in get_events: {str(e)}")
        return events_error('UnknownError', 'An unknown error occurred.')


def event_list_response(data: dict) -> dict:
    """
    Format event list response.
    
    Args:
        data: Raw event data
        
    Returns:
        Formatted event list response
    """
    items = data.get('items', [])
    for item in items:
        item['marketstatus'] = item.get('marketstatus', [])
    return {**{'__typename': 'EventList'}, **data}


@app.resolver(type_name="Query", field_name="getEvent")
@tracer.capture_method
def get_event(eventId: str, timestamp: float = None) -> dict:
    """
    Get a specific event by ID, optionally at a specific point in time.
    
    Args:
        eventId: ID of the event to retrieve
        timestamp: Optional timestamp to get historical data
        
    Returns:
        Event data or error response
    """
    try:
        current_event = table.get_item(Key={'eventId': eventId})['Item']

        if timestamp is None:
            return event_response(current_event)

        current_event_ts = datetime.fromisoformat(
            current_event['updatedAt'][0:-1])
        requested_ts = datetime.fromtimestamp(timestamp)

        if current_event_ts < requested_ts:
            return event_response(current_event)

        # get the first entry from history that is older than the request
        matched_events = history_table.query(
            KeyConditionExpression='eventId = :e AND #t < :t',
            ExpressionAttributeValues={
                ':e': eventId,
                ':t': Decimal(requested_ts.timestamp())
            },
            ExpressionAttributeNames={
                '#t': 'timestamp'
            },
            Limit=1,
            ScanIndexForward=False
        )['Items']

        # We won't have matched events if the timestamp is further back than our history retention
        if not matched_events:
            return events_error('InputError', 'The history for this event is not queryable for the requested timestamp')

        return event_response(matched_events[0])
    except dynamodb.meta.client.exceptions.ResourceNotFoundException:
        return events_error('InputError', 'The event does not exist')
    except ClientError as e:
        logger.error(f"DynamoDB client error in get_event: {str(e)}")
        return events_error('UnknownError', 'An unknown error occurred.')
    except Exception as e:
        logger.error(f"Error in get_event: {str(e)}")
        return events_error('UnknownError', 'An unknown error occurred.')


@app.resolver(type_name="Mutation", field_name="updateEventOdds")
@tracer.capture_method
def update_event_odds(input: dict) -> dict:
    """
    Update the odds for an event.
    
    Args:
        input: Event odds data to update
        
    Returns:
        Updated event data or error response
    """
    try:
        now = scalar_types_utils.aws_datetime()
        response = table.update_item(
            Key={'eventId': input['eventId']},
            UpdateExpression="set homeOdds=:h, awayOdds=:a, drawOdds=:d, updatedAt=:u",
            ConditionExpression="attribute_exists(eventId)",
            ExpressionAttributeValues={
                ':h': input['homeOdds'],
                ':a': input['awayOdds'],
                ':d': input['drawOdds'],
                ':u': now
            },
            ReturnValues="ALL_NEW")
        current_event = response['Attributes']

        # Write the current state to the history log to persist for the configured time
        epoch = Decimal(time.time())
        history_entry = {**current_event, **
                         {'timestamp': epoch, 'expiry': epoch + history_retention_seconds}}
        history_table.put_item(Item=history_entry)

        return event_response(current_event)
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return events_error('InputError', 'The event does not exist')
    except ClientError as e:
        logger.error(f"DynamoDB client error in update_event_odds: {str(e)}")
        return events_error('UnknownError', 'An unknown error occurred.')
    except Exception as e:
        logger.error(f"Error in update_event_odds: {str(e)}")
        return events_error('UnknownError', 'An unknown error occurred.')


@app.resolver(type_name="Mutation", field_name="suspendMarket")
@tracer.capture_method
def suspend_market(input: dict) -> dict:
    """
    Suspend a market for an event.
    
    Args:
        input: Market data to suspend
        
    Returns:
        Updated event data or error response
    """
    try:
        # Check if the market exists in the marketstatus field
        response = table.get_item(Key={'eventId': input['eventId']}, ProjectionExpression='marketstatus')
        existing_markets = response.get('Item', {}).get('marketstatus', [])

        existing_market = next((market for market in existing_markets if market['name'] == input['market']), None)
        if existing_market:
            existing_market['status'] = 'Suspended'
        else:
            # Add new market to existing_markets
            existing_markets.append({'name': input['market'], 'status': 'Suspended'})

        # Update the marketstatus field
        update_expression = "SET marketstatus = :marketstatus"
        expression_values = {
            ':marketstatus': existing_markets
        }

        response = table.update_item(
            Key={'eventId': input['eventId']},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues="ALL_NEW")
        current_event = response['Attributes']

        # Write the current state to the history log
        epoch = Decimal(time.time())
        history_entry = {**current_event, **
                         {'timestamp': epoch, 'expiry': epoch + history_retention_seconds}}
        history_table.put_item(Item=history_entry)

        return event_response(current_event)
    except ClientError as e:
        logger.error(f"DynamoDB client error in suspend_market: {str(e)}")
        return events_error('UnknownError', 'An unknown error occurred.')
    except Exception as e:
        logger.error(f"Error in suspend_market: {str(e)}")
        return events_error('UnknownError', 'An unknown error occurred.')


@app.resolver(type_name="Mutation", field_name="unsuspendMarket")
@tracer.capture_method
def unsuspend_market(input: dict) -> dict:
    """
    Unsuspend a market for an event.
    
    Args:
        input: Market data to unsuspend
        
    Returns:
        Updated event data or error response
    """
    try:
        # Check if the market exists in the marketstatus field
        response = table.get_item(Key={'eventId': input['eventId']}, ProjectionExpression='marketstatus')
        existing_markets = response.get('Item', {}).get('marketstatus', [])

        existing_market = next((market for market in existing_markets if market['name'] == input['market']), None)
        if existing_market:
            existing_market['status'] = 'Active'
        else:
            # Add new market to existing_markets
            existing_markets.append({'name': input['market'], 'status': 'Active'})

        # Update the marketstatus field
        update_expression = "SET marketstatus = :marketstatus"
        expression_values = {
            ':marketstatus': existing_markets
        }

        response = table.update_item(
            Key={'eventId': input['eventId']},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues="ALL_NEW")
        current_event = response['Attributes']

        # Write the current state to the history log
        epoch = Decimal(time.time())
        history_entry = {**current_event, **
                         {'timestamp': epoch, 'expiry': epoch + history_retention_seconds}}
        history_table.put_item(Item=history_entry)

        return event_response(current_event)
    except ClientError as e:
        logger.error(f"DynamoDB client error in unsuspend_market: {str(e)}")
        return events_error('UnknownError', 'An unknown error occurred.')
    except Exception as e:
        logger.error(f"Error in unsuspend_market: {str(e)}")
        return events_error('UnknownError', 'An unknown error occurred.')


@app.resolver(type_name="Mutation", field_name="closeMarket")
@tracer.capture_method
def close_market(input: dict) -> dict:
    """
    Close a market for an event.
    
    Args:
        input: Market data to close
        
    Returns:
        Updated event data or error response
    """
    try:
        response = table.update_item(
            Key={'eventId': input['eventId']},
            UpdateExpression="SET marketstatus = list_append(if_not_exists(marketstatus, :empty_list), :status)",
            ExpressionAttributeValues={
                ':empty_list': [],
                ':status': [{'name': input['market'], 'status': 'Closed'}]
            },
            ReturnValues="ALL_NEW")
        current_event = response['Attributes']

        # Write the current state to the history log
        epoch = Decimal(time.time())
        history_entry = {**current_event, **
                         {'timestamp': epoch, 'expiry': epoch + history_retention_seconds}}
        history_table.put_item(Item=history_entry)

        return event_response(current_event)
    except ClientError as e:
        logger.error(f"DynamoDB client error in close_market: {str(e)}")
        return events_error('UnknownError', 'An unknown error occurred.')
    except Exception as e:
        logger.error(f"Error in close_market: {str(e)}")
        return events_error('UnknownError', 'An unknown error occurred.')


@app.resolver(type_name="Mutation", field_name="finishEvent")
@tracer.capture_method
def finish_event(input: dict) -> dict:
    """
    Mark an event as finished.
    
    Args:
        input: Event data to update
        
    Returns:
        Updated event data or error response
    """
    try:
        now = scalar_types_utils.aws_datetime()
        response = table.update_item(
            Key={'eventId': input['eventId']},
            UpdateExpression="set eventStatus=:d, updatedAt=:u, outcome=:o",
            ConditionExpression="attribute_exists(eventId)",
            ExpressionAttributeValues={
                ':d': input['eventStatus'],
                ':u': now,
                ':o': input['outcome']
            },
            ReturnValues="ALL_NEW")
        current_event = response['Attributes']

        # Write the current state to the history log to persist for the configured time
        epoch = Decimal(time.time())
        history_entry = {**current_event, **
                         {'timestamp': epoch, 'expiry': epoch + history_retention_seconds}}
        history_table.put_item(Item=history_entry)

        return event_response(current_event)
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return events_error('InputError', 'The event does not exist')
    except ClientError as e:
        logger.error(f"DynamoDB client error in finish_event: {str(e)}")
        return events_error('UnknownError', 'An unknown error occurred.')
    except Exception as e:
        logger.error(f"Error in finish_event: {str(e)}")
        return events_error('UnknownError', 'An unknown error occurred.')


@app.resolver(type_name="Mutation", field_name="triggerFinishEvent")
@tracer.capture_method
def trigger_finish_event(input: dict) -> dict:
    """
    Trigger an event finish notification.
    
    Args:
        input: Event data with outcome
        
    Returns:
        Event data or error response
    """
    try:
        # Effectively just raising event back to event bridge
        current_event = get_event(input['eventId'])
        current_event["outcome"] = input["outcome"]
        send_event(current_event, 'EventClosed')
        return event_response(current_event)
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return events_error('InputError', 'The event does not exist')
    except ClientError as e:
        logger.error(f"DynamoDB client error in trigger_finish_event: {str(e)}")
        return events_error('UnknownError', 'An unknown error occurred.')
    except Exception as e:
        logger.error(f"Error in trigger_finish_event: {str(e)}")
        return events_error('UnknownError', 'An unknown error occurred.')


@app.resolver(type_name="Mutation", field_name="triggerSuspendMarket")
@tracer.capture_method
def trigger_suspend_market(input: dict) -> dict:
    """
    Trigger a market suspension notification.
    
    Args:
        input: Market data to suspend
        
    Returns:
        Event data or error response
    """
    try:
        # Fetch the current event data
        current_event = get_event(input['eventId'])

        # Prepare the event details
        event_details = {
            'eventId': current_event['eventId'],
            'market': input['market'],
            'eventStatus': current_event['eventStatus']
        }

        # Send the event to the EventBridge
        send_event(event_details, 'MarketSuspended')

        return event_response(current_event)
    except ClientError as e:
        logger.error(f"DynamoDB client error in trigger_suspend_market: {str(e)}")
        return events_error('UnknownError', 'An unknown error occurred.')
    except Exception as e:
        logger.error(f"Error in trigger_suspend_market: {str(e)}")
        return events_error('UnknownError', 'An unknown error occurred.')


@app.resolver(type_name="Mutation", field_name="triggerUnsuspendMarket")
@tracer.capture_method
def trigger_unsuspend_market(input: dict) -> dict:
    """
    Trigger a market unsuspension notification.
    
    Args:
        input: Market data to unsuspend
        
    Returns:
        Event data or error response
    """
    try:
        # Fetch the current event data
        current_event = get_event(input['eventId'])

        # Prepare the event details
        event_details = {
            'eventId': current_event['eventId'],
            'market': input['market'],
            'eventStatus': current_event['eventStatus']
        }

        # Send the event to the EventBridge
        send_event(event_details, 'MarketUnsuspended')

        return event_response(current_event)
    except ClientError as e:
        logger.error(f"DynamoDB client error in trigger_unsuspend_market: {str(e)}")
        return events_error('UnknownError', 'An unknown error occurred.')
    except Exception as e:
        logger.error(f"Error in trigger_unsuspend_market: {str(e)}")
        return events_error('UnknownError', 'An unknown error occurred.')


@app.resolver(type_name="Mutation", field_name="addEvent")
@tracer.capture_method
def add_event(input: dict) -> dict:
    """
    Add a new event.
    
    Args:
        input: Event data to add
        
    Returns:
        Added event data or error response
    """
    try:
        table.put_item(Item=input)
        return event_response(input)
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return events_error('InputError', 'The event could not be added in the dynamodb table')
    except ClientError as e:
        logger.error(f"DynamoDB client error in add_event: {str(e)}")
        return events_error('UnknownError', 'An unknown error occurred while adding event.')
    except Exception as e:
        logger.error(f"Error in add_event: {str(e)}")
        return events_error('UnknownError', 'An unknown error occurred while adding event.')


def form_event(detail_type, event_data, market_name=None):
    """
    Create a properly formatted event for EventBridge.
    
    Args:
        detail_type: The type of event
        event_data: The event payload
        market_name: Optional market name
        
    Returns:
        Formatted event for EventBridge
    """
    try:
        return {
            'Source': 'com.thirdparty',
            'DetailType': detail_type,
            'Detail': json.dumps(event_data),
            'EventBusName': event_bus_name
        }
    except Exception as e:
        logger.error(f"Error forming event: {str(e)}")
        raise


def send_event(current_event, detail_type, market_name=None):
    """
    Send an event to EventBridge.
    
    Args:
        current_event: Event data to send
        detail_type: Type of event
        market_name: Optional market name
    """
    try:
        event_entry = form_event(detail_type, current_event, market_name)
        events.put_events(Entries=[event_entry])
    except Exception as e:
        logger.error(f"Error sending event: {str(e)}")
        raise


def events_error(error_type: str, error_msg: str) -> dict:
    """
    Create an error response.
    
    Args:
        error_type: Type of error
        error_msg: Error message
        
    Returns:
        Formatted error response
    """
    return {'__typename': error_type, 'message': error_msg}


def event_response(data: dict) -> dict:
    """
    Create a success response for a single event.
    
    Args:
        data: Event data
        
    Returns:
        Formatted event response
    """
    return {**{'__typename': 'Event'}, **data}


@logger.inject_lambda_context(correlation_id_path=correlation_paths.APPSYNC_RESOLVER, log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """
    Main Lambda handler function.
    
    Args:
        event: Lambda event
        context: Lambda context
        
    Returns:
        AppSync resolver response
    """
    try:
        return app.resolve(event, context)
    except Exception as e:
        logger.error(f"Error in lambda handler: {str(e)}")
        return {"errors": [{"message": "Internal server error"}]}
