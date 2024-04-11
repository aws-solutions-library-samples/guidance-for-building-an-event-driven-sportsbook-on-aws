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
        logger.exception({'ClientError': e})
        return events_error('UnknownError', 'An unknown error occurred.')
    except Exception as e:
        logger.exception({'UnknownError': e})
        return events_error('UnknownError', 'An unknown error occurred.')

def event_list_response(data: dict) -> dict:
    items = data.get('items', [])
    print(items)
    for item in items:
        item['marketstatus'] = item.get('marketstatus', [])
    return {**{'__typename': 'EventList'}, **data}


@app.resolver(type_name="Query", field_name="getEvent")
@tracer.capture_method
def get_event(eventId: str, timestamp: float = None) -> dict:
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
    except dynamodb.meta.client.exceptions.ResourceNotFoundException as e:
        return events_error('InputError', 'The event does not exist')
    except ClientError as e:
        logger.exception({'ClientError': e})
        return events_error('UnknownError', 'An unknown error occured.')
    except Exception as e:
        logger.exception({'UnknownError': e})
        return events_error('UnknownError', 'An unknown error occured.')


@app.resolver(type_name="Mutation", field_name="updateEventOdds")
@tracer.capture_method
def update_event_odds(input: dict) -> dict:
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
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException as e:
        return events_error('InputError', 'The event does not exist')
    except ClientError as e:
        logger.exception({'ClientError': e})
        return events_error('UnknownError', 'An unknown error occured.')
    except Exception as e:
        logger.exception({'UnknownError': e})
        return events_error('UnknownError', 'An unknown error occured.')

@app.resolver(type_name="Mutation", field_name="suspendMarket")
@tracer.capture_method
def suspend_market(input: dict) -> dict:
    try:
        now = scalar_types_utils.aws_datetime()
        update_expression = ""
        expression_values = {}

        # Check if the market exists in the marketstatus field
        response = table.get_item(Key={'eventId': input['eventId']}, ProjectionExpression='marketstatus')
        existing_markets = response.get('Item', {}).get('marketstatus', [])

        existing_market = next((market for market in existing_markets if market['name'] == input['market']), None)
        if existing_market:
            existing_market['status'] = 'Suspended'

        else:
            #add new market to existing_markets
            existing_markets.append({'name': input['market'], 'status': 'Suspended'})

        #iterate through existing_markets and generate "SET" message to dynamodb
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
        logger.exception({'ClientError': e})
        return events_error('UnknownError', 'An unknown error occurred.')
    except Exception as e:
        logger.exception({'UnknownError': e})
        return events_error('UnknownError', 'An unknown error occurred.')

@app.resolver(type_name="Mutation", field_name="unsuspendMarket")
@tracer.capture_method
def unsuspend_market(input: dict) -> dict:
    try:
        now = scalar_types_utils.aws_datetime()
        update_expression = ""
        expression_values = {}

        # Check if the market exists in the marketstatus field
        response = table.get_item(Key={'eventId': input['eventId']}, ProjectionExpression='marketstatus')
        existing_markets = response.get('Item', {}).get('marketstatus', [])

        existing_market = next((market for market in existing_markets if market['name'] == input['market']), None)
        if existing_market:
            existing_market['status'] = 'Active'

        else:
            #add new market to existing_markets
            existing_markets.append({'name': input['market'], 'status': 'Active'})

        #iterate through existing_markets and generate "SET" message to dynamodb
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
        logger.exception({'ClientError': e})
        return events_error('UnknownError', 'An unknown error occurred.')
    except Exception as e:
        logger.exception({'UnknownError': e})
        return events_error('UnknownError', 'An unknown error occurred.')

@app.resolver(type_name="Mutation", field_name="closeMarket")
@tracer.capture_method
def close_market(input: dict) -> dict:
    try:
        now = scalar_types_utils.aws_datetime()
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
        logger.exception({'ClientError': e})
        return events_error('UnknownError', 'An unknown error occurred.')
    except Exception as e:
        logger.exception({'UnknownError': e})
        return events_error('UnknownError', 'An unknown error occurred.')

@app.resolver(type_name="Mutation", field_name="finishEvent")
@tracer.capture_method
def finish_event(input: dict) -> dict:
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
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException as e:
        return events_error('InputError', 'The event does not exist')
    except ClientError as e:
        logger.exception({'ClientError': e})
        return events_error('UnknownError', 'An unknown error occured.')
    except Exception as e:
        logger.exception({'UnknownError': e})
        return events_error('UnknownError', 'An unknown error occured.')


@app.resolver(type_name="Mutation", field_name="triggerFinishEvent")
@tracer.capture_method
def trigger_finish_event(input: dict) -> dict:
    try:
        #effectively just raising event back to event bridge
        current_event = get_event(input['eventId'])
        current_event["outcome"] = input["outcome"]
        send_event(current_event, 'EventClosed')
        print(current_event)
        return event_response(current_event)
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException as e:
        return events_error('InputError', 'The event does not exist')
    except ClientError as e:
        logger.exception({'ClientError': e})
        return events_error('UnknownError', 'An unknown error occured.')
    except Exception as e:
        logger.exception({'UnknownError': e})
        return events_error('UnknownError', 'An unknown error occured.')

@app.resolver(type_name="Mutation", field_name="triggerSuspendMarket")
@tracer.capture_method
def trigger_suspend_market(input: dict) -> dict:
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
        logger.exception({'ClientError': e})
        return events_error('UnknownError', 'An unknown error occurred.')
    except Exception as e:
        logger.exception({'UnknownError': e})
        return events_error('UnknownError', 'An unknown error occurred.')

@app.resolver(type_name="Mutation", field_name="triggerUnsuspendMarket")
@tracer.capture_method
def trigger_unsuspend_market(input: dict) -> dict:
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
        logger.exception({'ClientError': e})
        return events_error('UnknownError', 'An unknown error occurred.')
    except Exception as e:
        logger.exception({'UnknownError': e})
        return events_error('UnknownError', 'An unknown error occurred.')

@app.resolver(type_name="Mutation", field_name="addEvent")
@tracer.capture_method
def add_event(input: dict) -> dict:
    try:
        logger.info('Adding event %s to DynamoDB Table', input)
        table.put_item(Item=input)
        return event_response(input)
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException as e:
        return events_error('InputError', 'The event could not be added in the dynamodb table')
    except ClientError as e:
        logger.exception({'ClientError': e})
        return events_error('UnknownError', 'An unknown error occured while adding event.')
    except Exception as e:
        return events_error('UnknownError', 'An unknown error occured while adding event.')

def form_event(detail_type, event_data, market_name=None):
    return {
        'Source': 'com.thirdparty',
        'DetailType': detail_type,
        'Detail': json.dumps(event_data),
        'EventBusName': event_bus_name
    }


def send_event(current_event, detail_type, market_name=None):
    event_entry = form_event(detail_type, current_event, market_name)
    response = events.put_events(Entries=[event_entry])
    logger.info(f'Event sent to EventBridge: {response}')

def events_error(errorType: str, error_msg: str) -> dict:
    return {'__typename': errorType, 'message': error_msg}


def event_response(data: dict) -> dict:
    return {**{'__typename': 'Event'}, **data}


def event_list_response(data: dict) -> dict:
    return {**{'__typename': 'EventList'}, **data}


@logger.inject_lambda_context(correlation_id_path=correlation_paths.APPSYNC_RESOLVER, log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
