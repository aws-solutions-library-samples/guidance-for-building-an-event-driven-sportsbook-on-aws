import * as React from 'react';
import {
    Typography,
    Box,
    Accordion,
    AccordionDetails,
    AccordionSummary,
    IconButton,
    useMediaQuery,
    useTheme,
} from "@mui/material"

import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import EventOdds from "../components/admin/EventOdds";
import SystemEventsTable from "../components/admin/SystemEventsTable";

export default function Admin() {
  const [expanded, setExpanded] = React.useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  const handleChange = (panel) => (event, isExpanded) => {
    setExpanded(isExpanded ? panel : false);
  };
  
  return (
    <Box 
      mt={4} 
      sx={{ 
        maxWidth: "1600px",
        width: "100%",
        mx: "auto",
        px: { xs: 1, sm: 2 },
        overflow: 'hidden'
      }}
    >
      <Accordion expanded={expanded === 'eventOdds'} onChange={handleChange('eventOdds')}>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="eventOddsbh-content"
          id="eventOddsbh-header"
          sx={{ 
            color: 'text.primary', 
            fontSize: isMobile ? 16 : { xs: 20, sm: 24, md: 34 },
            fontWeight: 'medium',
            flexDirection: isMobile ? 'column' : 'row',
            alignItems: isMobile ? 'flex-start' : 'center',
            minHeight: isMobile ? '48px' : '64px',
            padding: isMobile ? '0px 8px' : undefined
          }}
        >
          <Typography 
            variant={isMobile ? "h6" : "h5"}
            sx={{ 
              width: isMobile ? '100%' : '33%', 
              flexShrink: 0, 
              padding: isMobile ? '4px 0' : 2,
              fontSize: isMobile ? '1rem' : undefined
            }}
          >
            Manage Markets
          </Typography>
          {!isMobile && (
            <Typography 
              sx={{ 
                color: 'text.secondary', 
                padding: 2
              }}
            >
              Suspend and close markets and events
            </Typography>
          )}
        </AccordionSummary>
        <AccordionDetails sx={{ overflow: 'hidden', padding: isMobile ? '8px 4px' : undefined }}>
          <EventOdds />
        </AccordionDetails>
      </Accordion>
      
      <Accordion expanded={expanded === 'systemEvents'} onChange={handleChange('systemEvents')}>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="systemEventsbh-content"
          id="systemEventsbh-header"
          sx={{ 
            color: 'text.primary', 
            fontSize: isMobile ? 16 : { xs: 20, sm: 24, md: 34 },
            fontWeight: 'medium',
            flexDirection: isMobile ? 'column' : 'row',
            alignItems: isMobile ? 'flex-start' : 'center',
            minHeight: isMobile ? '48px' : '64px',
            padding: isMobile ? '0px 8px' : undefined
          }}
        >
          <Typography 
            variant={isMobile ? "h6" : "h5"}
            sx={{ 
              width: isMobile ? '100%' : '33%', 
              flexShrink: 0, 
              padding: isMobile ? '4px 0' : 2,
              fontSize: isMobile ? '1rem' : undefined
            }}
          >
            Observe Events
          </Typography>
          {!isMobile && (
            <Typography 
              sx={{ 
                color: 'text.secondary', 
                padding: 2
              }}
            >
              View ongoing system events across sportsbook
            </Typography>
          )}
        </AccordionSummary>
        <AccordionDetails sx={{ overflow: 'hidden', padding: isMobile ? '8px 4px' : undefined }}>
          <SystemEventsTable />
        </AccordionDetails>
      </Accordion>
    </Box>
  );
}
