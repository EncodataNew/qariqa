const axios = require('axios');
const { serializeCookies } = require('./utils/session');

// CORS headers helper
const setCorsHeaders = () => ({
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, X-Odoo-Cookies, X-Odoo-Url',
});

// Netlify Function handler - mimics Odoo's call_model method
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
    const { model, method, args, kwargs } = JSON.parse(event.body);

    // Get session cookies from headers (sent by frontend)
    const cookiesHeader = event.headers['x-odoo-cookies'];
    const baseUrl = event.headers['x-odoo-url'];

    // Validate required parameters
    if (!model || !method) {
      return {
        statusCode: 400,
        headers: { 'Content-Type': 'application/json', ...setCorsHeaders() },
        body: JSON.stringify({
          error: 'Missing required fields',
          required: ['model', 'method']
        }),
      };
    }

    if (!cookiesHeader || !baseUrl) {
      return {
        statusCode: 401,
        headers: { 'Content-Type': 'application/json', ...setCorsHeaders() },
        body: JSON.stringify({
          error: 'Not authenticated',
          message: 'X-Odoo-Cookies and X-Odoo-Url headers required. Please authenticate first.'
        }),
      };
    }

    // Parse cookies from JSON string
    let cookies;
    try {
      cookies = JSON.parse(cookiesHeader);
    } catch (err) {
      return {
        statusCode: 400,
        headers: { 'Content-Type': 'application/json', ...setCorsHeaders() },
        body: JSON.stringify({
          error: 'Invalid cookies format',
          message: 'X-Odoo-Cookies must be a valid JSON object'
        }),
      };
    }

    console.log(`[CALL] ${model}.${method} for Odoo at ${baseUrl}`);

    // Prepare Odoo API call
    const callUrl = `${baseUrl}/web/dataset/call_kw`;
    const payload = {
      jsonrpc: '2.0',
      method: 'call',
      params: {
        model: model,
        method: method,
        args: args || [],
        kwargs: kwargs || {}
      }
    };

    // Prepare headers with session cookies
    const headers = {
      'Content-Type': 'application/json',
    };

    if (cookies && Object.keys(cookies).length > 0) {
      headers['Cookie'] = serializeCookies(cookies);
      console.log(`[CALL] Using stored cookies`);
    }

    // Make the API call
    const response = await axios.post(callUrl, payload, {
      headers: headers,
      timeout: 30000,
      validateStatus: () => true,
    });

    console.log(`[CALL] Response status: ${response.status}`);

    // Check for errors
    if (response.data && response.data.error) {
      console.error(`[CALL] Odoo error:`, response.data.error);

      // Check if session expired
      const errorMsg = response.data.error.data?.message || '';
      if (errorMsg.toLowerCase().includes('session') && errorMsg.toLowerCase().includes('expired')) {
        return {
          statusCode: 401,
          headers: { 'Content-Type': 'application/json', ...setCorsHeaders() },
          body: JSON.stringify({
            error: 'Session expired',
            message: 'Please authenticate again',
            details: response.data.error
          }),
        };
      }

      return {
        statusCode: 400,
        headers: { 'Content-Type': 'application/json', ...setCorsHeaders() },
        body: JSON.stringify({
          error: 'Odoo API error',
          message: errorMsg || response.data.error.message,
          details: response.data.error
        }),
      };
    }

    // Return the result
    const result = response.data?.result;
    console.log(`[CALL] Success - returned ${Array.isArray(result) ? result.length : typeof result} result`);

    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json', ...setCorsHeaders() },
      body: JSON.stringify({
        success: true,
        result: result
      }),
    };

  } catch (error) {
    console.error('[CALL] Error:', error.message);

    let statusCode = 500;
    let errorResponse = {
      error: 'Internal server error',
      message: error.message
    };

    if (error.response) {
      statusCode = error.response.status;
      errorResponse = {
        error: 'API call failed',
        message: error.message,
        details: error.response.data
      };
    }

    return {
      statusCode,
      headers: { 'Content-Type': 'application/json', ...setCorsHeaders() },
      body: JSON.stringify(errorResponse),
    };
  }
};
