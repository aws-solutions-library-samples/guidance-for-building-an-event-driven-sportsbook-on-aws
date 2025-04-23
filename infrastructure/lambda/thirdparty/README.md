# Third Party Service

## Overview
The Third Party Service is a collection of components that integrate external functionality and data sources into the Sportsbook application. It provides various utilities including AI-powered chatbot support, external data fetching for odds updates, and network latency monitoring across different AWS regions.

## Architecture
The service follows a serverless architecture built on AWS with the following components:

- **Chatbot**: Lambda function that provides AI-powered customer support using Amazon Bedrock and Kendra
- **Fetcher**: Lambda function that simulates fetching updated odds from external providers
- **PingInfo**: Lambda function that measures and reports network latency to different AWS regions

## Key Features

- **AI-Powered Support**: Conversational chatbot using Claude models via Amazon Bedrock
- **Knowledge Retrieval**: Integration with Amazon Kendra for information retrieval
- **Odds Simulation**: Simulated third-party odds updates for sporting events
- **Network Latency Monitoring**: Real-time latency measurements across AWS regions
- **GraphQL API**: Provides APIs for chatbot interaction and latency information
- **Error Handling**: Comprehensive error handling with proper exception management
- **Logging**: Structured logging with AWS Lambda Powertools

## Components

### Chatbot (`/chatbot`)
The chatbot component provides:
- AI-powered customer support using Claude models via Amazon Bedrock
- Conversation history tracking in DynamoDB
- Integration with Amazon Kendra for knowledge retrieval
- Context-aware responses that include current sporting events
- Robust error handling
- Structured logging

### Fetcher (`/fetcher`)
The fetcher component simulates:
- Polling external APIs for updated odds
- Random generation of new odds for sporting events
- Publishing odds updates to EventBridge for consumption by other services
- Implementing proper error handling
- Using structured logging for better observability

### PingInfo (`/pinginfo`)
The pinginfo component provides:
- Network latency measurements to multiple AWS regions
- GraphQL API for retrieving latency information
- Real-time monitoring of network performance
- Error handling with specific error types
- Structured logging
- Comprehensive documentation

## Data Models

### Chatbot
- `sessionId`: Unique identifier for a chat session
- `prompt`: User message
- Conversation history stored in DynamoDB

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
- **Amazon Bedrock**: For AI-powered conversational capabilities
- **Amazon Kendra**: For knowledge retrieval and information search
- **EventBridge**: For publishing odds updates
- **DynamoDB**: For storing conversation history
- **AppSync**: For GraphQL API endpoints
- **Live Market Service**: Provides event data to the chatbot and receives odds updates

## Testing

The Third Party Service includes comprehensive unit tests:
- Tests for chatbot responses
- Tests for odds generation
- Tests for latency measurements
- Tests for error handling scenarios

Tests are implemented using pytest and mock AWS services to ensure the service functions correctly in isolation.

## Use Cases

### Chatbot
- Providing customer support for sportsbook users
- Answering questions about sporting events and betting
- Offering contextual information based on current events

### Fetcher
- Simulating real-world odds updates from external providers
- Keeping the sportsbook's odds current and competitive
- Triggering market updates based on external data

### PingInfo
- Monitoring network performance across regions
- Helping users select optimal regions for low-latency betting
- Supporting operational monitoring and troubleshooting

## Security

The service implements security through:
- Input validation for all API requests
- AWS IAM roles and policies for access control
- Secure integration with AWS services
- Proper error handling and logging
- Prevention of information leakage

## Example Interactions

### Chatbot
```
User: "What sporting events are happening today?"
Chatbot: "Currently running events include Manchester United vs Liverpool, LA Lakers vs Chicago Bulls, and Wimbledon Finals."
```

### PingInfo
```json
{
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
    }
  ]
}
```

## Monitoring and Observability

The service uses:
- AWS Lambda Powertools for structured logging
- AWS X-Ray for distributed tracing
- CloudWatch for metrics and logs
