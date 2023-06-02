export const getEvents = /* GraphQL */ `
  query GetEvents($startKey: String) {
    getEvents(startKey: $startKey) {
      ... on EventList {
        items {
          eventId
          odds
          home
          away
          start
          end
          updatedAt
        }
        nextToken
      }
      ... on Error {
        message
      }
    }
  }
`;
export const getWallet = /* GraphQL */ `
  query GetWallet {
    getWallet {
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
export const getWalletByUserId = /* GraphQL */ `
  query GetWalletByUserId($userId: ID!) {
    getWalletByUserId(userId: $userId) {
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
