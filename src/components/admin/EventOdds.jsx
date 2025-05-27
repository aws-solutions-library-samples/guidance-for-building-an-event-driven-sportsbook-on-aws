import { Typography, Card, Button, Box, ButtonGroup, useMediaQuery, useTheme } from "@mui/material";
import CancelIcon from '@mui/icons-material/Cancel';
import { DataGrid } from "@mui/x-data-grid";
import { useEvents, useFinishEvent, useMarket } from "../../hooks/useEvents";
import { generateClient } from 'aws-amplify/api';
import { suspendMarketMutation, closeMarketMutation, triggerUnsuspendMarketMutation, triggerSuspendMarketMutation } from "../../graphql/mutations";
import { useState } from "react";
import { useEffect } from "react";

const client = generateClient();

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
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

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
      const response = await client.graphql({
        query: triggerSuspendMarketMutation,
        variables: { input }
      })
    } catch (error) {
      // TODO: Proper logging
    }
  };

  const handleUnsuspend = async () => {
    try {
      const input = { eventId: params.row.eventId, market: params.field };
      const response = await client.graphql({
        query: triggerUnsuspendMarketMutation,
        variables: { input }
      })
    } catch (error) {
      // TODO: Proper logging
    }
  };

  const handleClose = () => {
    closeMarket({ event: params.row.eventId, market: params.field });
  };

  return (
    <ButtonGroup 
      orientation={isMobile ? "vertical" : "horizontal"}
      size="small"
    >
      <Button
        variant="outlined"
        size="small"
        onClick={marketStatus === 'Suspended' ? handleUnsuspend : handleSuspend}
        disabled={isLoading}
        sx={{ fontSize: isMobile ? 11 : 'inherit', whiteSpace: 'nowrap' }}
      >
        {marketStatus === 'Suspended' ? 'Unsuspend' : 'Suspend'}
      </Button>
      <Button
        variant="outlined"
        size="small"
        color="error"
        onClick={handleClose}
        disabled={isLoading}
        sx={{ fontSize: isMobile ? 11 : 'inherit', whiteSpace: 'nowrap' }}
      >
        Close
      </Button>
    </ButtonGroup>
  );
};

const suspendMarket = async ({ event, market }) => {
  try {
    const input = { eventId: event, market };
    const response = await client.graphql({
      query: suspendMarketMutation,
      variables: { input }
    })
    console.log(`Market '${market}' (${event}) suspended`);
  } catch (error) {
    console.error(`Error suspending market '${market}' (${event}):`, error);
  }
};

const closeMarket = async ({ event, market }) => {
  try {
    const input = { eventId: event, market };
    const response = await client.graphql({
      query: closeMarketMutation,
      variables: { input }
    })
    console.log(`Market '${market}' (${event}) closed`);
  } catch (error) {
    console.error(`Error closing market '${market}' (${event}):`, error);
  }
};

export const EventOdds = () => {
  const { data: events, isLoading: loadingEvents } = useEvents();
  const { mutateAsync: triggerFinishEvent } = useFinishEvent();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));
  
  const handleTriggerFinishEvent = (eventId, outcome) => triggerFinishEvent(
    { data: { eventId: eventId, outcome: outcome, eventStatus: 'finished'  } }
  );
  
  const handleFinishEvent = async (eventId, outcome) => {
    // console.log('closing event', {'eventId': eventId, 'outcome': outcome})
    handleTriggerFinishEvent(eventId, outcome);
  };
    
  if (loadingEvents) return <Typography>Loading...</Typography>;

  const columns = [
    {
      field: "eventName",
      headerName: "Event",
      sortable: false,
      flex: isMobile ? 1.5 : 2,
      minWidth: isMobile ? 150 : 250,
      renderCell: ({ row }) => (
        <Box sx={{ 
          width: '100%', 
          overflow: 'hidden',
          padding: isMobile ? '4px 0' : '8px 0'
        }}>
          <Typography 
            variant={isMobile ? "subtitle2" : "body1"}
            fontWeight={600}
            sx={{ 
              fontSize: isMobile ? 12 : 16,
              whiteSpace: 'normal',
              lineHeight: 1.3,
              overflow: 'hidden',
              textOverflow: 'ellipsis'
            }}
          >
            {row.home} vs {row.away}
          </Typography>
          <Typography 
            variant={"caption"}
            sx={{ 
              fontSize: isMobile ? 10 : 12,
              display: 'block',
              marginTop: '4px'
            }}
          >
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
      minWidth: isMobile ? 100 : 150,
      renderCell: renderOdds,
    },
    {
      field: "drawOdds",
      headerName: "Draw",
      flex: 1,
      sortable: false,
      align: "center",
      headerAlign: "center",
      minWidth: isMobile ? 100 : 150,
      renderCell: renderOdds,
    },
    {
      field: "awayOdds",
      headerName: "Away Win",
      flex: 1,
      sortable: false,
      align: "center",
      headerAlign: "center",
      minWidth: isMobile ? 100 : 150,
      renderCell: renderOdds,
    },
    {
      field: "eventActions",
      headerName: "Actions",
      flex: 1,
      align: "center",
      sortable: false,
      headerAlign: "center",
      minWidth: isMobile ? 100 : 150,
      renderCell: (params) => {
        return (
          <Button
            size="small"
            variant="contained"
            startIcon={!isMobile && <CancelIcon />}
            onClick={() => {
              handleFinishEvent(params.row.eventId, 'homeWin')
            }}
            sx={{ 
              fontSize: isMobile ? 11 : 'inherit',
              whiteSpace: 'nowrap'
            }}
          >
            {isMobile ? 'End' : 'End Event'}
          </Button>
        )
      }
    }
  ];

  return (
    <Card 
      sx={{ 
        maxWidth: '100%',
        overflow: 'hidden'
      }}
    >
      <Box sx={{ 
        width: '100%', 
        height: { xs: 400, sm: 500, md: 600 },
        '& .MuiDataGrid-root': {
          '& .MuiDataGrid-cell': {
            padding: isMobile ? '8px 4px' : '16px',
          },
          '& .MuiDataGrid-columnHeader': {
            padding: isMobile ? '8px 4px' : '16px',
          },
          '& .MuiDataGrid-columnHeaderTitle': {
            fontSize: isMobile ? 12 : 'inherit',
            fontWeight: 'bold',
            whiteSpace: 'normal',
            lineHeight: 1.2
          }
        }
      }}>
        <DataGrid
          rows={events}
          columns={columns}
          initialState={{
            pagination: {
              paginationModel: {
                pageSize: isTablet ? 5 : 10,
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
          pageSizeOptions={isTablet ? [5, 10] : [10, 25]}
          rowHeight={isMobile ? 80 : 70}
          sx={{
            '& .MuiDataGrid-cell': {
              whiteSpace: 'normal !important',
              wordBreak: 'break-word'
            }
          }}
        />
      </Box>
    </Card>
  );
};

export default EventOdds;
