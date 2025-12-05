import React from "react";
import { Box, CssBaseline, Grid } from "@mui/material";
import Sidebar from "./Sidebar";
import Chat from "./Chat";
import EmbeddedFiles from "./EmbeddedFiles";

export default function App() {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <CssBaseline />
      <Grid container spacing={0}>
        <Grid item xs={3}>
          <Sidebar />
        </Grid>
        <Grid item xs={6}>
          <Chat />
        </Grid>
        <Grid item xs={3}>
          <EmbeddedFiles />
        </Grid>
      </Grid>
    </Box>
  );
}
