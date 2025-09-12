import React from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import MerchantDashboard from "./pages/MerchantDashboard";
import CustomerDashboard from "./pages/CustomerDashboard";
import CrossInsights from "./pages/CrossInsights";
import AIQueryDashboard from "./pages/AIQueryDashboard";
import { Box } from "@mui/material";

export default function App() {
  return (
    <Router>
      <Box sx={{ p: 2, borderBottom: "1px solid #eee", mb: 2 }}>
        <Link to="/merchants" style={{ marginRight: 16 }}>Merchants</Link>
        <Link to="/customers" style={{ marginRight: 16 }}>Customers</Link>
        {/* <Link to="/cross-insights" style={{ marginRight: 16 }}>Cross Insights</Link> */}
        <Link to="/ai-analytics">AI Analytics</Link>
      </Box>
      <Routes>
        <Route path="/merchants" element={<MerchantDashboard />} />
        <Route path="/customers" element={<CustomerDashboard />} />
        {/* <Route path="/cross-insights" element={<CrossInsights />} /> */}
        <Route path="/ai-analytics" element={<AIQueryDashboard />} />
        <Route path="*" element={<MerchantDashboard />} />
      </Routes>
    </Router>
  );
}