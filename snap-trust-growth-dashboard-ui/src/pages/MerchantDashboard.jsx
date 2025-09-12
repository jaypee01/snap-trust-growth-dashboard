import React, { useEffect, useState, useRef } from "react";
import {
  fetchMerchants,
  fetchMerchantById,
  fetchMerchantAverages,
} from "../api/merchants";
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
import {
  PieChart,
  Pie,
  Cell,
  Legend,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LineChart,
  Line,
} from "recharts";

// Professional color palette
const widgetColors = [
  "#005a9e",
  "#228b22",
  "#f4b942",
  "#d32f2f",
  "#546e7a",
  "#008080",
  "#6a1b9a",
  "#8d6e63",
];
const pieColors = ["#1976d2", "#43a047", "#fbc02d", "#8d6e63", "#6a1b9a"];
const barColor = "#1976d2";
const lineColor = "#6a1b9a";
const RADIAN = Math.PI / 180;

const renderCustomizedLabel = ({
  cx,
  cy,
  midAngle,
  outerRadius,
  percent,
  index,
  name,
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

export default function MerchantDashboard() {
  const [merchants, setMerchants] = useState([]);
  const [loadingMerchants, setLoadingMerchants] = useState(true);
  const [selectedMerchantId, setSelectedMerchantId] = useState(null);
  const [merchantDetail, setMerchantDetail] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [open, setOpen] = useState(false);

  const [averages, setAverages] = useState({});
  const rowRefs = useRef({});

  useEffect(() => {
    setLoadingMerchants(true);
    fetchMerchants(50)
      .then(setMerchants)
      .finally(() => setLoadingMerchants(false));

    fetchMerchantAverages()
      .then(setAverages)
      .catch(() => setAverages({}));
  }, []);

  // Metrics aggregation
  const metrics = React.useMemo(() => {
    if (!merchants.length) return {};

    const topMerchant = merchants[0]?.MerchantName || "-";

    const growthMap = {};
    merchants.forEach((m) => {
      const tenure = m.TenureMonths || 0;
      growthMap[tenure] = (growthMap[tenure] || 0) + 1;
    });
    const merchantGrowthData = Object.keys(growthMap)
      .sort((a, b) => Number(a) - Number(b))
      .map((month) => ({
        month: `${month} mo`,
        newMerchants: growthMap[month],
      }));

    return {
      totalMerchants: merchants.length,
      avgTrustScore:
        averages.AverageTrustScore !== undefined
          ? averages.AverageTrustScore.toFixed(2)
          : "—",
      avgRepaymentRate:
        averages.AverageRepaymentRate !== undefined
          ? (averages.AverageRepaymentRate * 100).toFixed(2)
          : "—",
      avgDisputeRate:
        averages.AverageDisputeRate !== undefined
          ? (averages.AverageDisputeRate * 100).toFixed(2)
          : "—",
      avgDefaultRate:
        averages.AverageDefaultRate !== undefined
          ? (averages.AverageDefaultRate * 100).toFixed(2)
          : "—",
      avgComplianceScore:
        averages.AverageComplianceScore !== undefined
          ? (averages.AverageComplianceScore * 100).toFixed(2)
          : "—",
      avgEngagementScore:
        averages.AverageEngagementScore !== undefined
          ? (averages.AverageEngagementScore * 100).toFixed(2)
          : "—",
      avgResponsivenessScore:
        averages.AverageResponsivenessScore !== undefined
          ? (averages.AverageResponsivenessScore * 100).toFixed(2)
          : "—",
      avgTransactionVolume:
        averages.AverageTransactionVolume !== undefined
          ? averages.AverageTransactionVolume.toFixed(2)
          : "—",
      topMerchant,
      merchantGrowthData,
    };
  }, [merchants, averages]);

  // Pie chart data (ExclusivityFlag distribution)
  const exclusivityData = React.useMemo(() => {
    const counts = merchants.reduce(
      (acc, m) => {
        const key = m.ExclusivityFlag ? "Exclusive" : "Non-Exclusive";
        acc[key] = (acc[key] || 0) + 1;
        return acc;
      },
      {}
    );
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [merchants]);

  const trustBarData = merchants.map((m) => ({
    name: m.MerchantName,
    TrustScore: Number(m.TrustScore),
    MerchantID: m.MerchantID,
  }));

  const scrollToMerchantRow = (merchantID) => {
    const ref = rowRefs.current[merchantID];
    if (ref && ref.scrollIntoView) {
      ref.scrollIntoView({ behavior: "smooth", block: "center" });
    }
    setSelectedMerchantId(merchantID);
  };

  const handleViewDetails = (merchantId) => {
    setSelectedMerchantId(merchantId);
    setMerchantDetail(null);
    setLoadingDetail(true);
    setOpen(true);
    fetchMerchantById(merchantId)
      .then(setMerchantDetail)
      .finally(() => setLoadingDetail(false));
  };

  const handleClose = () => {
    if (loadingDetail) return;
    setOpen(false);
    setSelectedMerchantId(null);
    setMerchantDetail(null);
  };

  function renderContentField(field) {
    if (typeof field === "string") {
      return field;
    }
    if (Array.isArray(field)) {
      return field.map((item, idx) =>
        typeof item === "string" ? (
          <div key={idx}>{item}</div>
        ) : (
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
      }}
    >
      <Typography
        variant="h4"
        sx={{
          mt: 2,
          mb: 2,
          color: "#005a9e",
          fontWeight: 700,
          textAlign: "center",
        }}
      >
        Merchant Dashboard
      </Typography>

      {/* KPIs Row */}
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: "repeat(8, 1fr)",
          gap: 1,
          mb: 2,
          width: "100%",
        }}
      >
        {[
          {
            label: "Total Merchants",
            value: metrics.totalMerchants,
            color: widgetColors[0],
          },
          {
            label: "Avg Trust Score",
            value: metrics.avgTrustScore,
            color: widgetColors[1],
          },
          {
            label: "Avg Repayment Rate",
            value: `${metrics.avgRepaymentRate}%`,
            color: widgetColors[2],
          },
          {
            label: "Avg Default Rate",
            value: `${metrics.avgDefaultRate}%`,
            color: widgetColors[3],
          },
          {
            label: "Avg Dispute Rate",
            value: `${metrics.avgDisputeRate}%`,
            color: widgetColors[4],
          },
          {
            label: "Avg Compliance",
            value: `${metrics.avgComplianceScore}%`,
            color: widgetColors[5],
          },
          {
            label: "Avg Responsiveness",
            value: `${metrics.avgResponsivenessScore}%`,
            color: widgetColors[6],
          },
          {
            label: "Top Merchant",
            value: metrics.topMerchant,
            color: widgetColors[7],
          },
        ].map((metric) => (
          <Paper
            key={metric.label}
            sx={{
              p: 1.2,
              textAlign: "center",
              background: metric.color,
              color: "#fff",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              borderRadius: 2,
              boxShadow: 1,
            }}
          >
            <Typography
              variant="subtitle2"
              sx={{ fontWeight: 500, fontSize: 14 }}
            >
              {metric.label}
            </Typography>
            <Typography
              variant="h6"
              sx={{ fontWeight: 700, fontSize: 20 }}
            >
              {metric.value}
            </Typography>
          </Paper>
        ))}
      </Box>

      {/* Charts Row */}
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: 1,
          mb: 2,
        }}
      >
        {/* Exclusivity Pie */}
        <Paper
          sx={{
            p: 1.2,
            background: "#f6f8fa",
            borderRadius: 2,
            boxShadow: 1,
          }}
        >
          <Typography
            variant="h6"
            sx={{
              mb: 1,
              color: "#005a9e",
              fontWeight: 700,
              textAlign: "center",
            }}
          >
            Exclusivity Distribution
          </Typography>
          <ResponsiveContainer width="100%" height={160}>
            <PieChart>
              <Pie
                data={exclusivityData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={55}
                labelLine={false}
                label={renderCustomizedLabel}
              >
                {exclusivityData.map((entry, idx) => (
                  <Cell
                    key={`cell-${idx}`}
                    fill={pieColors[idx % pieColors.length]}
                  />
                ))}
              </Pie>
              <Tooltip />
              <Legend verticalAlign="bottom" iconType="circle" />
            </PieChart>
          </ResponsiveContainer>
        </Paper>

        {/* Trust Scores Bar */}
        <Paper
          sx={{
            p: 1.2,
            background: "#f6f8fa",
            borderRadius: 2,
            boxShadow: 1,
          }}
        >
          <Typography
            variant="h6"
            sx={{
              mb: 1,
              color: "#1976d2",
              fontWeight: 700,
              textAlign: "center",
            }}
          >
            Merchant Trust Scores
          </Typography>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={trustBarData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" hide />
              <YAxis />
              <Tooltip />
              <Bar
                dataKey="TrustScore"
                fill={barColor}
                radius={[4, 4, 0, 0]}
                cursor="pointer"
                onClick={(data) => {
                  if (data && data.MerchantID) {
                    scrollToMerchantRow(data.MerchantID);
                  }
                }}
              />
            </BarChart>
          </ResponsiveContainer>
          <Typography
            variant="caption"
            sx={{ mt: 1, display: "block", textAlign: "center", color: "#555" }}
          >
            Click a bar to jump to merchant's record below
          </Typography>
        </Paper>

        {/* Growth Line */}
        <Paper
          sx={{
            p: 1.2,
            background: "#f6f8fa",
            borderRadius: 2,
            boxShadow: 1,
          }}
        >
          <Typography
            variant="h6"
            sx={{
              mb: 1,
              color: "#6a1b9a",
              fontWeight: 700,
              textAlign: "center",
            }}
          >
            Merchant Growth by Tenure
          </Typography>
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={metrics.merchantGrowthData || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="newMerchants"
                stroke={lineColor}
                strokeWidth={3}
                dot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </Paper>
      </Box>

      {/* Merchant List */}
      <Paper elevation={3} sx={{ mb: 2 }}>
        {loadingMerchants ? (
          <Box
            sx={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              height: 120,
            }}
          >
            <CircularProgress color="primary" />
          </Box>
        ) : (
          <Table>
            <TableHead>
              <TableRow sx={{ background: "#e3e8ee" }}>
                <TableCell
                  align="center"
                  sx={{ color: "#005a9e", fontWeight: 700 }}
                >
                  Merchant ID
                </TableCell>
                <TableCell
                  align="left"
                  sx={{ color: "#005a9e", fontWeight: 700 }}
                >
                  Name
                </TableCell>
                <TableCell
                  align="center"
                  sx={{ color: "#005a9e", fontWeight: 700 }}
                >
                  Trust Score
                </TableCell>
                <TableCell
                  align="center"
                  sx={{ color: "#005a9e", fontWeight: 700 }}
                >
                  Engagement
                </TableCell>
                <TableCell
                  align="center"
                  sx={{ color: "#005a9e", fontWeight: 700 }}
                >
                  Actions
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {merchants.map((row, idx) => (
                <TableRow
                  key={row.MerchantID}
                  ref={(el) => (rowRefs.current[row.MerchantID] = el)}
                  sx={{
                    background: idx % 2 === 0 ? "#f8fafc" : "#f4f6f8",
                    "&:hover": { background: "#e3e8ee" },
                    border:
                      selectedMerchantId === row.MerchantID
                        ? "2px solid #1976d2"
                        : undefined,
                  }}
                >
                  <TableCell align="center">{row.MerchantID}</TableCell>
                  <TableCell align="left">{row.MerchantName}</TableCell>
                  <TableCell align="center">{row.TrustScore}</TableCell>
                  <TableCell align="center">{row.EngagementScore}</TableCell>
                  <TableCell align="center">
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => handleViewDetails(row.MerchantID)}
                      sx={{
                        borderColor: "#005a9e",
                        color: "#005a9e",
                        fontWeight: 600,
                        "&:hover": { background: "#e3e8ee" },
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

      {/* Modal for Merchant Details */}
      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle
          sx={{
            display: "flex",
            justifyContent: "space-between",
            background: "#005a9e",
            color: "#fff",
          }}
        >
          Merchant Details
          <IconButton
            aria-label="close"
            onClick={handleClose}
            disabled={loadingDetail}
            sx={{ color: "#fff" }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers>
          {loadingDetail ? (
            <Box
              sx={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                height: 120,
              }}
            >
              <CircularProgress color="primary" />
              <Typography sx={{ ml: 2 }}>Loading details...</Typography>
            </Box>
          ) : merchantDetail ? (
            <Box
              sx={{
                px: 3,
                py: 2,
                bgcolor: "#f3f6fb",
                borderRadius: 3,
                border: "2px solid #1976d2",
                mb: 2,
              }}
            >
              <Typography
                variant="h5"
                sx={{ color: "#1976d2", fontWeight: 800, mb: 1 }}
              >
                Merchant AI Insights
              </Typography>
              <Divider sx={{ width: "70%", mb: 2 }} />
              <Box sx={{ mb: 2 }}>
                <Typography
                  variant="subtitle2"
                  sx={{ color: "#388e3c", fontWeight: 700, mb: 1 }}
                >
                  Summary
                </Typography>
                <Typography
                  sx={{ bgcolor: "#e8f5e9", p: 2, borderRadius: 2 }}
                >
                  {renderContentField(merchantDetail.Summary)}
                </Typography>
              </Box>
              <Box>
                <Typography
                  variant="subtitle2"
                  sx={{ color: "#d32f2f", fontWeight: 700, mb: 1 }}
                >
                  Recommendations
                </Typography>
                <Typography
                  sx={{ bgcolor: "#ffebee", p: 2, borderRadius: 2 }}
                >
                  {renderContentField(merchantDetail.Recommendations)}
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
