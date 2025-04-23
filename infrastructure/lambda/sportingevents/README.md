# Sporting Events Service

## Overview
The Sporting Events Service is a key component of the Sportsbook application that serves as the entry point for external sporting event data. It receives information about upcoming and ongoing sporting events from third-party providers and integrates this data into the sportsbook ecosystem.

## Architecture
The service follows a serverless architecture built on AWS Lambda with the following components:

- **Receiver**: Lambda function that processes incoming sporting event data from external sources
- **Event Bridge Integration**: Publishes standardized event data to the application's event bus

## Key Features

- **External Data Integration**: Accepts sporting event data from third-party providers via API endpoints
- **Data Transformation**: Converts external data formats into the application's standardized event format
- **Event Publication**: Publishes event data to EventBridge for consumption by other services
- **Input Validation**: Validates incoming event data to ensure data integrity
- **Timestamp Normalization**: Converts various timestamp formats to a standardized ISO format
- **Error Handling**: Comprehensive error handling with proper exception management
- **Logging**: Structured logging with AWS Lambda Powertools

## Components

### Receiver (`/receiver`)
The receiver component is responsible for:
- Accepting HTTP POST requests containing sporting event data
- Validating and transforming the incoming data
- Publishing standardized event data to EventBridge
- Providing appropriate HTTP responses to the data provider
- Implementing robust error handling
- Using structured logging for better observability

## Data Model

The service processes sporting event data with the following key attributes:
- `eventId`: Unique identifier for the sporting event
- `homeTeam`: Name of the home team
- `awayTeam`: Name of the away team
- `startTime`: Scheduled start time of the event (Unix timestamp in milliseconds)
- `endTime`: Expected end time of the event (Unix timestamp in milliseconds)
- `updatedAt`: Timestamp of the last update (Unix timestamp in milliseconds)
- `duration`: Expected duration of the event
- `state`: Current status of the event (e.g., scheduled, in_progress, finished)
- `homeOdds`: Current odds for home team win
- `awayOdds`: Current odds for away team win
- `drawOdds`: Current odds for a draw

## Integration Points

The Sporting Events Service integrates with:
- **External Data Providers**: Receives sporting event data via HTTP endpoints
- **Live Market Service**: Provides event data for market creation and updates
- **Betting Service**: Supplies the foundational event data that bets are placed on
- **EventBridge**: For event-driven communication between services

## Event Flow

1. External data provider sends sporting event data to the service's API endpoint
2. The receiver Lambda function validates and transforms the data
3. The function publishes an `EventAdded` event to EventBridge
4. Other services (like Live Market) consume the event and create corresponding resources
5. The service returns a success or error response to the data provider

## Testing

The Sporting Events Service includes comprehensive unit tests:
- Tests for data validation
- Tests for event publication
- Tests for error handling scenarios

Tests are implemented using pytest and mock AWS services to ensure the service functions correctly in isolation.

## Security

The service implements security through:
- Input validation to prevent malformed data
- API Gateway authentication and authorization
- Error handling to prevent service disruption
- CloudWatch logging for audit trails
- Proper error handling to prevent information leakage

## Usage

External data providers can send sporting event data to the service's API endpoint using the following format:

```json
[
  {
    "eventId": "event-123",
    "homeTeam": "Team A",
    "awayTeam": "Team B",
    "startTime": 1648123200000,
    "endTime": 1648130400000,
    "updatedAt": 1648122000000,
    "duration": 7200,
    "state": "scheduled",
    "homeOdds": 1.95,
    "awayOdds": 3.25,
    "drawOdds": 3.50
  }
]
```

The service will respond with:
- HTTP 200: Successfully processed event data
- HTTP 400: Invalid event data format or missing required fields

## Monitoring and Observability

The service uses:
- AWS Lambda Powertools for structured logging
- CloudWatch for metrics and logs
- EventBridge for event tracking
