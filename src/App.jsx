import diceImage from "./assets/dice.jpeg";
import { Outlet } from "react-router-dom";
import { Amplify } from "aws-amplify";
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
  Snackbar,
  Alert,
} from "@mui/material";
import SportsbookAppBar from "./components/SportsbookAppBar";
import BetSlip from "./components/BetSlip";
import { BetSlipProvider } from "./providers/BetSlipProvider";
import { GlobalProvider } from "./providers/GlobalProvider";
import { useBetSlip } from "./providers/BetSlipContext";
import { useGlobal } from "./providers/GlobalContext";

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
  const {
    bShowSnackbar,
    closeSnackbar,
    snackbarMessage,
    snackbarSeverity,
  } = useGlobal();
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SportsbookAppBar user={user} signOut={signOut} />
      <Container disableGutters={true} maxWidth="xxl">
        <Snackbar open={bShowSnackbar} autoHideDuration={6000} onClose={closeSnackbar} anchorOrigin={{vertical: 'top', horizontal: 'center'}} >
          <Alert onClose={closeSnackbar} severity={snackbarSeverity} sx={{width: '100%'}} >
            {snackbarMessage}
          </Alert>
        </Snackbar>
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
                <BetSlip />
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
        <BetSlip />
      </Drawer>
    </ThemeProvider>
  );
}

const components = {
  Header() {
    return (
      <Typography textAlign={"center"} variant={"h4"} mb={2}>
        AWS Event Driven Sportsbook
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
      <GlobalProvider>
        <BetSlipProvider>
          <Authenticator components={components} formFields={formFields}>
            {({ signOut, user }) => <App signOut={signOut} user={user} />}
          </Authenticator>
        </BetSlipProvider>
      </GlobalProvider>
    </AmplifyThemeProvider>
  );
}
