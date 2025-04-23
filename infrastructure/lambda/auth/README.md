# Auth Service

## Overview
The Auth Service is a foundational component of the Sportsbook application that manages user authentication workflows and triggers downstream processes when authentication events occur. It integrates with AWS Cognito User Pools to handle user registration, confirmation, and sign-in processes.

## Architecture
The service follows a serverless architecture built on AWS with the following components:

- **Post Confirmation Lambda**: A Lambda function that executes after a user successfully confirms their registration
- **EventBridge Integration**: Publishes authentication events to EventBridge for consumption by other services

## Key Features

- **User Registration Flow**: Handles the post-confirmation step of user registration
- **Event Publication**: Publishes events when users complete registration
- **Cognito Integration**: Seamless integration with AWS Cognito User Pools
- **Event-Driven Architecture**: Enables downstream processes to react to authentication events
- **Error Handling**: Robust error handling with proper exception management
- **Logging**: Comprehensive logging with AWS Lambda Powertools

## Components

### Post Confirmation Lambda (`postConfirmation.py`)
The Post Confirmation Lambda function:
- Executes after a user successfully confirms their registration (email verification, phone verification, etc.)
- Captures the user ID from the Cognito event
- Publishes a `UserSignedUp` event to EventBridge
- Enables downstream services to perform user setup operations (e.g., wallet creation)
- Implements proper error handling with try-except blocks
- Uses structured logging for better observability

## Event Flow

1. User completes the registration process in AWS Cognito
2. User confirms their account (via email verification, phone verification, etc.)
3. Cognito triggers the Post Confirmation Lambda function
4. The Lambda function publishes a `UserSignedUp` event to EventBridge
5. Other services (like the Wallet Service) subscribe to this event and perform necessary setup operations

## Integration Points

The Auth Service integrates with:
- **AWS Cognito User Pools**: For user authentication and registration
- **EventBridge**: For publishing authentication events
- **Wallet Service**: Indirectly through events for wallet creation
- **User Service**: Indirectly through events for user setup

## Event Structure

The service publishes events with the following structure:

```json
{
  "Source": "com.auth",
  "DetailType": "UserSignedUp",
  "Detail": {
    "userId": "user-123"
  },
  "EventBusName": "sportsbook-event-bus"
}
```

## Testing

The Auth Service includes comprehensive unit tests:
- Tests for successful event publication
- Tests for different username scenarios
- Tests for error handling

Tests are implemented using pytest and mock AWS services to ensure the service functions correctly in isolation.

## Security

The service implements security through:
- AWS Cognito User Pools for secure authentication
- Proper event structure and validation
- AWS IAM roles and policies for access control
- Secure handling of user identifiers

## Monitoring and Observability

The service uses:
- AWS Lambda Powertools for structured logging
- AWS X-Ray for distributed tracing
- CloudWatch for metrics and logs

## Deployment

The Auth Service is deployed as part of the overall Sportsbook application using AWS SAM (Serverless Application Model). The deployment includes:
- Lambda functions for authentication triggers
- Integration with Cognito User Pools
- EventBridge rules for event routing
- IAM roles and policies for secure access
