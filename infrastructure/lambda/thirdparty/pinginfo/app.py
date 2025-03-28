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
    logger.debug(app.current_event)
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

        #start_time = time.time()
        #ec2_client.describe_regions()  # Ping call to Tokyo AWS location
        #latency = time.time() - start_time
        #item = {'items':[{'pingLocation': 'Tokyo', 'pingLatency': int(latency * 1000)}]}  # Convert latency to milliseconds

        #return getpinginfo_response(item)
    except KeyError:
        logger.error(f'Failed to get pinginfo ')
        return getpinginfo_error('NotFoundError', 'No ping info exists')
    except Exception as e:
        logger.error({'UnknownError': e})
        return getpinginfo_error('Unknown error', 'An unknown error occured.')

def getpinginfo_error(errorType: str, error_msg: str) -> dict:
    return {'__typename': errorType, 'message': error_msg}

def getpinginfo_response(data: dict) -> dict:
    return {**{'__typename': 'PingInfo'}, **data}

@logger.inject_lambda_context(correlation_id_path=correlation_paths.APPSYNC_RESOLVER, log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    logger.info(event)
    return app.resolve(event, context)