# GraphQL Utility Service

## Overview
The GraphQL Utility Service provides a shared library of utilities for interacting with AWS AppSync GraphQL APIs across the Sportsbook application. It simplifies the process of creating authenticated GraphQL clients and executing queries and mutations against AppSync endpoints from Lambda functions.

## Architecture
The service is implemented as a shared utility library that can be imported by other Lambda functions in the application. It provides:

- Authentication utilities for AWS AppSync
- Client creation for GraphQL operations
- Standardized approach to GraphQL interactions

## Key Features

- **AWS AppSync Integration**: Seamless integration with AWS AppSync GraphQL APIs
- **IAM Authentication**: Secure authentication using AWS Signature Version 4 (SigV4)
- **Client Management**: Simplified creation of GraphQL clients
- **Reusable Components**: Shared utilities to reduce code duplication across services
- **Standardized Approach**: Consistent pattern for GraphQL operations

## Components

### GraphQL Utilities (`gql_utils.py`)
The main utility module provides:
- `get_client()`: Function to create an authenticated GraphQL client for AppSync

## Usage

The GraphQL Utility Service can be imported and used by other Lambda functions as follows:

```python
from gql_utils import get_client
from gql import gql

# Create an authenticated client
region = "us-east-1"
appsync_url = "https://your-appsync-endpoint.amazonaws.com/graphql"
gql_client = get_client(region, appsync_url)

# Execute a GraphQL query or mutation
query = gql("""
    query GetWallet {
        getWallet {
            userId
            balance
        }
    }
""")

result = gql_client.execute(query)
```

## Authentication

The service handles authentication to AWS AppSync using AWS Signature Version 4 (SigV4), which:
- Uses AWS credentials from the Lambda execution environment
- Signs requests with the appropriate authentication headers
- Supports temporary credentials from IAM roles

## Integration Points

The GraphQL Utility Service integrates with:
- **AWS AppSync**: For executing GraphQL operations
- **IAM**: For authentication and authorization
- **Other Lambda Services**: Used by various services that need to make GraphQL calls

## Dependencies

The service depends on the following external libraries:
- `gql`: Python GraphQL client library
- `requests-aws4auth`: Library for AWS SigV4 authentication
- `requests`: HTTP library for making API calls
- `requests-toolbelt`: Extensions for the requests library

## Security

The service implements security through:
- AWS IAM authentication for AppSync
- Secure handling of AWS credentials
- HTTPS for all GraphQL communications
- Proper error handling

## Best Practices

When using the GraphQL Utility Service:
- Store AppSync endpoints in environment variables
- Handle GraphQL errors appropriately in your service
- Use specific queries rather than overfetching data
- Consider implementing retries for transient failures
- Cache GraphQL clients when appropriate for performance

## Deployment

The GraphQL Utility Service is deployed as part of the overall Sportsbook application using AWS SAM (Serverless Application Model). The deployment includes:
- Utility code packaged with Lambda functions that use it
- Dependencies specified in requirements.txt
