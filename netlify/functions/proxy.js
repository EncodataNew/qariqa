// Netlify Function wrapper for CORS proxy
// This adapts the Vercel-style proxy to Netlify's function signature

const axios = require('axios');

// Session storage - maps client session IDs to Odoo cookies
const sessionStore = new Map();

// Session timeout: 30 minutes
const SESSION_TIMEOUT = 30 * 60 * 1000;

// Generate unique session ID
const generateSessionId = () => {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
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

// Netlify Function handler
exports.handler = async (event, context) => {
  // Handle preflight requests
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, X-Client-Session-Id, Authorization',
        'Access-Control-Expose-Headers': 'Set-Cookie, X-Client-Session-Id',
        'Access-Control-Allow-Credentials': 'true',
      },
      body: '',
    };
  }

  try {
    // Get target URL from query parameter
    const targetUrl = event.queryStringParameters?.url;

    if (!targetUrl) {
      return {
        statusCode: 400,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ error: 'Missing URL parameter' }),
      };
    }

    // Decode the target URL
    const decodedUrl = decodeURIComponent(targetUrl);

    // Get or create client session ID
    let clientSessionId = event.headers['x-client-session-id'];
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
    if (event.headers.authorization) {
      headers['Authorization'] = event.headers.authorization;
    }

    // Make request to Odoo
    console.log(`Proxying ${event.httpMethod} request to: ${decodedUrl}`);

    const axiosConfig = {
      method: event.httpMethod,
      url: decodedUrl,
      headers: headers,
      timeout: 30000,
    };

    // Add body for POST/PUT/PATCH requests
    if (['POST', 'PUT', 'PATCH'].includes(event.httpMethod) && event.body) {
      axiosConfig.data = JSON.parse(event.body);
    }

    const response = await axios(axiosConfig);

    // Capture and store new cookies from response
    if (response.headers['set-cookie']) {
      const newCookies = parseCookies(response.headers['set-cookie']);
      sessionData.cookies = { ...sessionData.cookies, ...newCookies };
      sessionStore.set(clientSessionId, sessionData);
      console.log(`Updated cookies for session: ${clientSessionId}`);
    }

    // Return response with session ID
    return {
      statusCode: response.status,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': 'true',
        'X-Client-Session-Id': clientSessionId,
      },
      body: JSON.stringify(response.data),
    };

  } catch (error) {
    console.error('Proxy error:', error.message);

    if (error.response) {
      // Forward error response from Odoo
      return {
        statusCode: error.response.status,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
        body: JSON.stringify(error.response.data || { error: error.message }),
      };
    }

    // Network or other errors
    return {
      statusCode: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
      body: JSON.stringify({
        error: 'Proxy error',
        message: error.message,
      }),
    };
  }
};
