import React, { useState } from "react";
import { postAIQuery } from "../api/aiQuery";
import { Container, Typography, TextField, Button, CircularProgress } from "@mui/material";

export default function AIQueryDashboard() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleQuery = async () => {
    if (!query) return;
    setLoading(true);
    try {
      const res = await postAIQuery(query);
      setResult(res);
    } catch (err) {
      console.error(err);
      setResult({ error: "Failed to fetch AI response" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Typography variant="h4" sx={{ my: 2 }}>
        AI Analytics / Query
      </Typography>
      <TextField
        label="Ask AI anything about merchants/customers..."
        fullWidth
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        sx={{ mb: 2 }}
      />
      <Button
        variant="contained"
        onClick={handleQuery}
        disabled={loading || !query}
        sx={{ minWidth: 120, position: "relative" }}
      >
        {loading ? (
          <CircularProgress size={24} sx={{ color: "#fff" }} />
        ) : (
          "Submit Query"
        )}
      </Button>
      {result && (
        <pre
          style={{
            marginTop: 24,
            background: "#f7f7f7",
            padding: 16,
            borderRadius: 4,
          }}
        >
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </Container>
  );
}
