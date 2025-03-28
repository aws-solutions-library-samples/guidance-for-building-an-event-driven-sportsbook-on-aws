import json
import boto3
import json
from os import getenv
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain import PromptTemplate
from langchain.llms.bedrock import Bedrock
from langchain.chains import ConversationalRetrievalChain
import re
from langchain.retrievers import AmazonKendraRetriever
from langchain.memory.chat_message_histories import DynamoDBChatMessageHistory
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import AppSyncResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

from langchain_community.chat_models import BedrockChat
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser

tracer = Tracer()
logger = Logger()
app = AppSyncResolver()
session = boto3.Session()
dynamodb = session.resource('dynamodb')
table_name = getenv('DB_TABLE')
table_name_history = getenv('DB_TABLE_CHATHISTORY')

table = dynamodb.Table(table_name)

session = boto3.Session()
aws_region = 'us-west-2'
index_id = '2014f5ad-125f-47e3-80a2-88d3805575d0'
_template_new = """
Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.
Chat History:
{chat_history}
Follow Up Input: {question}

"""

CONDENSE_QUESTION_PROMPT1 = PromptTemplate.from_template(_template_new)

prompt_template = f"""
You're an casino support agent. 
I ask you a question regarding current state of a casino or informational question. 
Your job is to answer my question and give recommendations based on the context that you have available. 
Reject any irrelevant questions with max 1 sentence and stop responding. 
Never provide recommendations instead of what's asked and use only context.
"""

bedrock_client = session.client(service_name='bedrock-runtime', region_name=aws_region, endpoint_url='https://bedrock-runtime.'+aws_region+'.amazonaws.com')

@app.resolver(type_name="Mutation", field_name="sendChatbotMessage")
@tracer.capture_method
def send_chatbot_message(input: dict) -> dict:
    conversation_id = input["sessionId"]
    
    try: 
        kendra_client = session.client(service_name='kendra', region_name=aws_region)
        kendra_retriever = AmazonKendraRetriever(client=kendra_client, index_id=index_id)
        # Get the input from the request payload
        #print the langchain version
        
        currentEventsData = "Currently running events " + get_events()[:800]
        
        payload = input["prompt"].strip()+currentEventsData
        #replace all double quotes with single quotes in payload
        payload = payload.replace('"', "'")

        cl_llm = Bedrock(model_id="anthropic.claude-v2", client=bedrock_client, model_kwargs={"max_tokens_to_sample": 500}) # change model_id here

        message_history = DynamoDBChatMessageHistory(
            table_name=table_name_history, session_id=conversation_id
        )
        
        logger.debug("session id", conversation_id)
    
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            chat_memory=message_history,
            input_key="question",
            output_key="answer",
            return_messages=True,
        )

        qa = ConversationalRetrievalChain.from_llm(
            llm=cl_llm,
            retriever=kendra_retriever,
            memory=memory,
            verbose = True,
            condense_question_prompt=CONDENSE_QUESTION_PROMPT1,
            chain_type='stuff',
        )
        
        currentEventsData = "Currently running events" + get_events()[:800]
        # the LLMChain prompt to get the answer. the ConversationalRetrievalChange does not expose this parameter in the constructor
        qa.combine_docs_chain.llm_chain.prompt = PromptTemplate.from_template(
            """
        Website context: 
        <system>
        Currently running events: 
        """ + currentEventsData + """                                                        
        </system>               

        {context}

        Human: %s
        <q>{question}</q>

        Assistant:""" % (
            prompt_template
        ))

        question = payload
        if input_validation(question):
            trychat = []
            
            # Append the new question to the chat history
            trychat.append((question, ''))
            # Generate the prediction from the Conversational Retrieval Chain
            
            prediction = qa.run(question=question)
            response_body = '''{
                "completion": "'''+prediction+'''"
            }'''

            # Return the prediction as a JSON response
            return chatbot_response(json.loads(response_body, strict=False))
    
    except Exception as e:
        logger.debug({'UnknownError': e})
        return chatbot_error('UnknownError', 'An unknown error occured.')

def get_events() -> dict:
    try:
        args = {
            'FilterExpression': Key('eventStatus').eq('running')
        }

        response = table.scan(**args)
        result = {
            'items': response.get('Items', [])
        }
        
        logger.debug({'result': result})
     
        if response.get('LastEvaluatedKey'):
            result['nextToken'] = response['LastEvaluatedKey']['eventId']

        resultstring = ''

        for item in result['items']:
            resultstring += " ".join([' event id ', item['eventId'], ', home team name \'', item['home'], '\' vs ', ' guest team name \'', item['away'], '\' with odds ', 'away win \'', item['awayOdds'], '\' home win \'', item['homeOdds'], '\' draw \'', item['drawOdds'], '\';'])
        
        return resultstring

    except ClientError as e:
        logger.exception({'ClientError': e})
        return e
    except Exception as e:
        logger.exception({'UnknownError': e})
        return e

def chatbot_response(data: dict) -> dict:
    return {**{'__typename': 'ChatbotResponse'}, **data}
    
def chatbot_error(errorType: str, error_msg: str) -> dict:
    return {'__typename': errorType, 'message': error_msg}
    
def input_validation(input_str):
    pattern = r'^[a-zA-Z0-9\s\-!@#$%^&*(),\'/;.?":{}|<>]{1,10000}$'

    if re.match(pattern, input_str):
        return True
    else:
        return False
    
@logger.inject_lambda_context(correlation_id_path=correlation_paths.APPSYNC_RESOLVER, log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    logger.info(event)
    return app.resolve(event, context)