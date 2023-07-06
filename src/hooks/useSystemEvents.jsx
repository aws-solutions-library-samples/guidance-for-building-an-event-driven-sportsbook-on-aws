import { useEffect } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { API, graphqlOperation } from "aws-amplify";
import * as subscriptions from "../graphql/subscriptions.js";

export const CACHE_PATH = "system-events";
let idCount = 0;

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
                queryClient.setQueryData([CACHE_PATH], [{id: idCount, source: 'None', 'detailType': 'None', detail: 'None'}])
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
}

export default hooks;