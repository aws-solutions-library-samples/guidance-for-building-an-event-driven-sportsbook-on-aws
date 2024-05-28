import { Typography, Card, Button, Box, ButtonGroup } from "@mui/material";
import CancelIcon from '@mui/icons-material/Cancel';
import { DataGrid } from "@mui/x-data-grid";
import { useEvents, useFinishEvent, useMarket } from "../../hooks/useEvents";
import { API, graphqlOperation } from "aws-amplify";
import { suspendMarketMutation, closeMarketMutation, triggerUnsuspendMarketMutation, triggerSuspendMarketMutation } from "../../graphql/mutations";
import { useState } from "react";
import { useEffect } from "react";

const dateOptions = {
  year: "numeric",
  month: "short",
  day: "numeric",
  hour: "numeric",
  minute: "numeric",
};

const renderOdds = (params) => {
  const [isLoading, setIsLoading] = useState(false);
  const [marketStatus, setMarketStatus] = useState('');
  const suspendedMarkets = useMarket();

  //update marketStatus based on corresponding market status from suspendedMarkets array

  useEffect(() => {
    try{
    const markets = suspendedMarkets.find((market) => market.eventId === params.row.eventId)
    const marketstatus = markets?.marketstatus?.find((ms)=>ms.name == params.field);

    if (marketstatus) {
      setMarketStatus(marketstatus.status);
    } else {
      setMarketStatus('Active');
    }
  }
    catch(error){
      console.log(error)
    }
  });
  
  const handleSuspend = async () => {
    try {
      const input = { eventId: params.row.eventId, market: params.field };
      const response = await API.graphql(graphqlOperation(triggerSuspendMarketMutation, { input }));
      console.log(`Market '${params.field}' (${params.row.eventId}) suspended`);
    } catch (error) {
      console.error(`Error suspending market '${params.field}' (${params.row.eventId}):`, error);
    }
  };

  const handleUnsuspend = async () => {
    try {
      const input = { eventId: params.row.eventId, market: params.field };
      const response = await API.graphql(graphqlOperation(triggerUnsuspendMarketMutation, { input }));
      console.log(`Market '${params.field}' (${params.row.eventId}) unsuspended`);
    } catch (error) {
      console.error(`Error unsuspending market '${params.field}' (${params.row.eventId}):`, error);
    }
  };

  const handleClose = () => {
    closeMarket({ event: params.row.eventId, market: params.field });
  };

  return (
    <ButtonGroup>
      <Button
        variant="outlined"
        size="small"
        onClick={marketStatus === 'Suspended' ? handleUnsuspend : handleSuspend}
        disabled={isLoading}
      >
        {marketStatus === 'Suspended' ? 'Unsuspend' : 'Suspend'}
      </Button>
      <Button
        variant="outlined"
        size="small"
        color="error"
        onClick={handleClose}
        disabled={isLoading}
      >
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
            variant="contained"
            onClick={() => {
              EventOdds.handleFinishEvent(params.row.eventId, 'homeWin')
            }}>
                End Event
            </Button>
        </ButtonGroup>
    )
    
}

const suspendMarket = async ({ event, market }) => {
  try {
    const input = { eventId: event, market };
    const response = await API.graphql(graphqlOperation(suspendMarketMutation, { input }));
    console.log(`Market '${market}' (${event}) suspended`);
  } catch (error) {
    console.error(`Error suspending market '${market}' (${event}):`, error);
  }
};

const closeMarket = async ({ event, market }) => {
  try {
    const input = { eventId: event, market };
    const response = await API.graphql(graphqlOperation(closeMarketMutation, { input }));
    console.log(`Market '${market}' (${event}) closed`);
  } catch (error) {
    console.error(`Error closing market '${market}' (${event}):`, error);
  }
};

export const EventOdds = () => {
  const { data: events, isLoading: loadingEvents } = useEvents();
  const { mutateAsync: triggerFinishEvent } = useFinishEvent();
  const handleTriggerFinishEvent = (eventId, outcome) => triggerFinishEvent(
    { data: { eventId: eventId, outcome: outcome, eventStatus: 'finished'  } }
  );
  const handleFinishEvent = async (eventId, outcome) => {
    console.log('closing event', {'eventId': eventId, 'outcome': outcome})
    handleTriggerFinishEvent(eventId, outcome);
    console.log("Event finished. Good luck settling!");
  };
    
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
      field: "drawOdds",
      headerName: "Draw",
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
        field: "eventActions",
        headerName: "Actions",
        flex: 1,
        align: "center",
        sortable: false,
        headerAlign: "center",
        renderCell: (params) => {
          return (
            <ButtonGroup>
                <Button
                size="small"
                variant="contained"
                startIcon={<CancelIcon />}
                onClick={() => {
                  handleFinishEvent(params.row.eventId, 'homeWin')
                }}>
                    End Event
                </Button>
            </ButtonGroup>
        )
       }
    }
  ];

  

  return (
    <Card style={{ "maxWidth": '1600px'}}>
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
