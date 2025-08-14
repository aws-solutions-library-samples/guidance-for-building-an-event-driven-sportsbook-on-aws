# Guidance for Building an Event-Driven Sportsbook on AWS

## Table of Contents

1. [Overview](#overview)
    - [Architecture](#high-level-architecture)
    - [Cost](#cost)
2. [Prerequisites](#prerequisites)
    - [Operating System](#operating-system)
3. [Deployment Steps](#deployment-steps)
4. [Deployment Validation](#deployment-validation)
5. [Running the Guidance](#running-the-guidance)
6. [Next Steps](#next-steps)
7. [Cleanup](#cleanup)
8. [Notices](#notices)

***Optional***

8. [FAQ, known issues, additional considerations, and limitations](#faq-known-issues-additional-considerations-and-limitations-optional)
9. [Revisions](#revisions-optional)
10. [Authors](#authors-optional)

## Overview

This application demonstrates how to build an event-driven, serverless sportsbook application on AWS to help betting operating operators effectively handle spiky and seasonal traffic. Using microservices and serverless computing, the application shows operators how to overcome the scaling limitations of traditional sportsbook applications. Each microservice has its own documentation that provides more details about its purpose, architecture, and implementation.

Select a link from the following list to learn more about the microservice.

- [Auth Service](/infrastructure/lambda/auth/README.md) - Handles user authentication and authorization
- [Betting Service](/infrastructure/lambda/betting/README.md) - Manages betting operations
- [GraphQL Service](/infrastructure/lambda/gql/README.md) - Provides the GraphQL API layer
- [Live Market Service](/infrastructure/lambda/livemarket/README.md) - Handles live market data
- [Sporting Events Service](/infrastructure/lambda/sportingevents/README.md) - Manages sporting event data
- [System Events Service](/infrastructure/lambda/systemevents/README.md) - Handles system-wide events
- [Third Party Service](/infrastructure/lambda/thirdparty/README.md) - Integrates with third-party providers
- [Trading Service](/infrastructure/lambda/trading/README.md) - Manages trading operations
- [User Service](/infrastructure/lambda/user/README.md) - Handles user management
- [Wallet Service](/infrastructure/lambda/wallet/README.md) - Manages user wallet operations

### High Level Architecture

![High Level Architecture Diagram](./assets/images/architecture.png)

### Cost

_You are responsible for the cost of the AWS services used while running this Guidance. As of August 2025, the cost for running this Guidance with the default settings in AWS Region US EAST 1 (N. Virginia) > is approximately $5.28 per month for processing 50 bets daily._


### Sample Cost Table

The following table provides a sample cost breakdown for deploying this Guidance with the default parameters in the US East (N. Virginia) Region for one month assuming **non-production** traffic volumes.

| AWS service  | Dimensions | Cost [USD] |
| ----------- | ------------ | ------------ |
| [AWS AppSync](https://aws.amazon.com/appsync/pricing/) | 850,000 API requests per month  | $ 3.40 |
| [Amazon Cognito](https://aws.amazon.com/cognito/pricing/) | 1 active user per month without advanced security feature | $ 0.05 |
| [Amazon SQS](https://aws.amazon.com/sqs/pricing/) | 0.8 million standard queue per month | $ 0.32 |
| [Amazon DynamoDB](https://aws.amazon.com/dynamodb/pricing/) | 1 GB storage, 150,000 write requests, 300,000 read requests per month | $ 0.36 |
| [AWS Lambda](https://aws.amazon.com/lambda/pricing/) | 1,500,000 requests per month with 200 ms average duration, 256 MB memory, 512 ephemeral storage | $ 0.10 |
| [AWS Step Functions](https://aws.amazon.com/step-functions/pricing/) | 6000 workflow requests per month with 3 state transitions per workflow | $ 0.35 |
| [Amazon EventBridge](https://aws.amazon.com/eventbridge/pricing/) | 1,000,000 invocations, 500,000 events ingested, 500,000 events delivered per month | $ 0.70 |

## Prerequisites

### Operating System

These deployment instructions are optimized to best work on a Linux based system. Deployment to other operating systems may require additional steps.

The following tools are required to install the sample application.
- AWS CLI >= 2.15
- AWS SAM CLI >= 1.136


### Third-party tools

- NodeJS >= 22.18
- Python >= 3.12


## Deployment Steps

1. Clone the repo using command.
    ```bash
    git clone https://github.com/aws-solutions-library-samples/guidance-for-building-an-event-driven-sportsbook-on-aws.git event-driven-sportsbook
    ```

2. Change directory to the repository folder.
    ```bash
    cd event-driven-sportsbook
    ```

3. Initialise a Python virtual environment.
    ```bash
    python3 -m venv .venv
    ```

4. Activate the virtual environment.
    ```bash
    source .venv/bin/activate
    ```

5. Install the required Python libraries to the virtual environment.
    ```bash
    python3 -m pip install -r requirements.txt
    ```

6. Build and deploy the microservices.
    ```bash
    sam build
    sam deploy --guided --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_IAM
    ```

7. Provide a value for the `Stack Name` and `AWS Region` when you are prompted by the guided deployment process. 
    - `Stack Name`
        - _**Description:**_ The name of the Cloudformation application stack.
        - _**Example:**_ `sportsbook`
    - `AWS Region`
        - _**Description:**_ The AWS region where the application will be deployed.
        - _**Example:**_ `eu-west-2`

8. Accept the default values for the following parameters.
    - `EventBusName`
    - `AccessLogsBucket`
    - `CognitoAdvancedSecurity`
    - `GeoRestrictiontype`
    - `GeoRestrictionLocation`
    - `DomainName`
    - `CertificateArn`

9. Install the web application npm dependencies.
    ```
    npm install
    ``` 

10. Update the web application configuration, then build and deploy the web application.
    ```bash
    npm run config
    npm run build
    npm run deploy
    ```
    
    >[!TIP]
    >In order, these commands:
    >1. Generates a `.env.local` file with stack outputs from the infrastructure build
    >2. Builds the frontend application
    >3. Copies the application build to the s3 bucket that CloudFront points at


## Deployment Validation

* Using the AWS Management Console, open CloudFormation and verify that the sportsbook CloudFormation stack was successfully deployed.
* Get the web application URL - WebUrl from the CloudFormation stack outputs.


## Running the Guidance

* Go to the web application using a web browser.
* Register an account using a valid email address.


## Next Steps

Complete the Event-driven Sportsbook workshop to understand how the application works.


## Cleanup

1. Log intto the AWS Management Console then empty the sportsbook WebUIBucket Amazon S3 bucket.

2. Delete the sportsbook CloudFormation stack by executing the following command from the project root directory.
    ```bash
    sam delete --config-file samconfig.toml
    ```


## Notices

Include below mandatory legal disclaimer for Guidance

*Customers are responsible for making their own independent assessment of the information in this Guidance. This Guidance: (a) is for informational purposes only, (b) represents AWS current product offerings and practices, which are subject to change without notice, and (c) does not create any commitments or assurances from AWS and its affiliates, suppliers or licensors. AWS products or services are provided “as is” without warranties, representations, or conditions of any kind, whether express or implied. AWS responsibilities and liabilities to its customers are controlled by AWS agreements, and this Guidance is not part of, nor does it modify, any agreement between AWS and its customers.*
