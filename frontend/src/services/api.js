import axios from 'axios';

// Use Vite proxy for API calls in development, or environment variable for production
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Market API
export const marketAPI = {
  getOverview: () => api.get('/api/market/overview'),
  getHistory: () => api.get('/api/market/history'),
  getForecast: () => api.get('/api/market/forecast'),
  getMetrics: () => api.get('/api/market/metrics'),
};

// Countries API
export const countriesAPI = {
  getAll: (params = {}) => api.get('/api/countries', { params }),
  getDetail: (country) => api.get(`/api/countries/${encodeURIComponent(country)}`),
  getRiskRanking: (limit = 50) => api.get('/api/countries/risk', { params: { limit } }),
  getOpportunityRanking: (limit = 50) => api.get('/api/countries/opportunity', { params: { limit } }),
};

// Trading API
export const tradingAPI = {
  getModelInfo: () => api.get('/api/trading/model'),
  predict: (data) => api.post('/api/trading/predict', data),
};

// Scenario API
export const scenarioAPI = {
  simulate: (params) => api.post('/api/scenario/simulate', params),
};

export default api;
