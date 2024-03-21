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
        disabled={marketStatus?.status !== 'Active'}
      >
        {eventValue}
      </Button>
      <Typography sx={{ fontSize: 10, textAlign: "center" }}>{label}</Typography>
      </Box>
  );
}


export const EventOdds = () => {
  const { addToSlip } = useBetSlip();
  const { data: events, isLoading: loadingEvents } = useEvents();
  const suspendedMarkets = useMarket();
  const [marketStatus, setMarketStatus] = useState('');

  useEffect(() => {
    if(events!==undefined && suspendedMarkets.find!==undefined){
    events.map((event) => {
      const internalEvent = suspendedMarkets.find((market) => market.eventId === event.eventId);
      event.marketstatus = internalEvent?.marketstatus;
    })
  }
  });
  
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

  return (
    <Card style={{ maxWidth: "1600px", height: "220px" }}>
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
    </Card>
  );
};

export default EventOdds;
