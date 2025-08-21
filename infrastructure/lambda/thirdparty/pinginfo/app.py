import boto3
import json
import time
from botocore.client import BaseClient

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import AppSyncResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

tracer = Tracer()
logger = Logger()
app = AppSyncResolver()

session = boto3.Session()
regions = ['us-east-1', 'us-west-2', 'eu-west-2', 'ap-southeast-1', 'ap-northeast-1'] 

clients = {region: boto3.client('ec2', region_name=region) for region in regions}

@app.resolver(type_name="Query", field_name="getPingInfo")
@tracer.capture_method
def get_pinginfo() -> dict:
    """
    Get ping latency information from various AWS regions.
    
    Returns:
        Response with ping latency data or error
    """
    try:
        latency_data = []
        for region, client in clients.items():
            start = time.time()
            client.describe_regions()
            latency = time.time() - start
            latency_data.append({
                'pingLocation': region, 
                'pingLatency': int(latency * 1000)
            })
        return getpinginfo_response({'items': latency_data})
    except KeyError as e:
        logger.error(f"Failed to get ping info: {str(e)}")
        return getpinginfo_error('NotFoundError', 'No ping info exists')
    except Exception as e:
        logger.error(f"Unknown error in get_pinginfo: {str(e)}")
        return getpinginfo_error('UnknownError', 'An unknown error occurred.')


def getpinginfo_error(error_type: str, error_msg: str) -> dict:
    """
    Create an error response.
    
    Args:
        error_type: Type of error
        error_msg: Error message
        
    Returns:
        Formatted error response
    """
    return {'__typename': error_type, 'message': error_msg}


def getpinginfo_response(data: dict) -> dict:
    """
    Create a success response.
    
    Args:
        data: Response data
        
    Returns:
        Formatted success response
    """
    return {**{'__typename': 'PingInfo'}, **data}


@logger.inject_lambda_context(correlation_id_path=correlation_paths.APPSYNC_RESOLVER, log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """
    Main Lambda handler function.
    
    Args:
        event: Lambda event
        context: Lambda context
        
    Returns:
        AppSync resolver response
    """
    try:
        return app.resolve(event, context)
    except Exception as e:
        logger.error(f"Error in lambda handler: {str(e)}")
        return {"errors": [{"message": "Internal server error"}]}
