# Qariqa Project

Qariqa is an Odoo-based application with a React frontend for managing condominiums and related services.

## Project Structure

```
qariqa/
├── qariqa_frontend/        # React frontend application
│   ├── src/                # React source code
│   ├── public/             # Static assets
│   ├── index.html          # HTML entry point
│   ├── vite.config.ts      # Vite configuration
│   ├── package.json        # Frontend dependencies
│   └── [config files]      # TypeScript, ESLint, Tailwind configs
├── netlify/
│   └── functions/          # Netlify serverless functions
│       ├── odoo-auth.js    # Odoo authentication
│       ├── odoo-call.js    # Odoo API proxy
│       ├── proxy.js        # Legacy CORS proxy
│       └── dashboard.js    # Admin dashboard API
├── wallbox/                # Odoo backend modules
├── netlify.toml            # Netlify deployment configuration
└── package.json            # Root workspace configuration
```

## Quick Start

### Prerequisites

- Node.js 18 or higher
- npm

### Development

```bash
# Install dependencies (from root)
cd qariqa_frontend
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:8080`.

### Building for Production

```bash
# From root directory
npm run build

# Or from frontend directory
cd qariqa_frontend
npm run build
```

## Deployment

This project is configured for Netlify deployment:

1. **Frontend**: React app built from `qariqa_frontend/` directory
2. **Backend Functions**: Netlify Functions in `netlify/functions/` provide API proxying to Odoo

### Environment Variables

Configure these in Netlify:

- `VITE_API_BASE_URL` - URL of your Odoo instance (e.g., `https://your-odoo.example.com`)
- `VITE_ODOO_DATABASE` - Odoo database name
- `VITE_API_TIMEOUT` - API timeout in milliseconds (default: 30000)

## Architecture

### Frontend

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Components**: Radix UI with shadcn/ui
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query
- **Routing**: React Router

### Backend Integration

The app integrates with Odoo through Netlify Functions:

- `/api/odoo/auth` - Authentication endpoint
- `/api/odoo/call` - General API calls
- `/api/admin/dashboard` - Dashboard data aggregation

See [netlify/functions/README.md](netlify/functions/README.md) for API documentation.

## Documentation

- [CORS Setup](CORS_PROXY_SETUP.md) - Information about CORS handling
- [Deployment](DEPLOYMENT_SUMMARY.md) - Deployment strategies
- [API Integration](README_API_INTEGRATION.md) - Odoo API integration guide
- [Quick Start](QUICKSTART.md) - Getting started guide

## License

Proprietary
