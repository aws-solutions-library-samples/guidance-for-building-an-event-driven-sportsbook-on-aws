import { useContext, createContext } from "react";

export const globalContext = createContext([false, () => {}]);

export const useGlobal = () => {
  return useContext(globalContext);
};

export default {
  useGlobal,
  globalContext,
};
