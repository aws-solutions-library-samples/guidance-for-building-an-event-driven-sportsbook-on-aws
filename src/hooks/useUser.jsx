import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { generateClient } from 'aws-amplify/api';
import { getCurrentUser, fetchUserAttributes } from 'aws-amplify/auth';
import * as mutations from "../graphql/mutations.js";
import * as subscriptions from "../graphql/subscriptions.js";

export const CACHE_PATH = "user";

const client = generateClient();

export const useUser = (user) => {
  const [isLocked, setIsLocked] = useState(null);
  const queryClient = useQueryClient();

  useEffect(() => {
    // First check if user and user.attributes exist
    if (!user) {
      console.warn("User object is undefined in useUser hook");
      return;
    }

    // Handle both v5 and v6 user attribute structures
    const fetchLockStatus = async () => {
      try {
        // If user.attributes exists (v5 structure), use it directly
        if (user.attributes && user.attributes['custom:isLocked'] !== undefined) {
          setIsLocked(user.attributes['custom:isLocked'] === 'true');
        }
        // Otherwise, try to fetch attributes using v6 API
        else {
          const attributes = await fetchUserAttributes();
          setIsLocked(attributes['custom:isLocked'] === 'true');
        }
      } catch (error) {
        console.error("Error fetching user lock status:", error);
        setIsLocked(false); // Default to unlocked on error
      }
    };

    fetchLockStatus();

    const sub = client.graphql({
      query: subscriptions.updatedUserStatus
    }).subscribe({
      next: ({ data }) => {
        queryClient.setQueryData({
          queryKey: [CACHE_PATH],
          updater: () => {
            const newLockStatus = data.updatedUserStatus.isLocked === "true";
            setIsLocked(newLockStatus);
            // Refresh user attributes
            fetchUserAttributes();
            return newLockStatus;
          }
        });
      },
      error: (error) => console.warn(error),
    });

    return () => sub.unsubscribe();
  }, [user, queryClient]);

  return isLocked;
};

const getUser = async () => {
  try {
    return await getCurrentUser();
  } catch (error) {
    console.error("Error getting current user:", error);
    return null;
  }
};

export const useLockUser = (config = {}) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ data }) => {
      try {
        // First get the current user
        const currentUser = await getCurrentUser();

        // If no userId is provided in data, try to get it from the current user
        const input = {
          ...data,
          userId: data.userId || currentUser.userId || currentUser.username
        };

        // Then make the GraphQL call
        return await client.graphql({
          query: mutations.lockUser,
          variables: { input },
        });
      } catch (error) {
        console.log("Error when locking user data", error);
        throw error;
      }
    },
    onSuccess: () => {
      return queryClient.invalidateQueries({ queryKey: [CACHE_PATH] });
    },
    onError: (err, variables) => {
      console.error(err);
    },
    ...config,
  });
};

const hooks = {
  useLockUser,
  useUser: useUser
};

export default hooks;