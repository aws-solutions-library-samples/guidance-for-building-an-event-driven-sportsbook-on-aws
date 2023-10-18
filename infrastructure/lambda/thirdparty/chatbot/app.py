from datetime import datetime
from decimal import Decimal
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
app = AppSyncResolver()

session = boto3.Session()
aws_region = 'us-east-1'
bedrock_client = session.client(service_name='bedrock-runtime', region_name=aws_region, endpoint_url='https://bedrock-runtime.'+aws_region+'.amazonaws.com')

@app.resolver(type_name="Mutation", field_name="sendChatbotMessage")
@tracer.capture_method
def send_chatbot_message(input: dict) -> dict:
    logger.debug(app.current_event)
    print("Body here:")
    print("\n\nHuman: "+input["prompt"].strip()+"\n\nAssistant:")
    try:
        response = bedrock_client.invoke_model(
            body=json.dumps({
                "prompt": "\n\nHuman: "+input["prompt"].strip()+"\n\nAssistant:",
                "max_tokens_to_sample": 300,
                "temperature": 0.5,
                "top_k": 250,
                "top_p": 1,
                "stop_sequences": [
                    "\\n\\nHuman:"
                ],
                "anthropic_version": "bedrock-2023-05-31"
            }),
            modelId="anthropic.claude-v2", 
            accept="*/*",
            contentType="application/json"
        )
        response_body = json.loads(response.get('body').read())
        logger.debug("Response body: ")
        logger.debug(response_body)
        return chatbot_response(response_body)
    except Exception as e:
        logger.info({'UnknownError': e})
        return chatbot_error('UnknownError', 'An unknown error occured.')

def chatbot_response(data: dict) -> dict:
    return {**{'__typename': 'ChatbotResponse'}, **data}
    
def chatbot_error(errorType: str, error_msg: str) -> dict:
    return {'__typename': errorType, 'message': error_msg}
    
@logger.inject_lambda_context(correlation_id_path=correlation_paths.APPSYNC_RESOLVER, log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)