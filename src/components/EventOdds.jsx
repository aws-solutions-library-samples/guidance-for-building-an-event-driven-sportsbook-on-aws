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
  const marketStatus = params.row.marketstatus?.find((ms) => ms.name === eventType);
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


const renderButton = (event, eventType, eventValue, label = "") => {
  const { addToSlip } = useBetSlip();

  //Find market status that corresponds to eventType and put it into const
  const marketStatus = event?.marketstatus?.find((ms) => ms.name === eventType);

  return (
    <Box>
      <Button
        size="small"
        onClick={() => addToSlip(event, eventType)}
        disabled={marketStatus?.status === 'Suspended'}
        className="soccer-odds-button"
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
  const [showSlider, setShowSlider] = useState(true);


  if (events !== undefined && suspendedMarkets.find !== undefined) {
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
    slidesToShow: 4,
    slidesToScroll: 1,
    swipeToSlide: true,
    afterChange: function (index) {
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

  // Array of flag URLs
const flagUrls = [
  "https://cdn.sportmonks.com/images/soccer/teams/15/2447.png",
  "https://cdn.sportmonks.com/images/soccer/teams/9/6953.png",
  "https://cdn.sportmonks.com/images/soccer/teams/18/2706.png",
  "https://cdn.sportmonks.com/images/soccer/teams/26/2650.png",
  "https://cdn.sportmonks.com/images/soccer/teams/26/2394.png",
  "https://cdn.sportmonks.com/images/soccer/teams/29/1789.png",
  "https://cdn.sportmonks.com/images/soccer/teams/7/1703.png",
  "https://cdn.sportmonks.com/images/soccer/teams/28/1020.png",
  "https://cdn.sportmonks.com/images/soccer/teams/11/939.png",
  "https://cdn.sportmonks.com/images/soccer/teams/6/390.png",
  "https://cdn.sportmonks.com/images/soccer/teams/22/86.png",
  "https://cdn.sportmonks.com/images/soccer/teams/30/62.png",
  "https://cdn.sportmonks.com/images/soccer/teams/21/53.png"

];

// Function to get a random flag URL
const getRandomFlag = () => {
  const randomIndex = Math.floor(Math.random() * flagUrls.length);
  return flagUrls[randomIndex];
  
};

  return (
    <Card style={{ backgroundColor: "transparent", maxWidth: "1600px", height: showSlider ? "290px" : "750px" }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 2 }}>
        <Typography variant="h5" className="title">
          In Soccer Today
        </Typography>
        {/* <Button
      variant="contained"
      onClick={() => setShowSlider(!showSlider)}
    >
      {showSlider ? "Table" : "Slider"}
    </Button> */}
      </Box>
      {showSlider ? (
        <Slider {...settings}>
          {events.slice(0, 6).map((event) => (
            <div key={event.eventId} style={{ padding: "10px" }}>
              <Card className="soccer-today-card" style={{ margin: "10px" }}>

                <Box sx={{ padding: 2 }}>
                  <div class="match__head">
                    <div class="match__head__left">
                      <span class="icons">
                        <i class="icon-football"></i>
                      </span>
                      <span>
                        World Cup 2024
                      </span>
                    </div>
                    <span class="today">
                      Today / 12:00
                    </span>
                  </div>

                  <div class="match__vs">
                    <div class="match__vs__left">
                      <span>
                      {event.home}
                      </span>
                      <span class="flag">
                      <img src={getRandomFlag()} alt={event.home} />
                      </span>
                    </div>
                    <span class="vs">
                      Vs
                    </span>
                    <div class="match__vs__left">
                      <span class="flag">
                      <img src={getRandomFlag()} alt={event.home} />
                      </span>
                      <span>
                      {event.away}
                      </span>
                    </div>
                  </div>


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
      ) : (
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
      )}
    </Card>
  );
};

export default EventOdds;