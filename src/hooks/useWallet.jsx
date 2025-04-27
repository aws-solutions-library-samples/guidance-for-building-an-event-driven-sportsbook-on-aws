import { generateClient } from "aws-amplify/api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import * as queries from "../graphql/queries.js";
import * as mutations from "../graphql/mutations.js";

export const CACHE_PATH = "wallet";
const client = generateClient();

export const useWallet = (config = {}) => {
  return useQuery(
    [CACHE_PATH],
    () =>
      client.graphql({ query: queries.getWallet }).then((res) => {
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
      client.graphql({
        query: mutations.withdrawFunds,
        variables: { input: data },
      }).then((res)=> {
        const wallet = res.data.withdrawFunds;
        if (wallet["__typename"].includes("Error"))
          throw new Error(wallet["message"]);
        return wallet;
      }),
    {
      onSuccess: () => {
        return queryClient.invalidateQueries([CACHE_PATH]);
      },
      onError: (err, { id, dataType }) => {
        return { err };
      },
      ...config,
    }
  );
};

export const useDepositFunds = (config = {}) => {
  const queryClient = useQueryClient();
  return useMutation(
    ({ data }) =>
      client.graphql({
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
