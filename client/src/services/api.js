import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getHealth = async () => {
  const response = await api.get('/api/health');
  return response.data;
};

export const getStats = async () => {
  const response = await api.get('/api/stats');
  return response.data;
};

export const getAnomalies = async () => {
  const response = await api.get('/api/anomalies');
  return response.data;
};

export const queryNaturalLanguage = async (question) => {
  const response = await api.post('/api/query', { question });
  return response.data;
};

export const getTickets = async (filters = {}) => {
  const response = await api.get('/api/tickets', { params: filters });
  return response.data;
};

export const uploadCSV = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/api/upload-csv', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  return response.data;
};
