# CORS Proxy Setup for Odoo Integration

## Overview

This project includes a **session-aware CORS proxy** to handle Odoo API requests. The proxy solves CORS (Cross-Origin Resource Sharing) issues that occur when connecting a browser-based React app to an Odoo backend.

## Why Do We Need This?

When a browser-based app tries to connect directly to Odoo:

1. **CORS Restrictions**: Browsers block cross-origin requests due to security policies
2. **Cookie Issues**: Public CORS proxies strip session cookies, breaking Odoo authentication
3. **Session Management**: Odoo relies on session cookies that must persist across requests

## How Our Solution Works

```
┌──────────┐    ┌────────────────┐    ┌──────────┐
│ Browser  │───>│ Session-Aware  │───>│  Odoo    │
│          │<───│ CORS Proxy     │<───│ Backend  │
└──────────┘    └────────────────┘    └──────────┘
                        │
                 Session Store
                 (Maps Client → Cookies)
```

### Key Features

1. **Session-Aware**: Maintains Odoo session cookies server-side
2. **Client Tracking**: Uses `X-Client-Session-Id` header to map clients to sessions
3. **Transparent**: Works seamlessly with existing JWT authentication
4. **Persistent**: Sessions stored in localStorage, survive page reloads
5. **Auto-Cleanup**: Removes expired sessions after 30 minutes

## Project Structure

```
qariqa/
├── cors-proxy/
│   ├── api/
│   │   └── proxy.js           # Session-aware proxy handler
│   └── package.json           # Proxy dependencies
│
├── src/
│   └── lib/
│       └── api.ts             # Updated API client with session management
│
├── .env                       # Environment configuration
├── .env.example               # Environment template
└── vercel.json                # Deployment configuration
```

## Configuration

### Environment Variables

Update your `.env` file:

```env
# Odoo Backend Configuration
VITE_API_BASE_URL=http://localhost:8069

# CORS Proxy Configuration
VITE_USE_CORS_PROXY=false          # Set to 'true' to enable proxy
VITE_CORS_PROXY_URL=/api/proxy     # Proxy endpoint

# API Settings
VITE_API_TIMEOUT=30000
VITE_TOKEN_REFRESH_INTERVAL=300000
```

### When to Enable CORS Proxy

- **Development with CORS issues**: Set `VITE_USE_CORS_PROXY=true`
- **Production deployment**: Always use `VITE_USE_CORS_PROXY=true`
- **Local Odoo with CORS enabled**: Can use `VITE_USE_CORS_PROXY=false`

## Local Testing

### Option 1: Without CORS Proxy (Direct Connection)

If your Odoo instance has CORS headers configured:

```env
VITE_USE_CORS_PROXY=false
```

Your Odoo controller must include:
```python
@http.route('/v1/auth/login', methods=['POST'], cors='*', csrf=False, auth='public')
def login(self):
    # ... login logic
```

### Option 2: With CORS Proxy (Recommended)

Enable the proxy to avoid CORS issues:

```env
VITE_USE_CORS_PROXY=true
VITE_CORS_PROXY_URL=/api/proxy
```

The app will use Vite's dev server proxy. Configure in `vite.config.ts`:

```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api/proxy': {
        target: 'http://localhost:3000', // Local proxy server
        changeOrigin: true,
      }
    }
  }
});
```

Then run the proxy locally:

```bash
cd cors-proxy
npm install
node api/proxy.js
```

## Production Deployment (Vercel)

### Step 1: Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel
```

### Step 2: Configure Environment Variables in Vercel

Go to your Vercel project settings and add:

```
VITE_API_BASE_URL=https://your-odoo-instance.com
VITE_USE_CORS_PROXY=true
VITE_CORS_PROXY_URL=/api/proxy
```

### Step 3: Verify Deployment

The `vercel.json` configuration automatically:
- Builds your React app
- Deploys the CORS proxy as a serverless function
- Routes `/api/proxy` to the proxy handler
- Serves your React app for all other routes

## How It Works Internally

### 1. Initial Request (Login)

```
Browser                         Proxy                          Odoo
   │                              │                              │
   │──(1) POST /api/proxy?url=...─>│                              │
   │   Headers:                    │                              │
   │   - Content-Type             │                              │
   │                              │──(2) POST /v1/auth/login────>│
   │                              │                              │
   │                              │<─(3) Response + Cookies──────│
   │                              │   Set-Cookie: session_id=xyz │
   │                              │                              │
   │   Store cookies for          │                              │
   │   session_abc123 → xyz       │                              │
   │                              │                              │
   │<─(4) Response ────────────────│                              │
   │   Headers:                    │                              │
   │   - X-Client-Session-Id: abc123                             │
   │                              │                              │
   │  Save abc123 to              │                              │
   │  localStorage                │                              │
```

### 2. Subsequent Requests

```
Browser                         Proxy                          Odoo
   │                              │                              │
   │──(1) GET /api/proxy?url=...──>│                              │
   │   Headers:                    │                              │
   │   - X-Client-Session-Id: abc123                             │
   │                              │                              │
   │   Retrieve cookies for       │                              │
   │   session abc123             │                              │
   │                              │                              │
   │                              │──(2) GET /v1/condominiums───>│
   │                              │   Cookie: session_id=xyz     │
   │                              │                              │
   │                              │<─(3) Response ───────────────│
   │                              │                              │
   │<─(4) Response ────────────────│                              │
```

## Session Management

### Client Side (Browser)

```typescript
// Automatic in api.ts
const clientSessionId = localStorage.getItem('odoo_proxy_session_id');

// Added to all requests
headers['X-Client-Session-Id'] = clientSessionId;

// Captured from responses
const sessionId = response.headers['x-client-session-id'];
localStorage.setItem('odoo_proxy_session_id', sessionId);
```

### Server Side (Proxy)

```javascript
// Session store
const sessionStore = new Map();

// Session structure
{
  'session_abc123': {
    cookies: { session_id: 'xyz', ... },
    lastAccess: 1234567890
  }
}

// Auto-cleanup after 30 minutes
setInterval(cleanupExpiredSessions, 5 * 60 * 1000);
```

## Troubleshooting

### Issue: CORS errors still occurring

**Solution:**
1. Verify `VITE_USE_CORS_PROXY=true` in `.env`
2. Check proxy is running (Vercel deployment or local)
3. Check browser console for proxy errors
4. Verify `VITE_CORS_PROXY_URL` is correct

### Issue: Session not persisting

**Solution:**
1. Check browser localStorage for `odoo_proxy_session_id`
2. Verify proxy is storing cookies (check proxy logs)
3. Ensure session timeout hasn't expired (30 min default)

### Issue: 401 Unauthorized errors

**Solution:**
1. Verify Odoo credentials are correct
2. Check JWT token is being sent in Authorization header
3. Verify session cookies are being forwarded by proxy
4. Check Odoo backend authentication configuration

### Issue: Proxy timeout errors

**Solution:**
1. Increase `VITE_API_TIMEOUT` in `.env`
2. Check Odoo backend is responding
3. Verify network connectivity to Odoo

## Development Tips

### Debug Mode

Add logging to see proxy activity:

```javascript
// In proxy.js
console.log('Session ID:', clientSessionId);
console.log('Stored cookies:', sessionData.cookies);
console.log('Request URL:', decodedUrl);
```

### Testing Without Odoo

Use a mock Odoo server or API mocking tools:
- [json-server](https://github.com/typicode/json-server)
- [MSW (Mock Service Worker)](https://mswjs.io/)

### Local Proxy Development

Run proxy locally for development:

```bash
cd cors-proxy
npm install
# Add express for local server
npm install express cors

# Create local-server.js
node local-server.js
```

## Security Considerations

1. **Session Timeout**: Sessions expire after 30 minutes of inactivity
2. **HTTPS in Production**: Always use HTTPS for production deployments
3. **Environment Variables**: Keep API URLs and secrets in environment variables
4. **Session Cleanup**: Automatic cleanup prevents memory leaks
5. **No Sensitive Data Logging**: Avoid logging passwords or tokens

## Performance

- **Session Storage**: In-memory Map (fast, but resets on server restart)
- **Scalability**: For high-traffic apps, consider Redis for session storage
- **Caching**: React Query handles API response caching
- **Connection Pooling**: Axios reuses connections for better performance

## Alternative Solutions Considered

| Solution | Pros | Cons | Decision |
|----------|------|------|----------|
| Direct CORS | Simple | Requires Odoo config changes | ❌ Not flexible |
| Public Proxy | Easy setup | Strips cookies, insecure | ❌ Breaks sessions |
| Session-Aware Proxy | Solves all issues | Requires deployment | ✅ **Chosen** |
| Browser Extension | No server needed | User must install | ❌ Not scalable |

## Migration from Direct Connection

If you were connecting directly to Odoo:

1. Update `.env`:
   ```env
   VITE_USE_CORS_PROXY=true
   ```

2. No code changes needed - API client handles proxy automatically

3. Test login and API calls

4. Deploy with new configuration

## Resources

- [MDN: CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Vercel Serverless Functions](https://vercel.com/docs/functions)
- [Axios Documentation](https://axios-http.com/)
- [Odoo REST API](https://www.odoo.com/documentation/)

## Support

For issues or questions:
1. Check this documentation
2. Review proxy logs (Vercel Function Logs)
3. Check browser Network tab in DevTools
4. Verify environment variables are set correctly

---

**Last Updated:** 2025-01-26
**Version:** 1.0.0
**Status:** Production Ready ✅
