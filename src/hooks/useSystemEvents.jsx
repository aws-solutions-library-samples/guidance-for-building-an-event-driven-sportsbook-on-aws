import { useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { API, graphqlOperation } from "aws-amplify";
import * as subscriptions from "../graphql/subscriptions.js";

export const CACHE_PATH = "system-events";
let idCount = 0;

export const useClearHistory = () => {
    const queryClient = useQueryClient();
    return useMutation(
        [CACHE_PATH],
        () => {
            console.log('clearing history');
            queryClient.setQueryData([CACHE_PATH],[]);
            idCount = 0;
        },
    )
}

export const useSystemEvents = (config = {}) => {
    const queryClient = useQueryClient();
    useEffect(()=> {
        const sub = API.graphql(
            graphqlOperation(subscriptions.updatedSystemEvents)
        ).subscribe({
            next: ({provider, value}) => {
                queryClient.setQueryData([CACHE_PATH], (oldData) => {
                    const newEvent = { id: idCount++, ...value.data.updatedSystemEvents};
                    const newItems = oldData.filter(
                        //parse newEvent.detail with following schema "{eventId=39d96a19-4590-4492-8ac7-8f79934eeecb, market=homeOdds, eventStatus=running}" to object
                        (e) => e.id !== newEvent.id 
                        
                    );
                    newItems.push(newEvent);
                    return newItems;
                })
            },
            error: (error) => { console.warn(error); }
        });
        return () => {
            sub.unsubscribe();
        }
    }, []);

    return useQuery(
        [CACHE_PATH],
        () =>{
            // we don't fetch data, just return existing data
            let cachedData = queryClient.getQueryData([CACHE_PATH])
            if (cachedData == undefined){
                console.log('creating initial blank data')
                queryClient.setQueryData([CACHE_PATH], [{id: idCount, source: 'waiting...', 'detailType': '...', detail: '...'}])
            }
            return cachedData;
        },
        {
          refetchInterval: 0,
          useErrorBoundary: false,
          enabled: true,
          ...config,
        }
      );
}

const hooks = {
    useSystemEvents: useSystemEvents,
    useClearHistory: useClearHistory,
}

export default hooks;