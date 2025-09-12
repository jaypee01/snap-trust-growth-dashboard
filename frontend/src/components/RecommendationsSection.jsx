import {
  Paper,
  Typography,
  Box,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import { Lightbulb, CheckCircle } from "@mui/icons-material";

const RecommendationsSection = ({
  recommendations,
  entityId,
  entityType = "Customer",
}) => {
  return (
    <Paper elevation={3} sx={{ p: 3, mt: 3, borderRadius: 2 }}>
      <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
        <Lightbulb sx={{ color: "#FF9800", mr: 1 }} />
        <Typography variant="h6" sx={{ fontWeight: "bold" }}>
          AI Recommendations
        </Typography>
      </Box>
      <Divider sx={{ mb: 2 }} />

      {recommendations &&
      Array.isArray(recommendations) &&
      recommendations.length > 0 ? (
        <>
          {/* Introductory paragraph */}
          <Typography
            variant="body1"
            sx={{ mb: 3, lineHeight: 1.6, fontStyle: "italic" }}
          >
            Based on the provided {entityType.toLowerCase()} profile for{" "}
            {entityType} {entityId}, here are some actionable recommendations to
            improve trust, loyalty, and financial engagement:
          </Typography>

          <List sx={{ width: "100%", bgcolor: "background.paper" }}>
            {recommendations.map((recommendation, index) => (
              <ListItem key={index} alignItems="flex-start" sx={{ py: 1 }}>
                <ListItemIcon sx={{ minWidth: 32, mt: 0.5 }}>
                  <CheckCircle sx={{ color: "#4CAF50", fontSize: "1.2rem" }} />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography
                      variant="body1"
                      sx={{
                        lineHeight: 1.6,
                        fontWeight: "bold",
                        color: "#1976d2",
                        mb: 0.5,
                      }}
                    >
                      {recommendation.title}
                    </Typography>
                  }
                  secondary={
                    <Typography
                      variant="body2"
                      sx={{
                        lineHeight: 1.5,
                        color: "text.primary",
                      }}
                    >
                      {recommendation.description}
                    </Typography>
                  }
                />
              </ListItem>
            ))}
          </List>
        </>
      ) : (
        <Typography variant="body2" color="text.secondary">
          No recommendations available at this time.
        </Typography>
      )}
    </Paper>
  );
};

export default RecommendationsSection;
