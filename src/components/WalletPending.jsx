import {
  Button,
  Box,
  Typography,
  Card,
  CardMedia,
  CardContent,
  CircularProgress,
} from "@mui/material";
import logo from "../assets/logo.png";

export const WalletPending = () => {
  return (
    <Card>
      <CardMedia sx={{ height: 200 }} image={logo} title="Wallet Image" />
      <CardContent>
        <Typography gutterBottom component="div">
          Your wallet is currently processing, please wait...
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
