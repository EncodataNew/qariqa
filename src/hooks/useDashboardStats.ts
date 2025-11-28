/**
 * React Query hooks for Dashboard Statistics
 */

import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { getOdooCookies, getOdooBaseUrl } from '@/lib/odoo-auth';
import { transformOdooDashboardStats } from '@/lib/transformers';

/**
 * Fetch aggregated dashboard statistics
 */
export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const cookies = getOdooCookies();
      const baseUrl = getOdooBaseUrl();

      if (!cookies || !baseUrl) {
        throw new Error('Not authenticated');
      }

      const response = await axios.get('/api/admin/dashboard', {
        headers: {
          'X-Odoo-Cookies': JSON.stringify(cookies),
          'X-Odoo-Url': baseUrl,
        },
      });

      return transformOdooDashboardStats(response.data);
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 60 * 1000, // Refetch every minute for real-time dashboard
  });
}
