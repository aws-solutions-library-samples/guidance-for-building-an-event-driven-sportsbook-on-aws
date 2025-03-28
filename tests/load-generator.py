import time
import random
import requests
from requests_aws4auth import AWS4Auth
from typing import Optional
import boto3

# Configure AWS credentials
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_SESSION_TOKEN = 'IQoJb3JpZ2luX2VjEC0aDGV1LWNlbnRyYWwtMSJHMEUCIBdjy2pU2B9mbKqGD6rMA9B3LAAdh9yrDrnHaoYBwzD7AiEAvedfQD3pL6zrRsrNjtpI6/BhvCYTteQSsYy/vovi1Okq6wEIRhADGgw5NjcwNTczMTIxNjEiDIqoVc7l+QnGdx+wUCrIAaHu57ZZKxAy/7dzwp2/dejQhYAAnp42agyyCUhMhHISjunNG3y+fahmySKPgTwh/coiaYaej9ecoa6AJE+L9XTEaGa8R0X0NzqIt9DJEAQR92cPDT4FPDO2rFk5FNndqxTNFXOP1dKixgg+J99oNYwkEtRODqGxwn4tZSb99whu/bo5cYrsLc3te8Zs0N22IuT4jOI+aLH9ixkrw/veeOkv0ws7wgnpz9dnvLPVvFzotZijtWseV5ffPdk4pA9SxJZbd3mkYa0tMKv/9a8GOpgByRQkLXs4WZnLtsqnIUYY7muG2hCKGx1yauBI0A6z+DYF5ZUPspEdvbVwB9w5uRpQIt/XsSStsALV8oVkAT0Zb3wgshioTkb61C1ggPaurDgdMHcNT7iBAsNfnvkaQpgQPG2VMpbtHa9Q73/mZzzzL1fCfxpa8b5tFSb6oVIo1wRIMth9HJr5oHO3549vQbTtY5N6kUXVu/o='  # Required for temporary credentials

# GraphQL endpoint
GRAPHQL_ENDPOINT = 'https://65ends773vem3ca3gah35nhqlq.appsync-api.eu-central-1.amazonaws.com/graphql'

# GraphQL mutation for creating bets
CREATE_BETS_MUTATION = """
mutation CreateBets($input: CreateBetsInput!) {
  createBets(input: $input) {
    __typename
    ... on BetList {
      items {
        betId
        event {
          eventId
        }
        outcome
        odds
        amount
        placedAt
        userId
        betStatus
      }
      nextToken
    }
    ... on Error {
      message
    }
  }
}
"""

# Function to generate random bet requests
def generate_bet_requests(num_bets: int) -> list:
    bet_requests = []
    for _ in range(num_bets):
        event_id = 'event_id'  # Replace with a valid event ID
        outcome = random.choice(['homeWin', 'awayWin', 'draw'])
        odds = str(random.uniform(1.0, 10.0))
        amount = random.uniform(1.0, 100.0)
        bet_request = {
            'eventId': event_id,
            'outcome': outcome,
            'odds': odds,
            'amount': amount
        }
        bet_requests.append(bet_request)
    return bet_requests

# Function to send GraphQL requests
def send_graphql_request(query: str, variables: Optional[dict] = None) -> dict:
    aws_auth = AWS4Auth(
        AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY,
        'eu-central-1',
        'appsync'
    )

    headers = {
        'Content-Type': 'application/json',
        'X-Amz-Security-Token': AWS_SESSION_TOKEN
    }

    response = requests.post(
        GRAPHQL_ENDPOINT,
        json={'query': query, 'variables': variables},
        auth=aws_auth,
        headers=headers
    )

    return response.json()

# Main function for load generation
def main(bets_per_minute: int):
    while True:
        num_bets = min(bets_per_minute, 10)  # Cap at 10 bets per second
        bet_requests = generate_bet_requests(num_bets)

        variables = {
            'input': {
                'bets': bet_requests
            }
        }

        response = send_graphql_request(CREATE_BETS_MUTATION, variables)
        logger.debug(f'Response: {response}')

        if bets_per_minute <= 10:
            time.sleep(60 / bets_per_minute)
        else:
            time.sleep(0.1)

if __name__ == '__main__':
    bets_per_minute = 5  # Initial value, adjust as needed
    main(bets_per_minute)