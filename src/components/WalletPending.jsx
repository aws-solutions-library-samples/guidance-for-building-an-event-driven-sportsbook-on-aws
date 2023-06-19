import {
  Button,
  Box,
  Typography,
  Card,
  CardMedia,
  CardContent,
  CircularProgress,
} from "@mui/material";
import walletLogo from "../assets/wallet.jpeg";

export const WalletPending = () => {
  return (
    <Card>
      <CardMedia sx={{ height: 200 }} image={walletLogo} title="Wallet Image" />
      <CardContent>
        <Typography gutterBottom component="div">
          Your wallet is currently loading, please wait...
        </Typography>
        <Box
          sx={{
            mt: 2,
            display: "flex",
            justifyContent: "center",
          }}
        >
          <CircularProgress />
        </Box>
      </CardContent>
    </Card>
  );
};

export default WalletPending;
