# Sportsbook EDA

## Pre-requisites
To deploy this sample you will need to install:
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)

First install the UI dependencies from the project root:

```bash
npm install
```

## Deployment

There are two stages to deploying:
1. Deploy the backend infrastructure
2. Deploy the frontend application

Run the following command from the repository root to deploy the backend:

```bash
sam build
sam deploy --guided --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_IAM
```

The default parameters can be accepted or overridden as desired.

The stack will be deployed and config will be saved to `samconfig.toml`.
You can omit the `--guided` and `--capabilities` CLI options for subsequent deployments: `sam build && sam deploy`

### Deploy the frontend application

To deploy the frontend application, run the following commands:

```bash
npm run config
npm run build
npm run deploy
```

In order, these commands:

1. Generates a `.env.local` file with stack outputs from the infrastructure build
2. Builds the frontend application
3. Copies the application build to the s3 bucket that CloudFront points at

### Accessing the Web App

After completing the deployment steps UI is available at the `WebUrl` displayed in the stack outputs.
If you need to obtain the deployed web URL at any point, run the following command
from the project root:

```bash
npm run-script echo-ui-url
```


<details>
  <summary>Expand for Claude LLM prompt</summary>
  
  **Wallet Component Documentation**

**Overview**
The Wallet component is a part of a betting application built on AWS. It allows users to deposit and withdraw funds from their wallets, which are used for placing bets on events. The component is built using React.js for the frontend, AWS AppSync for the GraphQL API, and AWS Lambda functions for the backend logic.

**Architecture**
The Wallet component follows a serverless architecture on AWS. The frontend is built with React.js and uses Apollo Client to interact with the GraphQL API provided by AWS AppSync. The backend consists of AWS Lambda functions that handle various operations such as creating wallets, depositing funds, withdrawing funds, and deducting funds.

The AWS AppSync API connects to the Lambda functions and provides a GraphQL interface for the frontend to interact with. The Lambda functions emit messages to Amazon EventBridge, which triggers other Lambda functions to handle specific events, such as creating a wallet when a new user signs up.

The application is deployed using AWS SAM (Serverless Application Model) and includes CloudFormation templates for all components.

**Key Components**

1. **Frontend**
   - `Wallet.jsx`: The main React component that renders the wallet UI and handles user interactions.
   - `useWallet.jsx`: A custom React hook that fetches wallet data from the backend using GraphQL queries.
   - `useWithdrawFunds.jsx`: A custom React hook that handles withdrawing funds from the wallet.
   - `useDepositFunds.jsx`: A custom React hook that handles depositing funds into the wallet.

2. **Backend**
   - `wallet-service.yaml`: The AWS SAM template that defines the AWS resources for the Wallet component, including Lambda functions, DynamoDB table, and AppSync resolvers.
   - `wallet/receiver/app.py`: A Lambda function that listens to events from Amazon EventBridge and creates wallets for new users.
   - `wallet/resolvers/app.py`: A Lambda function that handles GraphQL resolvers for wallet operations, such as getting wallet data, withdrawing funds, and depositing funds.

3. **GraphQL**
   - `schema.graphql`: The GraphQL schema that defines the types, queries, and mutations for the Wallet component and other components in the application.
   - `queries.js`: A file containing GraphQL query definitions for fetching data, such as wallet information and events.
   - `mutations.js`: A file containing GraphQL mutation definitions for modifying data, such as creating wallets, withdrawing funds, and depositing funds.

**Key Features**

- **User Authentication**: The application integrates with AWS Cognito User Pools for user authentication and authorization.
- **Wallet Management**: Users can create, deposit funds into, and withdraw funds from their wallets.
- **Event-Driven Architecture**: The application uses Amazon EventBridge to trigger various events and handle them asynchronously.
- **Distributed Tracing**: AWS X-Ray is used for distributed tracing, allowing for monitoring and troubleshooting of the application.
- **Error Handling**: Errors are handled gracefully, with appropriate error messages displayed to the user.
- **Serverless**: The application is built using serverless technologies, enabling scalability and cost-efficiency.

**Data Storage**
The wallet data is stored in an AWS DynamoDB table named `WalletDataStore`. Each user has a unique `userId` as the partition key, and their wallet balance is stored as a `balance` attribute.

**Request Handling**

1. **Frontend Requests**
   - The frontend uses Apollo Client to send GraphQL queries and mutations to the AWS AppSync API.
   - The `useWallet` hook in `useWallet.jsx` fetches the wallet data by executing the `getWallet` query.
   - The `useWithdrawFunds` and `useDepositFunds` hooks handle withdrawing and depositing funds by executing the `withdrawFunds` and `depositFunds` mutations, respectively.

2. **Backend Request Processing**
   - The AWS AppSync API maps incoming GraphQL operations to corresponding Lambda function resolvers defined in `wallet-service.yaml`.
   - The `wallet/resolvers/app.py` file contains the Lambda function handlers for the resolvers.
   - The `get_wallet`, `withdraw_funds`, and `deposit_funds` functions in `wallet/resolvers/app.py` handle the respective operations by interacting with the DynamoDB table.
   - The `create_wallet` function in `wallet/resolvers/app.py` creates a new wallet entry in the DynamoDB table when a new user signs up.
   - The `wallet/receiver/app.py` file contains a Lambda function that listens to events from Amazon EventBridge and triggers the creation of a new wallet when a `UserSignedUp` event is received.

**Key Methods**

1. **Frontend**
   - `useWallet`: A React hook that fetches the wallet data from the backend using the `getWallet` GraphQL query.
   - `useWithdrawFunds`: A React hook that executes the `withdrawFunds` GraphQL mutation to withdraw funds from the user's wallet.
   - `useDepositFunds`: A React hook that executes the `depositFunds` GraphQL mutation to deposit funds into the user's wallet.

2. **Backend**
   - `get_wallet`: A Lambda function resolver that retrieves the user's wallet data from the DynamoDB table.
   - `withdraw_funds`: A Lambda function resolver that deducts the specified amount from the user's wallet balance in the DynamoDB table.
   - `deposit_funds`: A Lambda function resolver that adds the specified amount to the user's wallet balance in the DynamoDB table.
   - `create_wallet`: A Lambda function resolver that creates a new wallet entry in the DynamoDB table for a new user.
   - `handle_auth_event`: A Lambda function handler in `wallet/receiver/app.py` that listens for `UserSignedUp` events and triggers the creation of a new wallet.

**Development and Deployment**
The Wallet component is developed and deployed using AWS SAM (Serverless Application Model). The deployment process involves packaging the Lambda functions, creating or updating the necessary AWS resources (e.g., DynamoDB table, Lambda functions, AppSync API), and deploying the frontend application.

**Testing and Monitoring**
Unit tests and integration tests should be implemented for the frontend and backend components to ensure the correctness of the application. AWS CloudWatch is used for monitoring and logging the application's performance and errors.

**Security Considerations**
The application follows best practices for security, including:

- User authentication and authorization using AWS Cognito User Pools
- API access control through AWS AppSync and AWS IAM roles
- Data encryption at rest (DynamoDB) and in transit (HTTPS)
- Secure deployment process using AWS SAM and CloudFormation

**Dependencies and External Services**
The Wallet component depends on the following AWS services:

- AWS Lambda
- AWS AppSync
- AWS DynamoDB
- AWS EventBridge
- AWS X-Ray
- AWS Cognito User Pools
- AWS CloudWatch

Additionally, the frontend depends on the following external libraries:

- React.js
- Apollo Client
- Material-UI
</details>