import React, { useEffect, useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Box,
  Chip,
  CircularProgress,
  Alert,
  TablePagination,
} from "@mui/material";
import { useNavigate } from "react-router";
import QueryTextarea from "./QueryTextarea";

const ConsumersListing = () => {
  const [consumers, setConsumers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  const [isQueryMode, setIsQueryMode] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchConsumers = async () => {
      try {
        setLoading(true);
        setError(null);

        // Note: The backend route is /customers but we need to use the leaderboard endpoint
        // which is likely at /leaderboard/customers based on the file structure
        const response = await fetch(
          `http://localhost:8000/customers?limit=${rowsPerPage}&offset=${
            page * rowsPerPage
          }`
        );

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        setConsumers(data);
        setTotalCount(data.length); // Note: This is a simplified approach, ideally the API should return total count
      } catch (err) {
        console.error("Error fetching consumers:", err);
        setError("Failed to load consumers. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchConsumers();
  }, [page, rowsPerPage]);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleRowClick = (customerId) => {
    navigate(`/consumers/${customerId}`);
  };

  const handleQueryResult = (result) => {
    if (result.error) {
      // setError(result.error);
      // setIsQueryMode(false);
    } else {
      setConsumers(result); // Set consumers to only contain the query result
      setTotalCount(1);
      setIsQueryMode(true);
      setError(null);
    }
  };

  const getLoyaltyTierColor = (tier) => {
    switch (tier?.toLowerCase()) {
      case "gold":
        return "warning";
      case "silver":
        return "default";
      case "bronze":
        return "secondary";
      default:
        return "default";
    }
  };

  const formatTrustScore = (score) => {
    return typeof score === "number" ? score.toFixed(2) : "N/A";
  };

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="400px"
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box sx={{ display: "flex", alignItems: "flex-start", gap: 3, mb: 3 }}>
        <Box sx={{ flex: 1 }}>
          <Typography variant="h4" gutterBottom>
            Consumers
          </Typography>
          <Typography variant="body1" color="text.secondary">
            View and manage all consumers in the system
          </Typography>
        </Box>
        <QueryTextarea type="consumers" onQueryResult={handleQueryResult} />
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Customer ID</TableCell>
              <TableCell>Customer Name</TableCell>
              <TableCell align="right">Trust Score</TableCell>
              <TableCell align="center">Loyalty Tier</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {consumers.map((consumer) => (
              <TableRow
                key={consumer.CustomerID}
                hover
                onClick={() => handleRowClick(consumer.CustomerID)}
                sx={{
                  cursor: "pointer",
                  "&:hover": {
                    backgroundColor: "action.hover",
                  },
                }}
              >
                <TableCell>{consumer.CustomerID}</TableCell>
                <TableCell>
                  <Typography variant="body2" fontWeight="medium">
                    {consumer.CustomerName}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body2" fontWeight="medium">
                    {formatTrustScore(consumer.TrustScore)}
                  </Typography>
                </TableCell>
                <TableCell align="center">
                  <Chip
                    label={consumer.LoyaltyTier || "N/A"}
                    color={getLoyaltyTierColor(consumer.LoyaltyTier)}
                    size="small"
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {!isQueryMode && (
        <TablePagination
          component="div"
          count={totalCount}
          page={page}
          onPageChange={handleChangePage}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          rowsPerPageOptions={[5, 10, 25, 50]}
        />
      )}
    </Box>
  );
};

export default ConsumersListing;
