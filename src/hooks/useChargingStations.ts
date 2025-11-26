/**
 * React Query hooks for Charging Station operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
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
      const url = condominiumId
        ? `/v1/charging-stations?condominium_id=${condominiumId}`
        : '/v1/charging-stations';
      const { data } = await apiClient.get(url);
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
      const { data } = await apiClient.get(`/v1/charging-stations/${id}`);
      return transformOdooChargingStation(data);
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
      const { data } = await apiClient.get(`/v1/charging-stations?building_id=${buildingId}`);
      return transformArray(data, transformOdooChargingStation);
    },
    enabled: !!buildingId,
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
      const { data } = await apiClient.put(`/v1/charging-stations/${id}`, updates);
      return transformOdooChargingStation(data);
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
