from os import getenv
import json
import boto3
# from gql_utils import get_client
# from mutations import create_wallet
# from gql import gql

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

tracer = Tracer()
logger = Logger()

# appsync_url = getenv("APPSYNC_URL")
region = getenv("REGION")
event_bus_name = getenv('EVENT_BUS')
# gql_client = get_client(region, appsync_url)
session = boto3.Session()
events = session.client('events')


@tracer.capture_method
def handle_auth_event(event: dict, context: LambdaContext) -> dict:
    if event['detail-type'] == 'UserSignedUp':
        initialise_wallet(event)


@tracer.capture_method
def initialise_wallet(event: dict) -> None:
    user_info = {
        'userId': event['detail']['userId']
    }
    gql_input = {
        'input': user_info
    }
    response = gql_client.execute(gql(create_wallet), variable_values=gql_input)[
        'createWallet']

    if response['__typename'] == 'Wallet':
        raise_wallet_event('WalletCreated', user_info)
        logger.info("Wallet created")
    elif 'Error' in response['__typename']:
        raise_wallet_event('WalletCreateFailed', user_info)
        logger.exception("Failed to create wallet for new user")
        raise Exception(
            f"createWallet failed: {response['message']}")


@tracer.capture_method
def raise_wallet_event(detailType: str, detail: str) -> None:
    events.put_events(
        Entries=[
            {
                'Source': 'com.wallet',
                'DetailType': detailType,
                'Detail': json.dumps(detail),
                'EventBusName': event_bus_name
            },
        ]
    )


@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    logger.info(json.dumps(event))

    source = event.get('source')
    if source is None:
        return

    if source == 'com.auth':
        handle_auth_event(event, context)
