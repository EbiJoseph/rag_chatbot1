import React, { useState, useEffect } from "react";
import { Box, Typography, Button, Divider, LinearProgress } from "@mui/material";
import axios from "axios";

export default function Sidebar() {
  const [backendStatus, setBackendStatus] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);

  useEffect(() => {
    axios.get("http://127.0.0.1:8000/home").then(res => setBackendStatus(res.data)).catch(() => setBackendStatus(null));
  }, []);

  const handleFileChange = (e) => {
    setSelectedFiles(Array.from(e.target.files));
  };

  const handleUpload = async () => {
    if (!selectedFiles.length) return;
    setUploading(true);
    const formData = new FormData();
    selectedFiles.forEach(file => formData.append("files", file));
    // You need to implement the backend endpoint for file upload if not present
    await axios.post("http://127.0.0.1:8000/upload", formData).catch(() => {});
    setUploading(false);
    setSelectedFiles([]);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Upload & Embed Documents
      </Typography>
      <Divider sx={{ mb: 2 }} />
      <input
        type="file"
        multiple
        onChange={handleFileChange}
        style={{ marginBottom: 12 }}
      />
      <Button
        variant="contained"
        color="primary"
        onClick={handleUpload}
        disabled={uploading || !selectedFiles.length}
        fullWidth
        sx={{ mb: 2 }}
      >
        Upload
      </Button>
      {uploading && <LinearProgress sx={{ mb: 2 }} />}
      <Divider sx={{ my: 2 }} />
      <Typography variant="body2" color={backendStatus?.status === "ok" ? "green" : "red"}>
        Backend: {backendStatus?.status === "ok" ? "Ready" : "Not Ready"}
      </Typography>
      <Typography variant="caption" display="block" sx={{ mt: 1 }}>
        {backendStatus?.embedding}
        <br />
        {backendStatus?.vectorstore}
        <br />
        {backendStatus?.llm}
      </Typography>
    </Box>
  );
}
