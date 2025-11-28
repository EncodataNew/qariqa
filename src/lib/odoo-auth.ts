/**
 * Odoo authentication utilities for session management
 * Stores Odoo session cookies and metadata in localStorage
 */

// Storage keys
const ODOO_SESSION_KEY = 'odoo_session';
const ODOO_COOKIES_KEY = 'odoo_cookies';
const ODOO_BASE_URL_KEY = 'odoo_base_url';

// Odoo session interface
export interface OdooSession {
  sessionId: string;
  uid: number;
  username: string;
  database: string;
  baseUrl: string;
  serverVersion?: string;
  serverVersionInfo?: any;
}

/**
 * Store Odoo session and cookies
 */
export function setOdooSession(session: OdooSession, cookies: any): void {
  try {
    localStorage.setItem(ODOO_SESSION_KEY, JSON.stringify(session));
    localStorage.setItem(ODOO_COOKIES_KEY, JSON.stringify(cookies));
    localStorage.setItem(ODOO_BASE_URL_KEY, session.baseUrl);
    console.log('[ODOO-AUTH] Session stored:', { uid: session.uid, username: session.username });
  } catch (error) {
    console.error('Error storing Odoo session:', error);
  }
}

/**
 * Get stored Odoo session
 */
export function getOdooSession(): OdooSession | null {
  try {
    const sessionJson = localStorage.getItem(ODOO_SESSION_KEY);
    if (!sessionJson) {
      return null;
    }
    return JSON.parse(sessionJson);
  } catch (error) {
    console.error('Error retrieving Odoo session:', error);
    return null;
  }
}

/**
 * Get stored Odoo cookies
 */
export function getOdooCookies(): any | null {
  try {
    const cookiesJson = localStorage.getItem(ODOO_COOKIES_KEY);
    if (!cookiesJson) {
      return null;
    }
    return JSON.parse(cookiesJson);
  } catch (error) {
    console.error('Error retrieving Odoo cookies:', error);
    return null;
  }
}

/**
 * Get stored Odoo base URL
 */
export function getOdooBaseUrl(): string | null {
  try {
    return localStorage.getItem(ODOO_BASE_URL_KEY);
  } catch (error) {
    console.error('Error retrieving Odoo base URL:', error);
    return null;
  }
}

/**
 * Clear all Odoo authentication data
 */
export function clearOdooSession(): void {
  try {
    localStorage.removeItem(ODOO_SESSION_KEY);
    localStorage.removeItem(ODOO_COOKIES_KEY);
    localStorage.removeItem(ODOO_BASE_URL_KEY);
    console.log('[ODOO-AUTH] Session cleared');
  } catch (error) {
    console.error('Error clearing Odoo session:', error);
  }
}

/**
 * Check if user is authenticated with Odoo
 */
export function isOdooAuthenticated(): boolean {
  const session = getOdooSession();
  const cookies = getOdooCookies();
  return !!(session && cookies && session.uid);
}

/**
 * Get current user info from Odoo session
 */
export function getOdooUser() {
  const session = getOdooSession();
  if (!session) {
    return null;
  }

  return {
    id: session.uid,
    name: session.username,
    login: session.username,
    email: session.username, // Odoo doesn't provide email in session by default
  };
}
