import os
from requests_aws4auth import AWS4Auth
from gql import gql
from gql.client import Client
from gql.transport.requests import RequestsHTTPTransport
from boto3 import Session as AWSSession

def get_client(region, gql_endpoint):
    aws = AWSSession(aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                     aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                     aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
                     region_name=region)
    credentials = aws.get_credentials().get_frozen_credentials()
    auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        aws.region_name,
        'appsync',
        session_token=credentials.token,
    )
    transport = RequestsHTTPTransport(
        url=gql_endpoint,
        headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
        auth=auth
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)
    return client
