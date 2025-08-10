/**
 * API Service Layer - Shared Budgeting App
 * 
 * This module provides a centralized way to interact with the backend API.
 * It handles authentication, error handling, and provides methods for all
 * backend endpoints including transactions, categories, analytics, etc.
 */

import axios from 'axios';

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
let authToken = null;

export const setAuthToken = (token) => {
  authToken = token;
  if (token) {
    apiClient.defaults.headers.Authorization = `Bearer ${token}`;
    localStorage.setItem('authToken', token);
  } else {
    delete apiClient.defaults.headers.Authorization;
    localStorage.removeItem('authToken');
  }
};

export const getAuthToken = () => {
  if (!authToken) {
    authToken = localStorage.getItem('authToken');
    if (authToken) {
      apiClient.defaults.headers.Authorization = `Bearer ${authToken}`;
    }
  }
  return authToken;
};

// Initialize token from localStorage
getAuthToken();

// Request interceptor for debugging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`🔄 API Request: ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('🚨 Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('🚨 API Error:', error);
    
    // Handle unauthorized errors
    if (error.response?.status === 401 || error.response?.status === 403) {
      setAuthToken(null);
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

// ========================================
// Authentication API
// ========================================

export const authAPI = {
  register: async (userData) => {
    const response = await apiClient.post('/register', userData);
    return response.data;
  },

  login: async (credentials) => {
    const response = await apiClient.post('/login', credentials);
    if (response.data.access_token) {
      setAuthToken(response.data.access_token);
    }
    return response.data;
  },

  logout: () => {
    setAuthToken(null);
  },

  getCurrentUser: async () => {
    const response = await apiClient.get('/debug-auth');
    return response.data;
  },
};

// ========================================
// Transaction API
// ========================================

export const transactionAPI = {
  getTransactions: async (params = {}) => {
    const response = await apiClient.get('/transactions', { params });
    return response.data;
  },

  createTransaction: async (transactionData) => {
    const response = await apiClient.post('/transactions', transactionData);
    return response.data;
  },

  updateTransaction: async (id, transactionData) => {
    const response = await apiClient.put(`/transactions/${id}`, transactionData);
    return response.data;
  },

  deleteTransaction: async (id) => {
    const response = await apiClient.delete(`/transactions/${id}`);
    return response.data;
  },

  categorizeTransaction: async (id, categoryId) => {
    const response = await apiClient.post(`/transactions/${id}/categorize`, {
      category_id: categoryId
    });
    return response.data;
  },
};

// ========================================
// Category API
// ========================================

export const categoryAPI = {
  getCategories: async () => {
    const response = await apiClient.get('/categories');
    return response.data;
  },

  createCategory: async (categoryData) => {
    const response = await apiClient.post('/categories', categoryData);
    return response.data;
  },

  updateCategory: async (id, categoryData) => {
    const response = await apiClient.put(`/categories/${id}`, categoryData);
    return response.data;
  },

  deleteCategory: async (id) => {
    const response = await apiClient.delete(`/categories/${id}`);
    return response.data;
  },
};

// ========================================
// File Upload API
// ========================================

export const fileAPI = {
  uploadStatement: async (file, householdId = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (householdId) {
      formData.append('household_id', householdId);
    }

    const response = await apiClient.post('/upload-statement', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getUploadedFiles: async () => {
    const response = await apiClient.get('/files');
    return response.data;
  },
};

// ========================================
// Income API
// ========================================

export const incomeAPI = {
  getIncome: async (params = {}) => {
    const response = await apiClient.get('/income', { params });
    return response.data;
  },

  createIncome: async (incomeData) => {
    const response = await apiClient.post('/income', incomeData);
    return response.data;
  },

  updateIncome: async (id, incomeData) => {
    const response = await apiClient.put(`/income/${id}`, incomeData);
    return response.data;
  },

  deleteIncome: async (id) => {
    const response = await apiClient.delete(`/income/${id}`);
    return response.data;
  },
};

// ========================================
// Goals API
// ========================================

export const goalAPI = {
  getGoals: async () => {
    const response = await apiClient.get('/goals');
    return response.data;
  },

  createGoal: async (goalData) => {
    const response = await apiClient.post('/goals', goalData);
    return response.data;
  },

  updateGoal: async (id, goalData) => {
    const response = await apiClient.put(`/goals/${id}`, goalData);
    return response.data;
  },

  deleteGoal: async (id) => {
    const response = await apiClient.delete(`/goals/${id}`);
    return response.data;
  },

  addGoalContribution: async (id, amount, notes = '') => {
    const response = await apiClient.post(`/goals/${id}/contribute`, {
      amount,
      notes
    });
    return response.data;
  },
};

// ========================================
// Analytics API
// ========================================

export const analyticsAPI = {
  getSpendingTrends: async (months = 12) => {
    const response = await apiClient.get(`/analytics/spending-trends?months=${months}`);
    return response.data;
  },

  getCategoryAnalysis: async (startDate = null, endDate = null) => {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    
    const response = await apiClient.get('/analytics/category-analysis', { params });
    return response.data;
  },

  getMonthlyReport: async (year, month) => {
    const response = await apiClient.get(`/analytics/monthly-report/${year}/${month}`);
    return response.data;
  },

  getBudgetPerformance: async () => {
    const response = await apiClient.get('/analytics/budget-performance');
    return response.data;
  },

  getFinancialInsights: async () => {
    const response = await apiClient.get('/analytics/insights');
    return response.data;
  },
};

// ========================================
// Health Check API
// ========================================

export const healthAPI = {
  checkHealth: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  getDebugInfo: async () => {
    const response = await apiClient.get('/debug');
    return response.data;
  },
};

// Export default API object with all services
export default {
  auth: authAPI,
  transactions: transactionAPI,
  categories: categoryAPI,
  files: fileAPI,
  income: incomeAPI,
  goals: goalAPI,
  analytics: analyticsAPI,
  health: healthAPI,
};