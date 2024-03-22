import diceImage from "./assets/dice.jpeg";
import bgImage from "./assets/background.jpg";
import headerImage from "./assets/header.jpg";
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
  Snackbar,
  Alert,
  useTheme,
} from "@mui/material";
import SportsbookAppBar from "./components/SportsbookAppBar";
import SystemEvents from "./components/admin/SystemEvents";
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


const styles = {
  root: {
    backgroundSize: "cover",
    backgroundPosition: "center",
    backgroundRepeat: "no-repeat",
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column",
    backgroundImage: `url(${bgImage})`,
    color: "#ffffff", // Light text color
  },
};

const primaryColor = "rgb(25, 118, 80)";
const secondaryColor = "#e53935";

const getTheme = (isDarkMode) =>
  createTheme({
    palette: {
      mode: isDarkMode ? "dark" : "light",
      primary: {
        main: primaryColor,
      },
      secondary: {
        main: secondaryColor,
      },
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            color: isDarkMode ? "#fff" : "000", // Set the default button text color for dark mode
            //also change border color of a button
            border: "1px solid "+(isDarkMode ? "#fff" : primaryColor),
          },
        },
      },
    },
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
  const isLocked = useUser(user);
  const [isDarkMode, setIsDarkMode] = useState(false);

  const handleThemeChange = () => {
    setIsDarkMode(!isDarkMode);
  };

  const theme = getTheme(isDarkMode);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={styles.root}>
        <SportsbookAppBar user={user} signOut={signOut} isLocked={isLocked} handleThemeChange={handleThemeChange}
          isDarkMode={isDarkMode}/>
        <Container disableGutters={true} maxWidth="xxl">
          <Snackbar
            open={bShowSnackbar}
            autoHideDuration={6000}
            onClose={closeSnackbar}
            anchorOrigin={{ vertical: "top", horizontal: "center" }}
          >
            <Alert
              onClose={closeSnackbar}
              severity={snackbarSeverity}
              sx={{ width: "100%" }}
            >
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
                backgroundColor: isDarkMode ? "#000" : "#eee", // Darker background color
              }}
            >
              <img src={headerImage} alt="dice" style={{
                width: "100%",
                height: "200px",
                objectFit: "cover",
                objectPosition: "center",
              }}/>
              <Outlet />
            </Box>
            <Box
              sx={{
                height: "100%",
                paddingRight: showHub ? 11 : 0,
                display: { lg: "flex", xs: "none" },
                backgroundColor: isDarkMode ? "#000" : "#eee", // Darker background color
                overflowY: showHub ? "scroll" : "hidden",
              }}
            >
              <Collapse orientation="horizontal" in={showHub}>
                <Box
                  sx={{
                    width: "300px",
                    pr: "5px",
                    pl: "5px",
                    backgroundColor: isDarkMode ? "#000" : "#eee", // Darker background color
                  }}
                >
                  <Box
                    sx={{
                      pt: "5px",
                      backgroundColor: isDarkMode ? "#000" : "#eee", // Darker background color
                    }}
                  >
                    <BetSlip
                      onClose={() => setShowHub(false)}
                      isLocked={isLocked}
                    />
                  </Box>
                  <Box
                    sx={{
                      pt: "5px",
                      backgroundColor: isDarkMode ? "#000" : "#eee", // Darker background color
                    }}
                  >
                    <SystemEvents />
                  </Box>
                </Box>
              </Collapse>
            </Box>
            {!showHub && (
              <Fab
                color="primary"
                variant="extended"
                aria-label="add"
                sx={{
                  width: 280,
                  position: "absolute",
                  bottom: 10,
                  right: 10,
                  backgroundColor: "#424242", // Darker background color
                  color: "#ffffff", // Light text color
                }}
                onClick={() => setShowHub(!showHub)}
              >
                Open Bet slip
              </Fab>
            )}
          </Stack>
        </Container>
      </Box>
      <Drawer
        sx={{ display: { lg: "none", xs: "block" } }}
        PaperProps={{ sx: { width: 350, backgroundColor: "#333333" } }} // Darker drawer background
        anchor="right"
        variant={"temporary"}
        open={showHub}
        onClose={() => setShowHub(false)}
      >
        <BetSlip onClose={() => setShowHub(false)} isLocked={isLocked} />
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
    <AmplifyThemeProvider amplifyTheme={amplifyTheme}>
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