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
    """
    Seed the DynamoDB table with initial event data.
    
    Args:
        event: CloudFormation custom resource event
        context: Lambda context
        
    Returns:
        True if successful
    """
    try:
        with open('data.json', 'r') as f:
            events = json.load(f)

        now = scalar_types_utils.aws_datetime()
        with table.batch_writer() as batch:
            for event_item in events:
                event_item['updatedAt'] = now
                event_item['eventStatus'] = 'running'
                batch.put_item(Item=event_item)

        logger.info('Event seed complete')
        return True
    except Exception as e:
        logger.error(f"Error seeding events: {str(e)}")
        raise


def lambda_handler(event, context):
    """
    Main Lambda handler function triggered by CloudFormation custom resource.
    
    Args:
        event: CloudFormation custom resource event
        context: Lambda context
    """
    try:
        helper(event, context)
    except Exception as e:
        logger.error(f"Error in lambda handler: {str(e)}")
        raise
