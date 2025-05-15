# Third Party Service

## Overview
The Third Party Service is a collection of Lambda functions that integrate external functionality and data sources into the Sportsbook application. It currently consists of two main components: a Fetcher service that simulates third-party odds updates and a PingInfo service that measures network latency across different AWS regions.

## Architecture
The service follows a serverless architecture built on AWS with the following components:

- **Fetcher**: Lambda function that simulates fetching updated odds from external providers
- **PingInfo**: Lambda function that measures and reports network latency to different AWS regions

## Key Features

- **Odds Simulation**: Simulated third-party odds updates for sporting events with realistic house edge calculations
- **Network Latency Monitoring**: Real-time latency measurements across AWS regions
- **GraphQL API**: Provides API for latency information
- **EventBridge Integration**: Publishes odds updates to EventBridge for consumption by other services
- **Error Handling**: Comprehensive error handling with proper exception management
- **Logging**: Structured logging with AWS Lambda Powertools
- **Tracing**: Distributed tracing with AWS X-Ray

## Components

### Fetcher (`/fetcher`)
The fetcher component:
- Simulates polling external APIs for updated odds
- Generates random but realistic odds for predefined sporting events
- Applies a 10% house edge to the generated odds
- Ensures odds are unique and follow betting market rules
- Publishes odds updates to EventBridge for consumption by other services
- Implements proper error handling and retry logic
- Uses structured logging for better observability

### PingInfo (`/pinginfo`)
The pinginfo component:
- Measures network latency to multiple AWS regions (us-east-1, us-west-2, eu-west-2, ap-southeast-1, ap-northeast-1)
- Provides a GraphQL API for retrieving latency information
- Converts response time to milliseconds for easy consumption
- Implements proper error handling with specific error types
- Uses structured logging and tracing

## Data Models

### Fetcher
- Simulated odds updates with:
  - `eventId`: Identifier for the sporting event
  - `homeOdds`: Odds for home team win
  - `awayOdds`: Odds for away team win
  - `drawOdds`: Odds for a draw

### PingInfo
- Latency measurements with:
  - `pingLocation`: AWS region identifier
  - `pingLatency`: Measured latency in milliseconds

## Integration Points

The Third Party Service integrates with:
- **EventBridge**: For publishing odds updates from the Fetcher service
- **AppSync**: For GraphQL API endpoints from the PingInfo service
- **EC2 API**: For measuring latency to different regions

## Use Cases

### Fetcher
- Simulating real-world odds updates from external providers
- Keeping the sportsbook's odds current and competitive
- Triggering market updates based on external data
- Applying realistic house edge to maintain profitability

### PingInfo
- Monitoring network performance across regions
- Helping users select optimal regions for low-latency betting
- Supporting operational monitoring and troubleshooting

## Example Responses

### Fetcher EventBridge Event
```json
{
  "Source": "com.thirdparty",
  "DetailType": "UpdatedOdds",
  "Detail": {
    "eventId": "e46436a8-a916-4143-a05c-99d120eabfdb",
    "homeOdds": "2.5",
    "awayOdds": "3.2",
    "drawOdds": "4.1"
  },
  "EventBusName": "sportsbook-events"
}
```

### PingInfo GraphQL Response
```json
{
  "data": {
    "getPingInfo": {
      "__typename": "PingInfo",
      "items": [
        {
          "pingLocation": "us-east-1",
          "pingLatency": 45
        },
        {
          "pingLocation": "us-west-2",
          "pingLatency": 78
        },
        {
          "pingLocation": "eu-west-2",
          "pingLatency": 120
        },
        {
          "pingLocation": "ap-southeast-1",
          "pingLatency": 180
        },
        {
          "pingLocation": "ap-northeast-1",
          "pingLatency": 150
        }
      ]
    }
  }
}
```

## Monitoring and Observability

The service uses:
- AWS Lambda Powertools for structured logging
- AWS X-Ray for distributed tracing
- CloudWatch for metrics and logs
