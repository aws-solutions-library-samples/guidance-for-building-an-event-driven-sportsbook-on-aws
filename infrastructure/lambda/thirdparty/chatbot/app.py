import json
import boto3
import json
from os import getenv
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain import PromptTemplate
from langchain.llms.bedrock import Bedrock
from langchain.chains import ConversationalRetrievalChain
from langchain.llms.bedrock import Bedrock
import re
from langchain.retrievers import AmazonKendraRetriever
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import AppSyncResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

from langchain_community.chat_models import BedrockChat
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser

tracer = Tracer()
logger = Logger()
app = AppSyncResolver()
session = boto3.Session()
dynamodb = session.resource('dynamodb')
table_name = getenv('DB_TABLE')
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

prompt_template = "Use the context to answer the question at the end. If you don't know the answer from the context, do not answer from your knowledge and be precise. Dont fake the answer."

bedrock_client = session.client(service_name='bedrock-runtime', region_name=aws_region, endpoint_url='https://bedrock-runtime.'+aws_region+'.amazonaws.com')


@app.resolver(type_name="Mutation", field_name="sendChatbotMessage")
@tracer.capture_method
def send_chatbot_message(input: dict) -> dict:
    try: 
        kendra_client = session.client(service_name='kendra', region_name=aws_region)
        kendra_retriever = AmazonKendraRetriever(client=kendra_client, index_id=index_id)
        # Get the input from the request payload
        #print the langchain version
        
        bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1",
    )

    # Claude 3 Sonnet model ID
        model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        chat = BedrockChat(
            client=bedrock_runtime,
            model_id=model_id,
            model_kwargs={"temperature": 0}
        )
        parser = JsonOutputParser()

        system_message = f"""
            You're an casino support agent. 
            User gives you a question regarding current state of a casino or informational question. 
            Your job is to answer user's questions and give recommendations based on the context that you have available. 
            Reject any irrelevant questions with max 1 sentence and stop responding. 
            Never provide recommendations instead of what's asked and use only context.
        """
        currentEventsData = "Currently running events" + json.dumps(get_events())
        
        payload = input["prompt"].strip()+system_message+currentEventsData
        #replace all double quotes with single quotes in payload
        payload = payload.replace('"', "'")

        human_q = {
            "type": "text",
            "text": f"{payload}"
        }
        formatting_system_message = """
        Format the answer using the JSON format. 

        Example:

        {
            "completion": {
                    "Answer"
            }
        }    
        """
        
        messages = [
            #SystemMessage(content=),
            HumanMessage(content=[human_q]),
        ]

        prompt_config = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": payload},
                    ],
                }
            ],
        }
        body = json.dumps(prompt_config)

        #body = json.dumps(
        #    {
        #        "anthropic_version": "bedrock-2023-05-31",
        #        "max_tokens": 2000,
        #        "messages": messages
        #    }
        #)

        accept = 'application/json'
        contentType = 'application/json'
        response = bedrock_runtime.invoke_model(body=body, modelId=model_id, accept=accept, contentType=contentType)
        response_body = json.loads(response.get('body').read())
        answer = response_body["content"][0]["text"]
        #aimessage = chat.pipe(parser).invoke(messages)
        response_body = '''{
                "completion": "'''+answer+'''"
            }'''
            
        #print("prediction:",prediction)
        print("response_body:",response_body)
            
            # Return the prediction as a JSON response
        return chatbot_response(json.loads(response_body, strict=False))


        return chatbot_response(json.loads(response, strict=False))


        

        # cl_llm = Bedrock(model_id="anthropic.claude-v1", client=bedrock_client, model_kwargs={"max_tokens_to_sample": 500}) # change model_id here
        cl_llm = Bedrock(model_id="anthropic.claude-v2", client=bedrock_client, model_kwargs={"max_tokens_to_sample": 500}) # change model_id here
        memory_chain = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

       


        qa = ConversationalRetrievalChain.from_llm(
            llm=cl_llm,
            retriever=kendra_retriever,
            memory=memory_chain,
            #get_chat_history='No history so far',
            verbose = True,
            condense_question_prompt=CONDENSE_QUESTION_PROMPT1,
            chain_type='stuff',
        )
        
        currentEventsData = get_events()
        # the LLMChain prompt to get the answer. the ConversationalRetrievalChange does not expose this parameter in the constructor
        qa.combine_docs_chain.llm_chain.prompt = PromptTemplate.from_template("""

        Currently running events: 
        """ + currentEventsData + """                                                        
                                                                              
        {context}

        Human: %s
        <q>{question}</q>


        Assistant:""" % (
            prompt_template
        ))
        print("Payload:")
        print(payload)
        # Get the input text from the payload
        
        print("tag4")
        question = payload
        print("tag5")
        print("question:",question)
        if input_validation(question):
            #question = payload['question']

            #trychat = chathistory1
            trychat = []
            chat_history = trychat 
            print("chat_history:",chat_history)
            
            # Append the new question to the chat history
            trychat.append((question, ''))
            # Generate the prediction from the Conversational Retrieval Chain
            print(CONDENSE_QUESTION_PROMPT1.template)
            prediction = qa.run(question=question)
            response_body = '''{
                "completion": "'''+prediction+'''"
            }'''
            
            print("prediction:",prediction)
            print("response_body:",response_body)
            
            # Return the prediction as a JSON response
            return chatbot_response(json.loads(response_body, strict=False))
            #return response_body
    
    except Exception as e:
        logger.info({'UnknownError': e})
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
        if response.get('LastEvaluatedKey'):
            result['nextToken'] = response['LastEvaluatedKey']['eventId']

        resultstring = ''
        # parse result json to string
        return json.dumps(result)

        return result
        for item in result['items']:
            resultstring += " ".join([' home team ', item['home'], ' vs ', ' guest team ', item['away'], ' with odds ', 'away win ', item['awayOdds'], ' home win ', item['homeOdds'], ' draw ', item['drawOdds'], ';'])
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
    pattern = r'^[a-zA-Z0-9\s\-!@#$%^&*(),.?":{}|<>]{1,1000}$'

    if re.match(pattern, input_str):
        return True
    else:
        return False
    
@logger.inject_lambda_context(correlation_id_path=correlation_paths.APPSYNC_RESOLVER, log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
