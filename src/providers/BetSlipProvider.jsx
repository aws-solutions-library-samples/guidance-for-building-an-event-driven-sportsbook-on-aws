import { useState } from "react";
import { betSlipContext } from "./BetSlipContext.js";

export function BetSlipProvider(props) {
  const [showHub, setShowHub] = useState(true);
  const [pendingBets, setPendingBets] = useState([]);
  const [betInProgress, setInProgress] = useState(false);

  const outcomeMap = {
    homeOdds: "homeWin",
    awayOdds: "awayWin",
    drawOdds: "draw",
  };

  const addToSlip = (event, selection) => {
    const newPendingBet = {
      odds: event[selection],
      eventId: event.eventId,
      amount: 10,
      outcome: outcomeMap[selection],
    };

    setPendingBets([...pendingBets, newPendingBet]);
  };

  const removeFromSlip = (bet) => {
    setPendingBets(
      pendingBets.filter(
        (i) => !(i.eventId == bet.eventId && i.outcome == bet.outcome)
      )
    );
  }

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
        clearSlip,
        isValid,
        acceptCurrentOdds,
      }}
      {...props}
    />
  );
}

export default BetSlipProvider;
