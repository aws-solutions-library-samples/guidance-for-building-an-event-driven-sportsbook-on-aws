# Wallet Service

## Overview
The Wallet Service is a critical component of the Sportsbook application that manages user funds for betting activities. It provides functionality for users to deposit and withdraw funds, check their balance, and for the system to deduct funds when bets are placed. The service ensures secure and accurate financial transactions within the application.

## Architecture
The service follows a serverless architecture built on AWS with the following components:

- **Resolvers**: Lambda functions that handle GraphQL API requests for wallet operations
- **DynamoDB Integration**: Stores wallet data in a DynamoDB table
- **EventBridge Integration**: Publishes wallet-related events to EventBridge for consumption by other services

## Technical Specifications

- **Python Version**: 3.12+
- **Dependencies**: 
  - boto3 >= 1.28.0
  - aws-lambda-powertools >= 2.26.0
- **Type Annotations**: Full TypedDict support for all data structures
- **Pattern Matching**: Uses Python 3.12 match statements for cleaner control flow
- **Union Types**: Uses pipe operator (|) for return type annotations

## Key Features

- **Wallet Management**: Create and manage user wallets
- **Fund Operations**: Deposit, withdraw, and deduct funds from wallets
- **Balance Checking**: Query current wallet balance
- **Insufficient Funds Handling**: Proper validation and error handling for insufficient funds
- **Event Publication**: Publishes events for wallet creation and updates
- **GraphQL API**: Provides a robust API for wallet operations
- **Type Safety**: Comprehensive type annotations for improved code quality
- **Error Handling**: Comprehensive error handling with proper exception management
- **Logging**: Structured logging with AWS Lambda Powertools

## Components

### Resolvers (`/resolvers`)
The resolvers component handles GraphQL API requests for:
- Creating wallets (`createWallet`)
- Getting wallet information (`getWallet`, `getWalletByUserId`)
- Depositing funds (`depositFunds`)
- Withdrawing funds (`withdrawFunds`)
- Deducting funds for bets (`deductFunds`)

Each resolver includes:
- Input validation
- Error handling with specific error types
- Structured logging
- Comprehensive documentation

## Data Model

### TypedDict Definitions

```python
class WalletItem(TypedDict):
    userId: str
    balance: Decimal
    
class WalletResponse(TypedDict):
    __typename: str
    userId: str
    balance: Decimal
    
class ErrorResponse(TypedDict):
    __typename: str
    message: str
```

### DynamoDB Schema

Wallet data is stored in a DynamoDB table with the following key attributes:
- `userId`: Unique identifier for the user (partition key)
- `balance`: Current wallet balance (Decimal)

## Integration Points

The Wallet Service integrates with:
- **User Service**: Wallets are associated with user accounts
- **Betting Service**: Deducts funds when bets are placed
- **EventBridge**: For publishing wallet-related events
- **Frontend Application**: Provides API for wallet management

## Event Flow

1. When a new user signs up, a wallet is created for them
2. Users can deposit funds into their wallet
3. Users can withdraw funds from their wallet if sufficient balance exists
4. When a bet is placed, funds are deducted from the wallet
5. Wallet events are published to EventBridge for other services to consume

## Testing

The Wallet Service includes comprehensive unit tests:
- Tests for wallet creation
- Tests for deposit and withdrawal operations
- Tests for insufficient funds scenarios
- Tests for error handling

Tests are implemented using pytest and mock AWS services to ensure the service functions correctly in isolation.

## Security

The service implements security through:
- Authentication and authorization via AWS AppSync
- Input validation for all API operations
- Proper error handling for insufficient funds
- Secure financial transactions with proper validation
- AWS IAM roles and policies for access control
- Type safety with Python 3.12 TypedDict

## Event Structure

The service publishes events with the following structure:

```python
entry: EventEntry = {
    'Source': 'com.wallet',
    'DetailType': "detail-type",
    'Detail': {
      "userId": "user-id"
    },
    'EventBusName': "event-bus-name"
}
```

Example event:
```json
{
  "Source": "com.wallet",
  "DetailType": "WalletCreated",
  "Detail": {
    "userId": "user-123"
  },
  "EventBusName": "sportsbook-event-bus"
}
```

## Use Cases

The Wallet Service supports several key use cases:
- **Funding**: Users depositing funds into their account
- **Withdrawals**: Users withdrawing funds from their account
- **Betting**: System deducting funds when bets are placed
- **Balance Checking**: Users checking their current balance
- **Wallet Creation**: Creating wallets for new users

## Error Handling

The service handles various error scenarios:
- Insufficient funds for withdrawals or deductions
- Non-existent wallets
- Unknown errors with appropriate error messages
- Proper logging of errors for troubleshooting

### Error Response Example

```python
def wallet_error(error_type: str, error_msg: str) -> ErrorResponse:
    """Create an error response."""
    return {'__typename': error_type, 'message': error_msg}
```

## Code Examples

### Pattern Matching for Balance Checks

```python
match item['balance'] - withdraw_amount:
    case amount if amount >= 0:
        item['balance'] = amount
    case _:
        logger.debug('Insufficient funds for withdrawal request')
        return wallet_error('InsufficientFundsError', 'Wallet contains insufficient funds to withdraw')
```

### Union Return Types

```python
def get_wallet() -> WalletResponse | ErrorResponse:
    """Get wallet for the authenticated user."""
    # Implementation...
```

## Monitoring and Observability

The service uses:
- AWS Lambda Powertools for structured logging
- AWS X-Ray for distributed tracing
- CloudWatch for metrics and logs
