import { useEffect, useState } from "react";
import logo from "../assets/logo.png";
import MenuIcon from "@mui/icons-material/Menu";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import LogoutIcon from "@mui/icons-material/Logout";
import {
  AppBar,
  Box,
  Button,
  Container,
  IconButton,
  Menu,
  MenuItem,
  Toolbar,
  Typography,
  Stack,
  Popover,
} from "@mui/material";
import {
  usePopupState,
  bindTrigger,
  bindMenu,
} from "material-ui-popup-state/hooks";
import Wallet from "./Wallet";

import { Link, useLocation } from "react-router-dom";

const pages = ["about"];

function SportsbookAppBar({ user, signOut }) {
  const [anchorElNav, setAnchorElNav] = useState(null);
  const popupState = usePopupState({ variant: "popover", popupId: "wallet" });

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
          <Typography sx={{ mr: 2, display: { xs: "none", md: "flex" } }}>
            {user.attributes.email}
          </Typography>
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
          <Button color="inherit" onClick={signOut}>
            <LogoutIcon />
          </Button>
        </Toolbar>
      </Container>
    </AppBar>
  );
}
export default SportsbookAppBar;
