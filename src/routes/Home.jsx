import { Box, Container, Grid, Typography } from "@mui/material";

import Wallet from "../components/Wallet";
import EventOdds from "../components/EventOdds";

export default function Home() {
  return (
    <Box mt={4}>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={12} md={9}>
          <EventOdds />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Wallet balance={0} />
        </Grid>
      </Grid>
    </Box>
  );
}
