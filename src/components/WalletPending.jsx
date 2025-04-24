import {
  Button,
  Box,
  Typography,
  Card,
  CardMedia,
  CardContent,
  CircularProgress,
} from "@mui/material";

export const WalletPending = () => {
  return (
    <Card>
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
