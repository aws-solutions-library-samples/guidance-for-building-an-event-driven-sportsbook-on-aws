import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { API, graphqlOperation } from "aws-amplify";
import { Auth } from "aws-amplify";

import * as queries from "../graphql/queries.js";
import * as mutations from "../graphql/mutations.js";
import * as subscriptions from "../graphql/subscriptions.js";

export const CACHE_PATH = "events";

/*
const marketStatusSub = API.graphql(
  graphqlOperation(subscriptions.marketStatusUpdated)
).subscribe({
  next: ({ provider, value }) => {
    const eventId = value.data.marketStatusUpdated.eventId;
    const marketStatus = value.data.marketStatusUpdated.marketstatus || [];
    queryClient.setQueryData([CACHE_PATH], (oldData) => {
      const updatedEvents = oldData.map((event) => {
        if (event.eventId === eventId) {
          event.marketstatus = marketStatus;
        }
        return event;
      });
      return updatedEvents;
    });
    setSuspendedMarkets((prevState) => ({
      ...prevState,
      [eventId]: marketStatus.reduce(
        (acc, market) => ({
          ...acc,
          [market.name]: market.status === "Suspended",
        }),
        {}
      ),
    }));
  },
  error: (error) => console.warn(error),
});*/



export const useMarket = (user) => {
  const [suspendedMarkets, setSuspendedMarkets] = useState([]);
  const queryClient = useQueryClient();
  useEffect(() => {
    //make initial call to live market receiver getEvents and populate suspendedMarkets
    const marketStatusInitial = API.graphql(graphqlOperation(queries.getEvents)).then((data) => {
      const events = data.data.getEvents.items;
      const marketStatus = events.map((event) => ({
        eventId: event.eventId,
        marketstatus: event.marketstatus,
      }));
      setSuspendedMarkets(marketStatus);
      return ;
      //setSuspendedMarkets(marketStatus);
    });
    
    


    const sub = API.graphql(
      graphqlOperation(subscriptions.marketStatusUpdated)
    ).subscribe({
      next: ({ provider, value }) => {
        queryClient.setQueryData([CACHE_PATH], (oldData) => {
          const updatedEvents = oldData.map((event) => {
            if (event.eventId === value.data.marketStatusUpdated.eventId) {
              event.marketstatus = value.data.marketStatusUpdated.marketstatus;
            }
            return event;
          });
          return updatedEvents;
        });
        //Update suspendedMarkets with new values retrieved from subscription handler. 
        //SuspendedMarkets should follow the format [{eventId:xxxx, marketStatus: {name:yyyy, status: zzzz}}]
        setSuspendedMarkets((prevState) => {
          const eventIndex = (prevState.findIndex!==undefined)?prevState.findIndex(
            (event) => event.eventId === value.data.marketStatusUpdated.eventId
          ):-1;
        

          if (eventIndex === -1) {
            // If the event is not found in the previous state, add a new entry
            return [
              ...prevState,
              {
                eventId: value.data.marketStatusUpdated.eventId,
                marketstatus: value.data.marketStatusUpdated.marketstatus.reduce(
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

            updatedState[eventIndex].marketstatus = value.data.marketStatusUpdated.marketstatus.map(marketstatus => ({
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
  }, []);

  return suspendedMarkets;
};


  export const useEvents = (config = {}) => {
    const queryClient = useQueryClient();
    const dateKeys = ["start", "end", "updatedAt"];
    const deserializer = deserializeEvent([dateKeys]);
    //const [suspendedMarkets, setSuspendedMarkets] = useState(null);

    useEffect(() => {
      const sub = API.graphql(
        graphqlOperation(subscriptions.updatedEventOdds)
      ).subscribe({
        next: ({ provider, value }) => {
          queryClient.setQueryData([CACHE_PATH], (oldData) => {
            const newEvent = deserializer(value.data.updatedEventOdds);
            const newItems = oldData.filter(
              (e) => e.eventId !== newEvent.eventId
            );
            newItems.push(newEvent);
            return newItems;
          });
        },
        error: (error) => console.warn(error),
      });

      
      
      return () => {
        sub.unsubscribe();
        //marketStatusSub.unsubscribe();
      };
    }, []);

    return useQuery(
      [CACHE_PATH],
      () =>
        API.graphql({ query: queries.getEvents }).then((res) => {
          const result = res?.data?.getEvents?.items ?? [];
          return result.map(deserializer);
        }),
      {
        refetchInterval: 0,
        useErrorBoundary: false,
        enabled: true,
        ...config,
      }
    );
  };
  
// New hooks to handle "Suspend" and "Close" mutations
export const useSuspendMarket = (config = {}) => {
  const queryClient = useQueryClient();
  return useMutation(
    // Implement the GraphQL mutation to suspend a market
    // ...
    {
      onSuccess: () => {
        return queryClient.invalidateQueries([CACHE_PATH]);
      },
      onError: (err, { id, dataType }) => {
        console.error(err);
      },
      ...config,
    }
  );
};

export const useCloseMarket = (config = {}) => {
  const queryClient = useQueryClient();
  return useMutation(
    // Implement the GraphQL mutation to close a market
    // ...
    {
      onSuccess: () => {
        return queryClient.invalidateQueries([CACHE_PATH]);
      },
      onError: (err, { id, dataType }) => {
        console.error(err);
      },
      ...config,
    }
  );
};

export const useFinishEvent = (config = {}) => {
  const queryClient = useQueryClient();
  return useMutation(
    ({ data }) =>
      API.graphql({
        query: mutations.triggerFinishEvent,
        variables: { input: data },
      }),
    {
      onSuccess: () => {
        return queryClient.invalidateQueries([CACHE_PATH]);
      },
      onError: (err, { id, dataType }) => {
        console.error(err);
      },
      ...config,
    }
  );
};

const deserializeEvent = (dateKeys) => (event) => {
  return Object.fromEntries(
    Object.entries(event).map(([k, v]) =>
      dateKeys.includes(k) ? [k, new Date(v)] : [k, v]
    )
  );
};

const hooks = {
  useEvents: useEvents,
  useFinishEvent: useFinishEvent,
  useMarket: useMarket
};

export default hooks;
