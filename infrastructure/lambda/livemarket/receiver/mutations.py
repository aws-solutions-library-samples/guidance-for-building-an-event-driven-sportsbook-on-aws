update_event_odds = """
mutation MyMutation ($input: UpdateEventOddsInput!) {
  updateEventOdds(input: $input) {
    ... on Event {
      __typename
      start
      odds
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
