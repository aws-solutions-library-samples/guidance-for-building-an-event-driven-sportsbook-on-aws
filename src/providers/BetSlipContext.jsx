import React, { createContext, useContext } from 'react';

// Create the context
export const BetSlipContext = createContext();

// Create a hook to use the context
export const useBetSlip = () => {
  const context = useContext(BetSlipContext);
  if (!context) {
    throw new Error('useBetSlip must be used within a BetSlipProvider');
  }
  return context;
};
