import { useState } from "react";
import { globalContext } from "./GlobalContext";

export function GlobalProvider(props) {
    const [bShowSnackbar, setShowSnackbar] = useState(false);
    const [snackbarSeverity, setSnackbarSeverity] = useState('success');
    const [snackbarMessage, setSnackbarMessage] = useState('undefined error');

    const closeSnackbar = () => {
        setSnackbarMessage();
        setShowSnackbar(false);
    }

    const showError = (message) => {
        setSnackbarMessage(message);
        setSnackbarSeverity('error');
        setShowSnackbar(true);
    }

    const showWarning = (message) => {
        setSnackbarMessage(message);
        setSnackbarSeverity('warning');
        setShowSnackbar(true);
    }

    const showSuccess = (message) => {
        setSnackbarMessage(message);
        setSnackbarSeverity('success');
        setShowSnackbar(true);
    }

    return (
        <globalContext.Provider
            value={{
                bShowSnackbar,
                closeSnackbar,
                showError,
                showWarning,
                showSuccess,
                snackbarMessage,
                snackbarSeverity,
            }}
            {...props}
        />
    )
}

export default GlobalProvider;