import { API } from "aws-amplify";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import * as queries from "../graphql/queries.js";
import * as mutations from "../graphql/mutations.js";

export const CACHE_PATH = "wallet";

export const useWallet = (config = {}) => {
  return useQuery(
    [CACHE_PATH],
    () =>
      API.graphql({ query: queries.getWallet }).then((res) => {
        const wallet = res.data.getWallet;
        if (wallet["__typename"].includes("Error"))
          throw new Error(wallet["message"]);
        return wallet;
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

export const useWithdrawFunds = (config = {}) => {
  const queryClient = useQueryClient();
  return useMutation(
    ({ data }) =>
      API.graphql({
        query: mutations.withdrawFunds,
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

export const useDepositFunds = (config = {}) => {
  const queryClient = useQueryClient();
  return useMutation(
    ({ data }) =>
      API.graphql({
        query: mutations.depositFunds,
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

const hooks = {
  useWallet,
  useWithdrawFunds,
  useDepositFunds,
};

export default hooks;
