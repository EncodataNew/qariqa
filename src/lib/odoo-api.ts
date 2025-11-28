import axios, { AxiosInstance } from 'axios';
import {
  setOdooSession,
  getOdooSession,
  getOdooCookies,
  getOdooBaseUrl,
  clearOdooSession,
  isOdooAuthenticated as checkOdooAuth,
} from './odoo-auth';

/**
 * Odoo API Client
 * Uses Netlify Functions as a backend proxy to handle Odoo authentication and API calls
 */

// Create axios instance for calling our own API endpoints
const apiClient: AxiosInstance = axios.create({
  baseURL: '', // Use relative URLs to call our own Netlify functions
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Login to Odoo
 */
export async function loginOdoo(
  url: string,
  database: string,
  username: string,
  password: string
): Promise<any> {
  try {
    console.log('[ODOO-API] Logging in to Odoo...');

    const response = await apiClient.post('/api/odoo/auth', {
      url,
      database,
      username,
      password,
    });

    if (!response.data.success) {
      throw new Error(response.data.message || 'Authentication failed');
    }

    const { sessionId, uid, username: user, database: db, baseUrl, cookies, serverVersion, serverVersionInfo } = response.data;

    // Store session and cookies
    setOdooSession(
      {
        sessionId,
        uid,
        username: user,
        database: db,
        baseUrl,
        serverVersion,
        serverVersionInfo,
      },
      cookies
    );

    console.log('[ODOO-API] Login successful:', { uid, username: user });

    return {
      access_token: sessionId, // Use sessionId as token for compatibility
      refresh_token: sessionId,
      user: {
        id: uid,
        name: user,
        email: user,
        login: user,
      },
    };
  } catch (error: any) {
    console.error('[ODOO-API] Login error:', error);

    if (error.response?.data) {
      throw new Error(error.response.data.message || error.response.data.error || 'Login failed');
    }

    throw new Error(error.message || 'Login failed. Please check your credentials.');
  }
}

/**
 * Call Odoo model method
 */
export async function callOdoo(
  model: string,
  method: string,
  args: any[] = [],
  kwargs: any = {}
): Promise<any> {
  try {
    const cookies = getOdooCookies();
    const baseUrl = getOdooBaseUrl();

    if (!cookies || !baseUrl) {
      throw new Error('Not authenticated. Please login first.');
    }

    console.log(`[ODOO-API] Calling ${model}.${method}`);

    const response = await apiClient.post(
      '/api/odoo/call',
      {
        model,
        method,
        args,
        kwargs,
      },
      {
        headers: {
          'X-Odoo-Cookies': JSON.stringify(cookies),
          'X-Odoo-Url': baseUrl,
        },
      }
    );

    if (!response.data.success) {
      throw new Error(response.data.message || 'API call failed');
    }

    console.log(`[ODOO-API] Call successful`);
    return response.data.result;
  } catch (error: any) {
    console.error(`[ODOO-API] Call error:`, error);

    // Check if session expired
    if (error.response?.status === 401) {
      clearOdooSession();
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }

    if (error.response?.data) {
      throw new Error(error.response.data.message || error.response.data.error || 'API call failed');
    }

    throw new Error(error.message || 'API call failed');
  }
}

/**
 * Logout from Odoo
 */
export async function logoutOdoo(): Promise<void> {
  clearOdooSession();
  console.log('[ODOO-API] Logged out');
}

/**
 * Check if authenticated
 */
export function isAuthenticated(): boolean {
  return checkOdooAuth();
}

export default {
  login: loginOdoo,
  call: callOdoo,
  logout: logoutOdoo,
  isAuthenticated,
};
