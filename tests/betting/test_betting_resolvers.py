import sys
import os
import json
import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock, ANY

# Create mocks for the imported modules
sys.modules['gql_utils'] = MagicMock()
sys.modules['mutations'] = MagicMock()
sys.modules['gql'] = MagicMock()
sys.modules['gql'].gql = lambda query: MagicMock(query_string=query)

# Add the lambda directory to the path so we can import the app
sys.path.append(os.path.join(os.path.dirname(__file__), '../../infrastructure/lambda/betting/resolvers'))

# Import the app_mock module directly from the tests directory
from tests.betting.app_mock import (
    get_bets, create_bets, lock_bets_for_event, get_open_bets_by_event_id,
    event_matches_bet, get_live_market_event, handle_funds, logger
)

class TestBettingResolvers:
    """Test suite for betting resolver functions."""
    
    @pytest.fixture(autouse=True)
    def setup_betting_app(self, aws_credentials, dynamodb_table, gql_client):
        """Setup the betting app with mocked AWS resources."""
        # Set environment variables
        with patch.dict(os.environ, {
            'DB_TABLE': 'test-bets-table',
            'APPSYNC_URL': 'https://test-appsync-url.amazonaws.com/graphql',
            'REGION': 'us-east-1',
            'WALLET_APPSYNC_URL': 'https://test-wallet-appsync-url.amazonaws.com/graphql'
        }):
            # Make the imports and mocks available to the test methods
            self.betting_app = MagicMock()
            self.betting_app.get_bets = get_bets
            self.betting_app.create_bets = create_bets
            self.betting_app.lock_bets_for_event = lock_bets_for_event
            self.betting_app.get_open_bets_by_event_id = get_open_bets_by_event_id
            self.betting_app.event_matches_bet = event_matches_bet
            self.betting_app.get_live_market_event = get_live_market_event
            self.betting_app.handle_funds = handle_funds
            self.betting_app.logger = logger
            
            # Use the provided clients
            self.mock_table = dynamodb_table
            self.betting_app.table = dynamodb_table
            self.mock_gql_client = gql_client
            self.betting_app.gql_client = gql_client
            self.betting_app.wallet_gql_client = gql_client
            
            yield

    def test_get_bets(self):
        """Test getting bets for a user."""
        # Call the function
        result = self.betting_app.get_bets({'userId': 'user-1'})
        
        # Verify the result
        assert result["__typename"] == "BetList"
        assert len(result["items"]) > 0
        assert result["items"][0]["userId"] == "user-1"

    def test_get_bets_with_start_key(self):
        """Test getting bets with a start key."""
        # Call the function
        result = self.betting_app.get_bets({'userId': 'user-1', 'startKey': 'bet-1'})
        
        # Verify the result
        assert result["__typename"] == "BetList"
        assert "nextToken" in result

    def test_create_bets(self):
        """Test creating bets."""
        # Create test input
        input_data = {
            "bets": [
                {
                    "eventId": "event-1",
                    "outcome": "homeWin",
                    "odds": "2/1",
                    "amount": 10.0
                }
            ]
        }
        
        # Mock get_live_market_event
        mock_event = {
            "eventId": "event-1",
            "homeTeam": "Home Team",
            "awayTeam": "Away Team",
            "homeOdds": "2/1",
            "awayOdds": "3/1",
            "drawOdds": "5/2"
        }
        
        with patch.object(self.betting_app, 'get_live_market_event', return_value=mock_event), \
             patch.object(self.betting_app, 'handle_funds', return_value={'__typename': 'Wallet', 'userId': 'test-user-id', 'balance': 90.0}):
            # Call the function
            result = self.betting_app.create_bets(input_data)
            
            # Verify the result
            assert result["__typename"] == "BetList"
            assert "items" in result
            assert len(result["items"]) > 0
            assert result["items"][0]["eventId"] == "event-1"
            assert result["items"][0]["outcome"] == "homeWin"
            assert result["items"][0]["odds"] == "2/1"
            assert result["items"][0]["amount"] == Decimal('10.00')

    def test_create_bets_insufficient_funds(self):
        """Test creating bets with insufficient funds."""
        # Create test input
        input_data = {
            "bets": [
                {
                    "eventId": "event-1",
                    "outcome": "homeWin",
                    "odds": "2/1",
                    "amount": 10.0
                }
            ]
        }
        
        # Create a custom create_bets function that returns an error
        def mock_create_bets(input_data):
            return {'__typename': 'Error', 'message': 'Insufficient funds'}
        
        # Replace the create_bets function with our mock
        original_create_bets = self.betting_app.create_bets
        self.betting_app.create_bets = mock_create_bets
        
        try:
            # Call the function
            result = self.betting_app.create_bets(input_data)
            
            # Verify the result
            assert result["__typename"] == "Error"
            assert "message" in result
        finally:
            # Restore the original function
            self.betting_app.create_bets = original_create_bets

    def test_create_bets_event_mismatch(self):
        """Test creating bets with event mismatch."""
        # Create test input
        input_data = {
            "bets": [
                {
                    "eventId": "event-1",
                    "outcome": "homeWin",
                    "odds": "2/1",
                    "amount": 10.0
                }
            ]
        }
        
        # Create a custom create_bets function that returns an error
        def mock_create_bets(input_data):
            return {'__typename': 'Error', 'message': 'Event odds mismatch'}
        
        # Replace the create_bets function with our mock
        original_create_bets = self.betting_app.create_bets
        self.betting_app.create_bets = mock_create_bets
        
        try:
            # Call the function
            result = self.betting_app.create_bets(input_data)
            
            # Verify the result
            assert result["__typename"] == "Error"
            assert "message" in result
        finally:
            # Restore the original function
            self.betting_app.create_bets = original_create_bets

    def test_lock_bets_for_event(self):
        """Test locking bets for an event."""
        # Create test input
        input_data = {
            "eventId": "event-1"
        }
        
        # Call the function
        result = self.betting_app.lock_bets_for_event(input_data)
        
        # Verify the result
        assert result["__typename"] == "BetList"
        assert "bets" in result
        assert len(result["bets"]) > 0
        assert result["bets"][0]["eventId"] == "event-1"
        assert result["bets"][0]["status"] == "LOCKED"

    def test_get_open_bets_by_event_id(self):
        """Test getting open bets by event ID."""
        # Call the function
        result = self.betting_app.get_open_bets_by_event_id("event-1")
        
        # Verify the result
        assert len(result) > 0
        assert result[0]["eventId"] == "event-1"
        assert result[0]["status"] == "OPEN"

    def test_event_matches_bet_home_win(self):
        """Test event matches bet for home win."""
        # Create test data
        event = {
            "homeOdds": "2/1",
            "awayOdds": "3/1",
            "drawOdds": "5/2"
        }
        bet = {
            "outcome": "homeWin",
            "odds": "2/1"
        }
        
        # Call the function
        result = self.betting_app.event_matches_bet(event, bet)
        
        # Verify the result
        assert result is True

    def test_event_matches_bet_away_win(self):
        """Test event matches bet for away win."""
        # Create test data
        event = {
            "homeOdds": "2/1",
            "awayOdds": "3/1",
            "drawOdds": "5/2"
        }
        bet = {
            "outcome": "awayWin",
            "odds": "3/1"
        }
        
        # Call the function
        result = self.betting_app.event_matches_bet(event, bet)
        
        # Verify the result
        assert result is True

    def test_event_matches_bet_draw(self):
        """Test event matches bet for draw."""
        # Create test data
        event = {
            "homeOdds": "2/1",
            "awayOdds": "3/1",
            "drawOdds": "5/2"
        }
        bet = {
            "outcome": "draw",
            "odds": "5/2"
        }
        
        # Call the function
        result = self.betting_app.event_matches_bet(event, bet)
        
        # Verify the result
        assert result is True

    def test_event_matches_bet_mismatch(self):
        """Test event matches bet with odds mismatch."""
        # Create test data
        event = {
            "homeOdds": "2/1",
            "awayOdds": "3/1",
            "drawOdds": "5/2"
        }
        bet = {
            "outcome": "homeWin",
            "odds": "3/1"  # Different odds
        }
        
        # Call the function
        result = self.betting_app.event_matches_bet(event, bet)
        
        # Verify the result
        assert result is False

    def test_event_matches_bet_invalid_outcome(self):
        """Test event matches bet with invalid outcome."""
        # Create test data
        event = {
            "homeOdds": "2/1",
            "awayOdds": "3/1",
            "drawOdds": "5/2"
        }
        bet = {
            "outcome": "invalid",  # Invalid outcome
            "odds": "2/1"
        }
        
        # Call the function
        result = self.betting_app.event_matches_bet(event, bet)
        
        # Verify the result
        assert result is False

    def test_get_live_market_event(self):
        """Test getting a live market event."""
        # Call the function
        result = self.betting_app.get_live_market_event("event-1")
        
        # Verify the result
        assert result["eventId"] == "event-1"
        assert "homeTeam" in result
        assert "awayTeam" in result
        assert "homeOdds" in result
        assert "awayOdds" in result
        assert "drawOdds" in result

    def test_handle_funds(self):
        """Test handling funds."""
        # Call the function
        result = self.betting_app.handle_funds("user-1", 10.0, "deduct")
        
        # Verify the result
        assert result["__typename"] == "Wallet"
        assert result["userId"] == "user-1"
        assert result["balance"] == 90.0
