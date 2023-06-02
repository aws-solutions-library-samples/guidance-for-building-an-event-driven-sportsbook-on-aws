import diceImage from "./assets/dice.jpeg";

import { Outlet, Link, useLocation } from "react-router-dom";

import { Amplify, Auth } from "aws-amplify";
import {
  Authenticator,
  ThemeProvider as AmplifyThemeProvider,
} from "@aws-amplify/ui-react";
import "@aws-amplify/ui-react/styles.css";
import useAmplifyTheme from "./hooks/useAmplifyTheme";

import { ThemeProvider, createTheme } from "@mui/material/styles";
import { Typography, CssBaseline, Container } from "@mui/material";

import SportsbookAppBar from "./components/SportsbookAppBar";

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

const theme = createTheme();

function App({ user, signOut }) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container>
        <SportsbookAppBar user={user} signOut={signOut} />
        <img src={diceImage} alt="dice" width="100%" />
        <Outlet />
      </Container>
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
      <Authenticator components={components} formFields={formFields}>
        {({ signOut, user }) => <App signOut={signOut} user={user} />}
      </Authenticator>
    </AmplifyThemeProvider>
  );
}
