/**
 * React Query hooks for Condominium CRUD operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { callOdoo } from '@/lib/odoo-api';
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
      const data = await callOdoo('condominium.condominium', 'search_read', [[]], {
        fields: ['name', 'street', 'city', 'zip', 'state_id']
      });
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
      const data = await callOdoo('condominium.condominium', 'read', [[Number(id)]], {
        fields: ['name', 'street', 'city', 'zip', 'state_id', 'building_ids']
      });
      return transformOdooCondominium(data[0]);
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
      const id = await callOdoo('condominium.condominium', 'create', [{
        name: condominiumData.nome,
        street: condominiumData.indirizzo,
        city: condominiumData.citta,
        zip: condominiumData.cap,
      }], {});
      const data = await callOdoo('condominium.condominium', 'read', [[id]], {});
      return transformOdooCondominium(data[0]);
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
      await callOdoo('condominium.condominium', 'write', [[id], {
        name: updates.nome,
        street: updates.indirizzo,
        city: updates.citta,
        zip: updates.cap,
      }], {});
      const data = await callOdoo('condominium.condominium', 'read', [[id]], {});
      return transformOdooCondominium(data[0]);
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
      await callOdoo('condominium.condominium', 'unlink', [[id]], {});
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
