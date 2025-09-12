import { useState } from "react";
import { TextareaAutosize, Button, Box, CircularProgress } from "@mui/material";

const QueryTextarea = ({
  placeholder = "Add your query here...",
  minRows = 4,
  width = "500px",
  type = "merchants", // "merchants" or "consumers"
  onQueryResult,
  ...props
}) => {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const endpoint = "http://127.0.0.1:8000/ai-query/";

      // Append the instruction to maintain data structure
      const enhancedQuery =
        query.trim() +
        " and please maintain the input data structure in " +
        type;

      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: enhancedQuery }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (onQueryResult) {
        // Check if result.result exists and is an array
        if (result.result && Array.isArray(result.result)) {
          onQueryResult(result.result);
        } else {
          alert(result.result.message || "Server has encountered an error.");
        }
      }
    } catch (error) {
      console.error("Error submitting query:", error);
      if (onQueryResult) {
        onQueryResult({ error: "Failed to process query. Please try again." });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
      <TextareaAutosize
        minRows={minRows}
        placeholder={placeholder}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyPress}
        style={{
          width: width,
          padding: "12px 16px",
          border: "2px solid #e0e0e0",
          borderRadius: "12px",
          fontFamily: "inherit",
          fontSize: "14px",
          lineHeight: "1.5",
          resize: "none",
          outline: "none",
          transition: "border-color 0.2s ease",
          boxShadow: "0 2px 4px rgba(0,0,0,0.05)",
        }}
        onFocus={(e) => {
          e.target.style.borderColor = "#1976d2";
          e.target.style.backgroundColor = "#ffffff";
        }}
        onBlur={(e) => {
          e.target.style.borderColor = "#e0e0e0";
          e.target.style.backgroundColor = "#fafafa";
        }}
        {...props}
      />
      <Button
        variant="contained"
        onClick={handleSubmit}
        disabled={!query.trim() || loading}
        sx={{
          alignSelf: "flex-end",
          minWidth: "120px",
        }}
      >
        {loading ? (
          <CircularProgress size={20} color="inherit" />
        ) : (
          "Submit Query"
        )}
      </Button>
    </Box>
  );
};

export default QueryTextarea;
