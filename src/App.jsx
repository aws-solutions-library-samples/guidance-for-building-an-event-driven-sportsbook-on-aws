import diceImage from "./assets/dice.jpeg";
import { Outlet } from "react-router-dom";
import { Amplify } from "aws-amplify";
import { useEffect, useState } from "react";
import { useUser } from "./hooks/useUser";


import {
  Authenticator,
  ThemeProvider as AmplifyThemeProvider,
} from "@aws-amplify/ui-react";
import "@aws-amplify/ui-react/styles.css";
import useAmplifyTheme from "./hooks/useAmplifyTheme";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import {
  Typography,
  CssBaseline,
  Container,
  Drawer,
  Fab,
  Box,
  Stack,
  Collapse,
} from "@mui/material";
import SportsbookAppBar from "./components/SportsbookAppBar";
import BetSlip from "./components/BetSlip";
import { BetSlipProvider } from "./providers/BetSlipProvider";
import { useBetSlip } from "./providers/BetSlipContext";

import {
  AWS_REGION,
  AWS_USER_POOL_ID,
  AWS_USER_POOL_WEB_CLIENT_ID,
  AWS_APPSYNC_API_URL,
} from "./constants";

Amplify.configure({
  Auth: {
    region: AWS_REGION,
    userPoolId: AWS_USER_POOL_ID,
    userPoolWebClientId: AWS_USER_POOL_WEB_CLIENT_ID,
    mandatorySignIn: true,
  },
  aws_appsync_graphqlEndpoint: AWS_APPSYNC_API_URL,
  aws_appsync_region: AWS_REGION,
  aws_appsync_authenticationType: "AMAZON_COGNITO_USER_POOLS",
});

const theme = createTheme({
  breakpoints: {
    values: {
      xs: 0,
      sm: 600,
      md: 900,
      lg: 1200,
      xl: 1536,
      xxl: 1800,
    },
  },
});

function App({ user, signOut }) {
  
  const { showHub, setShowHub } = useBetSlip();
  const isLocked = useUser(user);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SportsbookAppBar user={user} signOut={signOut} isLocked={isLocked} />
      <Container disableGutters={true} maxWidth="xxl">
        <Stack
          direction={"row"}
          sx={{ position: "relative", height: "calc(100vh - 64px)" }}
        >
          <Box
            sx={{
              height: "100%",
              paddingBottom: "50px",
              position: "relative",
              overflowY: "scroll",
            }}
          >
            <img src={diceImage} alt="dice" width="100%" />
            <Outlet />
          </Box>
          <Box
            sx={{
              height: "100%",
              display: { lg: "flex", xs: "none" },
              background: "#fafafa",
            }}
          >
            <Collapse orientation="horizontal" in={showHub}>
              <Box sx={{ width: "300px" }}>
                <BetSlip isLocked={isLocked}/>
              </Box>
            </Collapse>
          </Box>
          <Fab
            color="primary"
            variant="extended"
            aria-label="add"
            sx={{ width: 280, position: "absolute", bottom: 10, right: 10 }}
            onClick={() => setShowHub(!showHub)}
          >
            {showHub ? "Close" : "Open"} Bet slip
          </Fab>
        </Stack>
      </Container>
      <Drawer
        sx={{ display: { lg: "none", xs: "block" } }}
        anchor="right"
        variant={"temporary"}
        open={showHub}
        onClose={() => setShowHub(false)}
      >
        <BetSlip isLocked={isLocked} />
      </Drawer>
    </ThemeProvider>
  );
}

const components = {
  Header() {
    return (
      <Typography textAlign={"center"} variant={"h4"} mb={2}>
        Sportsbook
      </Typography>
    );
  },
};

const formFields = {
  signIn: {
    username: {
      placeholder: "Enter Your Email Here",
      isRequired: true,
      label: "Email Address",
    },
  },
  signUp: {
    username: {
      placeholder: "Enter Your Email Here",
      isRequired: true,
      label: "Email Address",
    },
  },
};

export default function AuthenticatedApp() {
  const amplifyTheme = useAmplifyTheme();
  return (
    <AmplifyThemeProvider amplifyTheme={theme}>
      <BetSlipProvider>
        <Authenticator components={components} formFields={formFields}>
          {({ signOut, user }) => <App signOut={signOut} user={user} />}
        </Authenticator>
      </BetSlipProvider>
    </AmplifyThemeProvider>
  );
}
