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
            queryClient.setQueryData({
                queryKey: [CACHE_PATH],
                data: []
            });
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
                queryClient.setQueryData({
                    queryKey: [CACHE_PATH],
                    updater: (oldData) => {
                        const newEvent = { id: idCount++, ...data.updatedSystemEvents };
                        const newItems = oldData.filter(
                            // Parse newEvent.detail with following schema "{eventId=39d96a19-4590-4492-8ac7-8f79934eeecb, market=homeOdds, eventStatus=running}" to object
                            (e) => e.id !== newEvent.id
                        );
                        newItems.push(newEvent);
                        return newItems;
                    }
                });
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
            let cachedData = queryClient.getQueryData({ queryKey: [CACHE_PATH] });

            if (cachedData == undefined) {
                console.log('creating initial blank data');
                // Initialize with an empty array and immediately set it in the cache
                cachedData = [{id: idCount, source: 'waiting...', 'detailType': '...', detail: '...'}];
                queryClient.setQueryData({
                    queryKey: [CACHE_PATH],
                    data: cachedData
                });
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