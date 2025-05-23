# Sportsbook EDA - Project Overview

## Architecture Overview

The Sportsbook EDA (Event-Driven Architecture) is a comprehensive serverless application built on AWS that demonstrates a modern approach to building a sports betting platform. The application follows an event-driven microservices architecture, leveraging AWS serverless technologies to provide scalability, reliability, and maintainability.

## Core Technologies

- **AWS Serverless Stack**:
  - AWS Lambda for compute
  - Amazon DynamoDB for data storage
  - AWS AppSync for GraphQL API
  - Amazon EventBridge for event bus
  - AWS Cognito for authentication
  - AWS CloudFront for content delivery
  - AWS S3 for static web hosting
  - AWS SAM for infrastructure as code

- **Frontend**:
  - React.js with hooks
  - Material-UI for components
  - AWS Amplify for authentication and API integration
  - Apollo Client for GraphQL operations

- **Backend**:
  - Python 3.12 for Lambda functions
  - TypedDict for type safety
  - AWS Lambda Powertools for observability
  - EventBridge for inter-service communication

## Microservices Architecture

The application is composed of several microservices, each responsible for a specific domain:

1. **Auth Service**: Handles user authentication and authorization using AWS Cognito
   - Manages user sign-up, sign-in, and session management
   - Triggers wallet creation for new users

2. **Wallet Service**: Manages user funds
   - Provides deposit and withdrawal functionality
   - Tracks user balances
   - Validates fund availability for betting operations
   - Uses DynamoDB for persistent storage

3. **Betting Service**: Core betting functionality
   - Allows users to place bets on events
   - Manages bet status and settlement
   - Integrates with Wallet Service for fund management
   - Publishes bet-related events

4. **Live Market Service**: Manages real-time market data
   - Handles event odds and updates
   - Provides market suspension and resumption capabilities
   - Maintains event status (running, finished, settled)

5. **Sporting Events Service**: Manages sporting event data
   - Tracks event details, teams, and schedules
   - Publishes event status updates
   - Handles event creation and updates

6. **System Events Service**: Centralized event monitoring
   - Captures system-wide events for monitoring
   - Provides visibility into application activity
   - Supports debugging and troubleshooting

7. **Trading Service**: Handles odds management
   - Calculates and updates odds
   - Manages risk and exposure
   - Integrates with third-party providers

8. **User Service**: User profile management
   - Stores user preferences and settings
   - Manages user status (locked/unlocked)
   - Handles user-related operations

9. **GraphQL Service**: API layer
   - Provides unified API access through AppSync
   - Implements resolvers for various operations
   - Handles authentication and authorization

10. **Third Party Service**: External integrations
    - Connects with external data providers
    - Handles third-party API communication
    - Normalizes external data formats

## Event-Driven Communication

The application uses Amazon EventBridge as the central event bus for asynchronous communication between services. This approach:

- Decouples services for better maintainability
- Enables real-time updates across the application
- Supports eventual consistency patterns
- Facilitates extensibility through event subscribers

Key event types include:
- User registration events
- Wallet transaction events
- Bet placement events
- Market status changes
- Event outcome settlement
- System notifications

## Data Flow

1. **User Authentication**:
   - Users authenticate via Cognito
   - Auth tokens are used for API authorization
   - New user registration triggers wallet creation

2. **Betting Flow**:
   - User views available events from Live Market Service
   - User selects bets and adds to bet slip
   - Betting Service validates bets and checks funds with Wallet Service
   - Funds are deducted and bets are recorded
   - Events are published for bet placement

3. **Settlement Flow**:
   - Event outcomes are determined
   - Betting Service settles bets based on outcomes
   - Winning bets trigger payouts via Wallet Service
   - Settlement events are published

4. **Market Management**:
   - Trading Service updates odds
   - Live Market Service publishes market updates
   - Markets can be suspended or closed based on conditions

## Frontend Architecture

The React frontend uses:
- Component-based architecture with functional components
- React hooks for state management
- Context providers for shared state
- Custom hooks for API operations
- Responsive design with Material-UI
- Real-time updates via GraphQL subscriptions

Key components include:
- Authentication wrapper
- Event listings
- Bet slip management
- Wallet interface
- Admin controls
- System event monitoring

## Deployment and Infrastructure

The application is deployed using AWS SAM (Serverless Application Model):
- Infrastructure defined as code in template.yaml
- Nested stacks for individual services
- CloudFormation for resource provisioning
- CI/CD pipeline support

The frontend is deployed to:
- S3 for static hosting
- CloudFront for content delivery
- Custom domain support

## Security Considerations

- Cognito for authentication and authorization
- IAM roles for service permissions
- GraphQL API secured with Cognito and IAM
- Input validation on all operations
- Error handling with appropriate responses
- KMS for environment variable encryption

## Observability

- Structured logging with Lambda Powertools
- X-Ray for distributed tracing
- CloudWatch for metrics and logs
- System Events Service for application monitoring

## Testing Strategy

The application includes:
- Unit tests for Lambda functions
- Integration tests for service interactions
- End-to-end tests for critical flows
- Mock AWS services for local testing

## Key Features

- **User Management**: Registration, authentication, and profile management
- **Wallet Operations**: Deposits, withdrawals, and balance tracking
- **Event Browsing**: View and filter available sporting events
- **Betting**: Place bets on various outcomes with real-time odds
- **Real-time Updates**: Live odds changes and event status updates
- **Bet History**: View past bets and outcomes
- **Admin Controls**: Market management and system monitoring
- **Responsive Design**: Works on desktop and mobile devices

## Development Workflow

The project supports a modern development workflow with:
- Local development environment
- Pre-commit hooks for code quality
- TypeScript/Python type checking
- Comprehensive documentation
- Modular service architecture
