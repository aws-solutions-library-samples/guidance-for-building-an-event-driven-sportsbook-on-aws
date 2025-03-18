import { useEffect, useState } from "react";
import {
  Button,
  Box,
  Typography,
  Card,
  CardContent,
  CardActions,
  CircularProgress,
  Stack,
  IconButton,
} from "@mui/material";
import { useMarket } from "../hooks/useEvents";
import { green } from '@mui/material/colors';
import Slide from "@mui/material/Slide";

import BetSlipItem from "./BetSlipItem";

import { useBetSlip } from "../providers/BetSlipContext";
import { useGlobal } from "../providers/GlobalContext";
import { useCreateBets } from "../hooks/useBets";
import { Close } from "@mui/icons-material";

export const BetSlip = ({ onClose, isLocked }) => {
  const suspendedMarkets = useMarket();
  
      //iterate through pendingBets, find market that has same name as pendingBet.outcome and update the bet by adding market state 
      
 
  const {
    showError,
    showSuccess,
  } = useGlobal();
  const {
    pendingBets, clearSlip,
    betInProgress, setInProgress,
    isValid, acceptCurrentOdds, setPendingBets
  } = useBetSlip();
  const { mutateAsync: createBets } = useCreateBets();
  
  for(var pendingbet in pendingBets) {
    const market = suspendedMarkets.find((market) => market.eventId === pendingBets[pendingbet].eventId)

    //Disgusting, but i dont have much time
    const marketstatus = market?.marketstatus?.find((ms)=>{
      if(pendingBets[pendingbet].outcome === "homeWin" && ms.name === "homeOdds")
        return true;
      if(pendingBets[pendingbet].outcome === "awayWin" && ms.name === "awayOdds")
        return true;
      if(pendingBets[pendingbet].outcome === "draw" && ms.name === "drawOdds")
        return true;
      return false;
    });
    
    pendingBets[pendingbet].marketstatus = marketstatus;
  }

  const handlePlaceBets = () => {
    if(pendingBets.find(bet=>bet.marketstatus?.status==="Suspended")!==undefined){
      showError("One or more markets are suspended");
      return;
    }
    setInProgress(true);
    createBets({
      data: {
        bets: pendingBets.map((pb) => {
          return {
            eventId: pb.eventId,
            outcome: pb.outcome,
            odds: pb.selectedOdds,
            amount: pb.amount,
          };
        }),
      },
    })
      .then(() => {
        setInProgress(false);
        showSuccess("Bets placed. Good luck!")
        clearSlip();
      })
      .catch((err) => {
        setInProgress(false);
        if (err.message.includes("InsufficientFunds")) {
          showError("Insufficient Funds")
        } else {
          showError("Unidentified Error")
        }
      });
  };

  const updateBetAmount = (betId, newAmount) => {
    const updatedPendingBets = pendingBets.map((bet) => {
      if (bet.id === betId) {
        return { ...bet, amount: newAmount };
      }
      return bet;
    });
    // Update the pendingBets array in the BetSlip context or state
    // e.g., updatePendingBets(updatedPendingBets);
    setPendingBets(updatedPendingBets);
  };

  return (
    <Card className="betslip">
      <CardContent>
        <Stack
          mb={1}
          direction={"row"}
          justifyContent={"space-between"}
          alignItems={"center"}
        >
          <Typography variant="h5" component="div" className="title">
            Your Betslip
          </Typography>
          {/* <IconButton onClick={onClose}>
            <Close />
          </IconButton> */}
        </Stack>
        <Slide in={pendingBets.length > 0} direction="up" timeout={500}>
          <Stack spacing={1}>
            {pendingBets.map((bet, idx) => (
              <BetSlipItem 
                key={idx}
                bet={bet}
                updateBetAmount={updateBetAmount}
              />
            ))}
          </Stack>
        </Slide>
        {pendingBets.length === 0 && (
          <Typography>You have no bets added to your Betslip.</Typography>
        )}
      </CardContent>
      {(!isValid || isLocked) && (
      <Box sx={{ m: 1, position: 'relative', width: '100%' }}>
      <CardActions>
        
          <Button onClick={acceptCurrentOdds} className="accept-odds" size="large">
            Accept current odds
          </Button>
        
      </CardActions>
      </Box>
      )}
      <CardActions>
        <Box sx={{ m: 1, position: 'relative', width: '100%' }}>
        {pendingBets.length > 0 && (
          <Button
            onClick={handlePlaceBets}
            size="large"
            className="place-bets-button"
            variant="contained"
            disabled={betInProgress || !pendingBets.length || !isValid || isLocked || pendingBets.find(bet=>bet.marketstatus?.status==="Suspended")!==undefined}
          >
            Place Bets
          </Button>
          )}
          {(pendingBets.find(bet=>bet.marketstatus?.status==="Suspended")!==undefined) && (
          <Typography>One or more markets are suspended</Typography>
        )}

          {betInProgress && (
            <CircularProgress
              size={24}
              sx={{
                color: green[500],
                position: 'absolute',
                top: '50%',
                left: '50%',
                marginTop: '-12px',
                marginLeft: '-12px',
              }}
            />
          )}
        </Box>
      </CardActions>
    </Card>
  );
};

export default BetSlip;