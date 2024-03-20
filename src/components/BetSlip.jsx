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
import { green } from '@mui/material/colors';
import Slide from "@mui/material/Slide";

import BetSlipItem from "./BetSlipItem";

import { useBetSlip } from "../providers/BetSlipContext";
import { useGlobal } from "../providers/GlobalContext";
import { useCreateBets } from "../hooks/useBets";
import { Close } from "@mui/icons-material";

export const BetSlip = ({ onClose, isLocked }) => {
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
  

  const buttonSx = {
    ...(pendingBets.length > 0 && {
      bgcolor: green[500],
      '&:hover': {
        bgcolor: green[700],
      },
    }),
  };

  const handlePlaceBets = () => {
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
    <Card>
      <CardContent>
        <Stack
          mb={1}
          direction={"row"}
          justifyContent={"space-between"}
          alignItems={"center"}
        >
          <Typography variant="h5" component="div">
            Your Betslip
          </Typography>
          <IconButton onClick={onClose}>
            <Close />
          </IconButton>
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
          <Typography>You have no bets added to your betslip</Typography>
        )}
      </CardContent>
      <CardActions>
        {(!isValid || isLocked) && (
          <Button onClick={acceptCurrentOdds} size="small" variant="contained">
            Accept current odds
          </Button>
        )}
      </CardActions>
      <CardActions>
        <Box sx={{ m: 1, position: 'relative' }}>
          <Button
            onClick={handlePlaceBets}
            size="small"
            sx={buttonSx}
            variant="contained"
            disabled={betInProgress || !pendingBets.length || !isValid || isLocked}
          >
            Place Bets
          </Button>
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