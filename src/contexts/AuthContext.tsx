import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, getStoredUser, isAuthenticated as checkAuth, clearTokens } from '@/lib/auth';
import { getOdooUser, isOdooAuthenticated, clearOdooSession } from '@/lib/odoo-auth';
import { login as apiLogin, logout as apiLogout } from '@/lib/api';
import { toast } from 'sonner';
import { useQueryClient } from '@tanstack/react-query';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const queryClient = useQueryClient();

  // Check authentication status on mount
  useEffect(() => {
    const initAuth = () => {
      try {
        console.log('🚀 [QARIQA v2.0 - BUILD: 2025-01-28] Initializing with NEW Odoo Auth System');

        // Check Odoo authentication first
        if (isOdooAuthenticated()) {
          console.log('✅ [AUTH] Using Odoo authentication session');
          const odooUser = getOdooUser();
          setUser(odooUser);
          return;
        }

        // Fallback to JWT auth (backwards compatibility)
        const isAuth = checkAuth();
        if (isAuth) {
          const storedUser = getStoredUser();
          setUser(storedUser);
        } else {
          setUser(null);
          clearTokens();
          clearOdooSession();
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  // Login function
  const login = async (username: string, password: string) => {
    try {
      setIsLoading(true);
      // Clear cache before login to ensure fresh data for new user
      queryClient.clear();
      const response = await apiLogin(username, password);
      setUser(response.user);
      toast.success('Login effettuato con successo!');
    } catch (error: any) {
      console.error('Login error:', error);
      toast.error(error.message || 'Errore durante il login. Verifica le tue credenziali.');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = async () => {
    try {
      setIsLoading(true);
      await apiLogout();
      // Clear React Query cache to remove all cached data
      queryClient.clear();
      setUser(null);
      toast.success('Logout effettuato con successo!');
    } catch (error: any) {
      console.error('Logout error:', error);
      // Still clear local state and cache even if API call fails
      queryClient.clear();
      setUser(null);
      toast.error('Errore durante il logout.');
    } finally {
      setIsLoading(false);
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Custom hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
