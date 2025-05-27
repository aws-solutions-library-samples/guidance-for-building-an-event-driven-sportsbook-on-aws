import { Typography, Card, useTheme, useMediaQuery } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { useBets } from "../hooks/useBets";
import { darken, lighten, styled } from "@mui/material/styles";
import { Pagination } from '@mui/material';
import { decimalToFraction } from "../utils/oddsConverter";
import { useGlobal } from "../providers/GlobalContext";

const dateOptions = {
  year: "numeric",
  month: "short",
  day: "numeric",
  hour: "numeric",
  minute: "numeric",
};

const conditionFormat = {
  homeWin: "Home Win",
  awayWin: "Away Win",
  draw: "Draw",
};

const betStatusFormat = {
  placed: "Placed",
  resulted: "Resulted",
  settled: "Settled",
};

const getBackgroundColor = (color, mode) =>
  mode === "dark" ? darken(color, 0.7) : lighten(color, 0.7);

const getHoverBackgroundColor = (color, mode) =>
  mode === "dark" ? darken(color, 0.6) : lighten(color, 0.6);

const getSelectedBackgroundColor = (color, mode) =>
  mode === "dark" ? darken(color, 0.5) : lighten(color, 0.5);

const getSelectedHoverBackgroundColor = (color, mode) =>
  mode === "dark" ? darken(color, 0.4) : lighten(color, 0.4);

const StyledDataGrid = styled(DataGrid)(({ theme }) => ({
  // Make cell text black but keep headers visible in both light/dark mode
  "& .MuiDataGrid-cell": {
    color: "#000000",
  },
  "& .MuiDataGrid-columnHeaders": {
    color: theme.palette.mode === "dark" ? "#ffffff" : "#000000",
    backgroundColor: theme.palette.mode === "dark" ? "#333333" : "#f5f5f5",
  },
  // Remove scrollbar
  "& .MuiDataGrid-virtualScroller::-webkit-scrollbar": {
    display: "none",
  },
  "& .MuiDataGrid-virtualScroller": {
    msOverflowStyle: "none",
    scrollbarWidth: "none",
  },
  // Row styling
  "& .win-row": {
    backgroundColor: getBackgroundColor(
      theme.palette.success.main,
      theme.palette.mode
    ),
    color: "#000000",
    "&:hover": {
      backgroundColor: getHoverBackgroundColor(
        theme.palette.success.main,
        theme.palette.mode
      ),
    },
    "&.Mui-selected": {
      backgroundColor: getSelectedBackgroundColor(
        theme.palette.success.main,
        theme.palette.mode
      ),
      "&:hover": {
        backgroundColor: getSelectedHoverBackgroundColor(
          theme.palette.success.main,
          theme.palette.mode
        ),
      },
    },
  },
  "& .lose-row": {
    backgroundColor: getBackgroundColor(
      theme.palette.error.main,
      theme.palette.mode
    ),
    color: "#000000",
    "&:hover": {
      backgroundColor: getHoverBackgroundColor(
        theme.palette.error.main,
        theme.palette.mode
      ),
    },
    "&.Mui-selected": {
      backgroundColor: getSelectedBackgroundColor(
        theme.palette.error.main,
        theme.palette.mode
      ),
      "&:hover": {
        backgroundColor: getSelectedHoverBackgroundColor(
          theme.palette.error.main,
          theme.palette.mode
        ),
      },
    },
  },
  "& .draw-row": {
    backgroundColor: getBackgroundColor(
      theme.palette.warning.main,
      theme.palette.mode
    ),
    color: "#000000",
    "&:hover": {
      backgroundColor: getHoverBackgroundColor(
        theme.palette.warning.main,
        theme.palette.mode
      ),
    },
    "&.Mui-selected": {
      backgroundColor: getSelectedBackgroundColor(
        theme.palette.warning.main,
        theme.palette.mode
      ),
      "&:hover": {
        backgroundColor: getSelectedHoverBackgroundColor(
          theme.palette.warning.main,
          theme.palette.mode
        ),
      },
    },
  },
}));

const getRowClassName = (params) => {
  const { outcome, event, amount, odds } = params.row;
  
  // Make sure we're working with a valid number for odds
  if (odds === undefined || odds === null || odds === '') {
    return "draw-row";
  }
  
  // Use decimal odds for calculation
  const decimalOdds = parseFloat(odds);
  if (isNaN(decimalOdds)) {
    return "draw-row";
  }
  
  // For decimal odds, the formula is stake * (odds - 1)
  const winAmount = amount * (decimalOdds - 1);
  const profitAmount = winAmount;

  if (outcome === event.outcome && profitAmount > 0) {
    return "win-row";
  } else if (outcome === event.outcome && profitAmount <= 0) {
    return "draw-row";
  } else {
    return "lose-row";
  }
};

const calculateOutcome = (amount, odds, outcome, eventOutcome, currencySymbol) => {
  // Make sure we're working with a valid number for odds
  if (odds === undefined || odds === null || odds === '') {
    return 'N/A';
  }
  
  // Use decimal odds for calculation
  const decimalOdds = parseFloat(odds);
  if (isNaN(decimalOdds)) {
    return 'N/A';
  }
  
  // For decimal odds, the formula is stake * (odds - 1)
  const winAmount = amount * (decimalOdds - 1);
  const profitAmount = outcome === eventOutcome ? amount + winAmount : 0;
  
  // Round up the profitAmount to 2 digits
  const roundedProfitAmount = Math.round(profitAmount * 100) / 100;
  
  if (outcome !== eventOutcome) {
    return "-" + `${currencySymbol}${amount}`;
  } else {
    return `${currencySymbol}${roundedProfitAmount}`;
  }
};

export const BetHistory = () => {
  const { data: bets, isLoading: loadingBets } = useBets();
  const { oddsFormat, currencySymbol } = useGlobal();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  if (loadingBets) return <Typography>Loading Bets...</Typography>;

  // Define mobile and desktop columns separately
  const desktopColumns = [
    {
      field: "eventName",
      headerName: "Event",
      flex: 1,
      headerClassName: 'bets-theme-header',
      sortable: true,
      valueGetter: (value, row, column, apiRef) => {
        if (!row?.event?.home || !row?.event?.away) return 'N/A';
        return `${row.event.home} vs ${row.event.away}`;
      }
    },
    {
      field: "odds",
      headerName: "Your Odds",
      headerClassName: 'bets-theme-header',
      sortable: true,
      valueFormatter: ({ value }) => {
        // Make sure we're working with a valid number
        if (value === undefined || value === null || value === '') {
          return '';
        }
        
        // Convert to fraction for display if oddsFormat is fractional
        // console.log(`BetHistory odds: ${value} -> ${fractionOdds}`);
        const decimalOdds = parseFloat(value).toFixed(2);
        return oddsFormat === "decimal" ? decimalOdds : decimalToFraction(decimalOdds);
      },
    },
    {
      field: "outcome",
      headerName: "You bet on",
      headerClassName: 'bets-theme-header',
      sortable: true,
      valueFormatter: ({ value }) => conditionFormat[value],
    },
    {
      field: "result",
      headerName: "Outcome",
      headerClassName: 'bets-theme-header',
      sortable: true,
      valueGetter: (value, row, column, apiRef) => {
        if (!row?.event?.outcome) return 'N/A';
        return calculateOutcome(
          row.amount,
          row.odds,
          row.outcome,
          row.event.outcome,
          currencySymbol
        );
      }
    },
    {
      field: "event.outcome",
      headerName: "Event outcome",
      headerClassName: 'bets-theme-header',
      sortable: true,
      flex: 1,
      valueGetter: (value, row, column, apiRef) => {
        if (!row?.event?.outcome) return 'N/A';
        return row.event.outcome;
      },
      valueFormatter: ({ value }) => conditionFormat[value],
    },
    {
      field: "placedAt",
      headerName: "Placed",
      headerClassName: 'bets-theme-header',
      sortable: true,
      flex: 1,
      valueFormatter: ({ value }) =>{
        new Date(value).toLocaleString("en-GB", dateOptions)
      },        
    },
    {
      field: "betStatus",
      headerName: "Bet status",
      headerClassName: 'bets-theme-header',
      sortable: true,
      valueFormatter: ({ value }) => betStatusFormat[value],
    }
  ];
  
  // Simplified columns for mobile view
  const mobileColumns = [
    {
      field: "eventName",
      headerName: "Event",
      flex: 1,
      headerClassName: 'bets-theme-header',
      sortable: true,
      valueGetter: (params) =>
        `${params.row.event.home || ""} vs ${params.row.event.away || ""}`,
    },
    {
      field: "outcome",
      headerName: "Bet",
      headerClassName: 'bets-theme-header',
      width: 80,
      valueFormatter: ({ value }) => conditionFormat[value],
    },
    {
      field: "result",
      headerName: "Result",
      headerClassName: 'bets-theme-header',
      width: 80,
      valueGetter: (params) =>
        calculateOutcome(
          params.row.amount,
          params.row.odds,
          params.row.outcome,
          params.row.event.outcome,
          currencySymbol
        ),
    }
  ];

  const columns = isMobile ? mobileColumns : desktopColumns;

  return (
    <div style={{ padding: "9px" }} >
    <Card className="recent-trades">
      <Typography variant="h5" className="title" sx={{ padding: 2 }}>
        Placed Bets
      </Typography>
      <StyledDataGrid className="bets-datagrid"
        rows={bets}
        columns={columns}
        initialState={{
          pagination: {
            paginationModel: {
              pageSize: 5,
            },
          },
          sorting: {
            sortModel: [{ field: "placedAt", sort: "desc" }], // Initial sorting
          },
        }}
        getRowId={(row) => row?.betId}
        getRowClassName={getRowClassName}
        disableColumnSelector
        disableColumnFilter
        disableColumnMenu
        hideFooterPagination
        autoHeight
        pageSizeOptions={[5]}
      />
    </Card>
    </div>
  );
};

export default BetHistory;