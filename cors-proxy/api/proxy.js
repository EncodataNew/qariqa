// Session-aware CORS proxy for Odoo integration
// This proxy maintains Odoo session cookies server-side to avoid CORS issues

const axios = require('axios');

// Session storage - maps client session IDs to Odoo cookies
const sessionStore = new Map();

// Session timeout: 30 minutes
const SESSION_TIMEOUT = 30 * 60 * 1000;

// Generate unique session ID
const generateSessionId = () => {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

// Set CORS headers
const setCorsHeaders = (res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Client-Session-Id, Authorization');
  res.setHeader('Access-Control-Expose-Headers', 'Set-Cookie, X-Client-Session-Id');
  res.setHeader('Access-Control-Allow-Credentials', 'true');
};

// Parse cookies from Set-Cookie headers
const parseCookies = (setCookieHeaders) => {
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
};

// Serialize cookies for Cookie header
const serializeCookies = (cookies) => {
  return Object.entries(cookies)
    .map(([key, value]) => `${key}=${value}`)
    .join('; ');
};

// Clean up expired sessions
const cleanupExpiredSessions = () => {
  const now = Date.now();
  for (const [sessionId, session] of sessionStore.entries()) {
    if (now - session.lastAccess > SESSION_TIMEOUT) {
      sessionStore.delete(sessionId);
      console.log(`Cleaned up expired session: ${sessionId}`);
    }
  }
};

// Run cleanup every 5 minutes
setInterval(cleanupExpiredSessions, 5 * 60 * 1000);

// Main proxy handler
module.exports = async (req, res) => {
  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    setCorsHeaders(res);
    return res.status(200).end();
  }

  setCorsHeaders(res);

  try {
    // Get target URL from query parameter
    const targetUrl = req.query.url;

    if (!targetUrl) {
      return res.status(400).json({ error: 'Missing URL parameter' });
    }

    // Decode the target URL
    const decodedUrl = decodeURIComponent(targetUrl);

    // Get or create client session ID
    let clientSessionId = req.headers['x-client-session-id'];
    let sessionData = null;

    if (clientSessionId && sessionStore.has(clientSessionId)) {
      sessionData = sessionStore.get(clientSessionId);
      sessionData.lastAccess = Date.now();
    } else {
      // Create new session
      clientSessionId = generateSessionId();
      sessionData = {
        cookies: {},
        lastAccess: Date.now(),
      };
      sessionStore.set(clientSessionId, sessionData);
      console.log(`Created new session: ${clientSessionId}`);
    }

    // Prepare request headers
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    // Add stored cookies to request if any
    if (sessionData.cookies && Object.keys(sessionData.cookies).length > 0) {
      headers['Cookie'] = serializeCookies(sessionData.cookies);
    }

    // Forward Authorization header if present (for JWT)
    if (req.headers.authorization) {
      headers['Authorization'] = req.headers.authorization;
    }

    // Make request to Odoo
    console.log(`Proxying ${req.method} request to: ${decodedUrl}`);

    const axiosConfig = {
      method: req.method,
      url: decodedUrl,
      headers: headers,
      timeout: 30000,
    };

    // Add body for POST/PUT/PATCH requests
    if (['POST', 'PUT', 'PATCH'].includes(req.method) && req.body) {
      axiosConfig.data = req.body;
    }

    const response = await axios(axiosConfig);

    // Capture and store new cookies from response
    if (response.headers['set-cookie']) {
      const newCookies = parseCookies(response.headers['set-cookie']);
      sessionData.cookies = { ...sessionData.cookies, ...newCookies };
      sessionStore.set(clientSessionId, sessionData);
      console.log(`Updated cookies for session: ${clientSessionId}`);
    }

    // Send session ID back to client
    res.setHeader('X-Client-Session-Id', clientSessionId);

    // Forward the response
    return res.status(response.status).json(response.data);

  } catch (error) {
    console.error('Proxy error:', error.message);

    if (error.response) {
      // Forward error response from Odoo
      return res.status(error.response.status).json(
        error.response.data || { error: error.message }
      );
    }

    // Network or other errors
    return res.status(500).json({
      error: 'Proxy error',
      message: error.message,
    });
  }
};
