/**
 * Shared session utilities for Odoo API endpoints
 * Adapted from gantt-planner for Netlify Functions
 */

// Helper to parse cookies from Set-Cookie header
function parseCookies(setCookieHeaders) {
  if (!setCookieHeaders) return {};

  const cookies = {};
  const headerArray = Array.isArray(setCookieHeaders) ? setCookieHeaders : [setCookieHeaders];

  headerArray.forEach(cookieStr => {
    const parts = cookieStr.split(';')[0].split('=');
    if (parts.length === 2) {
      cookies[parts[0].trim()] = parts[1].trim();
    }
  });

  return cookies;
}

// Helper to serialize cookies for request
function serializeCookies(cookies) {
  return Object.entries(cookies)
    .map(([key, value]) => `${key}=${value}`)
    .join('; ');
}

module.exports = {
  parseCookies,
  serializeCookies
};
