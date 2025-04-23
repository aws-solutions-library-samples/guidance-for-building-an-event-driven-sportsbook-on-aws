"""
Mock implementation of gql for testing.
"""

class gql:
    def __init__(self, query_string):
        self.query_string = query_string
