import { Box, Typography, Card, CardContent, Button } from "@mui/material";
import { useBetSlip } from "../providers/BetSlipContext";
import { useEvent } from "../hooks/useEvent";
import DeleteIcon from "@mui/icons-material/Delete";

const conditionMap = {
  homeWin: "Home Win",
  awayWin: "Draw",
  draw: "Away Win",
};

export const BetSlipItem = ({ bet }) => {
  const { removeFromSlip } = useBetSlip();
  const { data: event, isLoading } = useEvent(bet.eventId);

  if (isLoading) return <Typography>Loading...</Typography>;

  const oddsChanged = bet.selectedOdds !== bet.currentOdds;

  return (
    <Card>
      <CardContent>
        <Box>
          <Typography variant={"subtitle1"}>
            {event.home} vs {event.away}
          </Typography>
          {oddsChanged && (
            <Typography variant={"subtitle2"}>
              Starting Odds {bet.selectedOdds}
            </Typography>
          )}
          <Typography variant={"subtitle2"}>
            Current Odds {bet.currentOdds} - {conditionMap[bet.outcome]}
          </Typography>
          <Typography variant={"caption"}>£{bet.amount}</Typography>
          <Button onClick={() => removeFromSlip(bet)}>
            <DeleteIcon />
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default BetSlipItem;
