import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { API, graphqlOperation } from "aws-amplify";
import * as mutations from "../graphql/mutations.js";
import * as subscriptions from "../graphql/subscriptions.js";
import { Auth } from "aws-amplify";

export const CACHE_PATH = "user";

export const useUser = (user) => {
  const [isLocked, setIsLocked] = useState(null);
  const queryClient = useQueryClient();
  useEffect(() => {
    setIsLocked(user.attributes['custom:isLocked']=='true');
    const sub = API.graphql(
      graphqlOperation(subscriptions.updatedUserStatus)
    ).subscribe({
      next: ({ provider, value }) => {
        queryClient.setQueryData([CACHE_PATH], () => {
          setIsLocked(value.data.updatedUserStatus.isLocked=="true");
          Auth.currentAuthenticatedUser({ bypassCache: true });
          return isLocked;
        });
      },
      error: (error) => console.warn(error),
    });

    return () => sub.unsubscribe();
  }, []);

  return isLocked;
};

const getUser = async () => {
  return await Auth.currentAuthenticatedUser();
}

export const useLockUser = (config = {}) => {
    const queryClient = useQueryClient();
    
    return useMutation(
      ({ data }) =>
      Auth.currentAuthenticatedUser({ bypassCache: true }).then(()=>{
        API.graphql({
          query: mutations.lockUser,
          variables: { input: data },
        })
      }).catch(console.log("Error when locking user data")),
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
  useLockUser,
  useUser: useUser
};

export default hooks;
