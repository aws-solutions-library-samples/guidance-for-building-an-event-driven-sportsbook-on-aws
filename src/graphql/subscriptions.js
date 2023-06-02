/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const updatedEventOdds = /* GraphQL */ `
  subscription UpdatedEventOdds {
    updatedEventOdds {
      ... on Event {
        eventId
        odds
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
