import { useEffect, useState } from "react";
import logo from "../assets/logo.png";

import EuroIcon from '@mui/icons-material/Euro';
import CurrencyPoundIcon from '@mui/icons-material/CurrencyPound';
import LogoutIcon from '@mui/icons-material/Logout'
import Settings from '@mui/icons-material/Settings';
import ListItemIcon from '@mui/material/ListItemIcon';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import MenuIcon from '@mui/icons-material/Menu';

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
import {
  usePopupState,
  bindTrigger,
  bindMenu,
} from "material-ui-popup-state/hooks";
import Wallet from "./Wallet";
import { useGlobal } from "../providers/GlobalContext";

import { Link, useLocation } from "react-router-dom";

const pages = ["About", "Admin"];

function SportsbookAppBar({ user, signOut }) {
  const [anchorElNav, setAnchorElNav] = useState(null);
  const { currencySymbol, toggleCurrency } = useGlobal();
  const popupState = usePopupState({ variant: "popover", popupId: "wallet" });
  const profileMenuState = usePopupState({ variant: "popover", popupId: "profile"});

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
          <IconButton 
           {...bindTrigger(profileMenuState)}
          >
            <Avatar />
          </IconButton>
        </Tooltip>
        <Menu
          {...bindMenu(profileMenuState)}
          PaperProps={{
            elevation: 0,
            sx: {
              overflow: 'visible',
              filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.32))',
              mt: 1.5,
              '& .MuiAvatar-root': {
                width: 32,
                height: 32,
                ml: -0.5,
                mr: 1,
              },
              '&:before': {
                content: '""',
                display: 'block',
                position: 'absolute',
                top: 0,
                right: 14,
                width: 10,
                height: 10,
                bgcolor: 'background.paper',
                transform: 'translateY(-50%) rotate(45deg)',
                zIndex: 0,
              },
            },
          }}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        >
          <MenuItem sx={{ mr: 2, display: { xs: "none", md: "flex" } }}>
            <Avatar /> {user.attributes.email}
          </MenuItem>
          <Divider />
          <MenuItem onClick={toggleCurrency}>
            <ListItemIcon>
              {currencySymbol == '£' &&
                <CurrencyPoundIcon />
              }
              {currencySymbol == '€' &&
                <EuroIcon />
              }
              {currencySymbol == '$' &&
                <AttachMoneyIcon />
              }
            </ListItemIcon>
            Switch currency
          </MenuItem>
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
  }

  return (
    <AppBar position="sticky" color="primary">
      <Container maxWidth="xxl">
        <Toolbar disableGutters>
          <img src={logo} width={48} alt="sportsbook logo" />
          <Typography
            variant="h6"
            noWrap
            component={Link}
            to="/"
            sx={{
              ml: 2,
              mr: 2,
              display: { xs: "none", md: "flex" },
              fontFamily: "monospace",
              fontWeight: 700,
              letterSpacing: ".2rem",
              color: "inherit",
              textDecoration: "none",
            }}
          >
            Sportsbook
          </Typography>

          <Box sx={{ flexGrow: 1, display: { xs: "flex", md: "none" } }}>
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleOpenNavMenu}
              color="inherit"
            >
              <MenuIcon />
            </IconButton>
            <Menu
              id="menu-appbar"
              anchorEl={anchorElNav}
              anchorOrigin={{
                vertical: "bottom",
                horizontal: "left",
              }}
              keepMounted
              transformOrigin={{
                vertical: "top",
                horizontal: "left",
              }}
              open={Boolean(anchorElNav)}
              onClose={handleCloseNavMenu}
              sx={{
                display: { xs: "block", md: "none" },
              }}
            >
              {pages.map((page) => (
                <MenuItem key={page} component={Link} to={page}>
                  <Typography
                    textAlign="center"
                    sx={{ textTransform: "capitalize", textDecoration: "none" }}
                  >
                    {page}
                  </Typography>
                </MenuItem>
              ))}
            </Menu>
          </Box>
          <Typography
            variant="h5"
            noWrap
            component={Link}
            to="/"
            sx={{
              mr: 2,
              display: { xs: "flex", md: "none" },
              flexGrow: 1,
              fontFamily: "monospace",
              fontWeight: 600,
              letterSpacing: ".2rem",
              color: "inherit",
              textDecoration: "none",
            }}
          >
            Sportsbook
          </Typography>
          <Stack
            direction="row"
            spacing={2}
            sx={{ flexGrow: 1, display: { xs: "none", md: "flex" } }}
          >
            {pages.map((page) => (
              <Button
                key={page}
                component={Link}
                to={page}
                sx={{ color: "white", display: "block" }}
              >
                {page}
              </Button>
            ))}
          </Stack>

          <IconButton color="inherit" {...bindTrigger(popupState)}>
            <AccountBalanceIcon />
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
              <Wallet />
            </Box>
          </Popover>
          
          {accountSettings()}

        </Toolbar>
      </Container>
    </AppBar>
  );
}
export default SportsbookAppBar;
