// Railway deployment server
// Serves both the React app and CORS proxy

const express = require('express');
const path = require('path');
const cors = require('cors');
const proxyHandler = require('./cors-proxy/api/proxy');

const app = express();
const PORT = process.env.PORT || 3000;

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
  res.json({
    status: 'ok',
    message: 'Wallbox Dashboard is running',
    timestamp: new Date().toISOString()
  });
});

// API Proxy endpoint
app.all('/api/proxy', async (req, res) => {
  try {
    await proxyHandler(req, res);
  } catch (error) {
    console.error('Proxy error:', error);
    res.status(500).json({ error: 'Internal proxy error' });
  }
});

// Serve static files from React build
app.use(express.static(path.join(__dirname, 'dist')));

// Handle client-side routing - send all other requests to index.html
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Wallbox Dashboard running on port ${PORT}`);
  console.log(`📡 Proxy endpoint: http://localhost:${PORT}/api/proxy`);
  console.log(`💚 Health check: http://localhost:${PORT}/health`);
  console.log(`🌐 Frontend: http://localhost:${PORT}`);
});
