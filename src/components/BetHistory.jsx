import { Typography, Card } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { useBets } from "../hooks/useBets";
import { darken, lighten, styled } from "@mui/material/styles";
import { Pagination } from '@mui/material';
import { decimalToFraction } from "../utils/oddsConverter";

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
  "& .win-row": {
    backgroundColor: getBackgroundColor(
      theme.palette.success.main,
      theme.palette.mode
    ),
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

const calculateOutcome = (amount, odds, outcome, eventOutcome) => {
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
    return "-" + `$${amount}`;
  } else {
    return `$${roundedProfitAmount}`;
  }
};

export const BetHistory = () => {
  const { data: bets, isLoading: loadingBets } = useBets();
  if (loadingBets) return <Typography>Loading Bets...</Typography>;

  const columns = [
    {
      field: "eventName",
      headerName: "Event",
      flex: 1,
      headerClassName: 'bets-theme-header',
      sortable: true, // Add sortable prop
      valueGetter: (params) =>
        `${params.row.event.home || ""} vs ${params.row.event.away || ""}`,
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
        
        // Convert to fraction for display
        const fractionOdds = decimalToFraction(value);
        // console.log(`BetHistory odds: ${value} -> ${fractionOdds}`);
        return fractionOdds;
      },
    },
    {
      field: "outcome",
      headerName: "You bet on",
      headerClassName: 'bets-theme-header',
      sortable: true, // Add sortable prop
      valueFormatter: ({ value }) => conditionFormat[value],
    },
    {
      field: "result",
      headerName: "Outcome",
      headerClassName: 'bets-theme-header',
      sortable: true, // Add sortable prop
      valueGetter: (params) =>
        calculateOutcome(
          params.row.amount,
          params.row.odds,
          params.row.outcome,
          params.row.event.outcome
        ),
    },
    {
      field: "event.outcome",
      headerName: "Event outcome",
      headerClassName: 'bets-theme-header',
      sortable: true, // Add sortable prop
      flex: 1,
      valueGetter: (params) =>
        `${params.row.event.outcome || ""}`,
      valueFormatter: ({ value }) => conditionFormat[value],
    },
    {
      field: "placedAt",
      headerName: "Placed",
      headerClassName: 'bets-theme-header',
      sortable: true, // Add sortable prop
      flex: 1,
      valueFormatter: ({ value }) =>
        new Date(value).toLocaleString("en-GB", dateOptions),
    },
    {
      field: "betStatus",
      headerName: "Bet status",
      headerClassName: 'bets-theme-header',
      sortable: true, // Add sortable prop
      valueFormatter: ({ value }) => betStatusFormat[value],
    }
  ];


  return (
    <div style={{ padding: "9px" }} >
    <Card className="recent-trades">
      <Typography variant="h5" className="title" sx={{ padding: 2 }}>
        Recent Trades
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
        pageSizeOptions={[10]}
        slotProps={{
          pagination: {
            className: 'custom-pagination'
          }
        }}
      />
    </Card>
    </div>
  );
};

export default BetHistory;