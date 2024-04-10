get_event = """
query GetEvent($eventId: ID!, $timestamp: Float) {
  getEvent(eventId: $eventId, timestamp: $timestamp) {
    ... on Event {
      __typename
      updatedAt
      start
      homeOdds
      home
      eventId
      end
      drawOdds
      awayOdds
      away
      outcome
    }
    ... on Error {
      __typename
      message
    }
  }
}
"""
