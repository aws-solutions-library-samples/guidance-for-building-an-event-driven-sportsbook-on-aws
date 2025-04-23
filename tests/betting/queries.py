"""
Mock implementation of queries for testing.
"""

# Mock queries
get_event = """
query GetEvent($eventId: ID!, $timestamp: Float) {
  getEvent(eventId: $eventId, timestamp: $timestamp) {
    eventId
    homeTeam
    awayTeam
    homeOdds
    awayOdds
    draw
    outcome
  }
}
"""

get_wallet = """
query GetWallet($userId: ID!) {
  getWallet(userId: $userId) {
    __typename
    ... on Wallet {
      userId
      balance
    }
    ... on Error {
      message
    }
  }
}
"""
