/**
 * Authentication utilities for token management
 */

// Storage keys
const ACCESS_TOKEN_KEY = 'wallbox_access_token';
const REFRESH_TOKEN_KEY = 'wallbox_refresh_token';
const USER_KEY = 'wallbox_user';
const TOKEN_EXPIRY_KEY = 'wallbox_token_expiry';

// User interface
export interface User {
  id: number;
  name: string;
  email: string;
  login: string;
}

/**
 * Decode JWT token payload
 */
function decodeToken(token: string): any {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Error decoding token:', error);
    return null;
  }
}

/**
 * Get token expiration time in milliseconds
 */
function getTokenExpiration(token: string): number | null {
  const payload = decodeToken(token);
  if (!payload || !payload.exp) {
    return null;
  }
  // JWT exp is in seconds, convert to milliseconds
  return payload.exp * 1000;
}

/**
 * Check if token is expired
 * @param token JWT token
 * @param bufferSeconds Buffer time in seconds to consider token as expired before actual expiry
 */
export function isTokenExpired(token: string, bufferSeconds: number = 0): boolean {
  const expiry = getTokenExpiration(token);
  if (!expiry) {
    return true;
  }

  const now = Date.now();
  const buffer = bufferSeconds * 1000;

  return now >= expiry - buffer;
}

/**
 * Store authentication tokens and user data
 */
export function setTokens(
  accessToken: string,
  refreshToken: string,
  user?: User
): void {
  try {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);

    // Store token expiry time
    const expiry = getTokenExpiration(accessToken);
    if (expiry) {
      localStorage.setItem(TOKEN_EXPIRY_KEY, expiry.toString());
    }

    if (user) {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    }
  } catch (error) {
    console.error('Error storing tokens:', error);
  }
}

/**
 * Get access token from storage
 */
export function getAccessToken(): string | null {
  try {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  } catch (error) {
    console.error('Error retrieving access token:', error);
    return null;
  }
}

/**
 * Get refresh token from storage
 */
export function getRefreshToken(): string | null {
  try {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  } catch (error) {
    console.error('Error retrieving refresh token:', error);
    return null;
  }
}

/**
 * Get stored user data
 */
export function getStoredUser(): User | null {
  try {
    const userJson = localStorage.getItem(USER_KEY);
    if (!userJson) {
      return null;
    }
    return JSON.parse(userJson);
  } catch (error) {
    console.error('Error retrieving user data:', error);
    return null;
  }
}

/**
 * Get token expiry time from storage
 */
export function getTokenExpiry(): number | null {
  try {
    const expiryStr = localStorage.getItem(TOKEN_EXPIRY_KEY);
    if (!expiryStr) {
      return null;
    }
    return parseInt(expiryStr, 10);
  } catch (error) {
    console.error('Error retrieving token expiry:', error);
    return null;
  }
}

/**
 * Clear all authentication data
 */
export function clearTokens(): void {
  try {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem(TOKEN_EXPIRY_KEY);
  } catch (error) {
    console.error('Error clearing tokens:', error);
  }
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  const token = getAccessToken();
  if (!token) {
    return false;
  }

  return !isTokenExpired(token);
}

/**
 * Get time until token expires in milliseconds
 */
export function getTimeUntilExpiry(): number | null {
  const token = getAccessToken();
  if (!token) {
    return null;
  }

  const expiry = getTokenExpiration(token);
  if (!expiry) {
    return null;
  }

  const timeLeft = expiry - Date.now();
  return timeLeft > 0 ? timeLeft : 0;
}

/**
 * Format time remaining as human-readable string
 */
export function formatTimeRemaining(milliseconds: number): string {
  const seconds = Math.floor(milliseconds / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);

  if (hours > 0) {
    return `${hours}h ${minutes % 60}m`;
  } else if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`;
  } else {
    return `${seconds}s`;
  }
}
