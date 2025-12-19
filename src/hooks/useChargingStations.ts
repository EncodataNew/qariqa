/**
 * React Query hooks for Charging Station operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { callOdoo } from '@/lib/odoo-api';
import { transformOdooChargingStation, transformArray } from '@/lib/transformers';
import type { ChargingStation } from '@/types/types';
import { toast } from 'sonner';

/**
 * Fetch all charging stations
 */
export function useChargingStations(condominiumId?: number | string) {
  return useQuery({
    queryKey: condominiumId ? ['charging-stations', 'condominium', condominiumId] : ['charging-stations'],
    queryFn: async () => {
      const domain = condominiumId ? [['condominium_id', '=', Number(condominiumId)]] : [];
      const data = await callOdoo('charging.station', 'search_read', [domain], {
        fields: ['name', 'status', 'charging_power', 'connector_type', 'building_id', 'condominium_id', 'parking_space_id', 'price_per_kwh', 'number_of_charging_sessions']
      });
      return transformArray(data, transformOdooChargingStation);
    },
    staleTime: 2 * 60 * 1000, // 2 minutes (shorter for real-time status)
  });
}

/**
 * Fetch single charging station by ID
 */
export function useChargingStation(id: number | string | undefined) {
  return useQuery({
    queryKey: ['charging-station', id],
    queryFn: async () => {
      const data = await callOdoo('charging.station', 'read', [[Number(id)]], {
        fields: ['name', 'status', 'charging_power', 'connector_type', 'building_id', 'condominium_id', 'manager_id', 'parking_space_id', 'price_per_kwh', 'number_of_charging_sessions', 'total_energy', 'total_recharged_cost']
      });
      return transformOdooChargingStation(data[0]);
    },
    enabled: !!id,
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 30 * 1000, // Refetch every 30 seconds for real-time status
  });
}

/**
 * Fetch charging stations by building ID
 */
export function useChargingStationsByBuilding(buildingId: number | string | undefined) {
  return useQuery({
    queryKey: ['charging-stations', 'building', buildingId],
    queryFn: async () => {
      const data = await callOdoo('charging.station', 'search_read', [
        [['building_id', '=', Number(buildingId)]]
      ], {
        fields: ['name', 'status', 'charging_power', 'connector_type', 'building_id', 'condominium_id', 'parking_space_id', 'price_per_kwh', 'number_of_charging_sessions']
      });
      return transformArray(data, transformOdooChargingStation);
    },
    enabled: !!buildingId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Fetch charging stations by parking space ID
 */
export function useChargingStationsByParkingSpace(parkingSpaceId: number | string | undefined) {
  return useQuery({
    queryKey: ['charging-stations', 'parking-space', parkingSpaceId],
    queryFn: async () => {
      const data = await callOdoo('charging.station', 'search_read', [
        [['parking_space_id', '=', Number(parkingSpaceId)]]
      ], {
        fields: ['name', 'status', 'charging_power', 'connector_type', 'building_id', 'condominium_id', 'parking_space_id', 'price_per_kwh', 'number_of_charging_sessions']
      });
      return transformArray(data, transformOdooChargingStation);
    },
    enabled: !!parkingSpaceId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Update charging station (e.g., status change)
 */
export function useUpdateChargingStation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, updates }: { id: number; updates: Partial<ChargingStation> }) => {
      await callOdoo('charging.station', 'write', [[id], {
        name: updates.nome,
        status: updates.stato,
        power: updates.potenza,
        connector_type: updates.tipo_connettore,
      }], {});
      const data = await callOdoo('charging.station', 'read', [[id]], {});
      return transformOdooChargingStation(data[0]);
    },
    onSuccess: (data) => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['charging-stations'] });
      queryClient.invalidateQueries({ queryKey: ['charging-station', data.id] });
      queryClient.invalidateQueries({ queryKey: ['condominiums'] });
      toast.success('Stazione di ricarica aggiornata con successo');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Errore durante l\'aggiornamento della stazione');
    },
  });
}
