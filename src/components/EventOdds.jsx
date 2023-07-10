import { Typography, Card, Button, Box } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { useEvents } from "../hooks/useEvents";
import { useBetSlip } from "../providers/BetSlipContext";

const dateOptions = {
  year: "numeric",
  month: "short",
  day: "numeric",
  hour: "numeric",
  minute: "numeric",
};

const renderOdds = (params) => {
  const { addToSlip } = useBetSlip();

  return (
    <Button
      variant="outlined"
      size="small"
      tabIndex={params.hasFocus ? 0 : -1}
      onClick={() => addToSlip(params.row, params.field)}
    >
      {params.value}
    </Button>
  );
};

export const EventOdds = () => {
  const { data: events, isLoading: loadingEvents } = useEvents();

  if (loadingEvents) return <Typography>Loading...</Typography>;

  const columns = [
    {
      field: "eventName",
      headerName: "Event",
      sortable: false,
      flex: 1,
      renderCell: ({ row }) => (
        <Box>
          <Typography variant={"subtitle2"} fontWeight={600}>
            {row.home} vs {row.away}
          </Typography>
          <Typography variant={"caption"}>
            Starts at {new Date(row.start).toLocaleString("en-GB", dateOptions)}
          </Typography>
        </Box>
      ),
    },
    {
      field: "homeOdds",
      headerName: "Home Win",
      sortable: false,
      align: "center",
      headerAlign: "center",
      renderCell: renderOdds,
    },
    {
      field: "awayOdds",
      headerName: "Away Win",
      sortable: false,
      align: "center",
      headerAlign: "center",
      renderCell: renderOdds,
    },
    {
      field: "drawOdds",
      headerName: "Draw",
      sortable: false,
      align: "center",
      headerAlign: "center",
      renderCell: renderOdds,
    },
    {
      field: "updatedAt",
    },
  ];

  return (
    <Card>
      <Typography variant="h5" sx={{ padding: 2 }}>
        Latest Odds
      </Typography>
      <DataGrid
        rows={events}
        columns={columns}
        initialState={{
          pagination: {
            paginationModel: {
              pageSize: 10,
            },
          },
          sorting: {
            sortModel: [{ field: "updatedAt", sort: "desc" }],
          },
          columns: {
            columnVisibilityModel: {
              updatedAt: false,
            },
          },
        }}
        getRowId={(row) => row?.eventId}
        disableColumnSelector
        disableColumnFilter
        disableColumnMenu
        pageSizeOptions={[10]}
      />
    </Card>
  );
};

export default EventOdds;
