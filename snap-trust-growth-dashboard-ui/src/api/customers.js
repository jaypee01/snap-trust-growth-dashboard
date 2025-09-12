import axios from 'axios';

const BASE_URL = 'http://127.0.0.1:8000';

export const fetchCustomers = async (limit = 10, sort_by = "TrustScore,LoyaltyTier", sort_order = "desc,desc") =>
  axios.get(`${BASE_URL}/customers/`, {
    params: { limit, sort_by, sort_order }
  }).then(res => res.data);

export const fetchCustomerById = async (id) =>
  axios.get(`${BASE_URL}/customers/${id}`).then(res => res.data);

export const fetchCustomerHistory = async (id) =>
  axios.get(`${BASE_URL}/customers/${id}/history`).then(res => res.data);

export const fetchCustomerSummaryExplain = async (id) =>
  axios.get(`${BASE_URL}/customers/${id}/summary/explain`).then(res => res.data);

export const postCustomerAIQuery = async (query) =>
  axios.post(`${BASE_URL}/customers/ai-query`, { query }).then(res => res.data);