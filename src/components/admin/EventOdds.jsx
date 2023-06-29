import { Typography, Card, Button, Box, ButtonGroup } from "@mui/material";
import CancelIcon from '@mui/icons-material/Cancel';
import { DataGrid } from "@mui/x-data-grid";
import { useEvents } from "../../hooks/useEvents";

const dateOptions = {
  year: "numeric",
  month: "short",
  day: "numeric",
  hour: "numeric",
  minute: "numeric",
};

const renderOdds = (params) => {

  return (
    <ButtonGroup>
        <Button
        variant="outlined"
        size="small"
        onClick={() => {
            suspendMarket({ event: params.row.eventId, market: params.field });
        }}
        >
            Suspend
        </Button>
        <Button         
        variant="outlined"
        size="small"
        color="error"
        onClick={() => {
            closeMarket({ event: params.row.eventId, market: params.field });
        }}>
            Close
        </Button>
    </ButtonGroup>
  );
};

const renderActions = (params) => {
    return (
        <ButtonGroup>
            <Button
            size="small"
            startIcon={<CancelIcon />}
            onClick={() => {
                console.log('closing event', params.row.eventId)
            }}>
                End Event
            </Button>
        </ButtonGroup>
    )
}

const suspendMarket = ({ event, market}) => {
    // call suspend event service
    console.log(`suspending market '${market}' (${event})`);
}

const closeMarket = ({ event, market}) => {
    console.log(`closing market '${market}' (${event})`);
}

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
      flex: 1,
      sortable: false,
      align: "center",
      headerAlign: "center",
      renderCell: renderOdds,
    },
    {
      field: "awayOdds",
      headerName: "Away Win",
      flex: 1,
      sortable: false,
      align: "center",
      headerAlign: "center",
      renderCell: renderOdds,
    },
    {
      field: "drawOdds",
      headerName: "Draw",
      flex: 1,
      sortable: false,
      align: "center",
      headerAlign: "center",
      renderCell: renderOdds,
    },
    {
        field: "eventActions",
        headerName: "Actions",
        flex: 1,
        align: "center",
        sortable: false,
        headerAlign: "center",
        renderCell: renderActions,
    }
  ];



  return (
    <Card>
      <Typography variant="h5" sx={{ padding: 2 }}>
        Current Events
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
