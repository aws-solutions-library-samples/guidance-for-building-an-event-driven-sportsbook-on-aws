import { Box, Typography, Card, CardContent, IconButton, TextField } from "@mui/material";
import DeleteIcon from '@mui/icons-material/Clear';
import { useBetSlip } from "../providers/BetSlipContext";
import { useGlobal } from "../providers/GlobalContext";
import { useEvent } from "../hooks/useEvent";
import { useState } from 'react';

const conditionMap = {
  homeWin: "Home Win",
  awayWin: "Draw",
  draw: "Away Win",
};

export const BetSlipItem = ({ bet, updateBetAmount }) => {
  const { removeFromSlip, updateInSlip } = useBetSlip();
  const { currencySymbol } = useGlobal();
  const { data: event, isLoading } = useEvent(bet.eventId);
  const [betAmount, setBetAmount] = useState(bet.amount);

  if (isLoading) return <Typography>Loading...</Typography>;
  const oddsChanged = bet.selectedOdds !== bet.currentOdds;

  const calculatePossibleWinning = () => {
    const [numerator, denominator] = bet.currentOdds.split('/').map(Number);
    const oddValue = numerator / denominator;
    return (betAmount * oddValue).toFixed(2);
  };

  const handleBetAmountChange = (event, bet) => {
    if(event!==undefined)
    {
      const newAmount = event.target.value;
      bet.amount = newAmount;
      updateInSlip(bet);
      setBetAmount(bet.amount);
    }
  };

  return (
    <Card className="betslip-card">
      <CardContent>
        <Box sx={bet.marketstatus?.status==='Suspended'?{ color: 'error.main' }:{ color: 'white' }}>
          <Typography variant={"subtitle1"} className="betslip-event" >
            {event.home} vs {event.away}
          </Typography>
          {oddsChanged && (
            <Typography variant={"subtitle2"}>
              Starting Odds: {bet.selectedOdds}
            </Typography>
          )}
          <Typography variant={"subtitle2"}>
            Current Odds: {bet.currentOdds} - {conditionMap[bet.outcome]}
          </Typography>
          <Box display="flex" alignItems="center" gap={2}> {/* Add gap prop */}
            <Box>
              <TextField className="bet-amount"
                type="number"
                value={betAmount}
                onChange={(e) => handleBetAmountChange(e, bet)}
                InputProps={{ startAdornment: <Typography className="currency-symbol">{currencySymbol}</Typography> }}
              />
            </Box>
            <Box>
              <Typography variant={"subtitle2"}>
                Possible Winning: {currencySymbol}{calculatePossibleWinning()}
              </Typography>
            </Box>
          </Box>
          <IconButton
            color="error"
            size="small"
            onClick={() => removeFromSlip(bet)}>
            <DeleteIcon />
          </IconButton>
        </Box>
      </CardContent>
    </Card>
  );
};

export default BetSlipItem;