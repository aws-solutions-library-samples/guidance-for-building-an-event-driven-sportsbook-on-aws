import { useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { API, graphqlOperation } from "aws-amplify";
import { Auth } from "aws-amplify";

import * as queries from "../graphql/queries.js";
import * as mutations from "../graphql/mutations.js";
import * as subscriptions from "../graphql/subscriptions.js";

export const CACHE_PATH = "events";

export const useEvents = (config = {}) => {
  const queryClient = useQueryClient();
  const dateKeys = ["start", "end", "updatedAt"];
  const deserializer = deserializeEvent([dateKeys]);
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

    return () => sub.unsubscribe();
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
  useFinishEvent: useFinishEvent
};

export default hooks;
