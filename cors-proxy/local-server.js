// Local development server for CORS proxy
// Use this to test the proxy locally before deploying to Vercel

const express = require('express');
const cors = require('cors');
const proxyHandler = require('./api/proxy');

const app = express();
const PORT = 3001;

// Enable CORS
app.use(cors({
  origin: '*',
  credentials: true,
  exposedHeaders: ['X-Client-Session-Id']
}));

// Parse JSON bodies
app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', message: 'CORS Proxy is running' });
});

// Proxy endpoint
app.all('/api/proxy', async (req, res) => {
  try {
    await proxyHandler(req, res);
  } catch (error) {
    console.error('Proxy error:', error);
    res.status(500).json({ error: 'Internal proxy error' });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 CORS Proxy server running on http://localhost:${PORT}`);
  console.log(`📡 Proxy endpoint: http://localhost:${PORT}/api/proxy`);
  console.log(`💚 Health check: http://localhost:${PORT}/health`);
  console.log('\nReady to handle Odoo API requests!');
});
