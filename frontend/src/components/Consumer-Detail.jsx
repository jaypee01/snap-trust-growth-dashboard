import { useState, useEffect } from "react";
import {
  Container,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Box,
  Chip,
  CircularProgress,
  Alert,
  Avatar,
  LinearProgress,
  Divider,
  IconButton,
} from "@mui/material";
import {
  Person,
  TrendingUp,
  Warning,
  AccountBalance,
  Star,
  ArrowBack,
} from "@mui/icons-material";
import { useNavigate, useParams } from "react-router";
import { getScoreColor, getTierColor } from "../utils";
import RecommendationsSection from "./RecommendationsSection";

const ConsumerDetail = () => {
  const [consumerData, setConsumerData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const params = useParams();

  // Get customerId from URL params
  const customerId = params.customerId;

  // API call to fetch consumer data
  useEffect(() => {
    const fetchConsumerData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Make API request to the specified endpoint
        const response = await fetch(
          `http://127.0.0.1:8000/customers/${customerId}`
        );

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        setConsumerData(data);
      } catch (err) {
        setError(`Failed to fetch consumer data: ${err.message}`);
        console.error("Error fetching consumer data:", err);
      } finally {
        setLoading(false);
      }
    };

    if (customerId) {
      fetchConsumerData();
    }
  }, [customerId]);

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="400px"
        >
          <CircularProgress size={60} />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: "flex", alignItems: "center", gap: 2 }}>
        <IconButton
          onClick={() => navigate("/consumers")}
          sx={{ color: "#1976d2" }}
        >
          <ArrowBack />
        </IconButton>
        <Typography
          variant="h4"
          component="h1"
          sx={{ fontWeight: "bold", color: "#1976d2" }}
        >
          Consumer Profile
        </Typography>
      </Box>

      {/* Main Profile Card */}
      <Paper elevation={3} sx={{ p: 3, mb: 3, borderRadius: 2 }}>
        <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
          <Avatar
            sx={{
              bgcolor: "#1976d2",
              width: 80,
              height: 80,
              fontSize: "2rem",
              mr: 3,
            }}
          >
            <Person sx={{ fontSize: "3rem" }} />
          </Avatar>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h5" sx={{ fontWeight: "bold", mb: 1 }}>
              {consumerData.CustomerName}
            </Typography>
            <Typography
              variant="subtitle1"
              color="text.secondary"
              sx={{ mb: 1 }}
            >
              ID: {consumerData.CustomerID}
            </Typography>
            <Chip
              label={consumerData.LoyaltyTier}
              sx={{
                backgroundColor: getTierColor(consumerData.LoyaltyTier),
                color: "#000",
                fontWeight: "bold",
                fontSize: "0.875rem",
              }}
            />
          </Box>
          <Box sx={{ textAlign: "center" }}>
            <Typography
              variant="h3"
              sx={{
                color: getScoreColor(consumerData.TrustScore),
                fontWeight: "bold",
              }}
            >
              {consumerData.TrustScore}
            </Typography>
            <Typography variant="subtitle2" color="text.secondary">
              Trust Score
            </Typography>
          </Box>
        </Box>
      </Paper>

      {/* Stats Grid */}
      <Grid container spacing={3}>
        {/* Repayment Rate */}
        <Grid item xs={12} md={6}>
          <Card elevation={2} sx={{ height: "100%", borderRadius: 2 }}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <TrendingUp sx={{ color: "#4CAF50", mr: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                  Repayment Rate
                </Typography>
              </Box>
              <Typography
                variant="h4"
                sx={{ color: "#4CAF50", fontWeight: "bold", mb: 1 }}
              >
                {(consumerData.RepaymentRate * 100).toFixed(1)}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={consumerData.RepaymentRate * 100}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: "#E8F5E8",
                  "& .MuiLinearProgress-bar": {
                    backgroundColor: "#4CAF50",
                  },
                }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Default Rate */}
        <Grid item xs={12} md={6}>
          <Card elevation={2} sx={{ height: "100%", borderRadius: 2 }}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <Warning sx={{ color: "#FF5722", mr: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                  Default Rate
                </Typography>
              </Box>
              <Typography
                variant="h4"
                sx={{ color: "#FF5722", fontWeight: "bold", mb: 1 }}
              >
                {(consumerData.DefaultRate * 100).toFixed(1)}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={consumerData.DefaultRate * 100}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: "#FFF3E0",
                  "& .MuiLinearProgress-bar": {
                    backgroundColor: "#FF5722",
                  },
                }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Transaction Volume */}
        <Grid item xs={12} md={6}>
          <Card elevation={2} sx={{ height: "100%", borderRadius: 2 }}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <AccountBalance sx={{ color: "#1976d2", mr: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                  Transaction Volume
                </Typography>
              </Box>
              <Typography
                variant="h4"
                sx={{ color: "#1976d2", fontWeight: "bold" }}
              >
                {consumerData.TransactionVolume}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Transactions
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Dispute Count */}
        <Grid item xs={12} md={6}>
          <Card elevation={2} sx={{ height: "100%", borderRadius: 2 }}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <Star sx={{ color: "#FF9800", mr: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                  Dispute Count
                </Typography>
              </Box>
              <Typography
                variant="h4"
                sx={{
                  color:
                    consumerData.DisputeCount === 0 ? "#4CAF50" : "#FF9800",
                  fontWeight: "bold",
                }}
              >
                {consumerData.DisputeCount}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Active Disputes
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Summary Section */}
      <Paper elevation={3} sx={{ p: 3, mt: 3, borderRadius: 2 }}>
        <Typography variant="h6" sx={{ fontWeight: "bold", mb: 2 }}>
          Summary
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <Typography variant="body1" sx={{ lineHeight: 1.6 }}>
          {consumerData.Summary}
        </Typography>
      </Paper>

      {/* Recommendations Section */}
      <RecommendationsSection
        recommendations={consumerData.Recommendations}
        entityId={consumerData.CustomerID}
        entityType="Customer"
      />
    </Container>
  );
};

export default ConsumerDetail;
