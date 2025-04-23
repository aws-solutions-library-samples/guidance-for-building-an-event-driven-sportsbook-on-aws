"""
Mock implementation of mutations for testing.
"""

# Mock mutations
lock_bets_for_event = """
mutation LockBetsForEvent($input: LockBetsForEventInput!) {
  lockBetsForEvent(input: $input) {
    __typename
    ... on BetList {
      items {
        userId
        betId
        eventId
        outcome
        amount
        odds
        betStatus
      }
    }
    ... on Error {
      message
    }
  }
}
"""

deduct_funds = """
mutation DeductFunds($input: DeductFundsInput!) {
  deductFunds(input: $input) {
    __typename
    ... on Wallet {
      userId
      balance
    }
    ... on InsufficientFundsError {
      message
    }
    ... on Error {
      message
    }
  }
}
"""

deposit_funds = """
mutation DepositFunds($input: DepositFundsInput!) {
  depositFunds(input: $input) {
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
