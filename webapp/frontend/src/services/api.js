import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============================================================================
// Health & Stats
// ============================================================================

export const getHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

// ============================================================================
// Symptoms API
// ============================================================================

export const createSymptom = async (symptomData) => {
  const response = await api.post('/api/symptoms', symptomData);
  return response.data;
};

export const getSymptoms = async (limit = 10) => {
  const response = await api.get('/api/symptoms', { params: { limit } });
  return response.data;
};

export const getSymptomSummary = async (days = 30) => {
  const response = await api.get('/api/symptoms/summary', { params: { days } });
  return response.data;
};

// ============================================================================
// Cycles API
// ============================================================================

export const createCycle = async (cycleData) => {
  const response = await api.post('/api/cycles', cycleData);
  return response.data;
};

export const updateCycle = async (cycleId, cycleData) => {
  const response = await api.patch(`/api/cycles/${cycleId}`, cycleData);
  return response.data;
};

export const getCycles = async (limit = 6) => {
  const response = await api.get('/api/cycles', { params: { limit } });
  return response.data;
};

export const getCycleAnalytics = async (months = 6) => {
  const response = await api.get('/api/cycles/analytics', { params: { months } });
  return response.data;
};

// ============================================================================
// Analytics API
// ============================================================================

export const analyzeCorrelation = async (months = 3) => {
  const response = await api.get('/api/analytics/correlation', { params: { months } });
  return response.data;
};

export const analyzeTrends = async (symptomType = null, days = 90) => {
  const params = { days };
  if (symptomType) params.symptom_type = symptomType;
  const response = await api.get('/api/analytics/trends', { params });
  return response.data;
};

export const identifyPatterns = async (minOccurrences = 2) => {
  const response = await api.get('/api/analytics/patterns', {
    params: { min_occurrences: minOccurrences }
  });
  return response.data;
};

// ============================================================================
// Knowledge Base API
// ============================================================================

export const queryKnowledge = async (question, numSources = 3, categoryFilter = null) => {
  const response = await api.post('/api/knowledge/query', {
    question,
    num_sources: numSources,
    category_filter: categoryFilter
  });
  return response.data;
};

export const getKnowledgeStats = async () => {
  const response = await api.get('/api/knowledge/stats');
  return response.data;
};

// ============================================================================
// Authentication API
// ============================================================================

export const register = async (userData) => {
  const response = await api.post('/api/auth/register', userData);
  return response.data;
};

export const login = async (username, password) => {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  const response = await api.post('/api/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  return response.data;
};

export const getCurrentUser = async (token) => {
  const response = await api.get('/api/auth/me', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};

export const updateAPIKeys = async (token, keys) => {
  const response = await api.put('/api/auth/api-keys', keys, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};

// ============================================================================
// Chat API
// ============================================================================

export const sendChatMessage = async (token, messageData) => {
  const response = await api.post('/api/chat', messageData, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};

// Set auth token for all requests
export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

export default api;
