# Live Market Service

## Overview
The Live Market Service is a critical component of the Sportsbook application that manages real-time sporting event data, odds, and market status. It provides a dynamic, event-driven system for tracking and updating sporting events that users can place bets on.

## Architecture
The service follows a serverless architecture built on AWS with the following components:

- **Resolvers**: Lambda functions that handle GraphQL API requests for event data
- **Receiver**: Lambda functions that process event updates from SQS and EventBridge
- **Seed**: Lambda function that initializes the database with sample sporting events

## Key Features

- **Real-time Event Management**: Tracks live sporting events with current odds and status
- **Market Control**: Ability to suspend and unsuspend betting markets for specific events
- **Historical Data**: Maintains a time-series history of odds changes for auditing and verification
- **Event-Driven Updates**: Processes event updates through SQS and publishes changes to EventBridge
- **GraphQL API**: Provides a robust API for querying event data and making updates
- **Error Handling**: Comprehensive error handling with proper exception management
- **Logging**: Structured logging with AWS Lambda Powertools

## Components

### Resolvers (`/resolvers`)
Handles GraphQL API requests for:
- Retrieving all active events (`getEvents`)
- Retrieving a specific event, optionally at a historical timestamp (`getEvent`)
- Updating event odds (`updateEventOdds`)
- Suspending markets (`suspendMarket`)
- Unsuspending markets (`unsuspendMarket`)

Each resolver includes:
- Input validation
- Error handling with specific error types
- Structured logging
- Comprehensive documentation

### Receiver (`/receiver`)
Processes messages from SQS and EventBridge for:
- Updating odds for existing events
- Adding new sporting events
- Marking events as finished with outcomes
- Suspending and unsuspending markets

The receiver component:
- Processes SQS messages containing EventBridge events
- Handles event-specific logic based on event type
- Implements robust error handling
- Uses structured logging for better observability

### Seed (`/seed`)
Initializes the DynamoDB tables with sample sporting event data during deployment.

## Data Model

Events are stored in DynamoDB with the following key attributes:
- `eventId`: Unique identifier for the sporting event (partition key)
- `home`: Home team name
- `away`: Away team name
- `homeOdds`: Current odds for home team win
- `awayOdds`: Current odds for away team win
- `drawOdds`: Current odds for a draw
- `eventStatus`: Status of the event (running, finished)
- `marketstatus`: Array of market status objects (e.g., `[{"name": "win", "status": "Active"}]`)
- `updatedAt`: Timestamp of last update
- `start`: Scheduled start time
- `end`: Scheduled end time
- `duration`: Expected duration

Historical event data is stored in a separate DynamoDB table with:
- `eventId`: Event identifier (partition key)
- `timestamp`: Time of the snapshot (sort key)
- `expiry`: TTL for automatic deletion

## Integration Points

The Live Market Service integrates with:
- **Betting Service**: Provides event data and odds for bet placement
- **Settlement Service**: Provides event outcomes for bet settlement
- **Frontend Application**: Displays events and odds to users
- **EventBridge**: For event-driven communication between services

## Event Flow

1. Events are initially seeded in the database during deployment
2. External systems or admin actions trigger odds updates via SQS
3. The receiver processes these updates and calls the GraphQL API
4. Updated event data is stored in both the main table and history table
5. Event updates are published to EventBridge for other services to consume
6. When events finish, outcomes are recorded and markets are closed

## Testing

The Live Market Service includes comprehensive unit tests:
- Tests for resolvers (getEvents, getEvent, updateEventOdds)
- Tests for receiver functions
- Tests for error handling scenarios

Tests are implemented using pytest and mock AWS services to ensure the service functions correctly in isolation.

## Security

The service implements security through:
- Authentication and authorization via AWS AppSync
- Input validation on all API operations
- Secure event processing with SQS and EventBridge
- Data integrity through conditional updates
- Proper error handling to prevent information leakage

## Monitoring and Observability

The service uses:
- AWS Lambda Powertools for structured logging
- AWS X-Ray for distributed tracing
- CloudWatch for metrics and alarms
