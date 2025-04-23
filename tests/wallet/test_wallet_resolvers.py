import sys
import os
import json
import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, UTC

# Add the lambda directory to the path so we can import the app
sys.path.append(os.path.join(os.path.dirname(__file__), '../../infrastructure/lambda/wallet/resolvers'))

class TestWalletResolvers:
    """Test suite for wallet resolver functions."""
    
    @pytest.fixture(autouse=True)
    def setup_wallet_app(self, aws_credentials, dynamodb_resource, events_client, wallet_table):
        """Setup the wallet app with mocked AWS resources."""
        # Import the app module after setting up AWS credentials and mocks
        with patch.dict(os.environ, {
            'DB_TABLE': 'test-wallet-table',
            'EVENT_BUS': 'test-event-bus'
        }):
            # Import modules inside the test to ensure mocks are applied first
            import app as wallet_app
            from aws_lambda_powertools.utilities.data_classes import AppSyncResolverEvent
            
            # Patch the boto3 session and resources in the app module
            with patch.object(wallet_app, 'session') as mock_session, \
                 patch.object(wallet_app, 'dynamodb', dynamodb_resource), \
                 patch.object(wallet_app, 'table', wallet_table), \
                 patch.object(wallet_app, 'events', events_client), \
                 patch.object(wallet_app, 'raise_wallet_event') as mock_raise_event:
                
                # Configure the mock_raise_event to do nothing
                mock_raise_event.return_value = None
                
                # Make the imports and mocks available to the test methods
                self.wallet_app = wallet_app
                self.AppSyncResolverEvent = AppSyncResolverEvent
                self.mock_raise_event = mock_raise_event
                yield

    def test_get_wallet_success(self, wallet_table, appsync_event_get_wallet):
        """Test successful wallet retrieval."""
        # Setup: Create a wallet in the mock DynamoDB table
        wallet_table.put_item(
            Item={
                'userId': 'test-user-id',
                'balance': Decimal('100.00')
            }
        )
        
        # Convert dictionary to AppSyncResolverEvent and mock the AppSyncResolver current_event
        self.wallet_app.app.current_event = self.AppSyncResolverEvent(appsync_event_get_wallet)
        
        # Execute the function
        result = self.wallet_app.get_wallet()
        
        # Verify the result
        assert result['__typename'] == 'Wallet'
        assert result['userId'] == 'test-user-id'
        assert result['balance'] == Decimal('100.00')

    def test_get_wallet_not_found(self, wallet_table, appsync_event_get_wallet):
        """Test wallet retrieval when wallet doesn't exist."""
        # Convert dictionary to AppSyncResolverEvent and mock the AppSyncResolver current_event
        self.wallet_app.app.current_event = self.AppSyncResolverEvent(appsync_event_get_wallet)
        
        # Execute the function
        result = self.wallet_app.get_wallet()
        
        # Verify the result
        assert result['__typename'] == 'NotFoundError'
        assert 'No wallet exists for user' in result['message']

    def test_deposit_funds_success(self, wallet_table, appsync_event_deposit_funds):
        """Test successful funds deposit."""
        # Setup: Create a wallet in the mock DynamoDB table
        wallet_table.put_item(
            Item={
                'userId': 'test-user-id',
                'balance': Decimal('100.00')
            }
        )
        
        # Convert dictionary to AppSyncResolverEvent and mock the AppSyncResolver current_event
        self.wallet_app.app.current_event = self.AppSyncResolverEvent(appsync_event_deposit_funds)
        
        # Execute the function
        result = self.wallet_app.deposit_funds({'amount': '50.00'})
        
        # Verify the result
        assert result['__typename'] == 'Wallet'
        assert result['userId'] == 'test-user-id'
        assert result['balance'] == Decimal('150.00')
        
        # Verify the database was updated
        response = wallet_table.get_item(Key={'userId': 'test-user-id'})
        assert 'Item' in response
        assert response['Item']['balance'] == Decimal('150.00')

    def test_withdraw_funds_success(self, wallet_table, appsync_event_withdraw_funds):
        """Test successful funds withdrawal."""
        # Setup: Create a wallet in the mock DynamoDB table
        wallet_table.put_item(
            Item={
                'userId': 'test-user-id',
                'balance': Decimal('100.00')
            }
        )
        
        # Convert dictionary to AppSyncResolverEvent and mock the AppSyncResolver current_event
        self.wallet_app.app.current_event = self.AppSyncResolverEvent(appsync_event_withdraw_funds)
        
        # Execute the function
        result = self.wallet_app.withdraw_funds({'amount': '50.00'})
        
        # Verify the result
        assert result['__typename'] == 'Wallet'
        assert result['userId'] == 'test-user-id'
        assert result['balance'] == Decimal('50.00')
        
        # Verify the database was updated
        response = wallet_table.get_item(Key={'userId': 'test-user-id'})
        assert 'Item' in response
        assert response['Item']['balance'] == Decimal('50.00')

    def test_withdraw_funds_insufficient_balance(self, wallet_table, appsync_event_withdraw_funds):
        """Test withdrawal with insufficient funds."""
        # Setup: Create a wallet in the mock DynamoDB table with low balance
        wallet_table.put_item(
            Item={
                'userId': 'test-user-id',
                'balance': Decimal('20.00')
            }
        )
        
        # Convert dictionary to AppSyncResolverEvent and mock the AppSyncResolver current_event
        self.wallet_app.app.current_event = self.AppSyncResolverEvent(appsync_event_withdraw_funds)
        
        # Execute the function
        result = self.wallet_app.withdraw_funds({'amount': '50.00'})
        
        # Verify the result
        assert result['__typename'] == 'InsufficientFundsError'
        # Note: There's a typo in the original error message ("insufficuient")
        assert 'funds to withdraw' in result['message'].lower()
        
        # Verify the database was not updated
        response = wallet_table.get_item(Key={'userId': 'test-user-id'})
        assert 'Item' in response
        assert response['Item']['balance'] == Decimal('20.00')

    def test_create_wallet(self, wallet_table, appsync_event_create_wallet):
        """Test wallet creation."""
        # Convert dictionary to AppSyncResolverEvent and mock the AppSyncResolver current_event
        self.wallet_app.app.current_event = self.AppSyncResolverEvent(appsync_event_create_wallet)
        
        # Execute the function
        result = self.wallet_app.create_wallet({'userId': 'new-user-id'})
        
        # Verify the result
        assert result['__typename'] == 'Wallet'
        assert result['userId'] == 'new-user-id'
        assert result['balance'] == Decimal('0')
        
        # Verify the database was updated
        response = wallet_table.get_item(Key={'userId': 'new-user-id'})
        assert 'Item' in response
        assert response['Item']['balance'] == Decimal('0')
        
        # Verify the event was raised
        self.mock_raise_event.assert_called_once_with('WalletCreated', {'userId': 'new-user-id'})

    def test_deduct_funds_success(self, wallet_table, appsync_event_deduct_funds):
        """Test successful funds deduction."""
        # Setup: Create a wallet in the mock DynamoDB table
        wallet_table.put_item(
            Item={
                'userId': 'test-user-id',
                'balance': Decimal('100.00')
            }
        )
        
        # Convert dictionary to AppSyncResolverEvent and mock the AppSyncResolver current_event
        self.wallet_app.app.current_event = self.AppSyncResolverEvent(appsync_event_deduct_funds)
        
        # Execute the function
        result = self.wallet_app.deduct_funds({'userId': 'test-user-id', 'amount': '25.00'})
        
        # Verify the result
        assert result['__typename'] == 'Wallet'
        assert result['userId'] == 'test-user-id'
        assert result['balance'] == Decimal('75.00')
        
        # Verify the database was updated
        response = wallet_table.get_item(Key={'userId': 'test-user-id'})
        assert 'Item' in response
        assert response['Item']['balance'] == Decimal('75.00')

    def test_deduct_funds_insufficient_balance(self, wallet_table, appsync_event_deduct_funds):
        """Test deduction with insufficient funds."""
        # Setup: Create a wallet in the mock DynamoDB table with low balance
        wallet_table.put_item(
            Item={
                'userId': 'test-user-id',
                'balance': Decimal('20.00')
            }
        )
        
        # Convert dictionary to AppSyncResolverEvent and mock the AppSyncResolver current_event
        self.wallet_app.app.current_event = self.AppSyncResolverEvent(appsync_event_deduct_funds)
        
        # Execute the function
        result = self.wallet_app.deduct_funds({'userId': 'test-user-id', 'amount': '25.00'})
        
        # Verify the result
        assert result['__typename'] == 'InsufficientFundsError'
        # Note: This error message is different from the withdraw one
        assert 'funds to deduct' in result['message'].lower()
        
        # Verify the database was not updated
        response = wallet_table.get_item(Key={'userId': 'test-user-id'})
        assert 'Item' in response
        assert response['Item']['balance'] == Decimal('20.00')

    def test_get_wallet_by_user_id_success(self, wallet_table):
        """Test successful wallet retrieval by user ID."""
        # Setup: Create a wallet in the mock DynamoDB table
        wallet_table.put_item(
            Item={
                'userId': 'test-user-id',
                'balance': Decimal('100.00')
            }
        )
        
        # Execute the function
        result = self.wallet_app.get_wallet_by_user_id('test-user-id')
        
        # Verify the result
        assert result['__typename'] == 'Wallet'
        assert result['userId'] == 'test-user-id'
        assert result['balance'] == Decimal('100.00')

    def test_get_wallet_by_user_id_not_found(self, wallet_table):
        """Test wallet retrieval by user ID when wallet doesn't exist."""
        # Execute the function
        result = self.wallet_app.get_wallet_by_user_id('nonexistent-user-id')
        
        # Verify the result
        assert result['__typename'] == 'NotFoundError'
        assert 'No wallet exists for user' in result['message']

    def test_get_wallet_by_user_id_empty_input(self, wallet_table):
        """Test wallet retrieval with empty user ID."""
        # Execute the function
        result = self.wallet_app.get_wallet_by_user_id('')
        
        # Verify the result
        assert result['__typename'] == 'InputError'
        assert 'valid userId' in result['message']
