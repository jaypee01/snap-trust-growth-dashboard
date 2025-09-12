import { useEffect, useState } from "react";
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

const MerchantsListing = () => {
  const [merchants, setMerchants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  const [isQueryMode, setIsQueryMode] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchMerchants = async () => {
      try {
        setLoading(true);
        setError(null);

        // Note: The backend route is /merchants but we need to use the leaderboard endpoint
        // which is likely at /leaderboard/merchants based on the file structure
        const response = await fetch(
          `http://localhost:8000/merchants?limit=${rowsPerPage}&offset=${
            page * rowsPerPage
          }`
        );

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        setMerchants(data);
        setTotalCount(data.length); // Note: This is a simplified approach, ideally the API should return total count
      } catch (err) {
        console.error("Error fetching merchants:", err);
        setError("Failed to load merchants. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchMerchants();
  }, [page, rowsPerPage]);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
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

  const handleRowClick = (merchantId) => {
    navigate(`/merchants/${merchantId}`);
  };

  const handleQueryResult = (result) => {
    if (result.error) {
      // setError(result.error);
      // setIsQueryMode(false);
    } else {
      setMerchants(result); // Set merchants to only contain the query result
      setTotalCount(1);
      setIsQueryMode(true);
      setError(null);
    }
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
            Merchants
          </Typography>
          <Typography variant="body1" color="text.secondary">
            View and manage all merchants in the system
          </Typography>
        </Box>
        <QueryTextarea type="merchants" onQueryResult={handleQueryResult} />
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Merchant ID</TableCell>
              <TableCell>Merchant Name</TableCell>
              <TableCell align="center">Exclusive Partner</TableCell>
              <TableCell align="right">Trust Score</TableCell>
              <TableCell align="center">Loyalty Tier</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {merchants.map((merchant) => (
              <TableRow
                key={merchant.MerchantID}
                hover
                onClick={() => handleRowClick(merchant.MerchantID)}
                sx={{
                  cursor: "pointer",
                  "&:hover": {
                    backgroundColor: "action.hover",
                  },
                }}
              >
                <TableCell>{merchant.MerchantID}</TableCell>
                <TableCell>
                  <Typography variant="body2" fontWeight="medium">
                    {merchant.MerchantName}
                  </Typography>
                </TableCell>
                <TableCell align="center">
                  <Chip
                    label={merchant.ExclusivityFlag ? "Yes" : "No"}
                    color={merchant.ExclusivityFlag ? "primary" : "default"}
                    size="small"
                  />
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body2" fontWeight="medium">
                    {formatTrustScore(merchant.TrustScore)}
                  </Typography>
                </TableCell>
                <TableCell align="center">
                  <Chip
                    label={merchant.LoyaltyTier || "N/A"}
                    color={getLoyaltyTierColor(merchant.LoyaltyTier)}
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

export default MerchantsListing;
