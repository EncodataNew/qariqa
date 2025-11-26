/**
 * React Query hooks for Charging Session operations
 */

import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { transformOdooChargingSession, transformArray } from '@/lib/transformers';

interface ChargingSessionFilters {
  station_id?: number | string;
  user_id?: number | string;
  start_date?: string;
  end_date?: string;
  status?: string;
}

/**
 * Fetch charging sessions with optional filters
 */
export function useChargingSessions(filters?: ChargingSessionFilters) {
  return useQuery({
    queryKey: ['charging-sessions', filters],
    queryFn: async () => {
      const params = new URLSearchParams();

      if (filters?.station_id) params.append('station_id', String(filters.station_id));
      if (filters?.user_id) params.append('user_id', String(filters.user_id));
      if (filters?.start_date) params.append('start_date', filters.start_date);
      if (filters?.end_date) params.append('end_date', filters.end_date);
      if (filters?.status) params.append('status', filters.status);

      const url = `/v1/charging-sessions${params.toString() ? `?${params.toString()}` : ''}`;
      const { data } = await apiClient.get(url);
      return transformArray(data, transformOdooChargingSession);
    },
    staleTime: 1 * 60 * 1000, // 1 minute (short for real-time data)
  });
}

/**
 * Fetch single charging session by ID
 */
export function useChargingSession(id: number | string | undefined) {
  return useQuery({
    queryKey: ['charging-session', id],
    queryFn: async () => {
      const { data } = await apiClient.get(`/v1/charging-sessions/${id}`);
      return transformOdooChargingSession(data);
    },
    enabled: !!id,
    staleTime: 1 * 60 * 1000, // 1 minute
  });
}

/**
 * Fetch active charging sessions (in_corso)
 */
export function useActiveChargingSessions() {
  return useQuery({
    queryKey: ['charging-sessions', 'active'],
    queryFn: async () => {
      const { data } = await apiClient.get('/v1/charging-sessions?status=in_corso');
      return transformArray(data, transformOdooChargingSession);
    },
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 30 * 1000, // Refetch every 30 seconds for real-time updates
  });
}

/**
 * Fetch recent charging sessions (for dashboard)
 */
export function useRecentChargingSessions(limit: number = 10) {
  return useQuery({
    queryKey: ['charging-sessions', 'recent', limit],
    queryFn: async () => {
      const { data } = await apiClient.get(`/v1/charging-sessions?limit=${limit}`);
      return transformArray(data, transformOdooChargingSession);
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}
