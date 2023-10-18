import { Typography, Card } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";

import { useBets } from "../hooks/useBets";

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

export const BetHistory = () => {
  const { data: bets, isLoading: loadingBets } = useBets();
  if (loadingBets) return <Typography>Loading Bets...</Typography>;

  const columns = [
    {
      field: "eventName",
      headerName: "Event",
      flex: 1,
      sortable: false,
      valueGetter: (params) =>
        `${params.row.event.home || ""} vs ${params.row.event.away || ""}`,
    },
    {
      field: "odds",
      headerName: "Your Odds",
      sortable: false,
    },
    {
      field: "outcome",
      headerName: "Condition",
      sortable: false,
      valueFormatter: ({ value }) => conditionFormat[value],
    },
    {
      field: "placedAt",
      headerName: "Placed",
      sortable: false,
      flex: 1,
      valueFormatter: ({ value }) =>
        new Date(value).toLocaleString("en-GB", dateOptions),
    },
    {
      field: "betStatus",
      headerName: "Bet status",
      sortable: false,
      valueFormatter: ({ value }) => betStatusFormat[value],
    }
  ];

  return (
    <Card>
      <Typography variant="h5" sx={{ padding: 2 }}>
        Your bets
      </Typography>
      <DataGrid
        rows={bets}
        columns={columns}
        initialState={{
          pagination: {
            paginationModel: {
              pageSize: 10,
            },
          },
          sorting: {
            sortModel: [{ field: "placedAt", sort: "desc" }],
          },
        }}
        getRowId={(row) => row?.betId}
        disableColumnSelector
        disableColumnFilter
        disableColumnMenu
        pageSizeOptions={[10]}
      />
    </Card>
  );
};

export default BetHistory;
