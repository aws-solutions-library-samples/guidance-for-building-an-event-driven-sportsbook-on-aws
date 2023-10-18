import { Box } from "@mui/material";

import EventOdds from "../components/EventOdds";
import ChatBot from "../components/ChatBot";
import BetHistory from "../components/BetHistory";

export default function Home() {
  return (
    <Box mt={4}>
      <EventOdds />
      <BetHistory />
      <ChatBot />
    </Box>
  );
}
