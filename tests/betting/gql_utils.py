"""
Mock implementation of gql_utils for testing.
"""
from unittest.mock import MagicMock

def get_client(region, url):
    """
    Mock implementation of get_client function.
    Returns a mock GQL client.
    """
    mock_client = MagicMock()
    return mock_client
