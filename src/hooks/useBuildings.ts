/**
 * React Query hooks for Building CRUD operations
 */

import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { transformOdooBuilding, transformArray } from '@/lib/transformers';

/**
 * Fetch all buildings
 */
export function useBuildings() {
  return useQuery({
    queryKey: ['buildings'],
    queryFn: async () => {
      const { data } = await apiClient.get('/v1/buildings');
      return transformArray(data, transformOdooBuilding);
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Fetch single building by ID
 */
export function useBuilding(id: number | string | undefined) {
  return useQuery({
    queryKey: ['building', id],
    queryFn: async () => {
      const { data } = await apiClient.get(`/v1/buildings/${id}`);
      return transformOdooBuilding(data);
    },
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Fetch buildings by condominium ID
 */
export function useBuildingsByCondominium(condominiumId: number | string | undefined) {
  return useQuery({
    queryKey: ['buildings', 'condominium', condominiumId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/v1/buildings?condominium_id=${condominiumId}`);
      return transformArray(data, transformOdooBuilding);
    },
    enabled: !!condominiumId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
