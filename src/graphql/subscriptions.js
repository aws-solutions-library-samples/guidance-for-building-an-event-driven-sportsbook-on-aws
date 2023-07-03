/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const updatedEventOdds = /* GraphQL */ `
  subscription UpdatedEventOdds {
    updatedEventOdds {
      ... on Event {
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
      ... on Error {
        message
      }
    }
  }
`;

export const updatedUserStatus = /* GraphQL */ `
  subscription UpdatedUserStatus {
    updatedUserStatus {
      ... on User {
        userId
        isLocked
      }
      ... on Error {
        message
      }
    }
  }
`;
