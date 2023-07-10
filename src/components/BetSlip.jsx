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

import BetSlipItem from "./BetSlipItem";

import { useBetSlip } from "../providers/BetSlipContext";
import { useGlobal } from "../providers/GlobalContext";
import { useCreateBets } from "../hooks/useBets";

export const BetSlip = ({onClose}) => {
  const {
    showError,
    showSuccess,
  } = useGlobal();
  const { 
    pendingBets, clearSlip, 
    betInProgress, setInProgress,
    isValid, acceptCurrentOdds,
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
        {!isValid && (
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
            disabled={ betInProgress || !pendingBets.length || !isValid }
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
