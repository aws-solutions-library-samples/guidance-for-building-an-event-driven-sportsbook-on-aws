import { generateClient } from 'aws-amplify/api';
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import * as queries from "../graphql/queries.js";
import * as mutations from "../graphql/mutations.js";

export const CACHE_PATH = "bets";

const client = generateClient();

export const useBets = (config = {}) => {
  return useQuery({
    queryKey: [CACHE_PATH],
    queryFn: async () => {
      const res = await client.graphql({ query: queries.getBets });
      const bets = res.data.getBets;
      if (bets["__typename"].includes("Error"))
        throw new Error(bets["message"]);

      // Ensure all odds are properly formatted as strings
      const formattedBets = bets.items.map(bet => {
        // Parse the odds to ensure it's a proper number
        const decimalOdds = parseFloat(bet.odds);

        return {
          ...bet,
          odds: decimalOdds.toString() // Convert back to string for consistency
        };
      });

      return formattedBets;
    },
    refetchInterval: 0,
    useErrorBoundary: false,
    enabled: true,
    retry: true,
    retryDelay: 2000,
    ...config,
  });
};

export const useCreateBets = (config = {}) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ data }) => {
      // Use the decimal odds for creating bets
      // The backend will continue to use decimal odds for all calculations
      const betsWithDecimalOdds = {
        ...data,
        bets: data.bets.map(bet => ({
          ...bet,
          // Keep the odds as decimal (they're already in decimal format)
        }))
      };

      const res = await client.graphql({
        query: mutations.createBets,
        variables: { input: betsWithDecimalOdds },
      });

      const bets = res.data.createBets;
      if (bets["__typename"].includes("Error"))
        throw new Error(bets["__typename"]);

      return res;
    },
    onSuccess: () => {
      return queryClient.invalidateQueries({ queryKey: [CACHE_PATH] });
    },
    onError: (err) => {
      return err;
    },
    ...config,
  });
};

const hooks = {
  useBets,
  useCreateBets,
};

export default hooks;