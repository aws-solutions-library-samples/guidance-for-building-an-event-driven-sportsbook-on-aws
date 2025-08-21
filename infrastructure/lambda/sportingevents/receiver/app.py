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
    """
    Main Lambda handler function that processes sporting events.
    
    Args:
        event: Lambda event containing sporting events data
        context: Lambda context
        
    Returns:
        Response with status code and message
    """
    try:
        betting_events = json.loads(event.get('body'))
        date_format = '%Y-%m-%dT%H:%M:%SZ'
        
        for betting_event in betting_events:
            try:
                send_new_event(betting_event, date_format)
            except Exception as e:
                logger.error(f"Error processing betting event: {str(e)}")
                return {
                    'statusCode': 400,
                    'body': 'Bad Request!'
                }
                
        return {
            'statusCode': 200,
            'body': 'Successfully inserted event!'
        }
    except Exception as e:
        logger.error(f"Error in lambda handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': 'Internal Server Error'
        }


def send_new_event(betting_event, date_format):
    """
    Process and send a new sporting event to EventBridge.
    
    Args:
        betting_event: The event data to process
        date_format: Format string for date/time fields
        
    Raises:
        Exception: If required fields are missing or processing fails
    """
    try:
        # Extract required fields
        event_id = betting_event['eventId']
        home_team = betting_event['homeTeam']
        away_team = betting_event['awayTeam']
        
        # Process timestamps
        start_time = datetime.fromtimestamp(betting_event['startTime']/1000.0).strftime(date_format)
        end_time = datetime.fromtimestamp(betting_event['endTime']/1000.0).strftime(date_format)
        updated_at = datetime.fromtimestamp(betting_event['updatedAt']/1000.0).strftime(date_format)
        
        # Extract other fields
        duration = betting_event['duration']
        event_status = betting_event['state']
        away_odds = betting_event['awayOdds']
        draw_odds = betting_event['drawOdds']
        home_odds = betting_event['homeOdds']
        
        # Validate required fields
        if None in (event_id, home_team, away_team, start_time, duration, event_status):
            raise Exception("Null values are not allowed in required fields")
        
        # Prepare event item
        item = {
            'eventId': event_id,
            'home': home_team,
            'away': away_team,
            'start': str(start_time),
            'updatedAt': str(updated_at),
            'end': str(end_time),
            'duration': str(duration),
            'homeOdds': home_odds,
            'eventStatus': event_status,
            'drawOdds': draw_odds,
            'awayOdds': away_odds
        }
        
        # Send event to EventBridge
        eventsClient.put_events(
            Entries=form_event('EventAdded', item)
        )
    except KeyError as e:
        logger.error(f"Missing required field in betting event: {str(e)}")
        raise Exception(f"Missing required field: {str(e)}")
    except Exception as e:
        logger.error(f"Error sending new event: {str(e)}")
        raise Exception(f"Failed to process event: {str(e)}")


def form_event(detail_type, detail):
    """
    Create a properly formatted event for EventBridge.
    
    Args:
        detail_type: The type of event
        detail: The event payload
        
    Returns:
        List containing formatted event for EventBridge
    """
    try:
        return [{
            'Source': 'com.thirdparty',
            'DetailType': detail_type,
            'Detail': json.dumps(detail),
            'EventBusName': event_bus_name
        }]
    except Exception as e:
        logger.error(f"Error forming event: {str(e)}")
        raise Exception(f"Failed to form event: {str(e)}")
