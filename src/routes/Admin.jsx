import {
    Typography,
    Box,
} from "@mui/material"
import EventOdds from "../components/admin/EventOdds";

export default function Home() {
  return (
    <Box mt={4}>
      <Typography>Admin Page</Typography>
      <EventOdds />
    </Box>
  );
}
