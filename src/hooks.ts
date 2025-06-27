import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from './api';

// Document parsing hook
export const useParseDocument = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: apiService.parseDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
    },
  });
};

// Speech to text hook
export const useSpeechToText = () => {
  return useMutation({
    mutationFn: ({ audioFile, language }: { audioFile: File; language?: string }) =>
      apiService.speechToText(audioFile, language),
  });
};

// Query documents hook
export const useQueryDocuments = () => {
  return useMutation({
    mutationFn: ({ question, contextLimit, includeSources }: {
      question: string;
      contextLimit?: number;
      includeSources?: boolean;
    }) => apiService.queryDocuments(question, contextLimit, includeSources),
  });
};

// Get alerts hook
export const useAlerts = (limit = 10, severity?: string) => {
  return useQuery({
    queryKey: ['alerts', limit, severity],
    queryFn: () => apiService.getAlerts(limit, severity),
    refetchInterval: 30000, // Refresh every 30 seconds
  });
};

// Dashboard stats hook
export const useDashboardStats = () => {
  return useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: apiService.getDashboardStats,
    refetchInterval: 10000, // Refresh every 10 seconds
  });
};

// Health check hook
export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: apiService.healthCheck,
    refetchInterval: 60000, // Check every minute
  });
};