import boto3
import json

from aws_lambda_powertools import Logger

dynamodb_client = boto3.client('dynamodb')
logger = Logger()

def lambda_handler(event, context):
  betting_events = json.loads(event.get('body'))
  for betting_event in betting_events:
    try:
      write_event_to_dynamo(betting_event)
    except:
      return {
        'statusCode': 400,
        'body': 'Bad Request!'
      }
  return {
    'statusCode': 200,
    'body': 'Successfully inserted event!'
  }

def write_event_to_dynamo(betting_event):
  try:
    event_id = betting_event['eventId']
    home_team = betting_event['homeTeam']
    away_team = betting_event['awayTeam']
    start_time = betting_event['startTime']
    duration = betting_event['duration']
    state = betting_event['state']
    if None  in (event_id, home_team, away_team, start_time, duration, state):
      raise Exception("Null values are not allowed")
    logger.info(event_id)
    dynamodb_client.put_item(TableName='BettingEvents', Item={'id': {'S': event_id}, 'homeTeam': {'S': home_team},
                                                              'awayTeam': {'S': away_team}, 'startTime': {'N': str(start_time)}, 'duration': {'N': str(duration)}, 'state': {'S': state}})
    logger.info("Event saved!")
  except Exception:
    logger.exception(Exception)
    raise Exception
