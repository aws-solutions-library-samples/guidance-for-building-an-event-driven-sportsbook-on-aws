from os import getenv
import random
import json
import boto3

from fractions import Fraction
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

tracer = Tracer()
logger = Logger()

event_bus_name = getenv('EVENT_BUS')
session = boto3.Session()
eventsClient = session.client('events')

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
    logger.info(event)
    events = get_events()
    eventsClient.put_events(
        Entries=events
    )


@tracer.capture_method
def get_events():
    return [form_event('UpdatedOdds', e) for e in get_new_odds()]


@tracer.capture_method
def get_new_odds():
    # this method is a simulation of a real life scenario where you poll a third party api for new odds
    # in our case, we simulate some known events and emit new odds with some random chance
    results = []
    sample = random.sample(KNOWN_EVENTS, 3)
    for event in sample:
        results.append({
            'eventId': event['id'],
            'homeOdds': random_odds(),
            'awayOdds': random_odds(),
            'drawOdds': random_odds(),
        })

    return results


def random_odds():
    q = Fraction(random.randint(1, 9), random.randint(2, 9))

    return f'{q.numerator}/{q.denominator}'


def form_event(detailType, detail):
    return {
        'Source': 'com.thirdparty',
        'DetailType': detailType,
        'Detail': json.dumps(detail),
        'EventBusName': event_bus_name
    }
