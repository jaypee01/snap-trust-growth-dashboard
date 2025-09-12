import React from "react";
import { Paper, Typography, List, ListItem, ListItemText } from "@mui/material";

export default function AIInsightsPanel({ summary, recommendations }) {
  return (
    <Paper style={{ padding: 16, marginTop: 16 }}>
      <Typography variant="h6">AI Insights</Typography>
      <Typography variant="body1" style={{ marginBottom: 8 }}>{summary}</Typography>
      <Typography variant="subtitle1">Recommendations:</Typography>
      <List>
        {recommendations.map((rec, idx) => (
          <ListItem key={idx}>
            <ListItemText primary={rec.title} secondary={rec.description} />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
}