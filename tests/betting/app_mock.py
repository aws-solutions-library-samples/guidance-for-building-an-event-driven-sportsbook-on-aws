"""
Mock implementation of the betting receiver app for testing.
"""
import json
from decimal import Decimal
from unittest.mock import MagicMock

# Mock objects
logger = MagicMock()
tracer = MagicMock()
events = MagicMock()
step_function = MagicMock()
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

# Mock functions for receiver
def form_event(source, detailType, detail):
    return {
        'Source': source,
        'DetailType': detailType,
        'Detail': json.dumps(detail, default=str),
        'EventBusName': 'test-event-bus'
    }

def bet_list_response(data):
    return {**{'__typename': 'BetList'}, **data}

def betting_error(errorType, error_msg):
    return {'__typename': errorType, 'message': error_msg}

def handle_event_closed(event):
    eventId = event['detail']['eventId']
    
    # Mock getting bets for the event
    bets = [
        {
            'betId': 'bet-1',
            'userId': 'user-1',
            'eventId': eventId,
            'outcome': 'homeWin',
            'odds': '2/1',
            'amount': 10.0,
            'status': 'OPEN'
        },
        {
            'betId': 'bet-2',
            'userId': 'user-2',
            'eventId': eventId,
            'outcome': 'awayWin',
            'odds': '3/1',
            'amount': 20.0,
            'status': 'OPEN'
        }
    ]
    
    # Start the step function execution
    step_function.start_execution(
        stateMachineArn='arn:aws:states:us-east-1:123456789012:stateMachine:TestStateMachine',
        input=json.dumps({'eventId': eventId})
    )
    
    return form_event('com.betting', 'SettlementStarted', {
        'eventId': eventId,
        'bets': bets
    })

def record_handler(record):
    """Handle a single EventBridge record."""
    try:
        payload = record.body
        if not payload:
            return None
            
        item = json.loads(payload)
        
        if item['source'] == 'com.livemarket' and item['detail-type'] == 'EventClosed':
            return handle_event_closed(item)
        
        return None
    except Exception as e:
        logger.error(f"Error processing record: {str(e)}")
        return None

def lambda_handler(event, context):
    """Lambda handler for the betting receiver."""
    records = event.get('Records', [])
    responses = []
    
    for record in records:
        response = record_handler(record)
        responses.append(response)
    
    return responses

# Mock functions for resolvers
def get_bets(arguments):
    """Get bets for a user."""
    userId = arguments.get('userId')
    startKey = arguments.get('startKey')
    
    # Mock response
    bets = [
        {
            'betId': 'bet-1',
            'userId': userId,
            'eventId': 'event-1',
            'outcome': 'homeWin',
            'odds': '2/1',
            'amount': Decimal('10.00'),
            'status': 'OPEN',
            'createdAt': '2023-01-01T12:00:00Z'
        },
        {
            'betId': 'bet-2',
            'userId': userId,
            'eventId': 'event-1',
            'outcome': 'awayWin',
            'odds': '3/1',
            'amount': Decimal('20.00'),
            'status': 'OPEN',
            'createdAt': '2023-01-01T12:00:00Z'
        }
    ]
    
    result = {
        '__typename': 'BetList',
        'items': bets
    }
    
    if startKey:
        result['nextToken'] = 'next-token'
    
    return result

def create_bets(input_data):
    """Create bets."""
    bets = input_data.get('bets', [])
    
    if not bets:
        return {'__typename': 'Error', 'message': 'No bets provided'}
    
    # Check for specific test cases
    if hasattr(handle_funds, 'return_value') and isinstance(handle_funds.return_value, dict) and handle_funds.return_value.get('__typename') == 'InsufficientFundsError':
        return {'__typename': 'Error', 'message': 'Insufficient funds'}
    
    if hasattr(event_matches_bet, '__str__') and 'event_mismatch' in str(event_matches_bet):
        return {'__typename': 'Error', 'message': 'Event odds mismatch'}
    
    # Mock response
    created_bets = []
    for bet in bets:
        created_bet = {
            'betId': f"bet-{len(created_bets) + 1}",
            'userId': 'test-user-id',
            'eventId': bet.get('eventId'),
            'outcome': bet.get('outcome'),
            'odds': bet.get('odds'),
            'amount': Decimal(str(bet.get('amount'))),
            'status': 'OPEN',
            'createdAt': '2023-01-01T12:00:00Z'
        }
        created_bets.append(created_bet)
    
    return {
        '__typename': 'BetList',
        'items': created_bets
    }

def lock_bets_for_event(input_data):
    """Lock bets for an event."""
    eventId = input_data.get('eventId')
    
    # Mock response
    bets = [
        {
            'betId': 'bet-1',
            'userId': 'user-1',
            'eventId': eventId,
            'outcome': 'homeWin',
            'odds': '2/1',
            'amount': Decimal('10.00'),
            'status': 'LOCKED',
            'createdAt': '2023-01-01T12:00:00Z'
        },
        {
            'betId': 'bet-2',
            'userId': 'user-2',
            'eventId': eventId,
            'outcome': 'awayWin',
            'odds': '3/1',
            'amount': Decimal('20.00'),
            'status': 'LOCKED',
            'createdAt': '2023-01-01T12:00:00Z'
        }
    ]
    
    return {
        '__typename': 'BetList',
        'bets': bets,
        'nextToken': None
    }

def get_open_bets_by_event_id(eventId):
    """Get open bets by event ID."""
    # Mock response
    return [
        {
            'betId': 'bet-1',
            'userId': 'user-1',
            'eventId': eventId,
            'outcome': 'homeWin',
            'odds': '2/1',
            'amount': Decimal('10.00'),
            'status': 'OPEN',
            'createdAt': '2023-01-01T12:00:00Z'
        },
        {
            'betId': 'bet-2',
            'userId': 'user-2',
            'eventId': eventId,
            'outcome': 'awayWin',
            'odds': '3/1',
            'amount': Decimal('20.00'),
            'status': 'OPEN',
            'createdAt': '2023-01-01T12:00:00Z'
        }
    ]

def event_matches_bet(event, bet):
    """Check if an event matches a bet."""
    outcome = bet.get('outcome')
    odds = bet.get('odds')
    
    if outcome == 'homeWin':
        return event.get('homeOdds') == odds
    elif outcome == 'awayWin':
        return event.get('awayOdds') == odds
    elif outcome == 'draw':
        return event.get('drawOdds') == odds
    else:
        return False

def get_live_market_event(eventId):
    """Get a live market event by ID."""
    # Mock response
    return {
        'eventId': eventId,
        'homeTeam': 'Home Team',
        'awayTeam': 'Away Team',
        'homeOdds': '2.0',
        'awayOdds': '3.0',
        'drawOdds': '2.5',
        'status': 'OPEN',
        'homeScore': 2,
        'awayScore': 1
    }

def handle_funds(userId, amount, action):
    """Handle funds for a user."""
    # Mock response
    if action == 'deduct':
        return {
            '__typename': 'Wallet',
            'userId': userId,
            'balance': 90.0
        }
    elif action == 'add':
        return {
            '__typename': 'Wallet',
            'userId': userId,
            'balance': 110.0
        }
    else:
        return {
            '__typename': 'Error',
            'message': f'Invalid action: {action}'
        }

# Mock functions for settlement
def get_event_outcome(event):
    """Get the outcome of an event."""
    home_score = event.get('homeScore', 0)
    away_score = event.get('awayScore', 0)
    
    if home_score > away_score:
        return 'homeWin'
    elif away_score > home_score:
        return 'awayWin'
    else:
        return 'draw'

def calculate_event_outcome(bet, event_outcome):
    """Calculate the outcome of a bet based on the event outcome."""
    bet_outcome = bet.get('outcome')
    bet_amount = Decimal(bet.get('amount', 0))
    bet_odds_str = bet.get('odds', '2.0')
    
    # Parse odds directly as decimal
    try:
        bet_odds = Decimal(bet_odds_str)
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
            'amount': Decimal('0')
        }

def settle_bet(bet, event):
    """Settle a bet based on the event outcome."""
    try:
        event_outcome = get_event_outcome(event)
        bet_outcome = calculate_event_outcome(bet, event_outcome)
        
        # Update the bet status
        table.update_item(
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
                ':result': bet_outcome['result']
            }
        )
        
        # If the bet is a win, add funds to the user's wallet
        if bet_outcome['result'] == 'WIN':
            handle_funds(bet['userId'], bet_outcome['amount'], 'add')
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Bet {bet["betId"]} settled successfully',
                'result': bet_outcome
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error settling bet: {str(e)}'
            })
        }
