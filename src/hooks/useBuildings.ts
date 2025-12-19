/**
 * React Query hooks for Building CRUD operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { callOdoo } from '@/lib/odoo-api';
import { transformOdooBuilding, transformArray } from '@/lib/transformers';
import type { Building } from '@/types/types';
import { toast } from 'sonner';

/**
 * Fetch all buildings
 */
export function useBuildings() {
  return useQuery({
    queryKey: ['buildings'],
    queryFn: async () => {
      const data = await callOdoo('building.building', 'search_read', [[]], {
        fields: ['building_name', 'address', 'condominium_id', 'number_of_parking_spaces', 'number_of_charging_stations']
      });
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
      const data = await callOdoo('building.building', 'read', [[Number(id)]], {
        fields: ['building_name', 'address', 'condominium_id', 'manager_id', 'number_of_parking_spaces', 'number_of_charging_stations', 'number_of_users', 'parking_space_ids', 'charging_station_ids']
      });
      return transformOdooBuilding(data[0]);
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
      const data = await callOdoo('building.building', 'search_read', [
        [['condominium_id', '=', Number(condominiumId)]]
      ], {
        fields: ['building_name', 'address', 'condominium_id', 'number_of_parking_spaces', 'number_of_charging_stations']
      });
      return transformArray(data, transformOdooBuilding);
    },
    enabled: !!condominiumId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Create a new building
 */
export function useCreateBuilding() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (buildingData: Partial<Building>) => {
      const id = await callOdoo('building.building', 'create', [{
        building_name: buildingData.name,
        address: buildingData.address,
        condominium_id: buildingData.condominium_id,
      }], {});
      const data = await callOdoo('building.building', 'read', [[id]], {});
      return transformOdooBuilding(data[0]);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['buildings'] });
      toast.success('Edificio creato con successo');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Errore durante la creazione dell\'edificio');
    },
  });
}

/**
 * Update an existing building
 */
export function useUpdateBuilding() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, updates }: { id: number; updates: Partial<Building> }) => {
      await callOdoo('building.building', 'write', [[id], {
        building_name: updates.name,
        address: updates.address,
      }], {});
      const data = await callOdoo('building.building', 'read', [[id]], {});
      return transformOdooBuilding(data[0]);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['buildings'] });
      queryClient.invalidateQueries({ queryKey: ['building', data.id] });
      toast.success('Edificio aggiornato con successo');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Errore durante l\'aggiornamento dell\'edificio');
    },
  });
}

/**
 * Delete a building
 */
export function useDeleteBuilding() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await callOdoo('building.building', 'unlink', [[id]], {});
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['buildings'] });
      toast.success('Edificio eliminato con successo');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Errore durante l\'eliminazione dell\'edificio');
    },
  });
}
