import React, { useState } from "react";
import { Box, Typography, Button, Divider, List, ListItem, ListItemText, LinearProgress } from "@mui/material";
import axios from "axios";

export default function EmbeddedFiles() {
  const [embedding, setEmbedding] = useState(false);
  const [files, setFiles] = useState([]);

  const fetchFiles = () => {
    // In a real app, you might fetch this from the backend
    axios.get("http://127.0.0.1:8000/embedded_files").then(res => setFiles(res.data.files || []));
  };

  const handleEmbed = async () => {
    setEmbedding(true);
    await axios.post("http://127.0.0.1:8000/embed_all").catch(() => {});
    setEmbedding(false);
    fetchFiles();
  };

  React.useEffect(() => {
    fetchFiles();
  }, []);

  return (
    <Box sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Button
        variant="contained"
        color="secondary"
        onClick={handleEmbed}
        disabled={embedding}
        fullWidth
        sx={{ mb: 2 }}
      >
        {embedding ? "Embedding..." : "Embed New Documents"}
      </Button>
      {embedding && <LinearProgress sx={{ mb: 2 }} />}
      <Divider sx={{ mb: 2 }} />
      <Typography variant="h6" gutterBottom>
        Embedded Files
      </Typography>
      <Box sx={{ flex: 1, overflowY: 'auto', minHeight: 0 }}>
        <List dense>
          {files.length === 0 && <ListItem><ListItemText primary="No embedded files yet." /></ListItem>}
          {files.map((file, idx) => (
            <ListItem key={idx}>
              <ListItemText primary={file} />
            </ListItem>
          ))}
        </List>
      </Box>
    </Box>
  );
}
