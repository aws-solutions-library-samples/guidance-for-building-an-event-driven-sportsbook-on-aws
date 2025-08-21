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
export const createBets = /* GraphQL */ `
  mutation CreateBets($input: CreateBetsInput) {
    createBets(input: $input) {
      ... on BetList {
        __typename
        nextToken
        items {
          betId
          amount
          outcome
          odds
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
      }
      ... on Error {
        __typename
        message
      }
    }
  }
`;

export const lockUser = /* GraphQL */ `
  mutation LockUser($input: LockUserInput) {
    lockUser(input: $input) {
      ... on User {
        __typename
        userId
        isLocked
      }
      ... on Error {
        __typename
        message
      }
    }
  }
`;

export const triggerFinishEvent = /* GraphQL */ `
  mutation TriggerFinishEvent($input: FinishEventInput) {
    triggerFinishEvent(input: $input) {
      ... on Event {
        __typename
        eventId
        eventStatus
      }
      ... on Error {
        __typename
        message
      }
    }
  }
`;
export const suspendMarketMutation = /* GraphQL */ `
  mutation SuspendMarket($input: SuspendMarketInput!) {
    suspendMarket(input: $input) {
      ... on Event {
        eventId
        marketstatus {
          name
          status
        }
      }
      ... on Error {
        __typename
        message
      }
    }
  }
`;

export const unsuspendMarketMutation = /* GraphQL */ `
  mutation UnsuspendMarket($input: UnsuspendMarketInput!) {
    unsuspendMarket(input: $input) {
      ... on Event {
        eventId
        marketstatus {
          name
          status
        }
      }
      ... on Error {
        __typename
        message
      }
    }
  }
`;

export const closeMarketMutation = /* GraphQL */ `
  mutation CloseMarket($input: CloseMarketInput!) {
    closeMarket(input: $input) {
      ... on Event {
        eventId
        marketstatus {
          name
          status
        }
      }
      ... on Error {
        __typename
        message
      }
    }
  }
`;

export const triggerSuspendMarketMutation = /* GraphQL */ `
  mutation TriggerSuspendMarket($input: SuspendMarketInput!) {
    triggerSuspendMarket(input: $input) {
      ... on Event {
        eventId
        marketstatus {
          name
          status
        }
      }
      ... on Error {
        __typename
        message
      }
    }
  }
`;

export const triggerUnsuspendMarketMutation = /* GraphQL */ `
  mutation TriggerUnsuspendMarket($input: UnsuspendMarketInput!) {
    triggerUnsuspendMarket(input: $input) {
      ... on Event {
        eventId
        marketstatus {
          name
          status
        }
      }
      ... on Error {
        __typename
        message
      }
    }
  }
`;

