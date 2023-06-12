update_event_odds = """
mutation MyMutation ($input: UpdateEventOddsInput!) {
  updateEventOdds(input: $input) {
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
      updatedAt
    }
    ... on Error {
      __typename
      message
    }
  }
}
"""
