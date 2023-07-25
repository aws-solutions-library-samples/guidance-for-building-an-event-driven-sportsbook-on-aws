import * as React from 'react';
import {
    Typography,
    Box,
    Accordion,
    AccordionDetails,
    AccordionSummary,
    IconButton,
} from "@mui/material"

import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import EventOdds from "../components/admin/EventOdds";
import SystemEvents from "../components/admin/SystemEvents";

export default function Home() {
  const [expanded, setExpanded] = React.useState(false);
  // const {data: eventHistory, isLoading: clearningHistory} = useClearHistory(); 

  const handleChange = (panel) => (event, isExpanded) => {
    setExpanded(isExpanded ? panel : false);
  };
  return (
    <Box mt={4}>
      <Accordion expanded={expanded === 'eventOdds'} onChange={handleChange('eventOdds')}>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="eventOddsbh-content"
          id="eventOddsbh-header"
          sx={{ color: 'text.primary', fontSize: 34, fontWeight: 'medium' }}
        >
          <Typography variant="h5" sx={{ width: '33%', flexShrink: 0, padding:2 }}>Manage Markets</Typography>
          <Typography sx={{ color: 'text.secondary', padding: 2 }}>Supsend and close markets and events</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <EventOdds />
        </AccordionDetails>
      </Accordion>
      <Accordion>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
        >
          <Typography variant="h5" sx={{ width: '33%', flexShrink: 0, padding:2 }}>Observe Events</Typography>
          <Typography sx={{ color: 'text.secondary', padding: 2 }}>View ongoing system events across sportsbook</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <SystemEvents />
        </AccordionDetails>
      </Accordion>
    </Box>
  );
}
