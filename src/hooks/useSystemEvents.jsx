import { useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { generateClient } from 'aws-amplify/api';
import * as subscriptions from "../graphql/subscriptions.js";

export const CACHE_PATH = "system-events";
const client = generateClient();

let idCount = 0;

export const useClearHistory = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationKey: [CACHE_PATH],
        mutationFn: async () => {
            console.log('clearing history');
            queryClient.setQueryData([CACHE_PATH], []);
            idCount = 0;
            return true; // Return a value to indicate success
        },
    });
}

export const useSystemEvents = (config = {}) => {
    const queryClient = useQueryClient();

    useEffect(() => {
        const sub = client.graphql({
            query: subscriptions.updatedSystemEvents
        }).subscribe({
            next: ({ data }) => {
                // console.log('Received system event:', data.updatedSystemEvents);
                queryClient.setQueryData(
                    [CACHE_PATH],
                    (oldData = []) => {
                        // Use timestamp + counter to ensure unique IDs
                        const newEvent = { 
                            id: `${Date.now()}-${idCount++}`, 
                            ...data.updatedSystemEvents 
                        };
                        // Create a new array with the new event added
                        return [...oldData, newEvent];
                    }
                );
            },
            error: (error) => { console.warn(error); }
        });

        return () => {
            sub.unsubscribe();
        };
    }, [queryClient]);

    return useQuery({
        queryKey: [CACHE_PATH],
        queryFn: () => {
            // We don't fetch data, just return existing data
            let cachedData = queryClient.getQueryData([CACHE_PATH]);

            if (cachedData == undefined) {
                // Initialize with an empty array and immediately set it in the cache
                cachedData = [{id: `init-${Date.now()}`, source: 'waiting...', 'detailType': '...', detail: '...'}];
                queryClient.setQueryData([CACHE_PATH], cachedData);
            }

            return cachedData;
        },
        refetchInterval: 0,
        useErrorBoundary: false,
        enabled: true,
        ...config,
    });
}

const hooks = {
    useSystemEvents,
    useClearHistory,
};

export default hooks;