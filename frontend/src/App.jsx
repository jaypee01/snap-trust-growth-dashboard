import NavBar from "./components/Navbar";
import { Box } from "@mui/material";
import MerchantsDashboard from "./components/MerchantsDashboard";
import ConsumerDashboard from "./components/ConsumerDashboard";
import MerchantsListing from "./components/MerchantsListing";
import ConsumersListing from "./components/ConsumersListing";
import { Routes, Route, Navigate } from "react-router";
import MerchantDetail from "./components/Merchant-Detail";
import ConsumerDetail from "./components/Consumer-Detail";

function App() {
  return (
    <>
      <Box component="header">
        <NavBar />
      </Box>
      <Box component="main" sx={{ mt: "10vh" }}>
        <Routes>
          <Route path="/" element={<Navigate to="/merchants" />} />
          <Route path="/merchants" element={<MerchantsListing />} />
          <Route path="/consumers" element={<ConsumersListing />} />
          <Route path="/merchants-dashboard" element={<MerchantsDashboard />} />
          <Route path="/consumer-dashboard" element={<ConsumerDashboard />} />
          <Route path="/consumers/:customerId" element={<ConsumerDetail />} />
          <Route path="/merchants/:merchantId" element={<MerchantDetail />} />
          <Route path="*" element={<Navigate to="/merchants" />} />
        </Routes>
      </Box>
    </>
  );
}

export default App;
