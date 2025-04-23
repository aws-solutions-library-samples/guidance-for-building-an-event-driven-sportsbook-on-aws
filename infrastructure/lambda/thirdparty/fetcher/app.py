from os import getenv
import random
import json
import boto3

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

# Initialize AWS Lambda Powertools for tracing and logging
tracer = Tracer()
logger = Logger()

# Get EventBridge bus name from environment variables
event_bus_name = getenv('EVENT_BUS')
# Initialize AWS session and EventBridge client
session = boto3.Session()
eventsClient = session.client('events')

# List of predefined sporting events with unique IDs
# In a production environment, these would likely come from a database or external API
KNOWN_EVENTS = [
    {'id': 'e46436a8-a916-4143-a05c-99d120eabfdb'},
    {'id': '9a3d7a1f-4cf8-4db8-a13d-421ee9c35703'},
    {'id': '0f66c58b-81eb-42c8-a058-62e54bba6493'},
    {'id': 'a613af9f-c76d-4384-ac43-96fcae0db562'},
    {'id': '53837eee-4ba4-49f2-87be-76969b8ee68d'},
    {'id': 'ec1fec4d-2cdb-4c54-bb43-a7f89f73107d'},
    {'id': '250a3a85-324f-4f4b-ae8d-f0419e4a20a6'},
    {'id': 'a0ed26b1-626e-4e30-8111-cc2b8e0293d7'},
    {'id': '8badd072-b6e2-41fe-9c55-6d719b4af546'},
    {'id': 'ceac8915-fa87-4e08-93a7-e17c9a509fae'}
]


@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """
    Main Lambda handler function that processes events and publishes updated odds.
    
    This function is triggered periodically to simulate fetching updated odds from
    a third-party provider and publishing them to EventBridge for downstream processing.
    
    Args:
        event: Lambda event object (typically from CloudWatch scheduled event)
        context: Lambda context object with runtime information
        
    Returns:
        Response dictionary with status code and message
    """
    try:
        # Get formatted events with updated odds
        events = get_events()
        # Publish events to EventBridge
        response = eventsClient.put_events(Entries=events)
        return {"statusCode": 200, "body": json.dumps({"message": "Events published successfully"})}
    except Exception as e:
        logger.error(f"Error in lambda handler: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"message": "Error publishing events"})}


@tracer.capture_method
def get_events():
    """
    Get formatted events for EventBridge.
    
    Transforms the raw odds data into properly formatted EventBridge events
    with the correct source, detail type, and event bus.
    
    Returns:
        List of formatted events ready for EventBridge
    """
    try:
        # For each set of new odds, create a properly formatted EventBridge event
        return [form_event('UpdatedOdds', e) for e in get_new_odds()]
    except Exception as e:
        logger.error(f"Error getting events: {str(e)}")
        return []


@tracer.capture_method
def get_new_odds():
    """
    Simulate polling a third-party API for new odds.
    
    This method simulates a real-life scenario where you poll a third-party API
    for new odds. It:
    1. Selects a random subset of known events
    2. Generates random odds for each event
    3. Ensures the odds are unique and follow betting market rules
    4. Applies a house edge of approximately 10% (factor of 1.1)
    
    The generated odds represent the decimal odds for home win, away win, and draw,
    with the sum of implied probabilities being approximately 1.1 (representing a 10% house edge).
    
    Returns:
        List of events with updated odds
    """
    try:
        results = []
        # Randomly select 3 events to update
        sample = random.sample(KNOWN_EVENTS, 3)
        for event in sample:
            count = 0
            odds = []
            
            # Generate three random values between 0.1 and 1
            # These represent the relative probabilities before normalization
            r1 = random.uniform(0.1, 1)
            r2 = random.uniform(0.1, 1)
            r3 = random.uniform(0.1, 1)
            
            # Calculate the sum for normalization
            sum = r1 + r2 + r3

            # Convert to odds with a house edge of 10% (factor of 1.1)
            # and round to 1 decimal place
            odds.append(round(((r1 * 1.1) /sum), 1))
            odds.append(round(((r2 * 1.1) /sum), 1))
            odds.append(round(((r3 * 1.1) /sum), 1))

            # Ensure all odds are unique by regenerating if duplicates exist
            # This loop will try up to 5 times to generate unique odds
            while (odds[0] == odds[1] or odds[0] == odds[2] or odds[1] == odds[2]):
                r1 = random.uniform(0.1, 1)
                r2 = random.uniform(0.1, 1)
                r3 = random.uniform(0.1, 1)
                
                sum = r1 + r2 + r3

                odds[0] = round(((r1 * 1.1) /sum), 1)
                odds[1] = round(((r2 * 1.1) /sum), 1)
                odds[2] = round(((r3 * 1.1) /sum), 1)
                
                # Break after 5 attempts to avoid potential infinite loop
                if count > 5:
                    break
                count += 1

            # Sort odds in ascending order
            odds.sort()
            
            # Assign the highest odds to home team (favoring home team slightly)
            home_odds = 1/odds[2]
            
            # Randomly choose between the two lower odds values for away team
            temp_odds = random.choice([odds[0], odds[1]])
            away_odds = 1/temp_odds

            # Assign the remaining odds value to draw
            if temp_odds == odds[0]:
                draw_odds = 1/odds[1]
            else:
                draw_odds = 1/odds[0]

            # Calculate total implied probability (should be ~1.1 with house edge)
            total_odds = odds[0] + odds[1] + odds[2]
            logger.info(f"Total probability with house edge: {total_odds}, "
                        f"home_odds: {home_odds}, away_odds: {away_odds} and draw_odds: {draw_odds}")
            
            # Add the event with its new odds to the results
            results.append({
                'eventId': event['id'],
                'homeOdds': str(home_odds),
                'awayOdds': str(away_odds),
                'drawOdds': str(draw_odds),
            })
        return results
    except Exception as e:
        logger.error(f"Error generating new odds: {str(e)}")
        return []


def form_event(detail_type, detail):
    """
    Create a properly formatted event for EventBridge.
    
    Formats the event according to EventBridge requirements with:
    - Source: Identifying the event origin (third-party provider)
    - DetailType: Categorizing the event (UpdatedOdds)
    - Detail: The actual payload with event data
    - EventBusName: The target event bus
    
    Args:
        detail_type: The type of event (e.g., 'UpdatedOdds')
        detail: The event payload containing the odds data
        
    Returns:
        Formatted event ready for EventBridge
    """
    try:
        return {
            'Source': 'com.thirdparty',
            'DetailType': detail_type,
            'Detail': json.dumps(detail),
            'EventBusName': event_bus_name
        }
    except Exception as e:
        logger.error(f"Error forming event: {str(e)}")
        return None
