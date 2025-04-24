import { useState } from "react";
import { globalContext } from "./GlobalContext";
import { use } from "react";

export function GlobalProvider(props) {
    const [bShowSnackbar, setShowSnackbar] = useState(false);
    const [snackbarSeverity, setSnackbarSeverity] = useState('success');
    const [snackbarMessage, setSnackbarMessage] = useState('undefined error');
    const [currencySymbol, setCurrency] = useState('£');
    const [oddsFormat, setOddsFormat] = useState('decimal');

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

    const toggleCurrency = () => {
        switch(currencySymbol){
            case '£':
                setCurrency('€');
                return;
            case '€':
                setCurrency('$');
                return;
            case '$':
                setCurrency('£');
                return;
            default:
                setCurrency('£');
        }
    }

    const toggleOddsFormat = () => {
        switch(oddsFormat){
            case 'decimal':
                setOddsFormat('fractional');
                return;
            case 'fractional':
                setOddsFormat('decimal');
                return;
            default:
                setOddsFormat('decimal');
        }
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
                currencySymbol,
                toggleCurrency,
                oddsFormat,
                toggleOddsFormat,
            }}
            {...props}
        />
    )
}

export default GlobalProvider;