import { useState } from "react";
import { betSlipContext } from "./BetSlipContext.js";
import { fetchEvent } from "../hooks/useEvent.jsx";
import { useQueries } from "@tanstack/react-query";
import { useDeepCompareEffect } from "react-use";

export const oddsMap = {
  homeWin: "homeOdds",
  awayWin: "awayOdds",
  draw: "drawOdds",
};

export function BetSlipProvider(props) {
  const [showHub, setShowHub] = useState(true);
  const [pendingBets, setPendingBets] = useState([]);
  const [betInProgress, setInProgress] = useState(false);

  const eventQueries = useQueries({
    queries: pendingBets.map((b) => {
      return {
        queryKey: ["event", b.eventId],
        queryFn: () => fetchEvent(b.eventId),
        refetchInterval: 5000,
        useErrorBoundary: false,
        enabled: true,
        retry: true,
        retryDelay: 2000,
      };
    }),
  });

  const eventData = eventQueries.map((q) => q.data);

  useDeepCompareEffect(() => {
    setPendingBets((pb) =>
      pb.map((i) => {
        const newData = eventData.find((e) => e?.eventId === i.eventId);
        if (newData && newData[oddsMap[i.outcome]] !== i.currentOdds) {
          console.log(
            `Change in ${i.eventId}: ${i.currentOdds} -> ${
              newData[oddsMap[i.outcome]]
            }`
          );
          i.currentOdds = newData[oddsMap[i.outcome]];
        }
        return i;
      })
    );
  }, [eventData]);

  const outcomeMap = {
    homeOdds: "homeWin",
    awayOdds: "awayWin",
    drawOdds: "draw",
  };

  const addToSlip = (event, selection) => {
    console.log(`Adding ${selection} bet to slip. bet: `, event);
    const newPendingBet = {
      selectedOdds: event[selection],
      currentOdds: event[selection],
      eventId: event.eventId,
      amount: 10,
      outcome: outcomeMap[selection],
    };

    setPendingBets((e) => e.concat(newPendingBet));
  };

  const isValid = pendingBets.every((i) => i.selectedOdds === i.currentOdds);

  const acceptCurrentOdds = () => {
    setPendingBets((e) =>
      e.map((i) => ({
        ...i,
        selectedOdds: i.currentOdds,
      }))
    );
  };

  const removeFromSlip = (bet) => {
    setPendingBets(
      pendingBets.filter(
        (i) => !(i.eventId == bet.eventId && i.outcome == bet.outcome)
      )
    );
  };

  const updateInSlip = (bet) => {
    setPendingBets(
      (pendingBet) => {
        if (pendingBet.eventId == bet.eventId) {
          return { ...pendingBet, amount: bet.amount };
        }
        return pendingBet;
      }
    );
  };

  const clearSlip = () => {
    setPendingBets([]);
  };

  return (
    <betSlipContext.Provider
      value={{ 
        showHub, 
        setShowHub, 
        pendingBets, 
        betInProgress, 
        setInProgress,
        addToSlip, 
        removeFromSlip, 
        updateInSlip,
        clearSlip,
        isValid,
        acceptCurrentOdds,
      }}
      {...props}
    />
  );
}

export default BetSlipProvider;
