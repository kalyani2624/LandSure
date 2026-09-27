import axios from 'axios';

const BACKEND_URL = import.meta.env.VITE_API_BASE_URL || '';

// Create Axios Instance
const api = axios.create({
  baseURL: BACKEND_URL,
  timeout: 45000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request Interceptor: Attach JWT Bearer Token if available in localStorage
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('sih_auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor: Handle Unauthorized errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token and redirect to login if unauthorized
      localStorage.removeItem('sih_auth_token');
      localStorage.removeItem('sih_auth_user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (username, password) => {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    
    const response = await api.post('/api/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    
    const { access_token } = response.data;
    localStorage.setItem('sih_auth_token', access_token);
    
    // Fetch profile info immediately
    const profileResponse = await api.get('/api/auth/me');
    const user = profileResponse.data;
    localStorage.setItem('sih_auth_user', JSON.stringify(user));
    
    return { token: access_token, user };
  },
  
  register: async (username, email, password, role = 'Official') => {
    const response = await api.post('/api/auth/register', { username, email, password, role });
    return response.data;
  },
  
  logout: () => {
    localStorage.removeItem('sih_auth_token');
    localStorage.removeItem('sih_auth_user');
  },
  
  getCurrentUser: () => {
    try {
      const user = localStorage.getItem('sih_auth_user');
      return user ? JSON.parse(user) : null;
    } catch {
      return null;
    }
  },
  
  getToken: () => {
    return localStorage.getItem('sih_auth_token') || null;
  },

  isAuthenticated: () => {
    const token = localStorage.getItem('sih_auth_token');
    const userStr = localStorage.getItem('sih_auth_user');
    if (!token || !userStr) return false;
    try {
      return JSON.parse(userStr) !== null;
    } catch {
      return false;
    }
  }
};

export const documentService = {
  upload: async (file, language = 'Auto') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', language);
    
    const response = await api.post('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },
  
  list: async () => {
    const response = await api.get('/api/documents');
    return response.data;
  },
  
  getDetails: async (id) => {
    const response = await api.get(`/api/documents/${id}`);
    return response.data;
  },

  getExtractionDebug: async (id) => {
    const response = await api.get(`/api/documents/${id}/extraction-debug`);
    return response.data;
  },

  getFileUrl: (id) => {
    return `${BACKEND_URL}/api/documents/${id}/file`;
  },

  getPreprocessedFileUrl: (id) => {
    return `${BACKEND_URL}/api/documents/${id}/preprocessed-file`;
  },

  getCertificateUrl: (id) => {
    return `${BACKEND_URL}/api/documents/${id}/certificate`;
  }
};

export const recordService = {
  search: async (filters = {}) => {
    const response = await api.get('/api/records', { params: filters });
    return response.data;
  },
  
  getDetails: async (id) => {
    const response = await api.get(`/api/records/${id}`);
    return response.data;
  },

  getRecordDetails: async (id) => {
    const response = await api.get(`/api/records/${id}`);
    return response.data;
  },
  
  getExportCSVUrl: () => {
    return `${BACKEND_URL}/api/records/export/csv`;
  },
  
  getExportPDFUrl: (id) => {
    return `${BACKEND_URL}/api/records/export/pdf/${id}`;
  },

  downloadCertificate: (id) => {
    window.open(`${BACKEND_URL}/api/records/export/pdf/${id}`, '_blank');
  }
};

export const verificationService = {
  getPendingList: async () => {
    const response = await api.get('/api/verification/list');
    return response.data;
  },
  
  verifyRecord: async (documentId, fields, approved = true) => {
    const response = await api.put(`/api/verification/${documentId}/verify`, fields, {
      params: { approved }
    });
    return response.data;
  },

  submitReview: async (payload) => {
    const { document_id, decision, reviewed_fields } = payload;
    const approved = decision === 'Approved';
    const response = await api.put(`/api/verification/${document_id}/verify`, reviewed_fields, {
      params: { approved }
    });
    return response.data;
  },
  
  getAudits: async (recordId) => {
    const response = await api.get(`/api/verification/${recordId}/audits`);
    return response.data;
  }
};

export const dashboardService = {
  getStats: async () => {
    const response = await api.get('/api/dashboard/stats');
    return response.data;
  }
};

export default api;
