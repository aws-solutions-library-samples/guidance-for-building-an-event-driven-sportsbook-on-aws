import { Box, Typography, Card, CardContent } from "@mui/material";

const conditionMap = {
  homeWin: "Home Win",
  awayWin: "Draw",
  draw: "Away Win",
};

export const BetSlipItem = ({ bet }) => {
  return (
    <Card>
      <CardContent>
        <Box>
          <Typography variant={"subtitle1"}>{bet.eventId}</Typography>
          <Typography variant={"subtitle2"}>
            Odds {bet.odds} - {conditionMap[bet.outcome]}
          </Typography>
           <Typography variant={"caption"}>£{bet.amount}</Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default BetSlipItem;
