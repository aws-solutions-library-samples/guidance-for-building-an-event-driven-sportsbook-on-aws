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
