import { useState } from "react";
import { betSlipContext } from "./BetSlipContext.js";

export function BetSlipProvider(props) {
  const [showHub, setShowHub] = useState(true);
  const [pendingBets, setPendingBets] = useState([]);

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
    console.log('removing bet from slip. bet: ', bet);
    let newPendingBets = [];
    pendingBets.forEach(b => {
      if (b != bet) newPendingBets.push(b)
    });
    setPendingBets(newPendingBets);
  }

  const clearSlip = () => {
    setPendingBets([]);
  };

  return (
    <betSlipContext.Provider
      value={{ showHub, setShowHub, pendingBets, addToSlip, removeFromSlip, clearSlip }}
      {...props}
    />
  );
}

export default BetSlipProvider;
