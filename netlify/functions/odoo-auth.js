const axios = require('axios');
const { parseCookies } = require('./utils/session');

// CORS headers helper
const setCorsHeaders = () => ({
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
});

// Netlify Function handler
exports.handler = async (event, context) => {
  // Handle OPTIONS preflight
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 204,
      headers: setCorsHeaders(),
      body: '',
    };
  }

  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers: { 'Content-Type': 'application/json', ...setCorsHeaders() },
      body: JSON.stringify({ error: 'Method not allowed' }),
    };
  }

  try {
    const { url, database, username, password } = JSON.parse(event.body);

    if (!url || !database || !username || !password) {
      return {
        statusCode: 400,
        headers: { 'Content-Type': 'application/json', ...setCorsHeaders() },
        body: JSON.stringify({
          error: 'Missing required fields',
          required: ['url', 'database', 'username', 'password']
        }),
      };
    }

    // Clean URL
    const baseUrl = url.replace(/\/$/, '');
    const authUrl = `${baseUrl}/web/session/authenticate`;

    // Prepare authentication payload
    const payload = {
      jsonrpc: '2.0',
      method: 'call',
      params: {
        db: database,
        login: username,
        password: password,
      }
    };

    console.log(`[AUTH] Authenticating to ${authUrl} as ${username}`);

    // Make authentication request
    const response = await axios.post(authUrl, payload, {
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
      validateStatus: () => true, // Don't throw on any status
    });

    console.log(`[AUTH] Response status: ${response.status}`);

    // Check for errors in response
    if (response.data && response.data.error) {
      console.error('[AUTH] Odoo returned error:', response.data.error);
      return {
        statusCode: 401,
        headers: { 'Content-Type': 'application/json', ...setCorsHeaders() },
        body: JSON.stringify({
          error: 'Authentication failed',
          message: response.data.error.data?.message || 'Invalid credentials',
          details: response.data.error
        }),
      };
    }

    // Extract authentication result
    const result = response.data?.result;
    if (!result || !result.uid) {
      console.error('[AUTH] No UID in response:', response.data);
      return {
        statusCode: 401,
        headers: { 'Content-Type': 'application/json', ...setCorsHeaders() },
        body: JSON.stringify({
          error: 'Authentication failed',
          message: 'No user ID returned from Odoo'
        }),
      };
    }

    // Parse session cookies from Odoo response
    const setCookieHeaders = response.headers['set-cookie'];
    const cookies = parseCookies(setCookieHeaders);

    console.log(`[AUTH] Received cookies:`, Object.keys(cookies));
    console.log(`[AUTH] Authenticated uid=${result.uid}, session_id=${result.session_id}`);

    // Return cookies to frontend (frontend will store in localStorage)
    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json', ...setCorsHeaders() },
      body: JSON.stringify({
        success: true,
        sessionId: result.session_id,
        uid: result.uid,
        username: result.username || username,
        database: result.db || database,
        baseUrl: baseUrl,
        cookies: cookies,
        serverVersion: result.server_version,
        serverVersionInfo: result.server_version_info
      }),
    };

  } catch (error) {
    console.error('[AUTH] Error:', error.message);

    let statusCode = 500;
    let errorResponse = {
      error: 'Internal server error',
      message: error.message
    };

    if (error.response) {
      statusCode = error.response.status;
      errorResponse = {
        error: 'Authentication request failed',
        message: error.message,
        details: error.response.data
      };
    } else if (error.code === 'ECONNREFUSED') {
      statusCode = 503;
      errorResponse = {
        error: 'Cannot connect to Odoo server',
        message: 'Connection refused. Check if Odoo URL is correct and accessible.'
      };
    } else if (error.code === 'ETIMEDOUT') {
      statusCode = 504;
      errorResponse = {
        error: 'Connection timeout',
        message: 'Odoo server did not respond in time'
      };
    }

    return {
      statusCode,
      headers: { 'Content-Type': 'application/json', ...setCorsHeaders() },
      body: JSON.stringify(errorResponse),
    };
  }
};
