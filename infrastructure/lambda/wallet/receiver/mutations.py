create_wallet = """
mutation CreateWallet ($input: CreateWalletInput!) {
  createWallet(input: $input) {
    ... on Wallet {
      __typename
      amount
      userId
    }
    ... on Error {
      __typename
      message
    }
  }
}
"""
