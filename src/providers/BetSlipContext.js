import { useContext, createContext } from "react";

export const betSlipContext = createContext([false, () => {}]);

export const useBetSlip = () => {
  return useContext(betSlipContext);
};

export default {
  useBetSlip,
  betSlipContext,
};
