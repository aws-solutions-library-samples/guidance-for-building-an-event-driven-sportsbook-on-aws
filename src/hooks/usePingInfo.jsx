import { generateClient } from "aws-amplify/api";
import { useQuery } from "@tanstack/react-query";
import * as queries from "../graphql/queries.js";


export const CACHE_PATH = "de-ping-info-def";

const client = generateClient();

export const usePingInfo = (config = {}) => {
    return useQuery(
      [CACHE_PATH],
      () =>
        client.graphql({ query: queries.getPingInfo }).then((res) => {
          const pingInfo = res.data.getPingInfo;
          if (pingInfo["__typename"].includes("Error"))
            throw new Error(wallet["message"]);
          return pingInfo;
        }),
      {
        refetchInterval: 0,
        useErrorBoundary: false,
        enabled: true,
        retry: true,
        retryDelay: 2000,
        ...config,
      }
    );
  };

  const hooks = {
    usePingInfo,
  };
  
  export default hooks;
  
