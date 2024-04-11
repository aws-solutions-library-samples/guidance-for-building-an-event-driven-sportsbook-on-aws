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
      eventStatus
    }
    ... on Error {
      __typename
      message
    }
  }
}
"""
