import time
from datetime import datetime
from decimal import Decimal
from os import getenv
import json
import boto3

from botocore.exceptions import ClientError

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
        args = {}
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
        return events_error('UnknownError', 'An unknown error occured.')
    except Exception as e:
        logger.exception({'UnknownError': e})
        return events_error('UnknownError', 'An unknown error occured.')


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
        send_event(current_event)
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

def form_event(userResponse):
    return {
        'Source': 'com.thirdparty',
        'DetailType': 'EventClosed',
        'Detail': json.dumps(userResponse),
        'EventBusName': event_bus_name
    }

def send_event(userResponse):
    data = form_event(userResponse)
    response = events.put_events(Entries=[data])
    return response

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
