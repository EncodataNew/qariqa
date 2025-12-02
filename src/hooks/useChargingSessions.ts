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
      // First, fetch charging sessions
      const sessions = await callOdoo('wallbox.charging.session', 'search_read', [[]], {
        fields: ['transaction_id', 'charging_station_id', 'customer_id', 'vehicle_id', 'start_time', 'end_time', 'total_duration', 'total_energy', 'cost', 'status'],
        limit: 100,
        order: 'id desc'
      });

      // Extract unique charging station IDs
      const stationIds = [...new Set(sessions.map((s: any) => s.charging_station_id?.[0]).filter(Boolean))];

      // Fetch charging stations with parking space info
      const stations = stationIds.length > 0
        ? await callOdoo('charging.station', 'search_read', [
            [['id', 'in', stationIds]]
          ], {
            fields: ['id', 'parking_space_id']
          })
        : [];

      // Create a map of station_id -> parking_space info
      const stationParkingMap = new Map(
        stations.map((station: any) => [
          station.id,
          {
            parking_space_id: station.parking_space_id?.[0] || 0,
            parking_space_name: station.parking_space_id?.[1] || ''
          }
        ])
      );

      // Merge parking space data into sessions
      const enrichedSessions = sessions.map((session: any) => {
        const stationId = session.charging_station_id?.[0];
        const parkingInfo = stationParkingMap.get(stationId);
        return {
          ...session,
          parking_space_id: parkingInfo?.parking_space_id,
          parking_space_name: parkingInfo?.parking_space_name
        };
      });

      return transformArray(enrichedSessions, transformOdooChargingSession);
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
