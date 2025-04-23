from datetime import datetime, UTC
from decimal import Decimal
from os import getenv
import json
import boto3
from typing import TypedDict, NotRequired, Annotated, Any
from dataclasses import dataclass, field

from aws_lambda_powertools.utilities.data_classes import AppSyncResolverEvent
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import AppSyncResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

# Type definitions using Python 3.12 features
class WalletItem(TypedDict):
    """
    Represents a wallet item in DynamoDB.
    
    Attributes:
        userId: Unique identifier for the user
        balance: Current wallet balance as Decimal
    """
    userId: str
    balance: Decimal
    
class WalletResponse(TypedDict):
    """
    Response format for wallet operations.
    
    Attributes:
        __typename: GraphQL type name
        userId: Unique identifier for the user
        balance: Current wallet balance as Decimal
    """
    __typename: str
    userId: str
    balance: Decimal
    
class ErrorResponse(TypedDict):
    """
    Response format for errors.
    
    Attributes:
        __typename: Error type name
        message: Error message
    """
    __typename: str
    message: str
    
class DepositInput(TypedDict):
    """
    Input for deposit funds mutation.
    
    Attributes:
        amount: Amount to deposit as string
    """
    amount: str
    
class WithdrawInput(TypedDict):
    """
    Input for withdraw funds mutation.
    
    Attributes:
        amount: Amount to withdraw as string
    """
    amount: str
    
class CreateWalletInput(TypedDict):
    """
    Input for create wallet mutation.
    
    Attributes:
        userId: User ID to create wallet for
    """
    userId: str
    
class DeductFundsInput(TypedDict):
    """
    Input for deduct funds mutation (admin operation).
    
    Attributes:
        userId: User ID to deduct funds from
        amount: Amount to deduct as string
    """
    userId: str
    amount: str
    
class EventDetail(TypedDict):
    """
    Event detail for wallet events.
    
    Attributes:
        userId: User ID associated with the event
    """
    userId: str
    
class EventEntry(TypedDict):
    """
    EventBridge event entry format.
    
    Attributes:
        Source: Event source
        DetailType: Type of event
        Detail: Event details as JSON string
        EventBusName: Target event bus
    """
    Source: str
    DetailType: str
    Detail: str
    EventBusName: str

# Initialize services
tracer = Tracer()
logger = Logger()
app = AppSyncResolver()

event_bus_name = getenv('EVENT_BUS')
table_name = getenv('DB_TABLE')
session = boto3.Session()
dynamodb = session.resource('dynamodb')
table = dynamodb.Table(table_name)
events = session.client('events')

# User pool resolvers
@app.resolver(type_name="Query", field_name="getWallet")
@tracer.capture_method
def get_wallet() -> WalletResponse | ErrorResponse:
    """
    Get wallet for the authenticated user.
    
    Retrieves the wallet information for the currently authenticated user.
    
    Returns:
        WalletResponse: Wallet information if found
        ErrorResponse: Error details if wallet not found or other error occurs
    """
    userId = get_user_id(app.current_event)
    
    try:
        item = _try_get_wallet(userId)
        return wallet_response(item)
    except KeyError:
        return wallet_error('NotFoundError', 'No wallet exists for user')
    except Exception as e:
        logger.error(f"Error getting wallet: {str(e)}")
        return wallet_error('UnknownError', 'An unknown error occurred.')


@app.resolver(type_name="Mutation", field_name="withdrawFunds")
@tracer.capture_method
def withdraw_funds(input: WithdrawInput) -> WalletResponse | ErrorResponse:
    """
    Withdraw funds from the user's wallet.
    
    Deducts the specified amount from the user's wallet if sufficient funds are available.
    
    Args:
        input: Withdrawal details including amount
        
    Returns:
        WalletResponse: Updated wallet information if successful
        ErrorResponse: Error details if insufficient funds or other error occurs
    """
    userId = get_user_id(app.current_event)

    try:
        item = _try_get_wallet(userId)
        withdraw_amount = Decimal(input['amount'])
        
        if item['balance'] >= withdraw_amount:
            item['balance'] -= withdraw_amount
        else:
            return wallet_error('InsufficientFundsError', 'Wallet contains insufficient funds to withdraw')

        table.update_item(
            Key={'userId': userId},
            UpdateExpression="set balance=:r",
            ExpressionAttributeValues={
                ':r': item['balance']
            },
            ReturnValues="UPDATED_NEW")

        return wallet_response(item)
    except KeyError:
        return wallet_error('NotFoundError', 'No wallet exists for user')
    except Exception as e:
        logger.error(f"Error withdrawing funds: {str(e)}")
        return wallet_error('UnknownError', 'An unknown error occurred.')


@app.resolver(type_name="Mutation", field_name="depositFunds")
@tracer.capture_method
def deposit_funds(input: DepositInput) -> WalletResponse | ErrorResponse:
    """
    Deposit funds into the user's wallet.
    
    Adds the specified amount to the user's wallet balance.
    
    Args:
        input: Deposit details including amount
        
    Returns:
        WalletResponse: Updated wallet information if successful
        ErrorResponse: Error details if wallet not found or other error occurs
    """
    userId = get_user_id(app.current_event)

    try:
        item = _try_get_wallet(userId)
        item['balance'] += Decimal(input['amount'])

        table.update_item(
            Key={'userId': userId},
            UpdateExpression="set balance=:r",
            ExpressionAttributeValues={
                ':r': item['balance']
            },
            ReturnValues="UPDATED_NEW")

        return wallet_response(item)
    except KeyError:
        return wallet_error('NotFoundError', 'No wallet exists for user')
    except Exception as e:
        logger.error(f"Error depositing funds: {str(e)}")
        return wallet_error('UnknownError', 'An unknown error occurred.')


# IAM resolvers
@app.resolver(type_name="Query", field_name="getWalletByUserId")
@tracer.capture_method
def get_wallet_by_user_id(userId: str) -> WalletResponse | ErrorResponse:
    """
    Get wallet by user ID (admin operation).
    
    Retrieves wallet information for any user by their ID.
    This is an administrative operation.
    
    Args:
        userId: ID of the user whose wallet to retrieve
        
    Returns:
        WalletResponse: Wallet information if found
        ErrorResponse: Error details if wallet not found or other error occurs
    """
    if not userId:
        return wallet_error('InputError', 'You must provide a valid userId')
    
    try:
        item = _try_get_wallet(userId)
        return wallet_response(item)
    except KeyError:
        return wallet_error('NotFoundError', 'No wallet exists for user')
    except Exception as e:
        logger.error(f"Error getting wallet by userId: {str(e)}")
        return wallet_error('UnknownError', 'An unknown error occurred.')


@app.resolver(type_name="Mutation", field_name="createWallet")
@tracer.capture_method
def create_wallet(input: CreateWalletInput) -> WalletResponse:
    """
    Create a new wallet for a user.
    
    Creates a new wallet with zero balance for the specified user
    and raises a WalletCreated event.
    
    Args:
        input: User ID for whom to create the wallet
        
    Returns:
        WalletResponse: New wallet information
        ErrorResponse: Error details if creation fails
    """
    try:
        item: WalletItem = {
            'userId': input['userId'],
            'balance': Decimal(0),
        }
        
        table.put_item(Item=item)
        
        # Use event detail with proper typing
        event_detail: EventDetail = {'userId': input['userId']}
        raise_wallet_event('WalletCreated', event_detail)
        
        return wallet_response(item)
    except Exception as e:
        logger.error(f"Error creating wallet: {str(e)}")
        return wallet_error('UnknownError', 'An unknown error occurred.')


@app.resolver(type_name="Mutation", field_name="deductFunds")
@tracer.capture_method
def deduct_funds(input: DeductFundsInput) -> WalletResponse | ErrorResponse:
    """
    Deduct funds from a user's wallet (admin operation).
    
    Deducts the specified amount from a user's wallet if sufficient funds are available.
    This is an administrative operation.
    
    Args:
        input: User ID and amount to deduct
        
    Returns:
        WalletResponse: Updated wallet information if successful
        ErrorResponse: Error details if insufficient funds or other error occurs
    """
    userId = input['userId']
    amount = Decimal(input['amount'])

    try:
        item = _try_get_wallet(userId)
        
        if item['balance'] >= amount:
            item['balance'] -= amount
        else:
            return wallet_error('InsufficientFundsError', 'Wallet contains insufficient funds to deduct')

        table.update_item(
            Key={'userId': userId},
            UpdateExpression="set balance=:r",
            ExpressionAttributeValues={
                ':r': item['balance']
            },
            ReturnValues="UPDATED_NEW")

        return wallet_response(item)
    except KeyError:
        return wallet_error('NotFoundError', 'No wallet exists for user')
    except Exception as e:
        logger.error(f"Error deducting funds: {str(e)}")
        return wallet_error('UnknownError', 'An unknown error occurred.')


def _try_get_wallet(userId: str) -> WalletItem:
    """
    Get wallet from DynamoDB by user ID.
    
    Args:
        userId: ID of the user whose wallet to retrieve
        
    Returns:
        WalletItem: Wallet information from DynamoDB
        
    Raises:
        KeyError: If wallet does not exist
    """
    return table.get_item(
        Key={"userId": userId}
    )["Item"]


def get_user_id(event: AppSyncResolverEvent) -> str:
    """
    Extract user ID from AppSync event.
    
    Args:
        event: AppSync resolver event
        
    Returns:
        str: User ID from the event identity
    """
    return event.identity.sub


def wallet_error(error_type: str, error_msg: str) -> ErrorResponse:
    """
    Create an error response.
    
    Args:
        error_type: Type of error
        error_msg: Error message
        
    Returns:
        ErrorResponse: Formatted error response
    """
    return {'__typename': error_type, 'message': error_msg}


def wallet_response(data: WalletItem) -> WalletResponse:
    """
    Create a wallet response.
    
    Args:
        data: Wallet data
        
    Returns:
        WalletResponse: Formatted wallet response
    """
    return {'__typename': 'Wallet', **data}


@tracer.capture_method
def raise_wallet_event(detail_type: str, detail: EventDetail) -> None:
    """
    Publish an event to EventBridge.
    
    Args:
        detail_type: Type of event
        detail: Event details
    """
    try:
        entry: EventEntry = {
            'Source': 'com.wallet',
            'DetailType': detail_type,
            'Detail': json.dumps(detail),
            'EventBusName': event_bus_name
        }
        
        events.put_events(Entries=[entry])
    except Exception as e:
        logger.error(f"Error raising wallet event: {str(e)}")


@logger.inject_lambda_context(correlation_id_path=correlation_paths.APPSYNC_RESOLVER, log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """
    Lambda handler function.
    
    Args:
        event: Lambda event
        context: Lambda context
        
    Returns:
        dict: AppSync resolver response
    """
    return app.resolve(event, context)
