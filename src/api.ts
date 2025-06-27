import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API interfaces
export interface ParsedDocument {
  file_id: string;
  filename: string;
  content: string;
  metadata: Record<string, any>;
  page_count?: number;
  word_count?: number;
}

export interface ASRResponse {
  transcript: string;
  confidence: number;
  duration?: number;
  language: string;
}

export interface QueryResponse {
  answer: string;
  sources: Array<{
    document_id: string;
    filename: string;
    similarity_score: number;
    excerpt: string;
    metadata: Record<string, any>;
  }>;
  confidence: number;
  processing_time: number;
}

export interface AnomalyAlert {
  id: string;
  document_id: string;
  anomaly_type: string;
  severity: string;
  description: string;
  confidence: number;
  detected_at: string;
  metadata: Record<string, any>;
}

export interface DashboardStats {
  total_documents: number;
  total_queries: number;
  avg_processing_time: number;
  anomalies_detected: number;
  last_processed?: string;
}

// API functions
export const apiService = {
  // Document parsing
  parseDocument: async (file: File): Promise<ParsedDocument> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api/parse', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Speech to text
  speechToText: async (audioFile: File, language = 'en-US'): Promise<ASRResponse> => {
    const formData = new FormData();
    formData.append('audio_file', audioFile);
    formData.append('language', language);
    
    const response = await api.post('/api/asr', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Query documents
  queryDocuments: async (question: string, contextLimit = 5, includeSources = true): Promise<QueryResponse> => {
    const response = await api.post('/api/query', {
      question,
      context_limit: contextLimit,
      include_sources: includeSources,
    });
    return response.data;
  },

  // Get alerts
  getAlerts: async (limit = 10, severity?: string): Promise<AnomalyAlert[]> => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (severity) params.append('severity', severity);
    
    const response = await api.get(`/api/alerts?${params}`);
    return response.data;
  },

  // Get dashboard stats
  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await api.get('/api/dashboard/stats');
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;