from os import getenv
import json
import boto3

from aws_lambda_powertools.utilities.data_classes import AppSyncResolverEvent
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import AppSyncResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

tracer = Tracer()
logger = Logger()

session = boto3.Session()
events = session.client('events')
event_bus_name = getenv('EVENT_BUS')

@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    logger.info(json.dumps(event))

    detail = { 'userId': event['userName'] }

    events.put_events(
        Entries=[
            {
                'Source': 'com.auth',
                'DetailType': 'UserSignedUp',
                'Detail': json.dumps(detail),
                'EventBusName': event_bus_name
            },
        ]
    )
    return event
