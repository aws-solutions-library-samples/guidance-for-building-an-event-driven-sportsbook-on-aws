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

finish_event = """
mutation FinishEvent ($input: FinishEventInput!) {
  finishEvent(input: $input) {
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

add_event = """
mutation AddEvent ($input: AddEventInput!) {
  addEvent(input: $input) {
    ... on Event {
      __typename
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
      __typename
      message
    }
  }
}
"""

lock_bets_for_event = """
mutation MyMutation ($input: LockBetsForEventInput!){
  lockBetsForEvent (input: $input){
    ... on BetList {
      __typename
      nextToken
      items {
        amount
        userId
        betId
        odds
        outcome
        event{
          eventId
        }
      }
    }
    ... on UnknownError {
      __typename
      message
    }
    ... on InputError {
      __typename
      message
    }
    ... on NotFoundError {
      __typename
      message
    }
    ... on InsufficientFundsError {
      __typename
      message
    }
  }
}
"""
