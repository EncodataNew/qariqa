/**
 * React Query hooks for User (Wallbox Partner) operations
 */

import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { transformOdooUser, transformArray } from '@/lib/transformers';

/**
 * Fetch all wallbox users
 */
export function useUsers(condominiumId?: number | string) {
  return useQuery({
    queryKey: condominiumId ? ['users', 'condominium', condominiumId] : ['users'],
    queryFn: async () => {
      const url = condominiumId ? `/v1/users?condominium_id=${condominiumId}` : '/v1/users';
      const { data } = await apiClient.get(url);
      return transformArray(data, transformOdooUser);
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Fetch single user by ID with vehicles and history
 */
export function useUser(id: number | string | undefined) {
  return useQuery({
    queryKey: ['user', id],
    queryFn: async () => {
      const { data } = await apiClient.get(`/v1/users/${id}`);
      return transformOdooUser(data);
    },
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
