/**
 * API Client Configuration
 * Centralized axios instance for backend communication
 */

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:7235';

// Debug logging
if (typeof window !== 'undefined') {
  console.log('🔧 API Configuration:');
  console.log('  NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);
  console.log('  API_BASE_URL:', API_BASE_URL);
  console.log('  Full API Endpoint:', `${API_BASE_URL}/api/v1`);
}

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('❌ API Error:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      baseURL: error.config?.baseURL,
      data: error.response?.data,
    });
    return Promise.reject(error);
  }
);

export default apiClient;
