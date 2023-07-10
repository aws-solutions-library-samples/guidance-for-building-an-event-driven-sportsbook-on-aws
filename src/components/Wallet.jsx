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

import { useGlobal } from "../providers/GlobalContext";

export const Wallet = () => {
  const { data: wallet, isLoading: loadingWallet } = useWallet();
  const { mutateAsync: withdrawFunds } = useWithdrawFunds();
  const { mutateAsync: depositFunds } = useDepositFunds();
  const { showError, showSuccess, currencySymbol } = useGlobal();

  const handleDeposit = () => {
    depositFunds({ data: { amount: 10 } }).then(() => {
      showSuccess('Funds added successfully')
    }).catch(()=> {
      showError('Funds could not be added')
    })
  }
  
  const handleWithdrawal = () => {
    withdrawFunds({ data: { amount: 10 } }).then(() => {
      showSuccess('Funds withdrawn successfully')
    }).catch(()=> {
      showError('Insufficient funds to withdraw')
    });
  }

  if (loadingWallet) return <WalletPending />;

  //console.log(wallet);
  return (
    <Card>
      <CardMedia sx={{ height: 200 }} image={walletLogo} title="Wallet Image" />
      <CardContent>
        <Typography gutterBottom variant="h5" component="div">
          Your Balance
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {currencySymbol}{(wallet.balance/100).toFixed(2)}
        </Typography>
      </CardContent>
      <CardActions>
        <Button size="small" variant="contained" onClick={handleDeposit}>
          Deposit
        </Button>
        <Button size="small" variant="contained" onClick={handleWithdrawal}>
          Withdraw
        </Button>
      </CardActions>
    </Card>
  );
};

export default Wallet;
