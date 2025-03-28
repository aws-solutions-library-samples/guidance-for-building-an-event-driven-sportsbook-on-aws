from os import getenv
import boto3
import json

from crhelper import CfnResource
from aws_lambda_powertools import Logger
from datetime import datetime

logger = Logger()

helper = CfnResource(json_logging=False, log_level='DEBUG',
                     boto_level='CRITICAL')

try:
    event_bus_name = getenv('EVENT_BUS')
    session = boto3.Session()
    eventsClient = session.client('events')
except Exception as e:
    helper.init_failure(e)

def lambda_handler(event, context):
    logger.info(event)
    betting_events = json.loads(event.get('body'))
    date_format = '%Y-%m-%dT%H:%M:%SZ'
    for betting_event in betting_events:
        try:
            send_new_event(betting_event, date_format)
        except:
            return {
                'statusCode': 400,
                'body': 'Bad Request!'
            }
    return {
        'statusCode': 200,
        'body': 'Successfully inserted event!'
    }


def send_new_event(betting_event, date_format):
    try:
        event_id = betting_event['eventId']
        home_team = betting_event['homeTeam']
        away_team = betting_event['awayTeam']

        start_time = datetime.fromtimestamp(betting_event['startTime']/1000.0).strftime(date_format)
        end_time = datetime.fromtimestamp(betting_event['endTime']/1000.0).strftime(date_format)
        updated_at = datetime.fromtimestamp(betting_event['updatedAt']/1000.0).strftime(date_format)
        duration = betting_event['duration']
        eventStatus = betting_event['state']
        away_odds = betting_event['awayOdds']
        draw_odds = betting_event['drawOdds']
        home_odds = betting_event['homeOdds']
        if None in (event_id, home_team, away_team, start_time, duration, eventStatus):
            raise Exception("Null values are not allowed")
        logger.debug(event_id)
        item = {
            'eventId': event_id,
            'home': home_team,
            'away': away_team,
            'start': str(start_time),
            'updatedAt': str(updated_at),
            'end': str(end_time),
            'duration': str(duration),
            'homeOdds': home_odds,
            'eventStatus': eventStatus,
            'drawOdds': draw_odds,
            'awayOdds': away_odds
        }
        logger.debug(item)
        eventsClient.put_events(
            Entries=form_event('EventAdded', item)
        )
        logger.debug("Event sent!")
    except Exception:
        logger.exception(Exception)
        raise Exception


def form_event(detailType, detail):
    return [{
        'Source': 'com.thirdparty',
        'DetailType': detailType,
        'Detail': json.dumps(detail),
        'EventBusName': event_bus_name
    }]