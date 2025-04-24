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
    
    // Ensure all odds are parsed as numbers for calculations
    const homeOdds = parseFloat(result.homeOdds);
    const awayOdds = parseFloat(result.awayOdds);
    const drawOdds = parseFloat(result.drawOdds);
    
    // console.log(`Event ${eventId} odds: home=${homeOdds}, away=${awayOdds}, draw=${drawOdds}`);
    
    return {
      ...result,
      homeOdds: homeOdds.toString(),
      awayOdds: awayOdds.toString(),
      drawOdds: drawOdds.toString()
    };
  });

const hooks = {
  useEvent,
};

export default hooks;
