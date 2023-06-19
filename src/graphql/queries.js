export const getEvents = /* GraphQL */ `
  query GetEvents($startKey: String) {
    getEvents(startKey: $startKey) {
      ... on EventList {
        items {
          eventId
          homeOdds
          awayOdds
          drawOdds
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
export const getBets = /* GraphQL */ `
  query GetEvents($startKey: String) {
    getBets(startKey: $startKey) {
      ... on BetList {
        __typename
        items {
          betId
          odds
          outcome
          placedAt
          event {
            away
            awayOdds
            drawOdds
            end
            eventId
            home
            homeOdds
            start
            updatedAt
          }
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
