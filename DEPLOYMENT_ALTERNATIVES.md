# Deployment Alternatives for Wallbox Dashboard

This guide provides multiple free hosting options for deploying your Wallbox Dashboard with the CORS proxy.

## 📊 Comparison Table

| Platform | Free Tier | Setup Difficulty | Best For | CORS Proxy |
|----------|-----------|------------------|----------|------------|
| **Netlify** | ✅ Generous | ⭐ Easy | Static + Functions | ✅ Serverless |
| **Railway** | ✅ $5 credit/month | ⭐⭐ Medium | Full-stack apps | ✅ Same server |
| **Render** | ✅ Yes (slower) | ⭐⭐ Medium | Full-stack apps | ✅ Same server |
| **Vercel** | ✅ Yes (1 project) | ⭐ Easy | Static + Functions | ✅ Serverless |
| **Fly.io** | ✅ Generous | ⭐⭐⭐ Advanced | Container apps | ✅ Docker |
| **Cloudflare Pages** | ✅ Unlimited | ⭐⭐ Medium | Static + Workers | ✅ Workers |

---

## 1. 🎯 Netlify (Recommended for Beginners)

**Best for:** Easy deployment with serverless functions
**Free Tier:** 100GB bandwidth, 300 build minutes/month

### Quick Deploy

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start)

### Manual Deployment

```bash
# 1. Install Netlify CLI
npm install -g netlify-cli

# 2. Login
netlify login

# 3. Initialize project
netlify init

# 4. Deploy
netlify deploy --prod
```

### Configuration

The `netlify.toml` file is already configured. Set these environment variables in Netlify UI:

```
VITE_API_BASE_URL=https://your-odoo.com
VITE_USE_CORS_PROXY=true
VITE_CORS_PROXY_URL=/.netlify/functions/proxy
```

### ✅ Pros
- Automatic HTTPS
- Global CDN
- Serverless functions included
- Easy rollbacks
- Preview deployments for PRs

### ❌ Cons
- Cold starts on functions
- Build minutes limit

---

## 2. 🚂 Railway (Recommended for Full-Stack)

**Best for:** Apps that need a persistent server
**Free Tier:** $5 credit/month (enough for testing)

### Quick Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

### Manual Deployment

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize and deploy
railway init
railway up
```

### Configuration

Set environment variables in Railway dashboard:

```
VITE_API_BASE_URL=https://your-odoo.com
VITE_USE_CORS_PROXY=true
VITE_CORS_PROXY_URL=/api/proxy
PORT=3000
```

### ✅ Pros
- No cold starts (always running)
- PostgreSQL database included (if needed later)
- Easy environment variables
- Automatic deploys from GitHub

### ❌ Cons
- $5/month credit depletes eventually
- Need credit card for verification

---

## 3. 🎨 Render

**Best for:** Free tier with no credit card required
**Free Tier:** Yes, but slower spin-up times

### Quick Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Manual Deployment

```bash
# 1. Create account at render.com
# 2. Connect GitHub repository
# 3. Choose "Web Service"
# 4. Use these settings:

Build Command: npm install && npm run build
Start Command: npm run render:start
```

### Configuration (render.yaml)

The `render.yaml` blueprint is included. Set these variables:

```
VITE_API_BASE_URL=https://your-odoo.com
VITE_USE_CORS_PROXY=true
VITE_CORS_PROXY_URL=/api/proxy
```

### ✅ Pros
- Truly free tier (no credit card)
- PostgreSQL included
- Auto-deploy from GitHub
- Easy to use

### ❌ Cons
- Free tier "spins down" after 15min inactivity
- Slower cold starts (30-60 seconds)
- Limited to 750 hours/month on free tier

---

## 4. ☁️ Vercel (If You Have Room)

**Best for:** Serverless deployments
**Free Tier:** 100GB bandwidth, Hobby projects

### Quick Deploy

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Deploy
vercel
```

### Configuration

The `vercel.json` is already configured. Environment variables:

```
VITE_API_BASE_URL=https://your-odoo.com
VITE_USE_CORS_PROXY=true
VITE_CORS_PROXY_URL=/api/proxy
```

### ✅ Pros
- Fastest CDN
- Excellent DX
- Preview deployments
- Edge functions

### ❌ Cons
- 1 project limit on free tier (you mentioned you hit this)

---

## 5. ✈️ Fly.io

**Best for:** Containerized applications
**Free Tier:** 3 shared-cpu VMs, 3GB storage

### Deployment

```bash
# 1. Install flyctl
curl -L https://fly.io/install.sh | sh

# 2. Login
fly auth login

# 3. Create Dockerfile (provided below)

# 4. Launch
fly launch

# 5. Deploy
fly deploy
```

### Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY cors-proxy/package*.json ./cors-proxy/

# Install dependencies
RUN npm install
RUN cd cors-proxy && npm install && cd ..

# Copy source
COPY . .

# Build app
RUN npm run build

# Expose port
EXPOSE 3000

# Start server
CMD ["node", "railway-server.js"]
```

### ✅ Pros
- True always-on hosting
- Multiple regions
- Scale to zero option
- Good performance

### ❌ Cons
- More complex setup
- Requires Docker knowledge
- Credit card required for verification

---

## 6. 🌐 Cloudflare Pages + Workers

**Best for:** Global edge deployment
**Free Tier:** Unlimited sites, 100k requests/day

### Quick Deploy

```bash
# 1. Install Wrangler
npm install -g wrangler

# 2. Login
wrangler login

# 3. Deploy Pages
wrangler pages publish dist

# 4. Deploy Worker (proxy function)
wrangler publish
```

### Configuration

You'll need to create a Worker for the proxy. See Cloudflare Workers documentation.

### ✅ Pros
- Unlimited bandwidth
- Global edge network
- Very fast
- DDoS protection

### ❌ Cons
- More complex proxy setup
- Different function syntax
- Learning curve for Workers

---

## 🎯 Quick Decision Guide

### Choose **Netlify** if:
- ✅ You want the easiest setup
- ✅ You're deploying from GitHub
- ✅ You want serverless functions
- ✅ You need preview deployments

### Choose **Railway** if:
- ✅ You need a persistent server (no cold starts)
- ✅ You might add a database later
- ✅ You're okay with $5/month credit
- ✅ You want simple full-stack hosting

### Choose **Render** if:
- ✅ You want completely free hosting
- ✅ You don't mind 30-60s cold starts
- ✅ You don't have a credit card
- ✅ Your app doesn't need 24/7 availability

### Choose **Fly.io** if:
- ✅ You know Docker
- ✅ You want control over infrastructure
- ✅ You need multi-region deployment
- ✅ You want container-based hosting

---

## 📝 Deployment Checklist

Before deploying to any platform:

- [ ] Build succeeds locally (`npm run build`)
- [ ] Environment variables documented
- [ ] `.env` is in `.gitignore`
- [ ] Odoo backend URL is accessible from internet
- [ ] CORS proxy configuration is correct
- [ ] Health check endpoint works (`/health`)

---

## 🔧 Platform-Specific Environment Variables

### For All Platforms

```env
# Required
VITE_API_BASE_URL=https://your-odoo.com
VITE_USE_CORS_PROXY=true

# Platform-specific proxy URL
# Netlify:
VITE_CORS_PROXY_URL=/.netlify/functions/proxy

# Railway/Render/Fly.io:
VITE_CORS_PROXY_URL=/api/proxy

# Vercel:
VITE_CORS_PROXY_URL=/api/proxy

# Optional
VITE_API_TIMEOUT=30000
VITE_TOKEN_REFRESH_INTERVAL=300000
```

### Platform-Specific

**Railway/Render/Fly.io only:**
```env
PORT=3000  # Server port
NODE_ENV=production
```

---

## 🧪 Testing After Deployment

1. **Check Health Endpoint**
   ```bash
   curl https://your-app.netlify.app/health
   # or
   curl https://your-app.up.railway.app/health
   ```

2. **Test CORS Proxy**
   ```bash
   curl -X OPTIONS https://your-app.com/api/proxy \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type"
   ```

3. **Test Login**
   - Navigate to your deployed URL
   - Open browser DevTools → Network tab
   - Try logging in
   - Check for successful API calls

---

## 🐛 Common Issues

### Build Fails

**Solution:**
```bash
# Test build locally first
npm run build

# Check Node version matches
node --version  # Should be 18+
```

### CORS Errors After Deployment

**Solution:**
- Verify `VITE_USE_CORS_PROXY=true`
- Check proxy URL matches platform
- Ensure proxy function is deployed

### 404 on Routes

**Solution:**
- Netlify/Vercel: Redirect rules in config
- Railway/Render: Express handles all routes in `railway-server.js`

### Cold Starts (Render Free Tier)

**Solution:**
- Use UptimeRobot or similar to ping `/health` every 5 minutes
- Or upgrade to paid tier ($7/month)

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid Tier | Best Value |
|----------|-----------|-----------|------------|
| Netlify | $0 (generous) | $19/mo | ⭐⭐⭐⭐⭐ |
| Railway | $5 credit/mo | $5/mo | ⭐⭐⭐⭐ |
| Render | $0 (with limits) | $7/mo | ⭐⭐⭐⭐⭐ |
| Vercel | $0 (1 project) | $20/mo | ⭐⭐⭐ |
| Fly.io | $0 (3 VMs) | Pay as you go | ⭐⭐⭐⭐ |
| Cloudflare | $0 (generous) | $5/mo Workers | ⭐⭐⭐⭐⭐ |

---

## 📚 Additional Resources

### Official Documentation
- [Netlify Docs](https://docs.netlify.com/)
- [Railway Docs](https://docs.railway.app/)
- [Render Docs](https://render.com/docs)
- [Vercel Docs](https://vercel.com/docs)
- [Fly.io Docs](https://fly.io/docs/)
- [Cloudflare Pages Docs](https://developers.cloudflare.com/pages/)

### Tutorials
- [Deploy React to Netlify](https://www.netlify.com/blog/2016/07/22/deploy-react-apps-in-less-than-30-seconds/)
- [Railway Getting Started](https://docs.railway.app/getting-started)
- [Render Node.js Guide](https://render.com/docs/deploy-node-express-app)

---

## 🎓 Recommendations

### For Testing (Your Use Case)
**Best Choice: Netlify** ⭐
- Free, no credit card
- Easy setup
- Serverless functions work perfectly
- Can deploy unlimited sites

**Alternative: Render**
- Completely free
- No credit card needed
- Good for testing (despite cold starts)

### For Production
**Best Choice: Railway** ⭐
- No cold starts
- Reliable performance
- $5/month is reasonable
- Easy database integration if needed

**Alternative: Fly.io**
- Best performance
- Multi-region deployment
- More control

---

## 🚀 Getting Started Now

**My recommendation for your testing needs:**

```bash
# Use Netlify - it's the easiest

# 1. Install CLI
npm install -g netlify-cli

# 2. Login
netlify login

# 3. Deploy
netlify deploy --prod

# 4. Set environment variables in Netlify UI
# VITE_API_BASE_URL=http://your-odoo.com
# VITE_USE_CORS_PROXY=true
# VITE_CORS_PROXY_URL=/.netlify/functions/proxy

# Done! Your app is live.
```

---

**Questions?** Check the troubleshooting section or refer to platform-specific docs.

**Last Updated:** 2025-01-26
**Version:** 1.0.0
