import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import { getAccessToken, getRefreshToken, setTokens, clearTokens, isTokenExpired } from './auth';
import { loginOdoo, logoutOdoo, isAuthenticated as isOdooAuth } from './odoo-api';

// API Response Types
export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: {
    id: number;
    name: string;
    email: string;
    login: string;
  };
}

export interface RefreshTokenResponse {
  access_token: string;
}

// API Error Class
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// CORS Proxy configuration
const USE_CORS_PROXY = import.meta.env.VITE_USE_CORS_PROXY === 'true';
const CORS_PROXY_URL = import.meta.env.VITE_CORS_PROXY_URL;
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8069';

// Create Axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: USE_CORS_PROXY ? CORS_PROXY_URL : API_BASE_URL,
  timeout: Number(import.meta.env.VITE_API_TIMEOUT) || 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Flag to prevent multiple refresh attempts
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: any) => void;
}> = [];

// Process queued requests after token refresh
const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else if (token) {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

// Client session ID for CORS proxy
let clientSessionId: string | null = null;

// Initialize client session ID from localStorage
if (typeof window !== 'undefined') {
  clientSessionId = localStorage.getItem('odoo_proxy_session_id');
}

// Request interceptor - Add JWT token to requests
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // Handle CORS proxy URL transformation
    if (USE_CORS_PROXY && config.url) {
      // Build the full target URL
      const targetUrl = config.url.startsWith('http')
        ? config.url
        : `${API_BASE_URL}${config.url}`;

      // Replace the URL with proxy URL + encoded target
      config.url = `?url=${encodeURIComponent(targetUrl)}`;

      // Add client session ID header if available
      if (clientSessionId) {
        config.headers['X-Client-Session-Id'] = clientSessionId;
      }
    }

    // Skip token injection for auth endpoints
    if (config.url?.includes('/auth/login') || config.url?.includes('/auth/refresh')) {
      return config;
    }

    const token = getAccessToken();

    if (token) {
      // Check if token is expired (with 1 minute buffer)
      if (isTokenExpired(token, 60)) {
        // Token is expired or will expire soon, try to refresh
        try {
          const newToken = await refreshAccessToken();
          config.headers.Authorization = `Bearer ${newToken}`;
        } catch (error) {
          // If refresh fails, clear tokens and proceed without auth
          clearTokens();
          // Redirect to login will be handled by the response interceptor
        }
      } else {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle token refresh on 401
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Capture client session ID from CORS proxy response
    if (USE_CORS_PROXY && typeof window !== 'undefined') {
      const sessionId = response.headers['x-client-session-id'];
      if (sessionId) {
        clientSessionId = sessionId;
        localStorage.setItem('odoo_proxy_session_id', sessionId);
      }
    }

    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Handle 401 Unauthorized - Token expired or invalid
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      if (isRefreshing) {
        // If already refreshing, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return apiClient(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const newToken = await refreshAccessToken();
        processQueue(null, newToken);
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        clearTokens();

        // Redirect to login page
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }

        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // Handle other errors
    const apiError = new ApiError(
      error.response?.data?.error || error.message || 'An error occurred',
      error.response?.status,
      error.response?.data
    );

    return Promise.reject(apiError);
  }
);

// Refresh access token using refresh token
async function refreshAccessToken(): Promise<string> {
  const refreshToken = getRefreshToken();

  if (!refreshToken) {
    throw new Error('No refresh token available');
  }

  try {
    // Use the main apiClient to benefit from CORS proxy if enabled
    const response = await apiClient.post<RefreshTokenResponse>(
      '/v1/auth/refresh',
      { refresh_token: refreshToken }
    );

    const { access_token } = response.data;

    // Update only the access token
    setTokens(access_token, refreshToken);

    return access_token;
  } catch (error) {
    clearTokens();
    throw new Error('Failed to refresh token');
  }
}

// API Methods

/**
 * Login user using Odoo authentication
 */
export async function login(username: string, password: string): Promise<LoginResponse> {
  try {
    // Get Odoo URL and database from environment variables
    const odooUrl = import.meta.env.VITE_API_BASE_URL || 'https://qariqa-staging.qariqa.com';
    const odooDatabase = import.meta.env.VITE_ODOO_DATABASE || 'main';

    console.log('%c📊 Odoo Configuration', 'background: #9C27B0; color: white; font-weight: bold; padding: 4px;');
    console.log(`  URL: ${odooUrl}`);
    console.log(`  Database: ${odooDatabase} ${import.meta.env.VITE_ODOO_DATABASE ? '(from env)' : '⚠️ (using fallback - env var not set!)'}`);
    console.log(`[API] Logging in to Odoo at ${odooUrl}, database: ${odooDatabase}`);

    // Use the new Odoo API
    const response = await loginOdoo(odooUrl, odooDatabase, username, password);

    // The response is already in the format we need
    return response;
  } catch (error: any) {
    console.error('Login error:', error);
    throw new ApiError(error.message || 'Login failed. Please check your credentials.');
  }
}

/**
 * Logout user and clear Odoo session
 */
export async function logout(): Promise<void> {
  try {
    await logoutOdoo();
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    clearTokens(); // Clear JWT tokens too (for backwards compatibility)
  }
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  // Check Odoo authentication first
  if (isOdooAuth()) {
    return true;
  }

  // Fallback to JWT token check (for backwards compatibility)
  const token = getAccessToken();
  if (!token) return false;

  // Check if token is expired
  return !isTokenExpired(token);
}

export default apiClient;
