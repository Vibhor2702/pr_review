# 🚀 Complete Cloudflare Deployment Guide

## Deploy PR Review Agent with Cloudflare Workers + Cloudflare Pages (100% Free Forever)

This guide walks you through deploying a **fully serverless, globally distributed** PR Review system using Cloudflare's free tier.

---

## 📋 Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    USER'S BROWSER                             │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   ↓
┌──────────────────────────────────────────────────────────────┐
│        Cloudflare Pages (Frontend - React/TypeScript)        │
│        https://pr-review.pages.dev                           │
│        - Unlimited bandwidth                                  │
│        - 500 builds/month                                     │
│        - Automatic SSL                                        │
│        - Global CDN                                           │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   │ API Calls
                   ↓
┌──────────────────────────────────────────────────────────────┐
│      Cloudflare Workers (Backend - Serverless API)           │
│      https://pr-review-worker.your-username.workers.dev      │
│      - 100,000 requests/day                                   │
│      - Global edge execution                                  │
│      - 10ms CPU time/request                                  │
│      - Automatic scaling                                      │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   │ AI Processing
                   ↓
┌──────────────────────────────────────────────────────────────┐
│           Google Gemini API (AI Reviews)                      │
│           - 60 requests/minute (free tier)                    │
│           - Advanced code analysis                            │
│           - Natural language insights                         │
└──────────────────────────────────────────────────────────────┘
```

**Total Monthly Cost: $0** 💰✨

---

## 🎯 Prerequisites (5 minutes setup)

### 1. **Cloudflare Account**
- Sign up at: https://dash.cloudflare.com/sign-up
- **Free tier** - no credit card required
- Verify your email

### 2. **Google Gemini API Key**
- Visit: https://aistudio.google.com/app/apikey
- Click "Create API Key"
- Copy and save it securely
- **Free tier**: 60 requests/minute

### 3. **GitHub Account**
- Your repository: https://github.com/Vibhor2702/pr_review
- Already set up ✅

### 4. **Node.js 18+**
- Download: https://nodejs.org/
- Verify: `node --version`

---

## 📦 Part 1: Deploy Backend (Cloudflare Workers)

### Step 1: Navigate to Workers Directory

```bash
cd workers
```

### Step 2: Install Dependencies

```bash
npm install
```

This installs:
- `wrangler` - Cloudflare CLI
- `@google/generative-ai` - Gemini SDK
- TypeScript & types

### Step 3: Login to Cloudflare

```bash
npx wrangler login
```

- Opens browser for authentication
- Click "Allow" to authorize
- Terminal will confirm: ✅ "Successfully logged in"

### Step 4: Get Your Account ID

```bash
npx wrangler whoami
```

Copy your `Account ID` (looks like: `a1b2c3d4e5f6g7h8i9j0`)

### Step 5: Update Configuration

Edit `wrangler.toml`:

```toml
# Uncomment and add your account ID
account_id = "your-account-id-here"
```

### Step 6: Set Gemini API Key (Secret)

```bash
npx wrangler secret put GEMINI_API_KEY
```

When prompted:
1. Paste your Gemini API key
2. Press Enter
3. You'll see: ✅ "Secret GEMINI_API_KEY created"

> 🔒 **Security Note**: Secrets are encrypted and never visible in logs or code!

### Step 7: Deploy! 🚀

```bash
npm run deploy
```

Output will show:

```
✨ Compiled Worker successfully
🌎 Uploading...
✨ Uploaded pr-review-worker (1.23 sec)
✨ Published pr-review-worker (0.45 sec)
  https://pr-review-worker.your-username.workers.dev
✨ Success! Your worker is live at the URL above
```

**🎉 Copy this URL - you'll need it for frontend!**

### Step 8: Test Your API

```bash
# Health check
curl https://pr-review-worker.your-username.workers.dev/api/status

# Should return:
# {
#   "ok": true,
#   "service": "PR Review API",
#   "version": "1.0.0",
#   ...
# }
```

✅ **Backend deployed successfully!**

---

## 🎨 Part 2: Deploy Frontend (Cloudflare Pages)

### Step 1: Connect GitHub to Cloudflare Pages

1. Go to: https://dash.cloudflare.com/pages
2. Click **"Create a project"**
3. Click **"Connect to Git"**
4. Select **GitHub**
5. Authorize Cloudflare Pages
6. Select repository: **`Vibhor2702/pr_review`**

### Step 2: Configure Build Settings

Fill in these settings:

```
Project name: pr-review
Production branch: master
Build command: cd frontend && npm install && npm run build
Build output directory: frontend/dist
```

### Step 3: Add Environment Variables

Click **"Add variable"** and enter:

| Variable Name | Value |
|--------------|-------|
| `VITE_API_URL` | `https://pr-review-worker.your-username.workers.dev` |
| `VITE_APP_NAME` | `PR Review Agent` |
| `VITE_APP_VERSION` | `1.0.0` |
| `VITE_ENABLE_DEMO_MODE` | `true` |

> ⚠️ **Critical**: Replace `your-username` with your actual Cloudflare username!

### Step 4: Deploy

1. Click **"Save and Deploy"**
2. Wait 2-3 minutes for build
3. You'll see: ✅ **"Success! Your site is live!"**

Your site will be at:
```
https://pr-review.pages.dev
```

### Step 5: Set Custom Domain (Optional)

If you have a custom domain:

1. Go to **Pages** → **Your Project** → **Custom domains**
2. Click **"Set up a custom domain"**
3. Enter your domain (e.g., `pr-review.your-domain.com`)
4. Follow DNS configuration instructions

✅ **Frontend deployed successfully!**

---

## 🔗 Part 3: Verify Integration

### 1. Test Frontend

Visit: `https://pr-review.pages.dev`

- Should load without errors
- Check browser console (F12) for API connection
- Should see: `🔗 API Base URL: https://pr-review-worker...`

### 2. Test API Connection

In browser console:

```javascript
fetch('https://pr-review-worker.your-username.workers.dev/api/status')
  .then(r => r.json())
  .then(console.log)
```

Should return status with `"ok": true`

### 3. Test Full Review Flow

1. Go to **Dashboard** page
2. Click **"New Review"**
3. Enter test data:
   - Provider: `github`
   - Owner: `test`
   - Repo: `demo`
   - PR Number: `1`
4. Click **"Review PR"**
5. Should see AI-generated review!

✅ **Full integration working!**

---

## 🛠️ Local Development

### Backend (Workers)

```bash
cd workers
npm run dev
```

Runs at: `http://localhost:8787`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs at: `http://localhost:5173`

### Test Locally

Update `frontend/.env.local`:

```bash
VITE_API_URL=http://localhost:8787
```

---

## 📊 Monitoring & Analytics

### View Worker Analytics

1. Go to: https://dash.cloudflare.com/workers
2. Select: **pr-review-worker**
3. Click: **Analytics**

You'll see:
- 📈 Requests per day
- ⏱️ Average response time
- ❌ Error rates
- 🌍 Geographic distribution

### View Pages Analytics

1. Go to: https://dash.cloudflare.com/pages
2. Select: **pr-review**
3. Click: **Analytics**

You'll see:
- 👥 Unique visitors
- 📄 Page views
- 🌍 Top countries
- 📱 Devices breakdown

### Live Logs

```bash
cd workers
npm run tail
```

Streams real-time logs from your Worker!

---

## 🔧 Troubleshooting

### Issue: "GEMINI_API_KEY not configured"

**Solution**:

```bash
cd workers
npx wrangler secret put GEMINI_API_KEY
```

### Issue: "CORS Error" in Browser

**Solution**: Check `wrangler.toml`:

```toml
[vars]
ALLOWED_ORIGINS = "https://pr-review.pages.dev,https://*.pages.dev"
```

Add your domain if using custom domain.

### Issue: Frontend shows "API Connection Failed"

**Solution**: 

1. Check Cloudflare Pages environment variables
2. Verify `VITE_API_URL` is correct
3. Redeploy: **Deployments** → **View details** → **Retry deployment**

### Issue: Worker returns 500 error

**Solution**:

```bash
cd workers
npx wrangler tail
```

Check logs for errors, then redeploy:

```bash
npm run deploy
```

### Issue: "Account ID not found"

**Solution**:

```bash
npx wrangler whoami
```

Copy account ID and update `wrangler.toml`.

---

## 🚀 Production Optimizations

### 1. Enable Caching

Add to `workers/src/index.ts`:

```typescript
return new Response(JSON.stringify(response), {
  headers: {
    ...headers,
    'Cache-Control': 'public, max-age=60',
  },
});
```

### 2. Add Rate Limiting

Use Cloudflare's built-in rate limiting in dashboard:
- **Security** → **WAF** → **Rate limiting rules**

### 3. Custom Domain for Worker

1. Go to **Workers** → **pr-review-worker** → **Triggers**
2. Click **"Add Custom Domain"**
3. Enter: `api.your-domain.com`
4. Update frontend `VITE_API_URL`

### 4. Enable Analytics

Add to `wrangler.toml`:

```toml
[observability]
enabled = true
```

---

## 💰 Cost Breakdown (Forever Free!)

| Service | Free Tier | Your Usage | Cost |
|---------|-----------|------------|------|
| **Cloudflare Workers** | 100K req/day | ~1K/day | $0 |
| **Cloudflare Pages** | Unlimited bandwidth | 10GB/month | $0 |
| **Google Gemini** | 60 req/min | ~100/day | $0 |
| **GitHub** | Unlimited repos | 1 repo | $0 |
| **SSL Certificates** | Free | Automatic | $0 |
| **Global CDN** | Free | 300+ locations | $0 |
| **TOTAL** | | | **$0/month** ✨ |

**Upgrade Options (Optional):**
- Workers Paid: $5/month (10M requests)
- Pages Pro: $20/month (Custom limits)
- Gemini Paid: Pay-as-you-go (after free tier)

---

## 🎯 Deployment Checklist

### Backend (Workers)

- [ ] `cd workers`
- [ ] `npm install`
- [ ] `npx wrangler login`
- [ ] Update `account_id` in `wrangler.toml`
- [ ] `npx wrangler secret put GEMINI_API_KEY`
- [ ] `npm run deploy`
- [ ] Copy Worker URL
- [ ] Test: `curl <worker-url>/api/status`

### Frontend (Pages)

- [ ] Go to https://dash.cloudflare.com/pages
- [ ] Connect GitHub repository
- [ ] Configure build settings
- [ ] Add environment variable: `VITE_API_URL=<worker-url>`
- [ ] Deploy
- [ ] Test site loads
- [ ] Test API connection in browser console
- [ ] Test full review flow

### Verification

- [ ] Worker responds to `/api/status`
- [ ] Worker responds to `/api/review`
- [ ] Frontend loads without errors
- [ ] Frontend connects to Worker API
- [ ] AI review works end-to-end
- [ ] Analytics working in Cloudflare dashboard

---

## 📚 Additional Resources

### Documentation
- **Cloudflare Workers**: https://developers.cloudflare.com/workers/
- **Cloudflare Pages**: https://developers.cloudflare.com/pages/
- **Wrangler CLI**: https://developers.cloudflare.com/workers/wrangler/
- **Gemini API**: https://ai.google.dev/docs

### Community
- **Cloudflare Discord**: https://discord.cloudflare.com
- **Workers Examples**: https://github.com/cloudflare/workers-sdk
- **Cloudflare Community**: https://community.cloudflare.com

### Support
- **Workers Documentation**: https://developers.cloudflare.com/workers/
- **Status Page**: https://www.cloudflarestatus.com
- **Support Portal**: https://support.cloudflare.com

---

## 🎉 Success!

Your PR Review Agent is now:
- ✅ **Globally distributed** across 300+ edge locations
- ✅ **Serverless** - no servers to manage
- ✅ **Forever free** - $0/month hosting
- ✅ **Auto-scaling** - handles traffic spikes
- ✅ **SSL secured** - automatic HTTPS
- ✅ **CI/CD integrated** - push to deploy

### Live URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | `https://pr-review.pages.dev` | User interface |
| **Backend API** | `https://pr-review-worker.*.workers.dev` | Serverless API |
| **GitHub** | `https://github.com/Vibhor2702/pr_review` | Source code |
| **Dashboard** | `https://dash.cloudflare.com` | Management |

---

## 🔄 Continuous Deployment

### Automatic Deployments

Every push to `master` triggers:

1. **Cloudflare Pages** auto-detects push
2. Builds frontend automatically
3. Deploys to production in ~2 minutes
4. Available at your Pages URL

### Manual Deployments

**Workers**:
```bash
cd workers
npm run deploy
```

**Pages** (via dashboard):
1. Go to Pages project
2. Click **"Create deployment"**
3. Select branch
4. Deploy

---

Made with ❤️ using Cloudflare Workers, Cloudflare Pages, and Google Gemini AI

**Questions?** Open an issue on GitHub: https://github.com/Vibhor2702/pr_review/issues
