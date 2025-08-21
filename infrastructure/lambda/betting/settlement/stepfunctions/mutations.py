deduct_funds = """
mutation DeductFunds ($input: DeductFundsInput!) {
  deductFunds(input: $input) {
    ... on Wallet {
      __typename
      balance
      userId
    }
    ... on Error {
      __typename
      message
    }
  }
}
"""

deposit_funds = """
mutation DepositFunds ($input: WithdrawOrDepositInput!) {
  depositFunds(input: $input) {
    ... on Wallet {
      __typename
      balance
      userId
    }
    ... on Error {
      __typename
      message
    }
  }
}
"""
