# User Service

## Overview
The User Service is a core component of the Sportsbook application that manages user accounts, authentication, and user-specific operations. It provides functionality for user account management, including the ability to lock and unlock user accounts for security and compliance purposes.

## Architecture
The service follows a serverless architecture built on AWS with the following components:

- **Resolvers**: Lambda functions that handle GraphQL API requests for user operations
- **Cognito Integration**: Direct integration with AWS Cognito User Pools for user management
- **EventBridge Integration**: Publishes user-related events to EventBridge for consumption by other services

## Key Features

- **User Account Management**: Provides operations to manage user accounts
- **Account Locking**: Ability to lock and unlock user accounts for security purposes
- **Event Publication**: Publishes events when user account status changes
- **Authentication Integration**: Seamless integration with AWS Cognito for authentication
- **GraphQL API**: Provides a robust API for user management operations
- **Error Handling**: Comprehensive error handling with proper exception management
- **Logging**: Structured logging with AWS Lambda Powertools

## Components

### Resolvers (`/resolvers`)
The resolvers component handles GraphQL API requests for:
- Locking user accounts (`lockUser`)
- Locking user accounts and generating events (`lockUserGenerateEvent`)

Each resolver includes:
- Input validation
- Error handling with specific error types
- Structured logging
- Comprehensive documentation

## Data Model

User data is primarily stored in AWS Cognito User Pools with the following key attributes:
- `userId`: Unique identifier for the user (sub)
- `custom:isLocked`: Boolean attribute indicating if the user account is locked

## Integration Points

The User Service integrates with:
- **AWS Cognito**: For user authentication and storage of user attributes
- **EventBridge**: For publishing user-related events
- **Wallet Service**: Indirectly through events for wallet-related operations
- **Frontend Application**: Provides API for user management

## Event Flow

1. User or administrator initiates an account lock/unlock operation
2. The resolver updates the user attributes in Cognito
3. An event is published to EventBridge with the user status change
4. Other services can subscribe to these events to take appropriate actions

## Testing

The User Service includes comprehensive unit tests:
- Tests for account locking and unlocking
- Tests for event generation
- Tests for error handling scenarios

Tests are implemented using pytest and mock AWS services to ensure the service functions correctly in isolation.

## Security

The service implements security through:
- AWS Cognito User Pools for secure authentication
- Input validation for all API operations
- Proper error handling and logging
- AWS IAM roles and policies for access control
- Prevention of information leakage

## Event Structure

The service publishes events with the following structure:

```json
{
  "Source": "com.pam",
  "DetailType": "userLocked",
  "Detail": {
    "__typename": "User",
    "isLocked": "true"
  },
  "EventBusName": "sportsbook-event-bus"
}
```

## Use Cases

The User Service supports several key use cases:
- **Account Security**: Locking accounts in case of suspicious activity
- **Compliance**: Restricting access for users who violate terms of service
- **Account Recovery**: Managing the account locking process during recovery
- **User Management**: Administrative control over user accounts

## Error Handling

The service handles various error scenarios:
- Unknown errors with appropriate error messages
- Proper logging of errors for troubleshooting
- Structured error responses for API consumers

## Monitoring and Observability

The service uses:
- AWS Lambda Powertools for structured logging
- AWS X-Ray for distributed tracing
- CloudWatch for metrics and logs
