import {
  Button,
  Typography,
  Card,
  CardContent,
  CardActions,
  CircularProgress,
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
    betInProgress, setInProgress,
  } = useBetSlip();
  const { mutateAsync: createBets } = useCreateBets();

  const handlePlaceBets = () => {
    setInProgress(true);
    createBets({ data: { bets: pendingBets } })
    .then(() => {
      setInProgress(false);
      showSuccess("Bets placed. Good luck!")
      clearSlip();
    })
    .catch((err) => {
      setInProgress(false);
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
          disabled={betInProgress || !pendingBets.length}
        >
          {betInProgress ? <CircularProgress /> : <Typography>Place Bets</Typography>}
        </Button>
      </CardActions>
    </Card>
  );
};

export default BetSlip;
