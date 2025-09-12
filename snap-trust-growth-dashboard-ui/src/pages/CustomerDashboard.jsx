import React, { useEffect, useState, useRef } from "react";
import { fetchCustomers, fetchCustomerById } from "../api/customers";
import {
  Container,
  Typography,
  Button,
  Paper,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  Box,
  Divider,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, LineChart, Line } from "recharts";

// Professional color palette
const widgetColors = [
  "#005a9e", "#228b22", "#f4b942", "#d32f2f", "#546e7a", "#008080", "#6a1b9a", "#8d6e63"
];
const pieColors = [
  "#1976d2", "#43a047", "#fbc02d", "#8d6e63", "#6a1b9a"
];
const barColor = "#1976d2";
const lineColor = "#6a1b9a";
const tableMinWidth = 900;

const RADIAN = Math.PI / 180;
const renderCustomizedLabel = ({
  cx, cy, midAngle, outerRadius, percent, index, name,
}) => {
  const radius = outerRadius + 16;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);
  return percent > 0.02 ? (
    <text
      x={x}
      y={y}
      fill="#333"
      textAnchor={x > cx ? "start" : "end"}
      dominantBaseline="central"
      fontSize={13}
      fontWeight={500}
    >
      {name}
    </text>
  ) : null;
};

function getMonthYear(dateString) {
  const d = new Date(dateString);
  return `${d.getFullYear()}-${(`0${d.getMonth() + 1}`).slice(-2)}`;
}

// New fetchAverages function for backend metrics
async function fetchAverages() {
  const resp = await fetch("http://127.0.0.1:8000/customers/metrics/averages");
  if (!resp.ok) throw new Error("Failed to fetch averages");
  return await resp.json();
}

export default function CustomerDashboard() {
  const [customers, setCustomers] = useState([]);
  const [loadingCustomers, setLoadingCustomers] = useState(true);
  const [selectedCustomerId, setSelectedCustomerId] = useState(null);
  const [customerDetail, setCustomerDetail] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [open, setOpen] = useState(false);

  // For backend averages
  const [averages, setAverages] = useState({ AverageRepaymentRate: null, AverageDefaultRate: null });

  // For scrolling to table row
  const rowRefs = useRef({});

  useEffect(() => {
    setLoadingCustomers(true);
    fetchCustomers(50)
      .then(setCustomers)
      .finally(() => setLoadingCustomers(false));

    // Fetch averages from backend
    fetchAverages()
      .then(setAverages)
      .catch(() => setAverages({ AverageRepaymentRate: null, AverageDefaultRate: null }));
  }, []);

  // Metrics
  const metrics = React.useMemo(() => {
    if (!customers.length) return {};

    const activeCustomers = customers.filter(
      c => c.IsActive === true || c.status === "active"
    ).length;

    const avgTrust = (
      customers.reduce((a, c) => a + (Number(c.TrustScore) || 0), 0) / customers.length
    ).toFixed(2);

    const platinumCount = customers.filter(c => c.LoyaltyTier === "Platinum").length;

    const growthMap = {};
    customers.forEach(c => {
      const month = getMonthYear(c.createdAt || c.CreatedDate || new Date());
      growthMap[month] = (growthMap[month] || 0) + 1;
    });
    const customerGrowthData = Object.keys(growthMap)
      .sort()
      .map(month => ({
        month,
        newCustomers: growthMap[month],
      }));

    const currentMonth = getMonthYear(new Date());
    const newCustomersThisMonth = growthMap[currentMonth] || 0;

    return {
      totalCustomers: customers.length,
      avgTrustScore: avgTrust,
      platinumCount,
      avgRepaymentRate: averages.AverageRepaymentRate !== null ? (averages.AverageRepaymentRate * 100).toFixed(2) : "—",
      defaultRate: averages.AverageDefaultRate !== null ? (averages.AverageDefaultRate * 100).toFixed(2) : "—",
      activeCustomers: customers.length,
      newCustomersThisMonth,
      topCustomer: customers[0]?.CustomerName || "-",
      customerGrowthData,
    };
  }, [customers, averages]);

  const loyaltyData = React.useMemo(() => {
    const tierCounts = customers.reduce((acc, curr) => {
      acc[curr.LoyaltyTier] = (acc[curr.LoyaltyTier] || 0) + 1;
      return acc;
    }, {});
    return Object.entries(tierCounts).map(([name, value]) => ({ name, value }));
  }, [customers]);

  const trustBarData = customers.map(c => ({
    name: c.CustomerName,
    TrustScore: Number(c.TrustScore),
    CustomerID: c.CustomerID,
  }));

  const scrollToCustomerRow = (customerID) => {
    const ref = rowRefs.current[customerID];
    if (ref && ref.scrollIntoView) {
      ref.scrollIntoView({ behavior: "smooth", block: "center" });
    }
    setSelectedCustomerId(customerID);
  };

  const handleViewDetails = (customerId) => {
    setSelectedCustomerId(customerId);
    setCustomerDetail(null);
    setLoadingDetail(true);
    setOpen(true);
    fetchCustomerById(customerId)
      .then(setCustomerDetail)
      .finally(() => setLoadingDetail(false));
  };

  const handleClose = () => {
    if (loadingDetail) return;
    setOpen(false);
    setSelectedCustomerId(null);
    setCustomerDetail(null);
  };

  function renderContentField(field) {
    if (typeof field === "string") {
      return field;
    }
    if (Array.isArray(field)) {
      return field.map((item, idx) =>
        typeof item === "string"
          ? <div key={idx}>{item}</div>
          : (
            <div key={idx} style={{ marginBottom: "8px" }}>
              {item.title && <strong>{item.title}</strong>}
              {item.description && <div>{item.description}</div>}
            </div>
          )
      );
    }
    if (typeof field === "object" && field !== null) {
      return (
        <div>
          {field.title && <strong>{field.title}</strong>}
          {field.description && <div>{field.description}</div>}
        </div>
      );
    }
    return null;
  }

  return (
    <Container
      maxWidth="xl"
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "stretch",
        px: 0,
        width: "100vw",
        minWidth: 0
      }}
    >
      <Typography variant="h4" sx={{ mt: 2, mb: 2, color: "#005a9e", fontWeight: 700, textAlign: "center" }}>
        Customer Dashboard
      </Typography>
      
      {/* Metrics in Single Row, fitted */}
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: "repeat(8, 1fr)",
          gap: 1,
          mb: 2,
          width: "100%",
          minWidth: 0,
        }}
      >
        {[
          { label: "Total Customers", value: metrics.totalCustomers, color: widgetColors[0] },
          { label: "Avg Trust Score", value: metrics.avgTrustScore, color: widgetColors[1] },
          { label: "Platinum Customers", value: metrics.platinumCount, color: widgetColors[2], textColor: "#333" },
          { label: "Top Customer", value: metrics.topCustomer, color: widgetColors[3] },
          { label: "Avg Repayment Rate", value: metrics.avgRepaymentRate !== "—" ? `${metrics.avgRepaymentRate}%` : "—", color: widgetColors[4] },
          { label: "Default Rate", value: metrics.defaultRate !== "—" ? `${metrics.defaultRate}%` : "—", color: widgetColors[5] },
          { label: "Active Customers", value: metrics.activeCustomers, color: widgetColors[6] },
          { label: "New This Month", value: metrics.newCustomersThisMonth, color: widgetColors[7] }
        ].map((metric, idx) => (
          <Paper
            key={metric.label}
            sx={{
              p: 1.2,
              textAlign: "center",
              background: metric.color,
              color: metric.textColor || "#fff",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              minWidth: 0,
              boxShadow: 1,
              borderRadius: 2,
              width: "100%",
            }}
          >
            <Typography variant="subtitle2" sx={{ fontWeight: 500, fontSize: 14 }}>{metric.label}</Typography>
            <Typography variant="h6" sx={{ fontWeight: 700, fontSize: 20 }}>{metric.value}</Typography>
          </Paper>
        ))}
      </Box>

      {/* Visuals in Single Row, fitted */}
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: 1,
          mb: 2,
          width: "100%",
          minWidth: 0,
        }}
      >
        <Paper sx={{ p: 1.2, background: "#f6f8fa", width: "100%", boxShadow: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minWidth: 0, borderRadius: 2 }}>
          <Typography variant="h6" sx={{ mb: 1, color: "#005a9e", fontWeight: 700, textAlign: "center", fontSize: 18 }}>Loyalty Tier Distribution</Typography>
          <ResponsiveContainer width="100%" height={160}>
            <PieChart>
              <Pie
                data={loyaltyData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={55}
                labelLine={false}
                label={renderCustomizedLabel}
              >
                {loyaltyData.map((entry, idx) => (
                  <Cell key={`cell-${idx}`} fill={pieColors[idx % pieColors.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend verticalAlign="bottom" iconType="circle" />
            </PieChart>
          </ResponsiveContainer>
        </Paper>
        <Paper sx={{ p: 1.2, background: "#f6f8fa", width: "100%", boxShadow: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minWidth: 0, borderRadius: 2 }}>
          <Typography variant="h6" sx={{ mb: 1, color: "#1976d2", fontWeight: 700, textAlign: "center", fontSize: 18 }}>Customer Trust Scores</Typography>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart
              data={trustBarData}
              onClick={e => {
                if (e && e.activePayload && e.activePayload[0]) {
                  const { CustomerID } = e.activePayload[0].payload;
                  scrollToCustomerRow(CustomerID);
                }
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" hide />
              <YAxis />
              <Tooltip />
              <Bar
                dataKey="TrustScore"
                fill={barColor}
                radius={[4, 4, 0, 0]}
                onClick={(data, index) => {
                  const { CustomerID } = trustBarData[index];
                  scrollToCustomerRow(CustomerID);
                }}
                cursor="pointer"
              />
            </BarChart>
          </ResponsiveContainer>
          <Typography variant="caption" sx={{ mt: 1, color: "#999" }}>
            Click a bar to jump to customer's record below
          </Typography>
        </Paper>
        <Paper sx={{ p: 1.2, background: "#f6f8fa", width: "100%", boxShadow: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minWidth: 0, borderRadius: 2 }}>
          <Typography variant="h6" sx={{ mb: 1, color: "#6a1b9a", fontWeight: 700, textAlign: "center", fontSize: 18 }}>Customer Growth Over Time</Typography>
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={metrics.customerGrowthData || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="newCustomers" stroke={lineColor} strokeWidth={3} dot={{ r: 5 }} />
            </LineChart>
          </ResponsiveContainer>
        </Paper>
      </Box>

      {/* Customer List with Details Button, fitted */}
      <Paper elevation={3} sx={{ mb: 2, boxShadow: 2, width: "100%", minWidth: 0 }}>
        {loadingCustomers ? (
          <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", height: 120 }}>
            <CircularProgress color="primary" />
          </Box>
        ) : (
          <Table sx={{ minWidth: 900, width: "100%" }}>
            <TableHead>
              <TableRow sx={{ background: "#e3e8ee" }}>
                <TableCell align="center" sx={{ color: "#005a9e", fontWeight: 700, fontSize: 16, borderRight: '1px solid #dde2e6', minWidth: 0 }}>Customer ID</TableCell>
                <TableCell align="left" sx={{ color: "#005a9e", fontWeight: 700, fontSize: 16, borderRight: '1px solid #dde2e6', minWidth: 0 }}>Name</TableCell>
                <TableCell align="center" sx={{ color: "#005a9e", fontWeight: 700, fontSize: 16, borderRight: '1px solid #dde2e6', minWidth: 0 }}>Trust Score</TableCell>
                <TableCell align="center" sx={{ color: "#005a9e", fontWeight: 700, fontSize: 16, borderRight: '1px solid #dde2e6', minWidth: 0 }}>Loyalty Tier</TableCell>
                <TableCell align="center" sx={{ color: "#005a9e", fontWeight: 700, fontSize: 16, minWidth: 0 }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {customers.map((row, idx) => (
                <TableRow
                  key={row.CustomerID}
                  ref={el => rowRefs.current[row.CustomerID] = el}
                  sx={{
                    background: idx % 2 === 0 ? "#f8fafc" : "#f4f6f8",
                    '&:hover': { background: "#e3e8ee" },
                    border: selectedCustomerId === row.CustomerID ? "2px solid #1976d2" : undefined,
                    transition: "border 0.2s"
                  }}
                >
                  <TableCell align="center" sx={{ fontWeight: 500, minWidth: 0 }}>{row.CustomerID}</TableCell>
                  <TableCell align="left" sx={{ fontWeight: 500, minWidth: 0 }}>{row.CustomerName}</TableCell>
                  <TableCell align="center" sx={{ fontWeight: 500, minWidth: 0 }}>{row.TrustScore}</TableCell>
                  <TableCell align="center" sx={{ fontWeight: 500, minWidth: 0 }}>{row.LoyaltyTier}</TableCell>
                  <TableCell align="center" sx={{ minWidth: 0 }}>
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => handleViewDetails(row.CustomerID)}
                      sx={{
                        borderColor: "#005a9e",
                        color: "#005a9e",
                        fontWeight: 600,
                        fontSize: 14,
                        textTransform: "none",
                        '&:hover': { background: "#e3e8ee", borderColor: "#005a9e" }
                      }}
                    >
                      View Details
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Paper>

      {/* Modal for Customer Details */}
      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            background: "#005a9e",
            color: "#fff",
            fontWeight: 700
          }}
        >
          Customer Details
          <IconButton
            aria-label="close"
            onClick={handleClose}
            disabled={loadingDetail}
            sx={{ ml: 2, color: "#fff" }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers>
          {loadingDetail ? (
            <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", height: 120 }}>
              <CircularProgress color="primary" />
              <Typography sx={{ ml: 2 }}>Loading details...</Typography>
            </Box>
          ) : customerDetail ? (
            <Box
              sx={{
                px: 3,
                py: 2,
                bgcolor: "#f3f6fb",
                borderRadius: 3,
                boxShadow: 3,
                border: "2px solid #1976d2",
                mb: 2,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                minWidth: 0,
              }}
            >
              <Typography
                variant="h5"
                sx={{
                  color: "#1976d2",
                  fontWeight: 800,
                  mb: 1,
                  letterSpacing: 1,
                  textTransform: "uppercase"
                }}
              >
                Customer AI Insights
              </Typography>
              <Divider sx={{ width: "70%", mb: 2 }} />
              <Box sx={{ width: "100%", textAlign: "left", mb: 2 }}>
                <Typography
                  variant="subtitle2"
                  sx={{
                    color: "#388e3c",
                    fontWeight: 700,
                    mb: 1,
                    fontSize: 16,
                  }}
                >
                  Summary
                </Typography>
                <Typography
                  sx={{
                    color: "#333",
                    fontWeight: 500,
                    fontSize: 16,
                    lineHeight: 1.7,
                    bgcolor: "#e8f5e9",
                    p: 2,
                    borderRadius: 2,
                  }}
                >
                  {renderContentField(customerDetail.Summary)}
                </Typography>
              </Box>
              <Box
                sx={{
                  bgcolor: "#fffde7",
                  p: 2,
                  borderRadius: 2,
                  width: "100%",
                  boxShadow: 2,
                  border: "1px solid #fbc02d",
                  textAlign: "left"
                }}
              >
                <Typography
                  variant="subtitle2"
                  sx={{
                    color: "#fbc02d",
                    fontWeight: 700,
                    mb: 1,
                    fontSize: 16,
                  }}
                >
                  Recommendations
                </Typography>
                <Typography
                  sx={{
                    color: "#333",
                    fontWeight: 500,
                    fontSize: 16,
                    lineHeight: 1.7
                  }}
                >
                  {renderContentField(customerDetail.Recommendations)}
                </Typography>
              </Box>
            </Box>
          ) : (
            <Typography>No details available.</Typography>
          )}
        </DialogContent>
      </Dialog>
    </Container>
  );
}