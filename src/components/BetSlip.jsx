import {
  Button,
  Typography,
  Card,
  CardContent,
  CardActions,
} from "@mui/material";

import BetSlipItem from "./BetSlipItem";

import { useBetSlip } from "../providers/BetSlipContext";
import { useGlobal } from "../providers/GlobalContext";
import { useCreateBets } from "../hooks/useBets";

export const BetSlip = () => {
  const {
    showError,
    showSuccess,
  } = useGlobal();
  const { 
    pendingBets, clearSlip, 
  } = useBetSlip();
  const { mutateAsync: createBets } = useCreateBets();

  const handlePlaceBets = () => {
    createBets({ data: { bets: pendingBets } })
    .then(() => {
      showSuccess("Bets placed. Good luck!")
      clearSlip();
    })
    .catch((err) => {
      if(err.message.includes("InsufficientFunds")){
        showError("Insufficient Funds")
      }else{ 
        showError("Unidentified Error")
      }
    });
  };

  return (
    <Card elevation={0} sx={{ backgroundColor: "transparent" }}>
      <CardContent>
        <Typography gutterBottom variant="h5" component="div">
          Your betslip
        </Typography>
        {pendingBets.map((bet) => (
          <BetSlipItem key={bet.eventId + bet.outcome} bet={bet} />
        ))}

        {pendingBets.length === 0 && (
          <Typography>You have no bets added to your betslip</Typography>
        )}
      </CardContent>
      <CardActions>
        <Button
          onClick={handlePlaceBets}
          size="small"
          variant="contained"
          disabled={!pendingBets.length}
        >
          Place Bets
        </Button>
      </CardActions>
    </Card>
  );
};

export default BetSlip;
