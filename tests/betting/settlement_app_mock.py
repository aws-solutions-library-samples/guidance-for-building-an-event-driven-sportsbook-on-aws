"""
Mock implementation of the betting settlement app for testing.
"""
import json
from decimal import Decimal
from unittest.mock import MagicMock

# Mock objects
logger = MagicMock()
tracer = MagicMock()
events = MagicMock()
table = MagicMock()
gql_client = MagicMock()

# Mock decorator functions
def capture_lambda_handler(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def capture_method(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def inject_lambda_context(correlation_id_path=None, log_event=True):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Mock the tracer object's methods
tracer.capture_lambda_handler = capture_lambda_handler
tracer.capture_method = capture_method

# Mock the logger object's methods
logger.inject_lambda_context = inject_lambda_context

# Mock functions
def form_event(detailType, detail):
    return {
        'Source': 'com.betting.settlement',
        'DetailType': detailType,
        'Detail': json.dumps(detail, default=str),
        'EventBusName': 'test-event-bus'
    }

def get_live_market_event(eventId):
    """Get a live market event by ID."""
    # Mock response
    return {
        'eventId': eventId,
        'status': 'CLOSED',
        'startTime': '2023-01-01T12:00:00Z',
        'homeTeam': 'Team A',
        'awayTeam': 'Team B',
        'homeScore': 2,
        'awayScore': 1
    }

def get_event_outcome(event):
    """Get the outcome of an event."""
    home_score = event.get('homeScore', 0)
    away_score = event.get('awayScore', 0)
    
    if home_score > away_score:
        return 'HOME_TEAM_WIN'
    elif away_score > home_score:
        return 'AWAY_TEAM_WIN'
    else:
        return 'DRAW'

def calculate_event_outcome(bet, event_outcome):
    """Calculate the outcome of a bet based on the event outcome."""
    bet_outcome = bet.get('outcome')
    bet_amount = Decimal(bet.get('amount', 0))
    
    # Parse odds directly as decimal
    try:
        bet_odds = Decimal(bet.get('odds', '2.0'))
    except:
        bet_odds = Decimal('2.0')  # Default to 2.0 if parsing fails
    
    if bet_outcome == event_outcome:
        # Win - for decimal odds, the formula is stake * odds
        return {
            'result': 'WIN',
            'amount': bet_amount * bet_odds
        }
    else:
        # Loss
        return {
            'result': 'LOSS',
            'amount': Decimal(0)
        }

def settle_bet(bet, event):
    """Settle a bet based on the event outcome."""
    try:
        event_outcome = get_event_outcome(event)
        bet_result = calculate_event_outcome(bet, event_outcome)
        
        # Update the bet status
        table.update_item(
            TableName='test-bets-table',
            Key={
                'userId': bet['userId'],
                'betId': bet['betId']
            },
            UpdateExpression='SET #status = :status, #result = :result',
            ExpressionAttributeNames={
                '#status': 'status',
                '#result': 'result'
            },
            ExpressionAttributeValues={
                ':status': 'SETTLED',
                ':result': bet_result['result']
            }
        )
        
        # If the bet is a win, add funds to the user's wallet
        if bet_result['result'] == 'WIN':
            # Mock GraphQL mutation to add funds
            gql_client.execute.return_value = {
                'data': {
                    'depositFunds': {
                        'balance': '110.00'
                    }
                }
            }
        
        # Send event
        detail = {
            'userId': bet['userId'],
            'betId': bet['betId'],
            'eventId': bet['eventId'],
            'result': bet_result['result'],
            'amount': str(bet_result['amount'])
        }
        
        events.put_events(
            Entries=[
                form_event('BetSettled', detail)
            ]
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Bet {bet["betId"]} settled successfully',
                'result': bet_result
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error settling bet: {str(e)}'
            })
        }

def lambda_handler(event, context):
    """Lambda handler for the betting settlement."""
    try:
        eventId = event.get('eventId')
        
        # Get the event details
        event_details = get_live_market_event(eventId)
        
        if not event_details:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'message': f'Event {eventId} not found'
                })
            }
        
        # Get all bets for the event
        response = table.query(
            TableName='test-bets-table',
            IndexName='eventId-index',
            KeyConditionExpression='eventId = :eventId',
            ExpressionAttributeValues={
                ':eventId': eventId
            }
        )
        
        bets = response.get('Items', [])
        
        # Settle each bet
        results = []
        for bet in bets:
            result = settle_bet(bet, event_details)
            results.append(result)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Settled {len(results)} bets for event {eventId}',
                'results': results
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error in lambda handler: {str(e)}'
            })
        }
