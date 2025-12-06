import React, { useState } from "react";
import { Box, CssBaseline, Grid, IconButton } from "@mui/material";
import Sidebar from "./Sidebar";
import Chat from "./Chat";
import EmbeddedFiles from "./EmbeddedFiles";
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [embeddedOpen, setEmbeddedOpen] = useState(true);

  return (
    <Box sx={{ flexGrow: 1 }}>
      <CssBaseline />
       <Box sx={{ display: 'flex', alignItems: 'center', mb: 1, justifyContent: 'space-between' }}>
         <Box sx={{ display: 'flex', alignItems: 'center' }}>
           <IconButton onClick={() => setSidebarOpen(!sidebarOpen)}>
             {sidebarOpen ? <CloseIcon /> : <MenuIcon />}
           </IconButton>
           <span style={{ marginRight: 16 }}>Upload</span>
         </Box>
         <Box sx={{ display: 'flex', alignItems: 'center' }}>
           <span style={{ marginRight: 8 }}>Embedded Files</span>
           <IconButton onClick={() => setEmbeddedOpen(!embeddedOpen)}>
             {embeddedOpen ? <CloseIcon /> : <MenuIcon />}
           </IconButton>
         </Box>
       </Box>
      <Grid container spacing={0} sx={{ height: 'calc(100vh - 56px)' }}>
        {sidebarOpen && (
          <Grid item xs={3} sx={{ height: '100%' }}>
            <Sidebar />
          </Grid>
        )}
        <Grid item xs={sidebarOpen && embeddedOpen ? 6 : sidebarOpen || embeddedOpen ? 9 : 12} sx={{ height: '100%' }}>
          <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Chat />
          </Box>
        </Grid>
        {embeddedOpen && (
          <Grid item xs={3} sx={{ height: '100%' }}>
            <EmbeddedFiles />
          </Grid>
        )}
      </Grid>
    </Box>
  );
}
