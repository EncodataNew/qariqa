# Quick Start Guide - Wallbox Dashboard

## 🚀 Running Locally

### Option 1: Direct Connection (No CORS Proxy)

If your Odoo instance has CORS enabled:

```bash
# 1. Ensure .env is configured
VITE_USE_CORS_PROXY=false
VITE_API_BASE_URL=http://localhost:8069

# 2. Install dependencies (if not already done)
npm install

# 3. Run the development server
npm run dev

# 4. Open browser
# http://localhost:8080
```

### Option 2: With CORS Proxy (Recommended)

To use the session-aware CORS proxy:

```bash
# 1. Update .env
VITE_USE_CORS_PROXY=true
VITE_CORS_PROXY_URL=http://localhost:3001/api/proxy
VITE_API_BASE_URL=http://localhost:8069

# 2. Install main app dependencies
npm install

# 3. Install proxy dependencies
cd cors-proxy
npm install
cd ..

# 4. Start the proxy server (in one terminal)
cd cors-proxy
npm start

# 5. Start the React app (in another terminal)
npm run dev

# 6. Open browser
# http://localhost:8080
```

## 📦 Production Deployment

### Deploy to Vercel

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login to Vercel
vercel login

# 3. Deploy
vercel

# 4. Set environment variables in Vercel Dashboard
VITE_API_BASE_URL=https://your-odoo.com
VITE_USE_CORS_PROXY=true
VITE_CORS_PROXY_URL=/api/proxy
```

The `vercel.json` configuration automatically:
- ✅ Deploys the React app
- ✅ Deploys the CORS proxy as a serverless function
- ✅ Configures routing

## 🔧 Configuration Reference

### Environment Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `VITE_API_BASE_URL` | Odoo backend URL | `http://localhost:8069` | ✅ Yes |
| `VITE_USE_CORS_PROXY` | Enable CORS proxy | `true` or `false` | ✅ Yes |
| `VITE_CORS_PROXY_URL` | Proxy endpoint | `/api/proxy` | When proxy enabled |
| `VITE_API_TIMEOUT` | Request timeout (ms) | `30000` | No (default: 30s) |

### When to Use CORS Proxy

| Scenario | Use Proxy? | Configuration |
|----------|-----------|---------------|
| Local development, Odoo without CORS | ✅ Yes | `VITE_USE_CORS_PROXY=true` |
| Local development, Odoo with CORS | ❌ No | `VITE_USE_CORS_PROXY=false` |
| Production (any Odoo) | ✅ Yes | `VITE_USE_CORS_PROXY=true` |
| Testing with mock API | ❌ No | `VITE_USE_CORS_PROXY=false` |

## 🧪 Testing the Setup

### 1. Check Dev Server

```bash
npm run dev
```

Expected output:
```
VITE v5.4.19 ready in XXX ms
➜ Local:   http://localhost:8080/
➜ Network: http://192.168.1.2:8080/
```

### 2. Check Proxy Server (if using)

```bash
cd cors-proxy
npm start
```

Expected output:
```
🚀 CORS Proxy server running on http://localhost:3001
📡 Proxy endpoint: http://localhost:3001/api/proxy
💚 Health check: http://localhost:3001/health
```

### 3. Test Login

1. Navigate to `http://localhost:8080`
2. You should see the login page
3. Enter Odoo credentials
4. Check browser DevTools Network tab:
   - Look for requests to `/api/proxy?url=...` (if using proxy)
   - Or direct requests to Odoo (if not using proxy)
   - Check for `X-Client-Session-Id` header in responses (with proxy)

### 4. Verify Session Persistence

1. Login successfully
2. Refresh the page
3. Should stay logged in (session persisted in localStorage)

## 🐛 Troubleshooting

### CORS Errors

**Symptoms:**
- Console shows "CORS policy blocked..."
- Network tab shows failed requests with CORS error

**Solutions:**
1. Enable CORS proxy: `VITE_USE_CORS_PROXY=true`
2. Verify proxy is running: `http://localhost:3001/health`
3. Check proxy URL in `.env` matches running proxy

### 401 Unauthorized

**Symptoms:**
- Cannot login
- All API requests return 401

**Solutions:**
1. Verify Odoo credentials
2. Check `VITE_API_BASE_URL` is correct
3. Verify Odoo backend is running
4. Check Odoo authentication is configured correctly

### Connection Refused

**Symptoms:**
- Network tab shows "ERR_CONNECTION_REFUSED"
- Cannot reach Odoo

**Solutions:**
1. Verify Odoo is running: `curl http://localhost:8069`
2. Check `VITE_API_BASE_URL` in `.env`
3. Ensure no firewall blocking connection

### Session Not Persisting

**Symptoms:**
- Must login after every page refresh
- Session lost frequently

**Solutions:**
1. Check browser localStorage for `odoo_proxy_session_id`
2. Verify cookies are being saved (DevTools > Application > Storage)
3. Check proxy session timeout (default 30 min)

### Build Errors

**Symptoms:**
- `npm run build` fails
- TypeScript errors

**Solutions:**
```bash
# Clear cache and rebuild
rm -rf node_modules dist
npm install
npm run build
```

## 📚 Documentation

- **CORS Proxy Setup**: See `CORS_PROXY_SETUP.md` for detailed proxy documentation
- **API Integration**: See `README_API_INTEGRATION.md` for API details
- **Main README**: See `README.claude` for project overview

## 🔐 Security Notes

### Development
- Use `http://localhost` for Odoo connection
- CORS proxy runs locally, no security concerns

### Production
- Always use HTTPS for Odoo: `https://your-odoo.com`
- Set secure environment variables in Vercel
- Never commit `.env` file to git
- Session timeout: 30 minutes (configurable in proxy.js)

## 📊 Features

- ✅ JWT Authentication with auto-refresh
- ✅ Session-aware CORS proxy
- ✅ Real-time data updates (React Query)
- ✅ Dashboard with statistics
- ✅ Condominium management
- ✅ Charging station monitoring
- ✅ User management
- ✅ Responsive UI (shadcn/ui + Tailwind)

## 🎯 Next Steps

After getting the app running:

1. **Configure Odoo Backend**
   - Install Wallbox module
   - Enable REST API v1 endpoints
   - Configure JWT authentication

2. **Test Core Features**
   - Login/logout
   - Dashboard statistics
   - Condominium CRUD operations
   - Charging station monitoring

3. **Production Deployment**
   - Deploy to Vercel
   - Configure environment variables
   - Test in production

4. **Optional Enhancements**
   - Set up CI/CD pipeline
   - Add monitoring and logging
   - Configure custom domain
   - Set up SSL certificates

## 💡 Tips

- Use browser DevTools Network tab to debug API calls
- Check Vercel Function Logs for proxy debugging in production
- Use React Query DevTools for cache inspection
- Keep `.env.example` updated with new variables

---

**Happy Coding!** 🎉

For questions or issues, check:
1. This Quick Start Guide
2. CORS_PROXY_SETUP.md
3. README_API_INTEGRATION.md
4. Browser console and Network tab
