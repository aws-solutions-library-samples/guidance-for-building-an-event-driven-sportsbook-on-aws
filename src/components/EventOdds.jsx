import { Typography, Card, Button, Box, Grid, useMediaQuery, useTheme } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import React, { useState, useRef, useEffect, forwardRef } from 'react';
import { useEvents, useMarket } from "../hooks/useEvents";
import { useBetSlip } from "../providers/BetSlipContext";
import { useGlobal } from "../providers/GlobalContext";
import Zoom from "@mui/material/Zoom";
import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';
import Slider from "react-slick";
import { decimalToFraction } from "../utils/oddsConverter";
import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';
import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos';

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
  const { oddsFormat } = useGlobal();

  //Find market status that corresponds to eventType and put it into const
  const marketStatus = event?.marketstatus?.find((ms) => ms.name === eventType);
  
  // Convert decimal odds to fraction for display
  const decimalNum = typeof eventValue === 'string' ? parseFloat(eventValue) : eventValue;
  const displayOdds = oddsFormat == "decimal" ? decimalNum.toFixed(2) : decimalToFraction(decimalNum);
  
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
  const { oddsFormat } = useGlobal();
  const eventType = params.field;
  const marketStatus = params.row.marketstatus?.find((ms) => ms.name === eventType);

  // Convert decimal odds to fraction for display
  const decimalNum = typeof params.value === 'string' ? parseFloat(params.value) : params.value;
  const displayOdds = oddsFormat == "decimal" ? decimalNum.toFixed(2) : decimalToFraction(decimalNum);
  
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
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const sliderRef = useRef(null);

  // Custom arrow components for the slider
  const NextArrow = (props) => {
    const { onClick } = props;
    return (
      <Button 
        className="slick-next-custom"
        onClick={onClick}
        sx={{
          position: 'absolute',
          right: 0,
          top: '50%',
          transform: 'translateY(-50%)',
          zIndex: 2,
          minWidth: '40px',
          backgroundColor: 'rgba(0,0,0,0.5)',
          color: 'white',
          '&:hover': {
            backgroundColor: 'rgba(0,0,0,0.7)',
          }
        }}
      >
        <ArrowForwardIosIcon />
      </Button>
    );
  };

  const PrevArrow = (props) => {
    const { onClick } = props;
    return (
      <Button 
        className="slick-prev-custom"
        onClick={onClick}
        sx={{
          position: 'absolute',
          left: 0,
          top: '50%',
          transform: 'translateY(-50%)',
          zIndex: 2,
          minWidth: '40px',
          backgroundColor: 'rgba(0,0,0,0.5)',
          color: 'white',
          '&:hover': {
            backgroundColor: 'rgba(0,0,0,0.7)',
          }
        }}
      >
        <ArrowBackIosIcon />
      </Button>
    );
  };

  // Array of flag URLs
  let flagUrls = [];
  [
    "cjfc",
    "ilfc",
    "edfc",
    "sefc",
    "ggfc",
    "rtfc",
    "ggufc",
    "sffc",
    "qpfc",
    "ttfc",
    "srfc",
    "cufc",
    "prfc",
    "csfc",
    "nnfc",
    "moonfc",
    "mmfc",
    "ckfc",
    "dlfc",
    "mffc"
  ].forEach(t => {
    flagUrls.push( new URL(`../assets/teams/${t}.png`, import.meta.url).href )
  });

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
    className: "soccer-slider",
    infinite: true,
    speed: 500,
    slidesToShow: 4,
    slidesToScroll: 1,
    swipeToSlide: true,
    nextArrow: <NextArrow />,
    prevArrow: <PrevArrow />,
    responsive: [
      {
        breakpoint: 1200,
        settings: {
          slidesToShow: 3,
          slidesToScroll: 1
        }
      },
      {
        breakpoint: 900,
        settings: {
          slidesToShow: 2,
          slidesToScroll: 1
        }
      },
      {
        breakpoint: 600,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1
        }
      }
    ]
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

  const handleSliderNext = React.useCallback(() => {
    sliderRef.current?.slickNext();
  }, []);

  return (
    <Card style={{ backgroundColor: "transparent", maxWidth: "1600px", minHeight: showSlider ? "420px" : "750px" }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 2 }}>
        <Typography variant="h5" className="title">
          In Soccer Today
        </Typography>
        <Button
          variant="outlined"
          size="small"
          onClick={handleSliderNext}
          sx={{ display: { xs: 'none', md: 'flex' } }}
        >
          See More
        </Button>
      </Box>
      {showSlider ? (
        <Box className="slider-container" sx={{ 
          padding: { xs: '0 10px', md: '0 40px' }, 
          position: 'relative',
          minHeight: '370px', // Fixed height to prevent collapse
          height: '370px'     // Explicit height setting
        }}>
          {events && events.length > 0 ? (
            <Slider ref={sliderRef} {...settings}>
              {events.slice(0, 10).map((event) => (
                <div key={event.eventId} style={{ padding: "10px" }}>
                  <Card className="soccer-today-card" style={{ margin: "10px", height: "350px" }}>
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
                      <div className="team-container">
                        {/* Home team - left aligned */}
                        <div className="team-flag-container">
                          <span className="flag">
                            <img src={getTeamFlag(event.home)} alt={event.home} />
                          </span>
                          <span className="team-name-horizontal">
                            {event.home}
                          </span>
                        </div>
                        
                        <span className="vs">
                          Vs
                        </span>
                        
                        {/* Away team - right aligned */}
                        <div className="away-team-container">
                          <span className="team-name-horizontal text-right">
                            {event.away}
                          </span>
                          <span className="flag">
                            <img src={getTeamFlag(event.away)} alt={event.away} />
                          </span>
                        </div>
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
            <Box sx={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center', 
              justifyContent: 'center',
              height: '370px', // Match the container height
              width: '100%',
              backgroundColor: 'rgba(32, 42, 57, 0.3)',
              borderRadius: '8px'
            }}>
              <Typography variant="h6" sx={{ color: 'text.secondary', mb: 2 }}>
                No events available today
              </Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                Check back later for upcoming events
              </Typography>
            </Box>
          )}
        </Box>
      ) : (
        <DataGrid
          rows={events && events.length > 0 ? events : []}
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
          getRowId={(row) => row?.eventId || Math.random().toString()}
          disableColumnSelector
          disableColumnFilter
          disableColumnMenu
          pageSizeOptions={[10]}
          sx={{
            minHeight: '400px',
            '.MuiDataGrid-main': {
              minHeight: '400px'
            },
            '.MuiDataGrid-virtualScroller': {
              minHeight: '350px'
            },
            '.MuiDataGrid-overlay': {
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: 'rgba(32, 42, 57, 0.3)',
              borderRadius: '4px'
            }
          }}
        />
      )}
    </Card>
  );
};

export default EventOdds;
