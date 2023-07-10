deduct_funds = """
mutation DeductFunds($input: DeductFundsInput!) {
  deductFunds(input: $input) {
    ... on Wallet {
      __typename
      balance
    }
    ... on Error {
      __typename
      message
    }
  }
}
"""