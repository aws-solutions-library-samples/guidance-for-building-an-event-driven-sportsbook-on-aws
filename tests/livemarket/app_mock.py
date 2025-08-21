"""
Mock implementation of the livemarket app for testing.
"""
import json
from unittest.mock import MagicMock

# Mock objects
logger = MagicMock()
tracer = MagicMock()
processor = MagicMock()
events = MagicMock()
session = MagicMock()
dynamodb = MagicMock()
table = MagicMock()
history_table = MagicMock()
gql_client = MagicMock()

# Mock decorator functions
def capture_lambda_handler(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def capture_method(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def inject_lambda_context(log_event=True):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Mock the tracer object's methods
tracer.capture_lambda_handler = capture_lambda_handler
tracer.capture_method = capture_method

# Mock the logger object's methods
logger.inject_lambda_context = inject_lambda_context

# Mock functions
def form_event(source, detailType, detail):
    return {
        'Source': source,
        'DetailType': detailType,
        'Detail': json.dumps(detail),
        'EventBusName': 'test-event-bus'
    }

def handle_updated_odds(item):
    update_info = {
        'eventId': item['detail']['eventId'],
        'homeOdds': item['detail']['homeOdds'],
        'awayOdds': item['detail']['awayOdds'],
        'drawOdds': item['detail']['drawOdds']
    }
    return form_event('com.livemarket', 'UpdatedOdds', update_info)

def handle_event_finished(item):
    update_info = {
        'eventId': item['detail']['eventId'],
        'eventStatus': 'finished',
        'outcome': item['detail']['outcome']
    }
    return form_event('com.livemarket', 'EventClosed', update_info)

def handle_market_suspended(item):
    update_info = {
        'eventId': item['detail']['eventId'],
        'market': item['detail']['market'],
    }
    return form_event('com.livemarket', 'MarketSuspended', update_info)

def handle_market_unsuspended(item):
    update_info = {
        'eventId': item['detail']['eventId'],
        'market': item['detail']['market'],
    }
    return form_event('com.livemarket', 'MarketUnsuspended', update_info)

def handle_add_event(item):
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
    return form_event('com.livemarket', 'EventAdded', add_event_info)

def record_handler(record):
    payload = record.body
    if payload:
        item = json.loads(payload)
        if item['source'] == 'com.trading':
            if item['detail-type'] == 'UpdatedOdds':
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
    logger.warning({"message": "Unknown record type", "record": item})
    return None

def lambda_handler(event, context):
    batch = event["Records"]
    with processor(records=batch, handler=record_handler):
        processed_messages = processor.process()
        logger.debug(processed_messages)

    output_events = [x[1]
                     for x in processed_messages if x[0] == "success" and x[1] is not None]
    if output_events:
        events.put_events(Entries=output_events)

    return processor.response()

# Mock resolver functions
def get_events(startKey=""):
    result = {
        'items': [
            {
                "eventId": "test-event-id-1",
                "homeTeam": "Home Team 1",
                "awayTeam": "Away Team 1",
                "startTime": "2025-04-01T15:00:00Z",
                "homeOdds": "2/1",
                "awayOdds": "3/1",
                "drawOdds": "5/2",
                "eventStatus": "running"
            }
        ]
    }
    if startKey:
        result['nextToken'] = 'next-token'
    return event_list_response(result)

def event_list_response(result):
    result['__typename'] = 'EventList'
    return result

def get_event(eventId):
    if eventId == 'not-found':
        return {
            '__typename': 'InputError',
            'message': 'Event does not exist'
        }
    return {
        '__typename': 'Event',
        'eventId': eventId,
        'homeTeam': 'Home Team',
        'awayTeam': 'Away Team',
        'startTime': '2025-04-01T15:00:00Z',
        'homeOdds': '2/1',
        'awayOdds': '3/1',
        'drawOdds': '5/2',
        'eventStatus': 'running'
    }

def update_event_odds(input_data):
    if input_data['eventId'] == 'not-found':
        return {
            '__typename': 'InputError',
            'message': 'Event does not exist'
        }
    return {
        '__typename': 'Event',
        'eventId': input_data['eventId'],
        'homeOdds': input_data['homeOdds'],
        'awayOdds': input_data['awayOdds'],
        'drawOdds': input_data['drawOdds'],
        'eventStatus': 'running'
    }

def suspend_market(input_data):
    return {
        '__typename': 'Event',
        'eventId': input_data['eventId'],
        'marketstatus': [
            {
                'name': input_data['market'],
                'status': 'Suspended'
            }
        ]
    }

def unsuspend_market(input_data):
    return {
        '__typename': 'Event',
        'eventId': input_data['eventId'],
        'marketstatus': [
            {
                'name': input_data['market'],
                'status': 'Active'
            }
        ]
    }

def finish_event(input_data):
    if input_data['eventId'] == 'not-found':
        return {
            '__typename': 'InputError',
            'message': 'Event does not exist'
        }
    return {
        '__typename': 'Event',
        'eventId': input_data['eventId'],
        'eventStatus': input_data['eventStatus'],
        'outcome': input_data['outcome']
    }

def add_event(input_data):
    return {
        '__typename': 'Event',
        **input_data
    }

# Mock the get_client function
def get_client(region, url):
    return gql_client
