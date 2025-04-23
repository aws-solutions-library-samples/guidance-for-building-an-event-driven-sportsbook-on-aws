# Trading Service

## Overview
The Trading Service is a critical component of the Sportsbook application that processes and transforms odds data from third-party providers. It acts as an intermediary layer between external odds sources and the internal live market system, allowing for odds assessment, risk management, and market adjustments before presenting final odds to users.

## Architecture
The service follows a serverless architecture built on AWS with the following components:

- **Receiver**: Lambda function that processes incoming odds updates from SQS and transforms them for internal use
- **EventBridge Integration**: Publishes processed odds updates to EventBridge for consumption by other services

## Key Features

- **Odds Processing**: Receives and processes odds updates from third-party providers
- **Event Transformation**: Transforms external events into the internal event format
- **Risk Management**: Provides a layer where odds can be adjusted based on risk assessment (placeholder for future implementation)
- **Event-Driven Design**: Fully integrated with the application's event-driven architecture
- **Scalable Processing**: Handles batch processing of odds updates efficiently

## Components

### Receiver (`/receiver`)
The receiver component is responsible for:
- Processing odds update events from SQS queues
- Transforming events from third-party format to internal format
- Publishing processed events to EventBridge under the trading namespace
- Providing a layer for future odds assessment and risk management

## Data Flow

1. Third-party services publish odds updates to EventBridge
2. These events are routed to an SQS queue
3. The Trading Service receiver processes events from the queue
4. The service transforms the events and publishes them under the `com.trading` namespace
5. Downstream services (like Live Market) consume these transformed events

## Integration Points

The Trading Service integrates with:
- **Third-Party Service**: Receives odds updates from external providers
- **Live Market Service**: Provides processed odds for market updates
- **EventBridge**: Receives events from and publishes events to the central event bus
- **SQS**: Processes events from SQS queues for reliable delivery

## Event Structure

The service processes and produces events with the following structure:

```json
{
  "Source": "com.trading",
  "DetailType": "UpdatedOdds",
  "Detail": {
    "eventId": "event-123",
    "homeOdds": "2/1",
    "awayOdds": "3/1",
    "drawOdds": "5/2"
  },
  "EventBusName": "sportsbook-event-bus"
}
```

## Security

The service implements security through:
- Input validation for all events
- Secure event processing with SQS and EventBridge
- AWS IAM roles and policies for access control
- Structured logging for audit trails

## Monitoring and Observability

The service uses:
- AWS Lambda Powertools for structured logging
- AWS X-Ray for distributed tracing
- CloudWatch for metrics and logs
- SQS dead-letter queues for failed event processing

## Deployment

The Trading Service is deployed as part of the overall Sportsbook application using AWS SAM (Serverless Application Model). The deployment includes:

- Lambda functions for event processing
- SQS queues for reliable event delivery
- IAM roles and policies for secure access
- CloudWatch log groups for monitoring
