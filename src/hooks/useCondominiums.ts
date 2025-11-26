/**
 * React Query hooks for Condominium CRUD operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { transformOdooCondominium, transformArray } from '@/lib/transformers';
import type { Condominio } from '@/types/types';
import { toast } from 'sonner';

/**
 * Fetch all condominiums
 */
export function useCondominiums() {
  return useQuery({
    queryKey: ['condominiums'],
    queryFn: async () => {
      const { data } = await apiClient.get('/v1/condominiums');
      return transformArray(data, transformOdooCondominium);
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Fetch single condominium by ID with buildings
 */
export function useCondominium(id: number | string | undefined) {
  return useQuery({
    queryKey: ['condominium', id],
    queryFn: async () => {
      const { data } = await apiClient.get(`/v1/condominiums/${id}`);
      return transformOdooCondominium(data);
    },
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Create a new condominium
 */
export function useCreateCondominium() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (condominiumData: Partial<Condominio>) => {
      const { data } = await apiClient.post('/v1/condominiums', condominiumData);
      return transformOdooCondominium(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['condominiums'] });
      toast.success('Condominio creato con successo');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Errore durante la creazione del condominio');
    },
  });
}

/**
 * Update an existing condominium
 */
export function useUpdateCondominium() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, updates }: { id: number; updates: Partial<Condominio> }) => {
      const { data } = await apiClient.put(`/v1/condominiums/${id}`, updates);
      return transformOdooCondominium(data);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['condominiums'] });
      queryClient.invalidateQueries({ queryKey: ['condominium', data.id] });
      toast.success('Condominio aggiornato con successo');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Errore durante l\'aggiornamento del condominio');
    },
  });
}

/**
 * Delete a condominium
 */
export function useDeleteCondominium() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/v1/condominiums/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['condominiums'] });
      toast.success('Condominio eliminato con successo');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Errore durante l\'eliminazione del condominio');
    },
  });
}
