import React, { useEffect, useState } from "react";
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Chip,
  Card,
  CardContent,
  IconButton,
  Divider,
  Badge
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import ClearIcon from "@mui/icons-material/Clear";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import PersonIcon from "@mui/icons-material/Person";
import TopMerchantsBar from "./charts/TopMerchantsBar";
import PaymentStatusPie from "./charts/PaymentStatusPie";
import DynamicChartRenderer from "./DynamicChartRenderer";

const Merchants = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({ topMerchantsByPayments: [], paymentStatusMix: [] });
  const [prompt, setPrompt] = useState("");
  const [aiResponse, setAiResponse] = useState("");
  const [isLoadingAi, setIsLoadingAi] = useState(false);
  const [error, setError] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [responseStatus, setResponseStatus] = useState("");
  const [generatedChart, setGeneratedChart] = useState(null);
  const [isChartResponse, setIsChartResponse] = useState(false);

  useEffect(() => {
    fetch("http://localhost:8000/dashboard/merchants")
      .then((r) => r.json())
      .then((json) => setData(json))
      .catch(() => setData({ topMerchantsByPayments: [], paymentStatusMix: [] }))
      .finally(() => setLoading(false));
  }, []);

  const handlePromptSubmit = async () => {
    if (!prompt.trim()) return;
    
    const userPrompt = prompt.trim();
    setIsLoadingAi(true);
    setError("");
    setAiResponse("");
    setResponseStatus("");
    
    // Add user message to chat history
    const newChatEntry = {
      id: Date.now(),
      type: "user",
      message: userPrompt,
      timestamp: new Date().toLocaleTimeString()
    };
    setChatHistory(prev => [...prev, newChatEntry]);
    
    try {
      const response = await fetch("http://localhost:8000/ai/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: userPrompt,
          userType: "merchant"
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setAiResponse(data.response);
      setResponseStatus(data.status || "success");
      
      // Check if this is a chart response
      if (data.isChart || data.status === "chart_code") {
        setIsChartResponse(true);
        setGeneratedChart(data.response);
      } else {
        setIsChartResponse(false);
        setGeneratedChart(null);
      }
      
      // Add AI response to chat history
      const aiChatEntry = {
        id: Date.now() + 1,
        type: "ai",
        message: data.response,
        timestamp: new Date().toLocaleTimeString(),
        status: data.status,
        note: data.note,
        isChart: data.isChart || data.status === "chart_code"
      };
      setChatHistory(prev => [...prev, aiChatEntry]);
      
    } catch (err) {
      setError(err.message || "Failed to get AI response");
    } finally {
      setIsLoadingAi(false);
    }
  };

  const handleSuggestedPrompt = (suggestedPrompt) => {
    setPrompt(suggestedPrompt);
  };

  const clearChat = () => {
    setChatHistory([]);
    setAiResponse("");
    setError("");
    setResponseStatus("");
  };

  const suggestedPrompts = [
    "Create a bar chart of top performing merchants",
    "Generate a pie chart for merchant trust score distribution",
    "Show me a line chart of merchant payment trends",
    "Create a bar chart comparing merchant payment volumes",
    "Generate a pie chart for merchant loyalty tier distribution",
    "Show me a line chart of merchant trust scores over time",
    "Create a bar chart of merchant dispute rates",
    "Generate a pie chart for merchant compliance scores",
    "Show me a line chart of merchant engagement trends",
    "Create a bar chart of merchant performance rankings"
  ];

  return (
    <Box sx={{ padding: 2 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Merchant Dashboard
      </Typography>
      
      {/* AI Chat Section */}
      <Paper elevation={3} sx={{ padding: 3, marginBottom: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 2 }}>
          <Typography variant="h6">
            Ask AI about Merchant Data
          </Typography>
          <Box>
            <Badge badgeContent={chatHistory.length} color="primary">
              <IconButton onClick={clearChat} color="secondary" title="Clear Chat">
                <ClearIcon />
              </IconButton>
            </Badge>
          </Box>
        </Box>

        {/* Suggested Prompts */}
        <Box sx={{ marginBottom: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            💡 Suggested Prompts:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {suggestedPrompts.map((suggestion, index) => (
              <Chip
                key={index}
                label={suggestion}
                onClick={() => handleSuggestedPrompt(suggestion)}
                variant="outlined"
                size="small"
                sx={{ cursor: 'pointer', '&:hover': { backgroundColor: 'primary.light', color: 'white' } }}
              />
            ))}
          </Box>
        </Box>

        {/* Chat History */}
        {chatHistory.length > 0 && (
          <Box sx={{ marginBottom: 2, maxHeight: 400, overflowY: 'auto' }}>
            {chatHistory.map((entry) => (
              <Box key={entry.id} sx={{ marginBottom: 2 }}>
                <Card variant="outlined">
                  <CardContent sx={{ padding: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', marginBottom: 1 }}>
                      {entry.type === 'user' ? <PersonIcon color="primary" /> : <SmartToyIcon color="secondary" />}
                      <Typography variant="subtitle2" sx={{ marginLeft: 1 }}>
                        {entry.type === 'user' ? 'You' : 'AI Assistant'}
                      </Typography>
                      <Typography variant="caption" sx={{ marginLeft: 'auto', color: 'text.secondary' }}>
                        {entry.timestamp}
                      </Typography>
                      {entry.status === 'fallback' && (
                        <Chip label="Fallback" size="small" color="warning" sx={{ marginLeft: 1 }} />
                      )}
                    </Box>
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                      {entry.message}
                    </Typography>
                    {entry.note && (
                      <Typography variant="caption" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                        {entry.note}
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Box>
            ))}
          </Box>
        )}

        {/* Input Section */}
        <Box sx={{ display: 'flex', gap: 2, marginBottom: 2 }}>
          <TextField
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            placeholder="Ask questions about merchant performance, payment trends, trust scores, or business insights..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={isLoadingAi}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && e.ctrlKey) {
                handlePromptSubmit();
              }
            }}
          />
          <Button
            variant="contained"
            endIcon={<SendIcon />}
            onClick={handlePromptSubmit}
            disabled={!prompt.trim() || isLoadingAi}
            sx={{ minWidth: 120 }}
          >
            {isLoadingAi ? <CircularProgress size={24} /> : "Send"}
          </Button>
        </Box>
        
        <Typography variant="caption" color="text.secondary">
          💡 Tip: Press Ctrl+Enter to send your message
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ marginTop: 2 }}>
            {error}
          </Alert>
        )}
      </Paper>

      {/* Generated Chart Section */}
      {isChartResponse && generatedChart && (
        <DynamicChartRenderer 
          chartCode={generatedChart} 
          data={data} 
          isLoading={isLoadingAi}
        />
      )}

      {/* Charts Section */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', padding: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          <Paper elevation={2} sx={{ padding: 3, marginBottom: 3 }}>
            <Typography variant="h6" gutterBottom>
              Top Merchants by Collected Payments
            </Typography>
            <TopMerchantsBar rows={data.topMerchantsByPayments} />
          </Paper>
          <Paper elevation={2} sx={{ padding: 3 }}>
            <Typography variant="h6" gutterBottom>
              Portfolio Payment Status Mix
            </Typography>
            <PaymentStatusPie data={data.paymentStatusMix} />
          </Paper>
        </>
      )}
    </Box>
  );
};

export default Merchants;
