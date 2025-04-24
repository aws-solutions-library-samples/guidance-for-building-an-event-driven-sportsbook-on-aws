import { Box } from "@mui/material";

import EventOdds from "../components/EventOdds";
import BetHistory from "../components/BetHistory";
import { useTheme } from "@mui/material/styles";

export default function Home() {
  const theme = useTheme();
  
  return (
    <Box>
      <Box sx={{
        padding: "5px 0px 5px 0px",
      }}>
        <EventOdds />
      </Box>
      <Box sx={{
        padding: "5px 0px 5px 0px",
      }}>
        <BetHistory />
      </Box>
    </Box>
  );
}
