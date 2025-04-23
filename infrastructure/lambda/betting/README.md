# Betting Service

## Overview
The Betting Service is a core component of the Sportsbook application that handles all aspects of bet placement, management, and settlement. It provides a serverless implementation using AWS Lambda functions to process betting operations through GraphQL APIs powered by AWS AppSync.

## Architecture
The service follows an event-driven serverless architecture with the following components:

- **Resolvers**: Lambda functions that handle GraphQL API requests for bet creation and retrieval
- **Receiver**: Lambda functions that process betting events from EventBridge
- **Settlement**: Step Functions workflow for handling bet settlement when sporting events conclude

## Key Features

- **Bet Placement**: Allows users to place bets on sporting events with different outcomes (homeWin, awayWin, draw)
- **Odds Validation**: Validates that bet odds match current market odds at placement time
- **Wallet Integration**: Automatically deducts funds from user wallets when bets are placed
- **Event-Driven Processing**: Uses EventBridge to emit events when bets are placed
- **Bet Retrieval**: Provides APIs to retrieve user bet history
- **Bet Settlement**: Processes bet outcomes when sporting events conclude
- **Error Handling**: Comprehensive error handling with proper exception management
- **Logging**: Structured logging with AWS Lambda Powertools

## Components

### Resolvers (`/resolvers`)
Handles GraphQL API requests for:
- Creating new bets (`createBets`)
- Retrieving user bets (`getBets`)
- Locking bets for event settlement (`lockBetsForEvent`)

Each resolver includes:
- Proper input validation
- Error handling with specific error types
- Structured logging
- Comprehensive documentation

### Receiver (`/receiver`)
Processes events from EventBridge related to betting activities, such as:
- Bet placement confirmations
- Event result notifications
- Event closure events that trigger bet settlement

The receiver component:
- Processes SQS messages containing EventBridge events
- Handles event-specific logic based on event type
- Triggers Step Functions for bet settlement
- Implements robust error handling

### Settlement (`/settlement/stepfunctions`)
Contains Step Functions workflows that:
- Process event results
- Determine winning bets
- Calculate payouts based on odds and bet amount
- Update bet statuses
- Trigger wallet credit operations for winning bets

## Data Model

Bets are stored in DynamoDB with the following key attributes:
- `userId`: The ID of the user who placed the bet (partition key)
- `betId`: A unique identifier for the bet (sort key)
- `eventId`: The ID of the sporting event the bet is placed on
- `odds`: The odds at the time of bet placement
- `placedAt`: Timestamp when the bet was placed
- `outcome`: The predicted outcome (homeWin, awayWin, draw)
- `betStatus`: Status of the bet (placed, resulted, settled)
- `amount`: The stake amount

## Integration Points

The Betting Service integrates with:
- **Wallet Service**: To deduct funds when bets are placed and credit winnings
- **Live Market Service**: To validate current odds and event status
- **Sporting Events Service**: To receive event results for settlement
- **EventBridge**: For event-driven communication between services

## Event Flow

1. User places bet through frontend application
2. GraphQL API triggers `createBets` resolver
3. Resolver validates bet details against current market odds
4. Funds are deducted from user wallet
5. Bet is stored in DynamoDB
6. Bet placement event is emitted to EventBridge
7. When event concludes, settlement process is triggered
8. Winning bets are identified and payouts processed

## Testing

The Betting Service includes comprehensive unit tests:
- Tests for resolvers (getBets, createBets, lockBetsForEvent)
- Tests for receiver functions
- Tests for settlement logic
- Tests for error handling scenarios

Tests are implemented using pytest and mock AWS services to ensure the service functions correctly in isolation.

## Security

The service implements security through:
- User authentication via AWS Cognito
- Authorization checks on all API operations
- Secure wallet integration for financial transactions
- Input validation to prevent injection attacks
- Proper error handling to prevent information leakage

## Monitoring and Observability

The service uses:
- AWS Lambda Powertools for structured logging
- AWS X-Ray for distributed tracing
- CloudWatch for metrics and logs

## Deployment

The Betting Service is deployed as part of the overall Sportsbook application using AWS SAM (Serverless Application Model). The deployment includes:
- Lambda functions for resolvers, receivers, and settlement
- DynamoDB tables for bet storage
- Step Functions workflows for settlement
- EventBridge rules for event routing
- IAM roles and policies for secure access
