import { Typography, Card } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { useEvents } from "../hooks/useEvents";

const dateOptions = {
  year: "numeric",
  month: "short",
  day: "numeric",
  hour: "numeric",
  minute: "numeric",
};

export const EventOdds = () => {
  const { data: events, isLoading: loadingEvents } = useEvents();

  if (loadingEvents) return <Typography>Loading...</Typography>;
  const sortedEvents = [...events].sort((a, b) => b.updatedAt - a.updatedAt);

  const columns = [
    {
      field: "eventName",
      headerName: "Event",
      flex: 1,
      sortable: false,
      valueGetter: (params) =>
        `${params.row.home || ""} vs ${params.row.away || ""}`,
    },
    {
      field: "homeOdds",
      headerName: "Home Win",
      sortable: false,
    },
    {
      field: "awayOdds",
      headerName: "Away Win",
      sortable: false,
    },
    {
      field: "drawOdds",
      headerName: "Draw",
      sortable: false,
    },
    {
      field: "start",
      headerName: "Starts",
      sortable: false,
      flex: 1,
      valueFormatter: ({ value }) =>
        new Date(value).toLocaleString("en-GB", dateOptions),
    },
    {
      field: "updatedAt",
      headerName: "Updated",
      sortable: false,
      flex: 1,
      valueFormatter: ({ value }) =>
        new Date(value).toLocaleString("en-GB", dateOptions),
    },
  ];

  return (
    <Card>
      <Typography variant="h5" sx={{ padding: 2 }}>
        Latest Odds
      </Typography>
      <DataGrid
        rows={sortedEvents}
        columns={columns}
        initialState={{
          pagination: {
            paginationModel: {
              pageSize: 10,
            },
          },
        }}
        getRowId={(row) => row?.eventId}
        sortingMode="server"
        disableColumnSelector
        disableColumnFilter
        disableColumnMenu
        pageSizeOptions={[10]}
      />
    </Card>
  );
};

export default EventOdds;
