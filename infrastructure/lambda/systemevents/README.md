# System Events Service

## Overview
The System Events Service is a core infrastructure component of the Sportsbook application that provides centralized event tracking, logging, and processing capabilities. It captures, stores, and distributes system events from various services across the application, enabling event-driven architecture patterns and providing a comprehensive audit trail of system activities.

## Architecture
The service follows a serverless architecture built on AWS with the following components:

- **Receiver**: Lambda function that processes incoming events from SQS and records them
- **Resolver**: Lambda function that handles GraphQL API requests for adding system events
- **EventBridge Integration**: Publishes processed events back to EventBridge for further processing

## Key Features

- **Event Capture**: Records system events from various services across the application
- **Event Enrichment**: Adds unique identifiers and additional metadata to events
- **Event Distribution**: Republishes events to EventBridge for downstream consumers
- **Audit Trail**: Maintains a record of all system activities for compliance and debugging
- **GraphQL API**: Provides an API for manually adding system events
- **Error Handling**: Comprehensive error handling with proper exception management
- **Logging**: Structured logging with AWS Lambda Powertools

## Components

### Receiver (`/receiver`)
The receiver component is responsible for:
- Processing events from SQS queues
- Enriching events with unique identifiers (UUID)
- Recording events via GraphQL API calls
- Republishing processed events to EventBridge
- Implementing robust error handling
- Using structured logging for better observability

### Resolver (`/resolver`)
The resolver component handles:
- GraphQL API requests for adding system events
- Validation of event data
- Logging of system events
- Error handling with specific error types
- Structured logging
- Comprehensive documentation

## Data Model

System events follow this structure:
- `systemEventId`: Unique identifier for the event (UUID)
- `source`: The service or component that generated the event
- `detailType`: The type of event (e.g., "UserSignedUp", "BetPlaced")
- `detail`: JSON object containing event-specific data

## Integration Points

The System Events Service integrates with:
- **All Application Services**: Receives events from various services
- **EventBridge**: Receives events from and publishes events to the central event bus
- **SQS**: Processes events from SQS queues
- **AppSync**: Provides GraphQL API for event recording

## Event Flow

1. Services publish events to EventBridge or SQS
2. The receiver Lambda processes events from SQS
3. Events are enriched with unique identifiers
4. Events are recorded via GraphQL API calls to the resolver
5. Processed events are republished to EventBridge
6. Downstream services can subscribe to specific event patterns

## Testing

The System Events Service includes comprehensive unit tests:
- Tests for event processing
- Tests for event enrichment
- Tests for error handling scenarios

Tests are implemented using pytest and mock AWS services to ensure the service functions correctly in isolation.

## Security

The service implements security through:
- Input validation for all events
- Secure event processing with SQS and EventBridge
- Structured logging for audit trails
- AWS IAM roles and policies for access control
- Proper error handling to prevent information leakage

## Use Cases

The System Events Service supports several key use cases:
- **Audit Trail**: Tracking all system activities for compliance and debugging
- **Event-Driven Processing**: Enabling asynchronous workflows across services
- **System Monitoring**: Providing visibility into system operations
- **Analytics**: Supporting data collection for business intelligence

## Monitoring and Observability

The service uses:
- AWS Lambda Powertools for structured logging
- AWS X-Ray for distributed tracing
- CloudWatch for metrics and logs
- EventBridge for event tracking

## Example Events

The service processes various types of events, including:

```json
{
  "source": "com.betting",
  "detail-type": "BetPlaced",
  "detail": {
    "userId": "user-123",
    "betId": "bet-456",
    "amount": 50.00,
    "eventId": "event-789"
  }
}
```

```json
{
  "source": "com.wallet",
  "detail-type": "FundsDeposited",
  "detail": {
    "userId": "user-123",
    "amount": 100.00,
    "transactionId": "txn-abc"
  }
}
```
