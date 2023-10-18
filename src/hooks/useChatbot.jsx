import { API } from "aws-amplify";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import * as mutations from "../graphql/mutations.js";

export const CACHE_PATH = "chatbot";

export const useSendChatbotMessage = (config = {}) => {
  const queryClient = useQueryClient();
  return useMutation(
    ({ data }) =>
      API.graphql({
        query: mutations.sendChatbotMessage,
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
  useSendChatbotMessage,
};

export default hooks;
