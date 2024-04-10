import React, { useRef, useEffect, useState } from "react";
import {
  Typography,
  Card,
  IconButton,
  Box,
  styled,
  keyframes,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import { useSystemEvents, useClearHistory } from "../../hooks/useSystemEvents";
import moment from "moment";
import Timeline from "@mui/lab/Timeline";
import TimelineItem from "@mui/lab/TimelineItem";
import TimelineSeparator from "@mui/lab/TimelineSeparator";
import TimelineConnector from "@mui/lab/TimelineConnector";
import TimelineContent from "@mui/lab/TimelineContent";
import TimelineOppositeContent from "@mui/lab/TimelineOppositeContent";
import TimelineDot from "@mui/lab/TimelineDot";
import RepeatIcon from "@mui/icons-material/Repeat";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorIcon from "@mui/icons-material/Error";
import StartIcon from "@mui/icons-material/Start";
import ThumbUpOffAltIcon from '@mui/icons-material/ThumbUpOffAlt';
import PauseIcon from "@mui/icons-material/Pause";
import RestartAltIcon from '@mui/icons-material/RestartAlt';import Button from "@mui/material/Button";
import { Unstable_Popup as BasePopup } from "@mui/base/Unstable_Popup";

const ChatContainer = styled(Box)(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  height: "500px",
  maxWidth: "100%",
  backgroundColor: theme.palette.background.paper,
  overflow: "auto",
  position: "relative",
  padding: theme.spacing(2),
}));

const grey = {
    50: '#F3F6F9',
    100: '#E5EAF2',
    200: '#DAE2ED',
    300: '#C7D0DD',
    400: '#B0B8C4',
    500: '#9DA8B7',
    600: '#6B7A90',
    700: '#434D5B',
    800: '#303740',
    900: '#1C2025',
  };
  
const PopupBody = styled('div')(
    ({ theme }) => `
    max-width: 650px;
    padding: 12px 16px;
    margin: 8px;
    border-radius: 8px;
    border: 1px solid ${theme.palette.mode === 'dark' ? grey[700] : grey[200]};
    background-color: ${theme.palette.mode === 'dark' ? grey[900] : '#fff'};
    box-shadow: ${
      theme.palette.mode === 'dark'
        ? `0px 4px 8px rgb(0 0 0 / 0.7)`
        : `0px 4px 8px rgb(0 0 0 / 0.1)`
    };
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.875rem;
    z-index: 1;
  `,
  );

  const SystemEvents = () => {
    const [anchor, setAnchor] = useState(null);
    const [selectedEvent, setSelectedEvent] = useState(null);
  
    const handleClick = (event, eventData) => {
      if (selectedEvent === eventData) {
        // Close the popup if the same event is clicked again
        setAnchor(null);
        setSelectedEvent(null);
      } else {
        setAnchor(event.currentTarget);
        setSelectedEvent(eventData);
      }
    };
  
    const handleClose = () => {
      setAnchor(null);
      setSelectedEvent(null);
    };
  
    const open = Boolean(anchor);
    const id = open ? "simple-popper" : undefined;
  
    const { data: systemEvents, isLoading: loadingSystemEvents } =
      useSystemEvents();
    const { mutateAsync: clearHistory } = useClearHistory();
    const containerRef = useRef(null);
  

  
    const handleScroll = () => {
      // Close the popup when scrolling the timeline
      setAnchor(null);
      setSelectedEvent(null);
    };
  
    const getIcon = (detailType) => {
      switch (detailType) {
        case "UpdatedOdds":
          return <RepeatIcon color="primary" />;
        case "EventClosed":
          return <ErrorIcon color="error" />;
        case "BetSettlementComplete":
          return <CheckCircleIcon color="success" />;
        case "SettlementStarted":
          return <StartIcon color="primary" />;
        case "BetsPlaced":
          return <ThumbUpOffAltIcon color="success" />;
        case "MarketSuspended":
          return <PauseIcon color="info" />;
        case "MarketUnsuspended":
          return <RestartAltIcon color="success" />;
        default:
          return null;
      }
    };
    const getEventName = (eventName) => {
      switch (eventName) {
        case "com.livemarket.UpdatedOdds":
            return "Updated Odds handled";
        case "com.trading.UpdatedOdds":
        case "com.thirdparty.UpdatedOdds":
          return "Updated Odds";
        case "com.livemarket.EventClosed":
          return "Live market Event Closed";
        case "com.thirdparty.EventClosed":
          return "Event Closed";
        case "com.livemarket.MarketSuspended":
            return "Market Suspended handled";
        case "com.thirdparty.MarketSuspended":
          return "Market Suspended";
        case "com.thirdparty.MarketUnsuspended":
          return "Market Unsuspended";
        case "com.livemarket.MarketUnsuspended":
            return "Market Unsuspended handled";
        case "com.betting.settlement.BetSettlementComplete":
          return "Bet Settlement Complete";
        case "com.betting.SettlementStarted":
          return "Settlement Started";
        case "com.betting.BetsPlaced":
          return "Bets Placed";
        default:
          return eventName;
      }
    };
  
    if (loadingSystemEvents) return <Typography>Loading...</Typography>;
  
    const events = systemEvents.slice(-6); // Retain only the last 20 events
  
    return (
        <Card style={{maxWidth: '100%'}}>
          <Box display="flex" justifyContent="flex-end" p={1}>
            <IconButton color="error" size="small" onClick={clearHistory}>
              Clear
              <DeleteIcon />
            </IconButton>
          </Box>
          <ChatContainer ref={containerRef} onScroll={handleScroll}>
            <Timeline style={{maxWidth: '100%'}}>
              {events.map((event, index) => {
                const isLeft = index % 2 === 0;
                const align = isLeft ? "right" : "left";
                return (
                  <TimelineItem key={index} style={{maxWidth: '100%'}}>
                  <TimelineOppositeContent
                    sx={{ m: "auto 0" }}
                    align={align}
                    maxWidth={"100%"}
                    variant="body2"
                    color="text.secondary"
                  >
                    {moment(event.timestamp).format("MMM D, YYYY h:mm A")}
                  </TimelineOppositeContent>
                  <TimelineSeparator>
                    <TimelineConnector />
                    <TimelineDot>{getIcon(event.detailType)}</TimelineDot>
                    <TimelineConnector />
                  </TimelineSeparator>
                  <TimelineContent sx={{ py: "12px", px: 2, maxWidth: "100%" }}>
                    <Typography variant="caption" style={{ wordWrap: "break-word" }}>
                      {getEventName(event.source+'.'+event.detailType)}
                    </Typography>
                    <Button
                      aria-describedby={id}
                      variant="outlined"
                      type="button"
                      onClick={(e) => handleClick(e, event)}
                    >
                      Details
                    </Button>
                    <BasePopup
                      id={id}
                      open={open && selectedEvent === event}
                      anchor={anchor}
                      onClose={handleClose}
                    >
                      <PopupBody>
                        <Typography variant="caption" component="span">
                          {selectedEvent?.detail}
                        </Typography>
                      </PopupBody>
                    </BasePopup>
                  </TimelineContent>
                  </TimelineItem>
            );
          })}
        </Timeline>
      </ChatContainer>
    </Card>
  );
};
  
  export default SystemEvents;