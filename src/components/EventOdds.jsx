import { Typography, Card, Button, Box } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import React, { useState, useRef, useEffect } from 'react';
import { useEvents, useMarket } from "../hooks/useEvents";
import { useBetSlip } from "../providers/BetSlipContext";
import Zoom from "@mui/material/Zoom";
import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';
import Slider from "react-slick";

const dateOptions = {
  year: "numeric",
  month: "short",
  day: "numeric",
  hour: "numeric",
  minute: "numeric",
};

const renderOdds = (params) => {
  const { addToSlip } = useBetSlip();
  const eventType = params.field;
  const marketStatus = params.row.marketstatus?.find((ms)=>ms.name === eventType);
  //disabled: (row.marketstatus?.find((ms)=>ms.name === "homeOdds").status !== 'Active'),

  return (
    <Button
      variant="outlined"
      size="small"
      tabIndex={params.hasFocus ? 0 : -1}
      onClick={() => addToSlip(params.row, params.field)}
      disabled={marketStatus?.status === 'Suspended'}
    >
      {params.value}
    </Button>
  );
};


const renderButton = (event, eventType, eventValue, label="") => {
  const { addToSlip } = useBetSlip();
  
  //Find market status that corresponds to eventType and put it into const
  const marketStatus = event?.marketstatus?.find((ms)=>ms.name === eventType);
 
  return (
    <Box>
      <Button
        variant="outlined"
        size="small"
        onClick={() => addToSlip(event, eventType)}
        disabled={marketStatus?.status === 'Suspended'}
      >
        {eventValue}
      </Button>
      <Typography sx={{ fontSize: 10, textAlign: "center" }}>{label}</Typography>
      </Box>
  );
}


export const EventOdds = () => {
  const { data: events, isLoading: loadingEvents } = useEvents();
  const suspendedMarkets = useMarket();

  
    if(events!==undefined && suspendedMarkets.find!==undefined){
    events.map((event) => {
      const internalEvent = suspendedMarkets.find((market) => market.eventId === event.eventId);
      event.marketstatus = internalEvent?.marketstatus;
    })
  }
  
  
  if (loadingEvents) return <Typography>Loading...</Typography>;
  const settings = {
    className: "center",
    infinite: true,
    centerPadding: "60px",
    slidesToShow: 5,
    swipeToSlide: true,
    variableWidth: true,
    afterChange: function(index) {
      console.log(
        `Slider Changed to: ${index + 1}, background: #222; color: #bada55`
      );
    }
  };

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
    <Card style={{ maxWidth: "1600px", height: "980px" }}>
      <Typography variant="h5" sx={{ padding: 2 }}>
        In Soccer Today
      </Typography>
      <Slider {...settings}>
        {events.map((event) => (
          <div key={event.eventId} style={{ padding: "10px" }}>
            <Card style={{ margin: "10px" }}>
              <Box sx={{ padding: 2 }}>
                <Typography variant="subtitle2" fontWeight={600}>
                  {event.home} vs {event.away}
                </Typography>
                <Typography variant="caption">
                  Starts at{" "}
                  {new Date(event.start).toLocaleString("en-GB", dateOptions)}
                </Typography>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-around",
                    marginTop: 1,
                  }}
                >
                  <Zoom in={true} timeout={500}>
                    {renderButton(event, "homeOdds", event.homeOdds, "Home")}
                  </Zoom>
                  <Zoom in={true} timeout={500}>
                    {renderButton(event, "drawOdds", event.drawOdds, "Draw")}
                  </Zoom>
                  <Zoom in={true} timeout={500}>
                    {renderButton(event, "awayOdds", event.awayOdds, "Away")}
                  </Zoom>
                </Box>
              </Box>
            </Card>
          </div>
        ))}
      </Slider>
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
