import { useEffect, useState } from "react";
import logo from "../assets/logo.png";
import { createTheme, ThemeProvider } from '@mui/material/styles';

import '../css/bootstrap.min.css';
import '../css/magnific-popup.css';
import '../css/owl.carousel.min.css';
import '../css/owl.theme.default.css';
import '../css/nice-select.css';
import '../css/animate.css';
import '../css/all.min.css';
import '../css/main.css';

import EuroIcon from '@mui/icons-material/Euro';
import CurrencyPoundIcon from '@mui/icons-material/CurrencyPound';
import LogoutIcon from '@mui/icons-material/Logout'
import Settings from '@mui/icons-material/Settings';
import ListItemIcon from '@mui/material/ListItemIcon';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import LocalAtmIcon from '@mui/icons-material/LocalAtm';
import MenuIcon from '@mui/icons-material/Menu';
import LockIcon from '@mui/icons-material/Lock';
import LockOpenIcon from '@mui/icons-material/LockOpen';
import { Switch } from "@mui/material";
import Brightness4Icon from "@mui/icons-material/Brightness4";
import Brightness7Icon from "@mui/icons-material/Brightness7";

import { Auth } from "aws-amplify";

import {
  AppBar,
  Box,
  Divider,
  Button,
  Container,
  IconButton,
  MenuItem,
  Menu,
  Toolbar,
  Typography,
  Stack,
  Popover,
  Tooltip,
  Avatar,
} from "@mui/material";

import AccountCircleRoundedIcon from '@mui/icons-material/AccountCircleRounded';
import { styled } from '@mui/material/styles';

import {
  usePopupState,
  bindTrigger,
  bindMenu,
} from "material-ui-popup-state/hooks";
import Wallet from "./Wallet";
import { useGlobal } from "../providers/GlobalContext";

import { Link, useLocation } from "react-router-dom";
import {
  useLockUser
} from "../hooks/useUser";

const pages = ["About", "Admin"];

// custom icons
const CustomAccountIcon = styled(AccountCircleRoundedIcon)({
  color: 'white',
  fontSize: 35,
});

const CustomWalletIcon = styled(LocalAtmIcon)({
  color: 'white',
  fontSize: 35,
});

function SportsbookAppBar({ user, signOut, isLocked, handleThemeChange, isDarkMode }) {
  const [anchorElNav, setAnchorElNav] = useState(null);
  const { currencySymbol, toggleCurrency } = useGlobal();

  const { mutateAsync: lockUser } = useLockUser();
  const handleLockUser = (lockStatus) => lockUser({ data: { isLocked: lockStatus, userId: user.username } });

  const popupState = usePopupState({ variant: "popover", popupId: "wallet" });
  const profileMenuState = usePopupState({ variant: "popover", popupId: "profile" });

  // const [anchorElProfile, setAnchorElProfile] = useState(null);
  // const profileMenuOpen = Boolean(anchorElProfile);

  const location = useLocation();
  useEffect(() => {
    setAnchorElNav(null);
  }, [location]);

  const handleOpenNavMenu = (event) => {
    setAnchorElNav(event.currentTarget);
  };
  const handleCloseNavMenu = () => {
    setAnchorElNav(null);
  };

  const accountSettings = () => {
    return (
      
      <Box>
        <Tooltip title="Account Settings">
          <IconButton {...bindTrigger(profileMenuState)}>
            <CustomAccountIcon />
          </IconButton>
        </Tooltip>
        <Menu
          {...bindMenu(profileMenuState)}
          PaperProps={{
            elevation: 0,
            sx: {
              overflow: "visible",
              filter: "drop-shadow(0px 2px 8px rgba(0,0,0,0.32))",
              mt: 1.5,
              "& .MuiAvatar-root": {
                width: 32,
                height: 32,
                ml: -0.5,
                mr: 1,
              },
              "&:before": {
                content: '""',
                display: "block",
                position: "absolute",
                top: 0,
                right: 14,
                width: 10,
                height: 10,
                bgcolor: "background.paper",
                transform: "translateY(-50%) rotate(45deg)",
                zIndex: 0,
              },
            },
          }}
          transformOrigin={{ horizontal: "right", vertical: "top" }}
          anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
        >
          <MenuItem sx={{ mr: 2, display: { xs: "none", md: "flex" } }}>
            <AccountCircleRoundedIcon /> {user.attributes.email}
          </MenuItem>
          <Divider />
          <MenuItem onClick={handleLock}>
            <ListItemIcon>
              {isLocked ? <LockOpenIcon /> : <LockIcon />}
            </ListItemIcon>
            {isLocked ? "Unlock Account" : "Lock Account"}
          </MenuItem>
          <MenuItem onClick={toggleCurrency}>
            <ListItemIcon>
              {currencySymbol == "£" && <CurrencyPoundIcon />}
              {currencySymbol == "€" && <EuroIcon />}
              {currencySymbol == "$" && <AttachMoneyIcon />}
            </ListItemIcon>
            Switch currency
          </MenuItem>
          {/* <MenuItem onClick={handleThemeChange}>
            <ListItemIcon>
              {isDarkMode ? <Brightness7Icon /> : <Brightness4Icon />}
            </ListItemIcon>
            {isDarkMode ? "Light Mode" : "Dark Mode"}
          </MenuItem> */}
          <MenuItem onClick={handleCloseNavMenu}>
            <ListItemIcon>
              <Settings fontSize="small" />
            </ListItemIcon>
            Settings
          </MenuItem>
          <MenuItem onClick={signOut}>
            <ListItemIcon>
              <LogoutIcon />
            </ListItemIcon>
            Logout
          </MenuItem>
        </Menu>
      </Box>
      
    );
  };

  //function that sets user "locked" attribute to provided boolean value
  const handleLock = async () => {
    handleLockUser(!isLocked);
    console.log("User lock status:" + !isLocked);
  };

  return (
    <>
      <header className="header-section">
        <div className="container-fluid p-0">
          <div className="header-wrapper">
            <div className="menu__left__wrap">
              <div className="logo-menu px-2">
                <Link to="/" className="logo">
                <img src={logo} alt="sportsbook logo" />
                </Link>
              </div>

              <Typography
            variant="h6"
            noWrap
            component={Link}
            to="/"
            sx={{
              ml: 2,
              mr: 2,
              mb: 0.5,
              display: { xs: "none", md: "flex" },
              fontWeight: 700,
              letterSpacing: ".2rem",
              color: "inherit",
              textDecoration: "none",
            }}
          >
            AWS Sportsbook
          </Typography>



              <ul className="main-menu">

              {pages.map((page) => (
                
                <li>
                  <Link to="/lives">
                    {page}
                    </Link>
                    </li>
                
              ))}
        
              </ul>
            </div>
            <div className="mneu-btn-grp">
              <div className="header-bar">
                <Typography sx={{ mr: 2, display: { xs: "none", md: "flex" } }}>
                  {user.attributes.email}
                </Typography>
              </div>
              <div className="header-bar">
                <IconButton color="inherit" {...bindTrigger(popupState)}>
                  <CustomWalletIcon />
                </IconButton>

                <Popover
                  {...bindMenu(popupState)}
                  anchorOrigin={{
                    vertical: "bottom",
                    horizontal: "right",
                  }}
                  transformOrigin={{
                    vertical: "top",
                    horizontal: "right",
                  }}
                >
                  <Box width={300}>
                    <Wallet isLocked={isLocked} />
                  </Box>
                </Popover>
              </div>

              {accountSettings()}

            </div>
          </div>
        </div>
      </header>
    </>
  );
}
export default SportsbookAppBar;
