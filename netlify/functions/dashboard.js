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
    console.log('[DASHBOARD] Base URL:', baseUrl);
    console.log('[DASHBOARD] User ID:', cookies.uid);

    // Fetch data from multiple Odoo models in parallel
    const [stations, activeSessions, users, condominiums, buildings, parkingSpaces, pendingInstallations, allSessions] = await Promise.all([
      // Charging stations
      callOdoo(baseUrl, cookies, 'charging.station', 'search_read', [[]], {
        fields: ['status', 'name', 'installation_date']
      }).catch(() => []),

      // Active charging sessions (Started status)
      callOdoo(baseUrl, cookies, 'wallbox.charging.session', 'search_count', [
        [['status', '=', 'Started']]
      ]).catch(() => 0),

      // Total users (partners)
      callOdoo(baseUrl, cookies, 'res.partner', 'search_count', [
        [['customer_rank', '>', 0]]
      ]).catch(() => 0),

      // Total condominiums
      callOdoo(baseUrl, cookies, 'condominium.condominium', 'search_count', [[]]).catch(() => 0),

      // Total buildings
      callOdoo(baseUrl, cookies, 'building.building', 'search_count', [[]]).catch(() => 0),

      // Total parking spaces
      callOdoo(baseUrl, cookies, 'parking.space', 'search_count', [[]]).catch(() => 0),

      // Pending installations (wallbox.order with state != 'done')
      callOdoo(baseUrl, cookies, 'wallbox.order', 'search_count', [
        [['state', '!=', 'done']]
      ]).catch(() => 0),

      // All sessions for revenue and charts
      callOdoo(baseUrl, cookies, 'wallbox.charging.session', 'search_read', [[]], {
        fields: ['cost', 'total_energy', 'start_time', 'customer_id', 'status'],
        limit: 1000,
        order: 'start_time desc'
      }).catch(() => []),
    ]);

    console.log('[DASHBOARD] Fetched data counts:');
    console.log('  - Stations:', stations?.length || 0);
    console.log('  - Active sessions:', activeSessions);
    console.log('  - Users:', users);
    console.log('  - Condominiums:', condominiums);
    console.log('  - Buildings:', buildings);
    console.log('  - Parking spaces:', parkingSpaces);
    console.log('  - Pending installations:', pendingInstallations);
    console.log('  - All sessions:', allSessions?.length || 0);

    if (allSessions && allSessions.length > 0) {
      console.log('[DASHBOARD] Sample session:', JSON.stringify(allSessions[0], null, 2));
    }

    // Calculate monthly kWh and revenue
    const currentMonth = new Date().toISOString().slice(0, 7); // YYYY-MM
    const monthlySessions = allSessions.filter(s => s.start_time && s.start_time.startsWith(currentMonth));
    const monthly_kwh = monthlySessions.reduce((sum, session) => sum + ((session.total_energy || 0) / 1000), 0);
    const monthly_revenue = allSessions.reduce((sum, session) => sum + (session.cost || 0), 0);

    // Count stations by status
    const stationsByStatus = {
      Available: 0,
      Charging: 0,
      Unavailable: 0,
      Faulted: 0,
    };

    stations.forEach(station => {
      const status = station.status || 'Unavailable';
      if (stationsByStatus[status] !== undefined) {
        stationsByStatus[status]++;
      } else {
        stationsByStatus.Unavailable++;
      }
    });

    // Calculate revenue chart data (last 7 days)
    const last7Days = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      const daySessions = allSessions.filter(s => s.start_time && s.start_time.startsWith(dateStr));
      const dayRevenue = daySessions.reduce((sum, s) => sum + (s.cost || 0), 0);
      last7Days.push({
        date: dateStr,
        revenue: Math.round(dayRevenue * 100) / 100
      });
    }

    console.log('[DASHBOARD] Revenue chart (last 7 days):', JSON.stringify(last7Days, null, 2));

    // Energy consumption data (last 30 days)
    const last30Days = [];
    for (let i = 29; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      const daySessions = allSessions.filter(s => s.start_time && s.start_time.startsWith(dateStr));
      const dayEnergy = daySessions.reduce((sum, s) => sum + ((s.total_energy || 0) / 1000), 0);
      last30Days.push({
        date: dateStr,
        energy: Math.round(dayEnergy * 100) / 100
      });
    }

    console.log('[DASHBOARD] Energy consumption chart sample (first 5 days):', JSON.stringify(last30Days.slice(0, 5), null, 2));
    console.log('[DASHBOARD] Stations by status:', JSON.stringify(stationsByStatus, null, 2));

    // Get current user info to filter sessions
    const currentUser = await callOdoo(baseUrl, cookies, 'res.users', 'search_read', [
      [['id', '=', cookies.uid || 0]]
    ], {
      fields: ['partner_id']
    }).catch(() => []);

    const userPartnerId = currentUser[0]?.partner_id?.[0];

    // My charging requests (sessions by current user)
    const myRequests = userPartnerId
      ? allSessions.filter(s => s.customer_id?.[0] === userPartnerId).length
      : 0;

    // Guest charging requests (assuming guests are those without regular customer status)
    const guestSessions = allSessions.filter(s => s.status === 'Started' || s.status === 'Ended');
    const guestRequestsCount = guestSessions.length;
    const guestRequestsCost = guestSessions.reduce((sum, s) => sum + (s.cost || 0), 0);

    // Distribution data
    const distributionData = [
      { name: 'Condominium', value: condominiums },
      { name: 'Building', value: buildings },
      { name: 'Parking Space', value: parkingSpaces }
    ];

    const dashboardStats = {
      total_stations: stations.length,
      active_sessions: activeSessions,
      monthly_kwh: Math.round(monthly_kwh * 100) / 100,
      total_users: users,
      total_condominiums: condominiums,
      pending_installations: pendingInstallations,
      revenue: Math.round(monthly_revenue * 100) / 100,
      my_charging_requests: myRequests,
      guest_charging_requests: guestRequestsCount,
      guest_charging_cost: Math.round(guestRequestsCost * 100) / 100,
      stations_by_status: stationsByStatus,
      revenue_chart: last7Days,
      energy_consumption_chart: last30Days,
      distribution_data: distributionData,
      installation_status: {
        completed: stations.filter(s => s.installation_date).length,
        pending: pendingInstallations
      }
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
