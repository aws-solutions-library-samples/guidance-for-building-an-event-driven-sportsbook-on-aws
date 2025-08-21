#!/bin/bash

# Install test dependencies if needed
pip install -r tests/requirements-test.txt

# Run tests with coverage and filter out deprecation warnings
PYTHONWARNINGS="ignore::DeprecationWarning" pytest tests/ --cov=infrastructure/lambda -v
