import { useRouteError } from "react-router-dom";

import { Container, Typography } from "@mui/material";
import { Link } from "react-router-dom";

export default function ErrorPage() {
  const error = useRouteError();
  console.error(error);

  return (
    <Container>
      <Typography variant="h2">Oops!</Typography>
      <Typography variant="h6">
        It looks like something has gone wrong!
      </Typography>
      <Link to="/">
        <Typography variant="h6">Return home</Typography>
      </Link>
    </Container>
  );
}
