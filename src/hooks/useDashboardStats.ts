/**
 * React Query hooks for Dashboard Statistics
 */

import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { transformOdooDashboardStats } from '@/lib/transformers';

/**
 * Fetch aggregated dashboard statistics
 */
export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const { data } = await apiClient.get('/v1/admin/dashboard');
      return transformOdooDashboardStats(data);
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 60 * 1000, // Refetch every minute for real-time dashboard
  });
}
