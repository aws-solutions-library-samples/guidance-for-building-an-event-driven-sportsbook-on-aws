import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { generateClient } from 'aws-amplify/api';

import * as queries from "../graphql/queries.js";
import * as mutations from "../graphql/mutations.js";
import * as subscriptions from "../graphql/subscriptions.js";

export const CACHE_PATH = "events";
const client = generateClient();

export const useMarket = (user) => {
  const [suspendedMarkets, setSuspendedMarkets] = useState([]);
  const queryClient = useQueryClient();

  useEffect(() => {
    // Make initial call to live market receiver getEvents and populate suspendedMarkets
    const fetchInitialMarketStatus = async () => {
      try {
        const data = await client.graphql({ query: queries.getEvents });
        const events = data.data.getEvents.items;
        const marketStatus = events.map((event) => ({
          eventId: event.eventId,
          marketstatus: event.marketstatus,
        }));
        setSuspendedMarkets(marketStatus);
      } catch (error) {
        console.error("Error fetching initial market status:", error);
      }
    };

    fetchInitialMarketStatus();

    const sub = client.graphql({
      query: subscriptions.marketStatusUpdated
    }).subscribe({
      next: ({ data }) => {
        // Update query cache
        queryClient.setQueryData({
          queryKey: [CACHE_PATH],
          updater: (oldData) => {
            const updatedEvents = oldData.map((event) => {
              if (event.eventId === data.marketStatusUpdated.eventId) {
                event.marketstatus = data.marketStatusUpdated.marketstatus;
              }
              return event;
            });
            return updatedEvents;
          }
        });

        // Update suspendedMarkets state
        setSuspendedMarkets((prevState) => {
          const eventIndex = (prevState.findIndex !== undefined) ?
            prevState.findIndex(event => event.eventId === data.marketStatusUpdated.eventId) : -1;

          if (eventIndex === -1) {
            // If the event is not found in the previous state, add a new entry
            return [
              ...prevState,
              {
                eventId: data.marketStatusUpdated.eventId,
                marketstatus: data.marketStatusUpdated.marketstatus.reduce(
                  (acc, marketstatus) => ([{
                    ...acc,
                    ["status"]: marketstatus.status,
                    ["name"]: marketstatus.name,
                  }]),
                  {}
                ),
              },
            ];
          } else {
            // If the event is found in the previous state, update its marketStatus
            const updatedState = [...prevState];
            updatedState[eventIndex].marketstatus = data.marketStatusUpdated.marketstatus.map(marketstatus => ({
              status: marketstatus.status,
              name: marketstatus.name
            }));
            return updatedState;
          }
        });
      },
      error: (error) => console.warn(error),
    });

    return () => sub.unsubscribe();
  }, [queryClient]);

  return suspendedMarkets;
};

export const useEvents = (config = {}) => {
  const queryClient = useQueryClient();
  const dateKeys = ["start", "end", "updatedAt"];
  const deserializer = deserializeEvent([dateKeys]);

  useEffect(() => {
    // Subscribe to updated event odds
    const updatedEventSub = client.graphql({
      query: subscriptions.updatedEventOdds
    }).subscribe({
      next: ({ data }) => {
        queryClient.setQueryData({
          queryKey: [CACHE_PATH],
          updater: (oldData) => {
            const newEvent = deserializer(data.updatedEventOdds);
            const newItems = oldData.filter(e => e.eventId !== newEvent.eventId);
            newItems.push(newEvent);
            return newItems;
          }
        });
      },
      error: (error) => console.warn(error),
    });

    // Subscribe to new events
    const addEventSub = client.graphql({
      query: subscriptions.addEvent
    }).subscribe({
      next: ({ data }) => {
        queryClient.setQueryData({
          queryKey: [CACHE_PATH],
          updater: (oldData) => {
            const newEvent = deserializer(data.addEvent);
            const newItems = oldData.filter(e => e.eventId !== newEvent.eventId);
            newItems.push(newEvent);
            return newItems;
          }
        });
      },
      error: (error) => console.warn(error),
    });

    return () => {
      updatedEventSub.unsubscribe();
      addEventSub.unsubscribe();
    };
  }, [queryClient, deserializer]);

  return useQuery({
    queryKey: [CACHE_PATH],
    queryFn: async () => {
      const res = await client.graphql({ query: queries.getEvents });
      const result = res?.data?.getEvents?.items ?? [];

      // Make sure we're working with decimal odds
      const eventsWithDecimalOdds = result.map(event => {
        // Ensure all odds are parsed as numbers for calculations
        const homeOdds = parseFloat(event.homeOdds);
        const awayOdds = parseFloat(event.awayOdds);
        const drawOdds = parseFloat(event.drawOdds);

        return {
          ...event,
          homeOdds: homeOdds.toString(),
          awayOdds: awayOdds.toString(),
          drawOdds: drawOdds.toString()
        };
      });

      return eventsWithDecimalOdds.map(deserializer);
    },
    refetchInterval: 0,
    useErrorBoundary: false,
    enabled: true,
    ...config,
  });
};

// New hooks to handle "Suspend" and "Close" mutations
export const useSuspendMarket = (config = {}) => {
  const queryClient = useQueryClient();

  return useMutation({
    // Implement the GraphQL mutation to suspend a market
    mutationFn: async (variables) => {
      // Add your implementation here
      return {};
    },
    onSuccess: () => {
      return queryClient.invalidateQueries({ queryKey: [CACHE_PATH] });
    },
    onError: (err, variables) => {
      console.error(err);
    },
    ...config,
  });
};

export const useCloseMarket = (config = {}) => {
  const queryClient = useQueryClient();

  return useMutation({
    // Implement the GraphQL mutation to close a market
    mutationFn: async (variables) => {
      // Add your implementation here
      return {};
    },
    onSuccess: () => {
      return queryClient.invalidateQueries({ queryKey: [CACHE_PATH] });
    },
    onError: (err, variables) => {
      console.error(err);
    },
    ...config,
  });
};

export const useFinishEvent = (config = {}) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ data }) => {
      return client.graphql({
        query: mutations.triggerFinishEvent,
        variables: { input: data },
      });
    },
    onSuccess: () => {
      return queryClient.invalidateQueries({ queryKey: [CACHE_PATH] });
    },
    onError: (err, variables) => {
      console.error(err);
    },
    ...config,
  });
};

const deserializeEvent = (dateKeys) => (event) => {
  return Object.fromEntries(
    Object.entries(event).map(([k, v]) =>
      dateKeys.includes(k) ? [k, new Date(v)] : [k, v]
    )
  );
};

const hooks = {
  useEvents,
  useFinishEvent,
  useMarket
};

export default hooks;