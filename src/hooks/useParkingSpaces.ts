/**
 * React Query hooks for Parking Space CRUD operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { callOdoo } from '@/lib/odoo-api';
import { transformOdooParkingSpace, transformArray } from '@/lib/transformers';
import type { ParkingSpace } from '@/types/types';
import { toast } from 'sonner';

/**
 * Fetch all parking spaces
 */
export function useParkingSpaces() {
  return useQuery({
    queryKey: ['parking-spaces'],
    queryFn: async () => {
      const data = await callOdoo('parking.space', 'search_read', [[]], {
        fields: ['name', 'building_id', 'condominium_id', 'parking_type', 'capacity', 'assigned_or_shared', 'number_of_charging_stations']
      });
      return transformArray(data, transformOdooParkingSpace);
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Fetch single parking space by ID
 */
export function useParkingSpace(id: number | string | undefined) {
  return useQuery({
    queryKey: ['parking-space', id],
    queryFn: async () => {
      const data = await callOdoo('parking.space', 'read', [[Number(id)]], {
        fields: ['name', 'building_id', 'condominium_id', 'parking_type', 'capacity', 'assigned_or_shared', 'number_of_charging_stations', 'charging_station_ids', 'owner_id', 'rental_status', 'monthly_fee']
      });
      return transformOdooParkingSpace(data[0]);
    },
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Fetch parking spaces by building ID
 */
export function useParkingSpacesByBuilding(buildingId: number | string | undefined) {
  return useQuery({
    queryKey: ['parking-spaces', 'building', buildingId],
    queryFn: async () => {
      const data = await callOdoo('parking.space', 'search_read', [
        [['building_id', '=', Number(buildingId)]]
      ], {
        fields: ['name', 'building_id', 'condominium_id', 'parking_type', 'capacity', 'assigned_or_shared', 'number_of_charging_stations']
      });
      return transformArray(data, transformOdooParkingSpace);
    },
    enabled: !!buildingId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Fetch parking spaces by condominium ID
 */
export function useParkingSpacesByCondominium(condominiumId: number | string | undefined) {
  return useQuery({
    queryKey: ['parking-spaces', 'condominium', condominiumId],
    queryFn: async () => {
      const data = await callOdoo('parking.space', 'search_read', [
        [['condominium_id', '=', Number(condominiumId)]]
      ], {
        fields: ['name', 'building_id', 'condominium_id', 'parking_type', 'capacity', 'assigned_or_shared', 'number_of_charging_stations']
      });
      return transformArray(data, transformOdooParkingSpace);
    },
    enabled: !!condominiumId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Create a new parking space
 */
export function useCreateParkingSpace() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (parkingSpaceData: Partial<ParkingSpace>) => {
      const id = await callOdoo('parking.space', 'create', [{
        name: parkingSpaceData.name,
        building_id: parkingSpaceData.building_id,
        condominium_id: parkingSpaceData.condominium_id,
        parking_type: parkingSpaceData.parking_type,
        capacity: parkingSpaceData.capacity,
        assigned_or_shared: parkingSpaceData.assigned_or_shared,
      }], {});
      const data = await callOdoo('parking.space', 'read', [[id]], {});
      return transformOdooParkingSpace(data[0]);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['parking-spaces'] });
      toast.success('Parcheggio creato con successo');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Errore durante la creazione del parcheggio');
    },
  });
}

/**
 * Update an existing parking space
 */
export function useUpdateParkingSpace() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, updates }: { id: number; updates: Partial<ParkingSpace> }) => {
      await callOdoo('parking.space', 'write', [[id], {
        name: updates.name,
        parking_type: updates.parking_type,
        capacity: updates.capacity,
        assigned_or_shared: updates.assigned_or_shared,
      }], {});
      const data = await callOdoo('parking.space', 'read', [[id]], {});
      return transformOdooParkingSpace(data[0]);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['parking-spaces'] });
      queryClient.invalidateQueries({ queryKey: ['parking-space', data.id] });
      toast.success('Parcheggio aggiornato con successo');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Errore durante l\'aggiornamento del parcheggio');
    },
  });
}

/**
 * Delete a parking space
 */
export function useDeleteParkingSpace() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await callOdoo('parking.space', 'unlink', [[id]], {});
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['parking-spaces'] });
      toast.success('Parcheggio eliminato con successo');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Errore durante l\'eliminazione del parcheggio');
    },
  });
}
