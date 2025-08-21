"""
Mock implementation of the betting resolvers app for testing.
"""
import json
from decimal import Decimal
from unittest.mock import MagicMock

# Mock objects
logger = MagicMock()
tracer = MagicMock()
app = MagicMock()
events = MagicMock()
table = MagicMock()
gql_client = MagicMock()
scalar_types_utils = MagicMock()

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

def resolver(type_name, field_name):
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

# Mock the app object's methods
app.resolver = resolver
app.current_event = MagicMock()
app.current_event.identity = MagicMock()
app.current_event.identity.sub = "test-user-id"
app.resolve = MagicMock()

# Mock functions
def get_user_id(event):
    return event.identity.sub

def get_bets(arguments):
    """Get bets for a user."""
    try:
        userId = get_user_id(app.current_event)
        limit = arguments.get('limit', 10)
        nextToken = arguments.get('nextToken')
        
        # Query parameters
        params = {
            'TableName': 'test-bets-table',
            'KeyConditionExpression': 'userId = :userId',
            'ExpressionAttributeValues': {
                ':userId': userId
            },
            'Limit': limit,
            'ScanIndexForward': False  # Sort in descending order (newest first)
        }
        
        # Add pagination token if provided
        if nextToken:
            params['ExclusiveStartKey'] = json.loads(nextToken)
        
        # Mock response
        response = {
            'Items': [
                {
                    'userId': userId,
                    'betId': 'bet-1',
                    'eventId': 'event-1',
                    'amount': Decimal('10.00'),
                    'odds': Decimal('1.5'),
                    'outcome': 'HOME_TEAM_WIN',
                    'status': 'OPEN',
                    'createdAt': '2023-01-01T12:00:00Z'
                }
            ],
            'Count': 1,
            'ScannedCount': 1
        }
        
        # Add LastEvaluatedKey if there are more results
        if limit == 1:
            response['LastEvaluatedKey'] = {
                'userId': userId,
                'betId': 'bet-1'
            }
        
        # Format the response
        result = {
            'bets': response['Items'],
            'nextToken': json.dumps(response.get('LastEvaluatedKey')) if response.get('LastEvaluatedKey') else None
        }
        
        return bet_list_response(result)
    except Exception as e:
        return betting_error('Error', str(e))

def create_bets(arguments):
    """Create bets for a user."""
    try:
        userId = get_user_id(app.current_event)
        bets = arguments.get('bets', [])
        
        # Check if user has sufficient funds
        total_amount = sum(Decimal(bet.get('amount', 0)) for bet in bets)
        
        # Mock wallet check
        wallet_response = {
            'data': {
                'getWallet': {
                    'balance': '100.00'
                }
            }
        }
        
        balance = Decimal(wallet_response['data']['getWallet']['balance'])
        
        if balance < total_amount:
            return betting_error('InsufficientFunds', f'Insufficient funds. Required: {total_amount}, Available: {balance}')
        
        # Check if all events exist and are valid
        for bet in bets:
            eventId = bet.get('eventId')
            
            # Mock event check
            event_response = {
                'data': {
                    'getLiveMarketEvent': {
                        'eventId': eventId,
                        'status': 'OPEN',
                        'startTime': '2023-01-01T12:00:00Z',
                        'homeTeam': 'Team A',
                        'awayTeam': 'Team B',
                        'homeScore': 0,
                        'awayScore': 0
                    }
                }
            }
            
            if not event_response['data']['getLiveMarketEvent']:
                return betting_error('EventNotFound', f'Event {eventId} not found')
            
            if event_response['data']['getLiveMarketEvent']['status'] != 'OPEN':
                return betting_error('EventClosed', f'Event {eventId} is not open for betting')
        
        # Create bets
        created_bets = []
        for bet in bets:
            betId = f'bet-{len(created_bets) + 1}'
            created_bet = {
                'userId': userId,
                'betId': betId,
                'eventId': bet.get('eventId'),
                'amount': Decimal(bet.get('amount')),
                'odds': Decimal(bet.get('odds')),
                'outcome': bet.get('outcome'),
                'status': 'OPEN',
                'createdAt': '2023-01-01T12:00:00Z'
            }
            created_bets.append(created_bet)
        
        # Deduct funds from wallet
        handle_funds(userId, total_amount, 'DEDUCT')
        
        # Format the response
        result = {
            'bets': created_bets,
            'nextToken': None
        }
        
        return bet_list_response(result)
    except Exception as e:
        return betting_error('Error', str(e))

def lock_bets_for_event(arguments):
    """Lock all open bets for an event."""
    try:
        eventId = arguments.get('eventId')
        
        # Get all open bets for the event
        bets = get_open_bets_by_event_id(eventId)
        
        # Update each bet to LOCKED status
        for bet in bets:
            table.update_item(
                TableName='test-bets-table',
                Key={
                    'userId': bet['userId'],
                    'betId': bet['betId']
                },
                UpdateExpression='SET #status = :status',
                ExpressionAttributeNames={
                    '#status': 'status'
                },
                ExpressionAttributeValues={
                    ':status': 'LOCKED'
                }
            )
        
        # Format the response
        result = {
            'bets': bets,
            'nextToken': None
        }
        
        return bet_list_response(result)
    except Exception as e:
        return betting_error('Error', str(e))

def get_open_bets_by_event_id(eventId):
    """Get all open bets for an event."""
    # Mock response
    return [
        {
            'userId': 'user-1',
            'betId': 'bet-1',
            'eventId': eventId,
            'amount': Decimal('10.00'),
            'odds': Decimal('1.5'),
            'outcome': 'HOME_TEAM_WIN',
            'status': 'OPEN',
            'createdAt': '2023-01-01T12:00:00Z'
        },
        {
            'userId': 'user-2',
            'betId': 'bet-2',
            'eventId': eventId,
            'amount': Decimal('20.00'),
            'odds': Decimal('2.0'),
            'outcome': 'AWAY_TEAM_WIN',
            'status': 'OPEN',
            'createdAt': '2023-01-01T12:00:00Z'
        }
    ]

def event_matches_bet(event, bet):
    """Check if the event outcome matches the bet outcome."""
    if not event or not bet:
        return False
    
    home_score = event.get('homeScore', 0)
    away_score = event.get('awayScore', 0)
    bet_outcome = bet.get('outcome')
    
    if bet_outcome == 'HOME_TEAM_WIN':
        return home_score > away_score
    elif bet_outcome == 'AWAY_TEAM_WIN':
        return away_score > home_score
    elif bet_outcome == 'DRAW':
        return home_score == away_score
    else:
        return False

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

def handle_funds(userId, amount, action):
    """Handle funds for a user."""
    if action == 'DEDUCT':
        # Mock deduct funds
        return {
            'data': {
                'withdrawFunds': {
                    'balance': '90.00'
                }
            }
        }
    elif action == 'ADD':
        # Mock add funds
        return {
            'data': {
                'depositFunds': {
                    'balance': '110.00'
                }
            }
        }
    else:
        return None

def form_event(detailType, detail):
    return {
        'Source': 'com.betting.resolvers',
        'DetailType': detailType,
        'Detail': json.dumps(detail, default=str),
        'EventBusName': 'test-event-bus'
    }

def send_event(detail, detailType):
    event = form_event(detailType, detail)
    response = events.put_events(Entries=[event])
    return response

def bet_list_response(data):
    return {**{'__typename': 'BetList'}, **data}

def betting_error(errorType, error_msg):
    return {'__typename': errorType, 'message': error_msg}

def lambda_handler(event, context):
    return app.resolve(event, context)
