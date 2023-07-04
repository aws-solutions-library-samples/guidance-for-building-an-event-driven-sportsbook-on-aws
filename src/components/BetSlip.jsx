import {
  Button,
  Typography,
  Card,
  CardContent,
  CardActions,
  Stack,
  IconButton,
} from "@mui/material";

import BetSlipItem from "./BetSlipItem";

import { useBetSlip } from "../providers/BetSlipContext";
import { useCreateBets } from "../hooks/useBets";
import { Close } from "@mui/icons-material";

export const BetSlip = ({ onClose }) => {
  const { pendingBets, clearSlip, isValid, acceptCurrentOdds } = useBetSlip();
  const { mutateAsync: createBets } = useCreateBets();

  const handlePlaceBets = () => {
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
    }).then(clearSlip);
  };

  return (
    <Card elevation={0} sx={{ backgroundColor: "transparent" }}>
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
        <Stack spacing={1}>
          {pendingBets.map((bet, idx) => (
            <BetSlipItem key={idx} bet={bet} />
          ))}
        </Stack>

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
        <Button
          onClick={handlePlaceBets}
          size="small"
          variant="contained"
          disabled={!pendingBets.length || !isValid}
        >
          Place Bets
        </Button>
      </CardActions>
    </Card>
  );
};

export default BetSlip;
