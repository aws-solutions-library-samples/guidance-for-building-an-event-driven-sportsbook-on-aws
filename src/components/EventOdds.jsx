import { Typography, Card, Button, Box } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import React, { useState, useRef, useEffect, forwardRef } from 'react';
import { useEvents, useMarket } from "../hooks/useEvents";
import { useBetSlip } from "../providers/BetSlipContext";
import Zoom from "@mui/material/Zoom";
import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';
import Slider from "react-slick";
import { decimalToFraction } from "../utils/oddsConverter";

const dateOptions = {
  year: "numeric",
  month: "short",
  day: "numeric",
  hour: "numeric",
  minute: "numeric",
};

// Create a forwardRef component for BetSlipButton to work with Zoom
const BetSlipButton = forwardRef(({ event, eventType, eventValue, label = "" }, ref) => {
  const { addToSlip } = useBetSlip();

  //Find market status that corresponds to eventType and put it into const
  const marketStatus = event?.marketstatus?.find((ms) => ms.name === eventType);
  
  // Convert decimal odds to fraction for display
  const displayOdds = decimalToFraction(eventValue);
  
  return (
    <Box ref={ref}>
      <Button
        size="small"
        onClick={() => addToSlip(event, eventType)}
        disabled={marketStatus?.status === 'Suspended'}
        className="soccer-odds-button"
      >
        {displayOdds}
      </Button>
      <Typography sx={{ fontSize: 10, textAlign: "center" }}>{label}</Typography>
    </Box>
  );
});

// Create a separate component for the odds cell renderer
const OddsCell = (params) => {
  const { addToSlip } = useBetSlip();
  const eventType = params.field;
  const marketStatus = params.row.marketstatus?.find((ms) => ms.name === eventType);

  // Convert decimal odds to fraction for display
  const displayOdds = decimalToFraction(params.value);
  
  return (
    <Button
      variant="outlined"
      size="small"
      tabIndex={params.hasFocus ? 0 : -1}
      onClick={() => addToSlip(params.row, params.field)}
      disabled={marketStatus?.status === 'Suspended'}
    >
      {displayOdds}
    </Button>
  );
};

export const EventOdds = () => {
  const { data: events, isLoading: loadingEvents } = useEvents();
  const suspendedMarkets = useMarket();
  const [showSlider, setShowSlider] = useState(true);

  // Array of flag URLs
  const flagUrls = [
    "src/assets/teams/cjfc.png",
    "src/assets/teams/ilfc.png",
    "src/assets/teams/dlfc.png",
    "src/assets/teams/sefc.png",
    "src/assets/teams/ggfc.png",
    "src/assets/teams/rtfc.png",
    "src/assets/teams/ggufc.png",
    "src/assets/teams/sffc.png",
    "src/assets/teams/qpfc.png",
    "src/assets/teams/ttfc.png",
    "src/assets/teams/srfc.png",
    "src/assets/teams/cufc.png",
    "src/assets/teams/cjfc.png",
    "src/assets/teams/ilfc.png",
    "src/assets/teams/edfc.png",
    "src/assets/teams/sefc.png",
    "src/assets/teams/ggufc.png",
    "src/assets/teams/rtufc.png",
  ];

  // Map to store team name to flag URL mapping
  const teamFlagMap = {};
  
  // Function to get a consistent flag URL for a team
  const getTeamFlag = (teamName) => {
    // If team already has an assigned flag, return it
    if (teamFlagMap[teamName]) {
      return teamFlagMap[teamName];
    }
    
    // Find an unused flag
    const usedFlags = Object.values(teamFlagMap);
    const availableFlags = flagUrls.filter(flag => !usedFlags.includes(flag));
    
    // If all flags are used, use the index in the original array based on team name hash
    if (availableFlags.length === 0) {
      const hash = teamName.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
      const index = hash % flagUrls.length;
      teamFlagMap[teamName] = flagUrls[index];
    } else {
      // Assign the first available flag
      teamFlagMap[teamName] = availableFlags[0];
    }
    
    return teamFlagMap[teamName];
  };

  // Update events with market status
  useEffect(() => {
    if (events && Array.isArray(events) && suspendedMarkets && Array.isArray(suspendedMarkets)) {
      events.forEach((event) => {
        const internalEvent = suspendedMarkets.find((market) => market.eventId === event.eventId);
        event.marketstatus = internalEvent?.marketstatus;
      });
    }
  }, [events, suspendedMarkets]);

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
      renderCell: (params) => <OddsCell {...params} />,
    },
    {
      field: "awayOdds",
      headerName: "Away Win",
      sortable: false,
      align: "center",
      headerAlign: "center",
      renderCell: (params) => <OddsCell {...params} />,
    },
    {
      field: "drawOdds",
      headerName: "Draw",
      sortable: false,
      align: "center",
      headerAlign: "center",
      renderCell: (params) => <OddsCell {...params} />,
    },
    {
      field: "updatedAt",
    },
  ];

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
          {events && events.slice(0, 6).map((event) => (
            <div key={event.eventId} style={{ padding: "10px" }}>
              <Card className="soccer-today-card" style={{ margin: "10px" }}>
                <Box sx={{ padding: 2 }}>
                  <div className="match__head">
                    <div className="match__head__left">
                      <span className="icons">
                        <i className="icon-football"></i>
                      </span>
                      <span>
                        World Cup 2024
                      </span>
                    </div>
                    <span className="today">
                      Today / 12:00
                    </span>
                  </div>

                  <div className="match__vs">
                    <div className="match__vs__left">
                      <span>
                      {event.home}
                      </span>
                      <span className="flag">
                      <img src={getTeamFlag(event.home)} alt={event.home} />
                      </span>
                    </div>
                    <span className="vs">
                      Vs
                    </span>
                    <div className="match__vs__left">
                      <span className="flag">
                      <img src={getTeamFlag(event.away)} alt={event.away} />
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
                      <BetSlipButton event={event} eventType="homeOdds" eventValue={event.homeOdds} label="Home" />
                    </Zoom>
                    <Zoom in={true} timeout={500}>
                      <BetSlipButton event={event} eventType="drawOdds" eventValue={event.drawOdds} label="Draw" />
                    </Zoom>
                    <Zoom in={true} timeout={500}>
                      <BetSlipButton event={event} eventType="awayOdds" eventValue={event.awayOdds} label="Away" />
                    </Zoom>
                  </Box>
                </Box>
              </Card>
            </div>
          ))}
        </Slider>
      ) : (
        <DataGrid
          rows={events || []}
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
