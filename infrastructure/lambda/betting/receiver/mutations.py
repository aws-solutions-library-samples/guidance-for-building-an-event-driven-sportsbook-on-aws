update_event_odds = """
mutation MyMutation ($input: UpdateEventOddsInput!) {
  updateEventStatus(input: $input) {
    ... on Event {
      __typename
      start
      homeOdds
      awayOdds
      drawOdds
      home
      eventId
      end
      away,
      updatedAt,
      status
    }
    ... on Error {
      __typename
      message
    }
  }
}
"""
