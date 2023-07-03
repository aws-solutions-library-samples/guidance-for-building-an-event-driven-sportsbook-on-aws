import { API } from "aws-amplify";
import { useQuery } from "@tanstack/react-query";
import * as queries from "../graphql/queries.js";

export const CACHE_PREFIX = "event-";

export const useEvent = (eventId, config = {}) => {
  return useQuery([CACHE_PREFIX, eventId], () => fetchEvent(eventId), {
    refetchInterval: 5000,
    useErrorBoundary: false,
    enabled: true,
    retry: true,
    retryDelay: 2000,
    ...config,
  });
};

export const fetchEvent = (eventId) =>
  API.graphql({
    query: queries.getEvent,
    variables: { eventId: eventId },
  }).then((res) => {
    const result = res.data.getEvent;
    if (result["__typename"].includes("Error"))
      throw new Error(result["message"]);
    return result;
  });

const hooks = {
  useEvent,
};

export default hooks;
