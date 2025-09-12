import axios from 'axios';

const BASE_URL = 'http://127.0.0.1:8000';

export const fetchMerchants = async (
  limit = 10,
  sort_by = "TrustScore,LoyaltyTier",
  sort_order = "desc,desc"
) =>
  axios.get(`${BASE_URL}/merchants/`, {
    params: { limit, sort_by, sort_order }
  }).then(res => res.data);

export const fetchMerchantById = async (id) =>
  axios.get(`${BASE_URL}/merchants/${id}`).then(res => res.data);

export const fetchMerchantHistory = async (id) =>
  axios.get(`${BASE_URL}/merchants/${id}/history`).then(res => res.data);

export const fetchMerchantSummaryExplain = async (id) =>
  axios.get(`${BASE_URL}/merchants/${id}/summary/explain`).then(res => res.data);

export const fetchMerchantBenchmark = async (id) =>
  axios.get(`${BASE_URL}/merchants/${id}/benchmark`).then(res => res.data);

export const postMerchantAIQuery = async (query) =>
  axios.post(`${BASE_URL}/merchants/ai-query`, { query }).then(res => res.data);

// ✅ NEW: Fetch aggregated average metrics
export const fetchMerchantAverages = async () =>
  axios.get(`${BASE_URL}/merchants/metrics/averages`).then(res => res.data);
