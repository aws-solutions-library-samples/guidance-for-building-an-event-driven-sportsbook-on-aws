from os import getenv
import boto3
import json

from crhelper import CfnResource

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes.appsync import scalar_types_utils

logger = Logger()

helper = CfnResource(json_logging=False, log_level='DEBUG',
                     boto_level='CRITICAL')

try:
    # Init clients and env vars here
    table_name = getenv('DB_TABLE')
    session = boto3.Session()
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table(table_name)
except Exception as e:
    helper.init_failure(e)


@helper.create
def create(event, context):
    with open('data.json', 'r') as f:
        events = json.load(f)

    logger.debug(events)
    now = scalar_types_utils.aws_datetime()
    with table.batch_writer() as batch:
        for event_item in events:
            event_item['updatedAt'] = now
            event_item['eventStatus'] = 'running'
            batch.put_item(Item=event_item)

    logger.debug('Event seed complete')

    return True



def lambda_handler(event, context):
    # This function is triggered by a CloudFormation custom resource.
    # It seeds a dynamodb table with some event data
    logger.info(event)
    helper(event, context)
