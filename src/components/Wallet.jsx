import {
  Button,
  Typography,
  Card,
  CardMedia,
  CardContent,
  CardActions,
} from "@mui/material";
import WalletPending from "./WalletPending";

import walletLogo from "../assets/wallet.jpeg";
import {
  useWallet,
  useWithdrawFunds,
  useDepositFunds,
} from "../hooks/useWallet";

export const Wallet = (isLocked) => {
  const { data: wallet, isLoading: loadingWallet } = useWallet();
  const { mutateAsync: withdrawFunds } = useWithdrawFunds();
  const { mutateAsync: depositFunds } = useDepositFunds();

  const handleDeposit = () => depositFunds({ data: { amount: 10 } });
  const handleWithdrawal = () => withdrawFunds({ data: { amount: 10 } });

  if (loadingWallet) return <WalletPending />;

  console.log(wallet);
  return (
    <Card>
      <CardMedia sx={{ height: 200 }} image={walletLogo} title="Wallet Image" />
      <CardContent>
        <Typography gutterBottom variant="h5" component="div">
          Your Balance
        </Typography>
        <Typography variant="body2" color="text.secondary">
          £{wallet.balance.toFixed(2)}
        </Typography>
      </CardContent>
      <CardActions>
        {/* TODO: I have no idea why is isLocked passed as an Object rather than boolean, thus this code is a bit dirty*/}
        <Button size="small" variant="contained" onClick={handleDeposit} disabled={isLocked.isLocked}>
          Deposit
        </Button>
        <Button size="small" variant="contained" onClick={handleWithdrawal} disabled={isLocked.isLocked}>
          Withdraw
        </Button>
      </CardActions>
    </Card>
  );
};

export default Wallet;
