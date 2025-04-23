"""
Mock implementation of mutations for testing.
"""

# Mock mutation for updating event odds
update_event_odds = """
mutation UpdateEventOdds($input: UpdateEventOddsInput!) {
  updateEventOdds(input: $input) {
    __typename
    ... on Event {
      eventId
      homeTeam
      awayTeam
      startTime
      homeOdds
      awayOdds
      drawOdds
      eventStatus
    }
    ... on Error {
      message
    }
  }
}
"""

# Mock mutation for adding an event
add_event = """
mutation AddEvent($input: AddEventInput!) {
  addEvent(input: $input) {
    __typename
    ... on Event {
      eventId
      home
      away
      homeOdds
      awayOdds
      drawOdds
      start
      end
      updatedAt
      duration
      eventStatus
    }
    ... on Error {
      message
    }
  }
}
"""

# Mock mutation for finishing an event
finish_event = """
mutation FinishEvent($input: FinishEventInput!) {
  finishEvent(input: $input) {
    __typename
    ... on Event {
      eventId
      eventStatus
      outcome
    }
    ... on Error {
      message
    }
  }
}
"""

# Mock mutation for suspending a market
suspend_market = """
mutation SuspendMarket($input: MarketInput!) {
  suspendMarket(input: $input) {
    __typename
    ... on Event {
      eventId
      marketstatus {
        name
        status
      }
    }
    ... on Error {
      message
    }
  }
}
"""

# Mock mutation for unsuspending a market
unsuspend_market = """
mutation UnsuspendMarket($input: MarketInput!) {
  unsuspendMarket(input: $input) {
    __typename
    ... on Event {
      eventId
      marketstatus {
        name
        status
      }
    }
    ... on Error {
      message
    }
  }
}
"""
