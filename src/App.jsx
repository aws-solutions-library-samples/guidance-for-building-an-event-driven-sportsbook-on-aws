import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";

import { Amplify, Auth } from "aws-amplify";
import { Authenticator, ThemeProvider } from "@aws-amplify/ui-react";
import "@aws-amplify/ui-react/styles.css";

import useAmplifyTheme from "./hooks/useAmplifyTheme";

import { AppBar, Button, Typography } from "@mui/material";

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
});

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

const App = ({ user, signOut }) => {
  const [count, setCount] = useState(0);
  return (
    <>
      <div>
        <a href="https://vitejs.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <p>Welcome {user.attributes.email}</p>
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.jsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
      <Button onClick={signOut}>Sign Out</Button>
    </>
  );
};

export default function AuthenticatedApp() {
  const theme = useAmplifyTheme();
  return (
    <ThemeProvider theme={theme}>
      <Authenticator components={components} formFields={formFields}>
        {({ signOut, user }) => <App signOut={signOut} user={user} />}
      </Authenticator>
    </ThemeProvider>
  );
}
