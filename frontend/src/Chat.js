import React, { useState, useRef, useEffect } from "react";
import { Box, Typography, Paper, TextField, Button, Divider } from "@mui/material";
import axios from "axios";
import ReactMarkdown from "react-markdown";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = { role: "user", content: input };
    setMessages((msgs) => [...msgs, userMsg]);
    setLoading(true);
    try {
      const res = await axios.post("http://127.0.0.1:8000/chat", { message: input });
      // Remove angle brackets from bot response
      const cleanResponse = res.data.response.replace(/[<>]/g, "");
      const botMsg = { role: "assistant", content: cleanResponse };
      setMessages((msgs) => [...msgs, botMsg]);
    } catch (e) {
      setMessages((msgs) => [...msgs, { role: "assistant", content: "Error: Could not reach backend." }]);
    }
    setInput("");
    setLoading(false);
  };

  return (
    <Box sx={{ p: 3, height: "90vh", display: "flex", flexDirection: "column" }}>
      <Typography variant="h5" gutterBottom>
        💬 RAG Chatbot
      </Typography>
      <Divider sx={{ mb: 2 }} />
      <Paper sx={{ flex: 1, overflowY: "auto", mb: 2, p: 2, bgcolor: "#fafafa" }}>
        {messages.map((msg, idx) => (
          <Box key={idx} sx={{ textAlign: msg.role === "user" ? "right" : "left", mb: 1 }}>
              {msg.role === "user" ? (
                <Typography variant="body2" color="primary">
                  <b>You:</b> {typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)}
                </Typography>
              ) : (
                <Paper elevation={0} sx={{ p: 1, bgcolor: "#f5f5f5" }}>
                  <Typography variant="body2" color="textSecondary">
                    <b>Bot:</b>
                  </Typography>
                  <ReactMarkdown>{typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)}</ReactMarkdown>
                </Paper>
              )}
          </Box>
        ))}
        <div ref={chatEndRef} />
      </Paper>
      <Box sx={{ display: "flex", gap: 1 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          disabled={loading}
        />
        <Button variant="contained" color="primary" onClick={handleSend} disabled={loading || !input.trim()}>
          Send
        </Button>
      </Box>
    </Box>
  );
}
