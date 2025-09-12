import axios from 'axios';

const BASE_URL = 'http://127.0.0.1:8000';

export const postAIQuery = async (query) =>
  axios.post(`${BASE_URL}/ai-query`, { query }).then(res => res.data);