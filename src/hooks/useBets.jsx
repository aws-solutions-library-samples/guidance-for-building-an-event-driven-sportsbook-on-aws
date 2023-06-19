import { API } from "aws-amplify";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import * as queries from "../graphql/queries.js";
import * as mutations from "../graphql/mutations.js";

export const CACHE_PATH = "bets";

export const useBets = (config = {}) => {
  return useQuery(
    [CACHE_PATH],
    () =>
      API.graphql({ query: queries.getBets }).then((res) => {
        const bets = res.data.getBets;
        if (bets["__typename"].includes("Error"))
          throw new Error(bets["message"]);
        return bets.items;
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

export const useCreateBets = (config = {}) => {
  const queryClient = useQueryClient();
  return useMutation(
    ({ data }) =>
      API.graphql({
        query: mutations.createBets,
        variables: { input: data },
      }).then((res) => {
        const bets = res.data.createBets;
        if (bets["__typename"].includes("Error"))
          throw new Error(bets["message"]);
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

const hooks = {
  useBets,
  useCreateBets,
};

export default hooks;
