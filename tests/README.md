# Sportsbook EDA Tests

This directory contains tests for the Sportsbook EDA application services.

## Test Structure

- `conftest.py`: Contains pytest fixtures shared across test modules
- `wallet/`: Tests for the wallet service
- `requirements-test.txt`: Test dependencies

## Running Tests

To run the tests, first install the test dependencies:

```bash
pip install -r tests/requirements-test.txt
```

Then run the tests using pytest:

```bash
# Run all tests
pytest tests/

# Run specific test module
pytest tests/wallet/test_wallet_resolvers.py

# Run with coverage report
pytest tests/ --cov=infrastructure/lambda
```

## Test Fixtures

The `conftest.py` file provides several fixtures for testing:

- `aws_credentials`: Sets up mock AWS credentials
- `dynamodb_client`: Provides a mocked DynamoDB client
- `dynamodb_resource`: Provides a mocked DynamoDB resource
- `events_client`: Provides a mocked EventBridge client
- `wallet_table`: Creates a test DynamoDB table for wallets
- `event_bus`: Creates a test EventBridge event bus
- Various AppSync event fixtures for different operations

## Mocking AWS Services

Tests use the `moto` library to mock AWS services:

- DynamoDB for data storage
- EventBridge for event publishing

This allows tests to run without actual AWS resources while still testing the service logic.

## Adding New Tests

To add tests for a new service:

1. Create a new directory under `tests/` for the service
2. Add test modules with appropriate test cases
3. Add any necessary fixtures to `conftest.py`
4. Update this README with information about the new tests
