/**
 * React Query hooks for Charging Session operations
 */

import { useQuery } from '@tanstack/react-query';
import { callOdoo } from '@/lib/odoo-api';
import { transformOdooChargingSession, transformArray } from '@/lib/transformers';

/**
 * Fetch all charging sessions
 */
export function useChargingSessions() {
  return useQuery({
    queryKey: ['charging-sessions'],
    queryFn: async () => {
      const data = await callOdoo('wallbox.charging.session', 'search_read', [[]], {
        fields: ['transaction_id', 'charging_station_id', 'parking_space_id', 'customer_id', 'vehicle_id', 'start_time', 'end_time', 'total_duration', 'total_energy', 'cost', 'status'],
        limit: 100,
        order: 'id desc'
      });
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
      const data = await callOdoo('wallbox.charging.session', 'read', [[Number(id)]], {
        fields: ['transaction_id', 'charging_station_id', 'customer_id', 'vehicle_id', 'start_time', 'end_time', 'total_duration', 'start_meter', 'stop_meter', 'total_energy', 'cost', 'status', 'max_amount_limit']
      });
      return transformOdooChargingSession(data[0]);
    },
    enabled: !!id,
    staleTime: 1 * 60 * 1000, // 1 minute
  });
}

/**
 * Fetch charging sessions by charging station ID
 */
export function useChargingSessionsByStation(stationId: number | string | undefined) {
  return useQuery({
    queryKey: ['charging-sessions', 'station', stationId],
    queryFn: async () => {
      const data = await callOdoo('wallbox.charging.session', 'search_read', [
        [['charging_station_id', '=', Number(stationId)]]
      ], {
        fields: ['transaction_id', 'charging_station_id', 'customer_id', 'vehicle_id', 'start_time', 'end_time', 'total_duration', 'total_energy', 'cost', 'status'],
        order: 'id desc'
      });
      return transformArray(data, transformOdooChargingSession);
    },
    enabled: !!stationId,
    staleTime: 1 * 60 * 1000, // 1 minute
  });
}

/**
 * Fetch active charging sessions (Started)
 */
export function useActiveChargingSessions() {
  return useQuery({
    queryKey: ['charging-sessions', 'active'],
    queryFn: async () => {
      const data = await callOdoo('wallbox.charging.session', 'search_read', [
        [['status', '=', 'Started']]
      ], {
        fields: ['transaction_id', 'charging_station_id', 'customer_id', 'vehicle_id', 'start_time', 'total_duration', 'total_energy', 'cost', 'status']
      });
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
      const data = await callOdoo('wallbox.charging.session', 'search_read', [[]], {
        fields: ['transaction_id', 'charging_station_id', 'customer_id', 'start_time', 'end_time', 'total_energy', 'cost', 'status'],
        limit: limit,
        order: 'id desc'
      });
      return transformArray(data, transformOdooChargingSession);
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}
