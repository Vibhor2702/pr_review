# 🚀 Cloudflare Workers Deployment Guide

## PR Review Agent - Serverless Backend

This is a **serverless, globally distributed API** that runs **forever for free** on Cloudflare Workers, powering the PR Review Agent with AI-driven code analysis.

---

## 🎯 What You Get

- ✅ **Forever Free**: Cloudflare Workers free tier (100,000 requests/day)
- ✅ **Global Performance**: Deployed to 300+ edge locations worldwide
- ✅ **Zero Maintenance**: No servers to manage, auto-scaling
- ✅ **Instant Deploys**: Deploy in seconds with `wrangler deploy`
- ✅ **AI-Powered**: Google Gemini integration for intelligent code reviews

---

## 📋 Prerequisites

1. **Cloudflare Account** (free): https://dash.cloudflare.com/sign-up
2. **Node.js 18+**: https://nodejs.org/
3. **Google Gemini API Key**: https://aistudio.google.com/app/apikey

---

## 🚀 Quick Start (5 minutes)

### Step 1: Install Dependencies

```bash
cd workers
npm install
```

### Step 2: Login to Cloudflare

```bash
npx wrangler login
```

This opens your browser to authenticate. Once done, you're ready!

### Step 3: Set Your Gemini API Key (Secret)

```bash
npx wrangler secret put GEMINI_API_KEY
```

When prompted, paste your Google Gemini API key and press Enter.

> ⚠️ **Important**: Secrets are encrypted and never visible in code or logs!

### Step 4: Update Account ID (Optional)

Get your account ID:

```bash
npx wrangler whoami
```

Copy your `Account ID` and add it to `wrangler.toml`:

```toml
account_id = "your-account-id-here"
```

### Step 5: Deploy! 🎉

```bash
npm run deploy
```

You'll see output like:

```
✨ Compiled Worker successfully
✨ Uploaded Worker to Cloudflare
✨ Deployed to: https://pr-review-worker.your-username.workers.dev
```

**🎊 That's it! Your API is live!**

---

## 🧪 Test Your Deployment

### 1. Health Check

```bash
curl https://pr-review-worker.your-username.workers.dev/api/status
```

Expected response:

```json
{
  "ok": true,
  "service": "PR Review API",
  "version": "1.0.0",
  "environment": "production",
  "timestamp": "2025-10-05T12:34:56.789Z",
  "endpoints": {
    "status": "/api/status",
    "review": "/api/review"
  }
}
```

### 2. Test AI Review

```bash
curl -X POST https://pr-review-worker.your-username.workers.dev/api/review \
  -H "Content-Type: application/json" \
  -d '{
    "diff": "+function add(a, b) { return a + b; }",
    "repo": "your-username/test-repo",
    "author": "your-username",
    "title": "Add addition function"
  }'
```

Expected response:

```json
{
  "score": 85,
  "grade": "B+",
  "summary": "Good code structure with clear function implementation.",
  "suggestions": [
    "Add input validation for type checking",
    "Include JSDoc comments for better documentation",
    "Consider edge cases like NaN or Infinity"
  ],
  "severity_breakdown": {
    "critical": 0,
    "high": 0,
    "medium": 2,
    "low": 1
  },
  "metadata": {
    "timestamp": "2025-10-05T12:34:56.789Z",
    "repo": "your-username/test-repo",
    "author": "your-username",
    "lines_changed": 1
  }
}
```

---

## 🔗 Connect to Frontend

### Step 1: Get Your Worker URL

After deployment, copy your Worker URL:

```
https://pr-review-worker.your-username.workers.dev
```

### Step 2: Configure Cloudflare Pages

1. Go to your Cloudflare Pages project: https://dash.cloudflare.com/pages
2. Select your `pr-review` project
3. Go to **Settings** → **Environment Variables**
4. Add production variable:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://pr-review-worker.your-username.workers.dev`
5. Click **Save**

### Step 3: Redeploy Frontend

Trigger a new deployment:

```bash
# In your frontend directory
git commit --allow-empty -m "Update API endpoint to Cloudflare Workers"
git push origin master
```

Cloudflare Pages will automatically rebuild with the new API URL!

---

## 🛠️ Local Development

### Start Local Dev Server

```bash
npm run dev
```

This starts a local Workers environment at `http://localhost:8787`

### Test Locally

```bash
# Health check
curl http://localhost:8787/api/status

# Review endpoint
curl -X POST http://localhost:8787/api/review \
  -H "Content-Type: application/json" \
  -d '{
    "diff": "+console.log(\"Hello World\");",
    "repo": "test/repo",
    "author": "developer"
  }'
```

### Local Environment Variables

Create `.dev.vars` file (already included):

```bash
GEMINI_API_KEY=your-local-api-key-here
```

> **Note**: `.dev.vars` is for local development only. Production uses `wrangler secret`.

---

## 📊 Monitor Your Worker

### View Deployment Logs

```bash
npm run tail
```

This streams real-time logs from your deployed Worker.

### Cloudflare Dashboard

Visit: https://dash.cloudflare.com/workers

Here you can see:
- ✅ Request metrics (requests/day, CPU time, errors)
- ✅ Analytics (response times, status codes)
- ✅ Logs and debugging info
- ✅ Custom domains setup

---

## 🔐 Security & Best Practices

### ✅ Secrets Management

- **Production secrets**: Use `wrangler secret put`
- **Never commit**: Secrets are encrypted and stored securely
- **Rotation**: Update secrets anytime with same command

### ✅ CORS Configuration

The Worker allows requests from:
- `https://pr-review.pages.dev` (your frontend)
- `https://*.pages.dev` (preview deployments)

To add custom domains, edit `wrangler.toml`:

```toml
[vars]
ALLOWED_ORIGINS = "https://pr-review.pages.dev,https://your-custom-domain.com"
```

### ✅ Rate Limiting

Free tier limits:
- **100,000 requests/day** (more than enough!)
- **10ms CPU time per request** (plenty for AI calls)

For higher limits, upgrade to Workers Paid ($5/month for 10M requests).

---

## 🎨 Customization

### Add Custom Domain

1. Go to Cloudflare Dashboard → Workers
2. Select your `pr-review-worker`
3. Click **Triggers** → **Custom Domains**
4. Add your domain (e.g., `api.your-domain.com`)

Update `wrangler.toml`:

```toml
[[routes]]
pattern = "api.your-domain.com/*"
zone_name = "your-domain.com"
```

### Modify AI Prompts

Edit `src/index.ts` → `analyzeWithGemini()` function to customize the review criteria and output format.

### Add More Endpoints

Add routes in `src/index.ts`:

```typescript
if (path === '/api/your-endpoint' && request.method === 'POST') {
  return handleYourEndpoint(request, env);
}
```

---

## 🐛 Troubleshooting

### Issue: "Authentication Error"

**Solution**: Run `npx wrangler login` again

### Issue: "GEMINI_API_KEY not configured"

**Solution**: Set the secret:

```bash
npx wrangler secret put GEMINI_API_KEY
```

### Issue: "CORS Error in Browser"

**Solution**: Check `ALLOWED_ORIGINS` in `wrangler.toml` includes your frontend URL

### Issue: "Worker not updating"

**Solution**: 
1. Clear cache: `npx wrangler deploy --no-cache`
2. Wait 30 seconds for global propagation

### Issue: "Deployment failed"

**Solution**: Check syntax with:

```bash
npm run build
```

---

## 📚 Additional Resources

- **Cloudflare Workers Docs**: https://developers.cloudflare.com/workers/
- **Wrangler CLI**: https://developers.cloudflare.com/workers/wrangler/
- **Gemini API**: https://ai.google.dev/docs
- **Workers Examples**: https://github.com/cloudflare/workers-sdk/tree/main/templates

---

## 🎯 Cost Breakdown

| Service | Free Tier | Usage | Cost |
|---------|-----------|-------|------|
| **Cloudflare Workers** | 100K req/day | API Backend | **$0/month** |
| **Cloudflare Pages** | Unlimited | Frontend | **$0/month** |
| **Google Gemini** | 60 req/min | AI Reviews | **$0/month** |
| **GitHub** | Unlimited public repos | Code Hosting | **$0/month** |
| **TOTAL** | | | **$0/month** ✨ |

---

## ✅ Deployment Checklist

- [ ] Install dependencies (`npm install`)
- [ ] Login to Cloudflare (`npx wrangler login`)
- [ ] Set Gemini API key (`npx wrangler secret put GEMINI_API_KEY`)
- [ ] Update account ID in `wrangler.toml`
- [ ] Deploy Worker (`npm run deploy`)
- [ ] Test endpoints (`curl` commands)
- [ ] Add Worker URL to Cloudflare Pages environment variables
- [ ] Redeploy frontend
- [ ] Verify integration works end-to-end

---

## 🎉 Success!

Your PR Review Agent is now running on a **globally distributed, serverless, forever-free** infrastructure!

**Architecture:**
```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────┐
│  Cloudflare     │ ───> │  Cloudflare      │ ───> │   Google    │
│  Pages          │      │  Workers         │      │   Gemini    │
│  (Frontend)     │      │  (API)           │      │   (AI)      │
└─────────────────┘      └──────────────────┘      └─────────────┘
   pr-review.pages.dev   pr-review-worker           AI Reviews
```

**Live URLs:**
- Frontend: `https://pr-review.pages.dev`
- Backend: `https://pr-review-worker.your-username.workers.dev`
- GitHub: `https://github.com/Vibhor2702/pr_review`

---

Made with ❤️ using Cloudflare Workers
