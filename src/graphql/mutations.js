export const createWallet = /* GraphQL */ `
  mutation CreateWallet($input: CreateWalletInput) {
    createWallet(input: $input) {
      ... on Wallet {
        __typename
        userId
        balance
      }
      ... on Error {
        __typename
        message
      }
    }
  }
`;
export const withdrawFunds = /* GraphQL */ `
  mutation WithdrawFunds($input: WithdrawOrDepositInput) {
    withdrawFunds(input: $input) {
      ... on Wallet {
        __typename
        userId
        balance
      }
      ... on Error {
        __typename
        message
      }
    }
  }
`;
export const depositFunds = /* GraphQL */ `
  mutation DepositFunds($input: WithdrawOrDepositInput) {
    depositFunds(input: $input) {
      ... on Wallet {
        __typename
        userId
        balance
      }
      ... on Error {
        __typename
        message
      }
    }
  }
`;
