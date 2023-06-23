import { Box, Typography, Card, CardContent, Button } from "@mui/material";
import { useBetSlip } from "../providers/BetSlipContext";

const conditionMap = {
  homeWin: "Home Win",
  awayWin: "Draw",
  draw: "Away Win",
};

export const BetSlipItem = ({ bet }) => {
  const { removeFromSlip } = useBetSlip();
  return (
    <Card>
      <CardContent>
        <Box>
          <Typography variant={"subtitle1"}>{bet.eventId}</Typography>
          <Typography variant={"subtitle2"}>
            Odds {bet.odds} - {conditionMap[bet.outcome]}
          </Typography>
          <Typography variant={"caption"}>£{bet.amount}</Typography>
          <Button onClick={() => removeFromSlip(bet)}>Remove</Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default BetSlipItem;
