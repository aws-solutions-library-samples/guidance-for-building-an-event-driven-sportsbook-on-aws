import { Box, Typography, Card, CardContent, IconButton } from "@mui/material";
import DeleteIcon from '@mui/icons-material/Delete';
import { useBetSlip } from "../providers/BetSlipContext";
import { useGlobal } from "../providers/GlobalContext";

const conditionMap = {
  homeWin: "Home Win",
  awayWin: "Draw",
  draw: "Away Win",
};

export const BetSlipItem = ({ bet }) => {
  const { removeFromSlip } = useBetSlip();
  const { currencySymbol } = useGlobal();

  return (
    <Card>
      <CardContent>
        <Box>
          <Typography variant={"subtitle1"}>{bet.eventId }</Typography>
          <Typography variant={"subtitle2"}>
            Odds {bet.odds} - {conditionMap[bet.outcome]}
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
