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
session = boto3.Session()
dynamodb = session.resource('dynamodb')
table = dynamodb.Table(table_name)


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


@app.resolver(type_name="Mutation", field_name="updateEventOdds")
@tracer.capture_method
def update_event_odds(input: dict) -> dict:
    try:
        response = table.update_item(
            Key={'eventId': input['eventId']},
            UpdateExpression="set homeOdds=:h, awayOdds=:a, drawOdds=:d, updatedAt=:u",
            ConditionExpression="attribute_exists(eventId)",
            ExpressionAttributeValues={
                ':h': input['homeOdds'],
                ':a': input['awayOdds'],
                ':d': input['drawOdds'],
                ':u': scalar_types_utils.aws_datetime()
            },
            ReturnValues="ALL_NEW")
        logger.info(response)

        return event_response(response['Attributes'])
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException as e:
        return events_error('InputError', 'The event does not exist')
    except ClientError as e:
        logger.exception({'ClientError': e})
        return events_error('UnknownError', 'An unknown error occured.')
    except Exception as e:
        logger.exception({'UnknownError': e})
        return events_error('UnknownError', 'An unknown error occured.')


def events_error(errorType: str, error_msg: str) -> dict:
    return {'__typename': errorType, 'message': error_msg}


def event_response(data: dict) -> dict:
    return {**{'__typename': 'Event'}, **data}


def event_list_response(data: dict) -> dict:
    return {**{'__typename': 'EventList'}, **data}


@logger.inject_lambda_context(correlation_id_path=correlation_paths.APPSYNC_RESOLVER)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    logger.info(event)
    return app.resolve(event, context)
