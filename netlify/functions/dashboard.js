const axios = require('axios');
const { serializeCookies } = require('./utils/session');

// CORS headers helper
const setCorsHeaders = () => ({
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, X-Odoo-Cookies, X-Odoo-Url',
});

// Helper to call Odoo model
async function callOdoo(baseUrl, cookies, model, method, args = [], kwargs = {}) {
  const callUrl = `${baseUrl}/web/dataset/call_kw`;
  const payload = {
    jsonrpc: '2.0',
    method: 'call',
    params: { model, method, args, kwargs }
  };

  const headers = {
    'Content-Type': 'application/json',
  };

  if (cookies && Object.keys(cookies).length > 0) {
    headers['Cookie'] = serializeCookies(cookies);
  }

  const response = await axios.post(callUrl, payload, {
    headers,
    timeout: 30000,
    validateStatus: () => true,
  });

  if (response.data && response.data.error) {
    throw new Error(response.data.error.data?.message || 'Odoo API error');
  }

  return response.data?.result;
}

// Netlify Function handler - Dashboard aggregation
exports.handler = async (event, context) => {
  // Handle OPTIONS preflight
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 204,
      headers: setCorsHeaders(),
      body: '',
    };
  }

  if (event.httpMethod !== 'GET') {
    return {
      statusCode: 405,
      headers: { 'Content-Type': 'application/json', ...setCorsHeaders() },
      body: JSON.stringify({ error: 'Method not allowed' }),
    };
  }

  try {
    const cookiesHeader = event.headers['x-odoo-cookies'];
    const baseUrl = event.headers['x-odoo-url'];

    if (!cookiesHeader || !baseUrl) {
      return {
        statusCode: 401,
        headers: { 'Content-Type': 'application/json', ...setCorsHeaders() },
        body: JSON.stringify({
          error: 'Not authenticated',
          message: 'X-Odoo-Cookies and X-Odoo-Url headers required.'
        }),
      };
    }

    const cookies = JSON.parse(cookiesHeader);

    console.log('[DASHBOARD] Fetching dashboard stats from Odoo');

    // Fetch data from multiple Odoo models in parallel
    const [stations, sessions, users, condominiums] = await Promise.all([
      // Charging stations
      callOdoo(baseUrl, cookies, 'charging.station', 'search_read', [[]], {
        fields: ['status', 'name']
      }).catch(() => []),

      // Active charging sessions
      callOdoo(baseUrl, cookies, 'wallbox.charging.session', 'search_count', [
        [['status', '=', 'in_corso']]
      ]).catch(() => 0),

      // Total users (partners)
      callOdoo(baseUrl, cookies, 'res.partner', 'search_count', [
        [['customer_rank', '>', 0]]
      ]).catch(() => 0),

      // Total condominiums
      callOdoo(baseUrl, cookies, 'condominium.condominium', 'search_count', [[]]).catch(() => 0),
    ]);

    // Calculate monthly kWh (from this month's sessions)
    const currentMonth = new Date().toISOString().slice(0, 7); // YYYY-MM
    const monthlySessions = await callOdoo(baseUrl, cookies, 'wallbox.charging.session', 'search_read', [
      [['start_time', '>=', `${currentMonth}-01`]]
    ], {
      fields: ['kwh_delivered']
    }).catch(() => []);

    const monthly_kwh = monthlySessions.reduce((sum, session) => sum + (session.kwh_delivered || 0), 0);

    // Count stations by status
    const stationsByStatus = {
      disponibile: 0,
      in_uso: 0,
      manutenzione: 0,
      offline: 0,
    };

    stations.forEach(station => {
      const status = station.status || 'offline';
      if (status.includes('disponibile') || status.includes('available')) {
        stationsByStatus.disponibile++;
      } else if (status.includes('uso') || status.includes('charging')) {
        stationsByStatus.in_uso++;
      } else if (status.includes('manutenzione') || status.includes('maintenance')) {
        stationsByStatus.manutenzione++;
      } else {
        stationsByStatus.offline++;
      }
    });

    const dashboardStats = {
      total_stations: stations.length,
      active_sessions: sessions,
      monthly_kwh: Math.round(monthly_kwh * 100) / 100,
      total_users: users,
      total_condominiums: condominiums,
      stations_by_status: stationsByStatus,
    };

    console.log('[DASHBOARD] Stats calculated:', dashboardStats);

    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json', ...setCorsHeaders() },
      body: JSON.stringify(dashboardStats),
    };

  } catch (error) {
    console.error('[DASHBOARD] Error:', error.message);

    let statusCode = 500;
    let errorResponse = {
      error: 'Internal server error',
      message: error.message
    };

    if (error.response?.status === 401) {
      statusCode = 401;
      errorResponse = {
        error: 'Session expired',
        message: 'Please log in again'
      };
    }

    return {
      statusCode,
      headers: { 'Content-Type': 'application/json', ...setCorsHeaders() },
      body: JSON.stringify(errorResponse),
    };
  }
};
