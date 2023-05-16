import { Box, Container, Grid, Typography } from "@mui/material";

import Wallet from "../components/Wallet";

export default function Home() {
  return (
    <Box mt={4}>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={3}>
          <Wallet balance={0} />
        </Grid>
      </Grid>
    </Box>
  );
}
