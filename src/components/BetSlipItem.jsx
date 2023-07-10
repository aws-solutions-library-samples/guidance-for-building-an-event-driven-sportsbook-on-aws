import { Box, Typography, Card, CardContent, IconButton } from "@mui/material";
import DeleteIcon from '@mui/icons-material/Delete';
import { useBetSlip } from "../providers/BetSlipContext";
import { useGlobal } from "../providers/GlobalContext";
import { useEvent } from "../hooks/useEvent";

const conditionMap = {
  homeWin: "Home Win",
  awayWin: "Draw",
  draw: "Away Win",
};

export const BetSlipItem = ({ bet }) => {
  const { removeFromSlip } = useBetSlip();
  const { currencySymbol } = useGlobal();
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
          <Typography variant={"caption"}>{currencySymbol}{(bet.amount/100).toFixed(2)}</Typography>
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
