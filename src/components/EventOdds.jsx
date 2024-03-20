import { Typography, Card, Button, Box } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { useEvents } from "../hooks/useEvents";
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

export const EventOdds = () => {
  const { addToSlip } = useBetSlip();
  const { data: events, isLoading: loadingEvents } = useEvents();

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

    <Card style={{ "maxWidth": '1600px', 'height': '220px' }}>
      <Typography variant="h5" sx={{ padding: 2 }}>
        In Soccer Today
      </Typography>
      <Slider {...settings}  >
  {events.map((event) => (
    <div key={event.eventId} style={{ padding: '10px' }}>
      <Card style={{ margin: '10px' }}>
        <Box sx={{ padding: 2 }}>
          <Typography variant="subtitle2" fontWeight={600}>
            {event.home} vs {event.away}
          </Typography>
          <Typography variant="caption">
            Starts at {new Date(event.start).toLocaleString('en-GB', dateOptions)}
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'space-around', marginTop: 1 }}>
            <Zoom in={true} timeout={500}>
              <Button variant="outlined" size="small" onClick={() => addToSlip(event, 'homeOdds')} style={{ margin: '2px' }}>
                {event.homeOdds}
              </Button>
            </Zoom>
            <Zoom in={true} timeout={500}>
              <Button variant="outlined" size="small" onClick={() => addToSlip(event, 'drawOdds')} style={{ margin: '2px' }}>
                {event.drawOdds}
              </Button>
            </Zoom>
            <Zoom in={true} timeout={500}>
              <Button variant="outlined" size="small" onClick={() => addToSlip(event, 'awayOdds')} style={{ margin: '2px' }}>
                {event.awayOdds}
              </Button>
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
