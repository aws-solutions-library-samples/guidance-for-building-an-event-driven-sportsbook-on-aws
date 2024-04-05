from os import getenv
import json
import boto3
from gql_utils import get_client
from mutations import update_event_odds, add_event, finish_event, lock_bets_for_event
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
        logger.info("Odds updated")
        return form_event('com.livemarket', 'UpdatedOdds', update_info)
    elif 'Error' in response['__typename']:
        logger.exception("Failed to update odds")
        raise ValueError(
            f"updateEventOdds failed: {response['message']}")

@tracer.capture_method
def handle_event_finished(item: dict) -> dict:
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
        logger.info("Event closed")
        return form_event('com.livemarket', 'EventClosed', update_info)
    elif 'Error' in response['__typename']:
        logger.exception("Failed to finish event")
        raise ValueError(
            f"finish_event failed: {response['message']}")

@tracer.capture_method
def handle_add_event(item: dict) -> dict:

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
        'state': item['detail']['state']

    }

    print('add_event_info', add_event_info)
    gql_input = {
        'input': add_event_info
    }

    try:
        response = gql_client.execute(gql(add_event), variable_values=gql_input)[
            'addEvent']

        print('response:', response)
        if response['__typename'] == 'Event':
            logger.info("Event closed")
            return form_event('com.livemarket', 'EventAdded', add_event_info)
        elif 'Error' in response['__typename']:
            logger.exception("Failed to add event")
            raise ValueError(
                f"add_event failed: {response['message']}")
    except Exception:
        logger.exception(Exception)
        raise Exception


def form_event(source, detailType, detail):
    return {
        'Source': source,
        'DetailType': detailType,
        'Detail': json.dumps(detail),
        'EventBusName': event_bus_name
    }

@tracer.capture_method
def record_handler(record: SQSRecord):
    # This function processes a record from SQS
    # Optionally return a dict which will be raised as a new event
    payload = record.body
    if payload:
        item = json.loads(payload)
        if item['source'] == 'com.trading':
            if item['detail-type'] == 'UpdatedOdds':
                return handle_updated_odds(item)
        if item['source'] == 'com.thirdparty':
            if item['detail-type'] == 'EventClosed':
                return handle_event_finished(item)
            elif item['detail-type'] == 'EventAdded':
                return handle_add_event(item)
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
