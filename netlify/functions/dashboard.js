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

    // Calculate revenue chart data - SHOW ALL DATA
    let revenueChartData = [];

    try {
      if (allSessions && allSessions.length > 0) {
        // Group sessions by date
        const sessionsByDate = {};
        allSessions.forEach(session => {
          try {
            if (session.start_time) {
              const dateStr = String(session.start_time).split(' ')[0]; // Handle both 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS' formats
              if (!sessionsByDate[dateStr]) {
                sessionsByDate[dateStr] = 0;
              }
              sessionsByDate[dateStr] += (session.cost || 0);
            }
          } catch (err) {
            console.error('[DASHBOARD] Error processing session for revenue:', err.message);
          }
        });

        // Convert to array and sort by date - SHOW ALL DATES
        revenueChartData = Object.entries(sessionsByDate)
          .map(([date, revenue]) => ({
            date,
            revenue: Math.round(revenue * 100) / 100
          }))
          .sort((a, b) => a.date.localeCompare(b.date));

        console.log('[DASHBOARD] Revenue chart - Total dates with data:', revenueChartData.length);
      } else {
        console.log('[DASHBOARD] No sessions found for revenue chart');
      }

      console.log('[DASHBOARD] Revenue chart data (first 5):', JSON.stringify(revenueChartData.slice(0, 5), null, 2));
      console.log('[DASHBOARD] Revenue chart data (last 5):', JSON.stringify(revenueChartData.slice(-5), null, 2));
    } catch (error) {
      console.error('[DASHBOARD] Error calculating revenue chart:', error.message);
      revenueChartData = [];
    }

    // Energy consumption data - SHOW ALL DATA
    let energyChartData = [];

    try {
      if (allSessions && allSessions.length > 0) {
        // Group sessions by date
        const energyByDate = {};
        allSessions.forEach(session => {
          try {
            if (session.start_time && session.total_energy) {
              const dateStr = String(session.start_time).split(' ')[0];
              if (!energyByDate[dateStr]) {
                energyByDate[dateStr] = 0;
              }
              energyByDate[dateStr] += (session.total_energy || 0) / 1000; // Convert Wh to kWh
            }
          } catch (err) {
            console.error('[DASHBOARD] Error processing session for energy:', err.message);
          }
        });

        // Convert to array and sort by date - SHOW ALL DATES
        energyChartData = Object.entries(energyByDate)
          .map(([date, energy]) => ({
            date,
            energy: Math.round(energy * 100) / 100
          }))
          .sort((a, b) => a.date.localeCompare(b.date));

        console.log('[DASHBOARD] Energy chart - Total dates with data:', energyChartData.length);
      } else {
        console.log('[DASHBOARD] No sessions found for energy chart');
      }

      console.log('[DASHBOARD] Energy consumption chart data (first 5):', JSON.stringify(energyChartData.slice(0, 5), null, 2));
      console.log('[DASHBOARD] Energy consumption chart data (last 5):', JSON.stringify(energyChartData.slice(-5), null, 2));
      console.log('[DASHBOARD] Stations by status:', JSON.stringify(stationsByStatus, null, 2));
    } catch (error) {
      console.error('[DASHBOARD] Error calculating energy chart:', error.message);
      energyChartData = [];
    }

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
    let distributionData = [];
    try {
      distributionData = [
        { name: 'Condominium', value: condominiums || 0 },
        { name: 'Building', value: buildings || 0 },
        { name: 'Parking Space', value: parkingSpaces || 0 }
      ];
      console.log('[DASHBOARD] Distribution data:', JSON.stringify(distributionData, null, 2));
    } catch (error) {
      console.error('[DASHBOARD] Error creating distribution data:', error.message);
      distributionData = [];
    }

    // Installation status
    let installationStatus = { completed: 0, pending: 0 };
    try {
      const completedInstallations = (stations || []).filter(s => s.installation_date).length;
      installationStatus = {
        completed: completedInstallations,
        pending: pendingInstallations || 0
      };
      console.log('[DASHBOARD] Installation status:', JSON.stringify(installationStatus, null, 2));
    } catch (error) {
      console.error('[DASHBOARD] Error creating installation status:', error.message);
    }

    const dashboardStats = {
      total_stations: (stations || []).length,
      active_sessions: activeSessions || 0,
      monthly_kwh: Math.round(monthly_kwh * 100) / 100,
      total_users: users || 0,
      total_condominiums: condominiums || 0,
      pending_installations: pendingInstallations || 0,
      revenue: Math.round(monthly_revenue * 100) / 100,
      my_charging_requests: myRequests || 0,
      guest_charging_requests: guestRequestsCount || 0,
      guest_charging_cost: Math.round(guestRequestsCost * 100) / 100,
      stations_by_status: stationsByStatus,
      revenue_chart: revenueChartData || [],
      energy_consumption_chart: energyChartData || [],
      distribution_data: distributionData || [],
      installation_status: installationStatus
    };

    console.log('[DASHBOARD] FINAL Stats object to return:');
    console.log('  - total_stations:', dashboardStats.total_stations);
    console.log('  - revenue_chart length:', dashboardStats.revenue_chart?.length);
    console.log('  - energy_consumption_chart length:', dashboardStats.energy_consumption_chart?.length);
    console.log('  - distribution_data length:', dashboardStats.distribution_data?.length);
    console.log('[DASHBOARD] Full stats:', JSON.stringify(dashboardStats, null, 2));

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
