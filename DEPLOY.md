# 🚀 PR Review Agent - Cloudflare Deployment Guide

Deploy your AI-powered PR Review system on **Cloudflare** - completely free, forever!

---

## 🎯 What You'll Deploy

```
┌─────────────────────────────────┐
│   Cloudflare Pages (Frontend)   │  ← React Dashboard
│   https://pr-review.pages.dev   │
└────────────┬────────────────────┘
             │
             ↓ API Calls
┌─────────────────────────────────┐
│  Cloudflare Workers (Backend)   │  ← Serverless API
│  pr-review-worker.workers.dev   │
└────────────┬────────────────────┘
             │
             ↓ AI Processing
┌─────────────────────────────────┐
│      Google Gemini API          │  ← Code Analysis
└─────────────────────────────────┘
```

**Cost: $0/month forever** 💰

---

## ✅ Prerequisites (5 minutes)

1. **Cloudflare Account** (free): https://dash.cloudflare.com/sign-up
2. **Google Gemini API Key** (free): https://aistudio.google.com/app/apikey
3. **Node.js 18+**: https://nodejs.org/
4. **GitHub**: Your repo at https://github.com/Vibhor2702/pr_review

---

## 🚀 Part 1: Deploy Backend (3 minutes)

### Step 1: Setup

```powershell
# Navigate to workers directory
cd workers

# Install dependencies
npm install

# Login to Cloudflare
npx wrangler login
```

Browser will open → Click **"Allow"** → You're logged in! ✅

### Step 2: Configure API Key

```powershell
# Set your Gemini API key (paste when prompted)
npx wrangler secret put GEMINI_API_KEY
```

### Step 3: Deploy!

```powershell
npm run deploy
```

**Copy your Worker URL**:
```
https://pr-review-worker.your-username.workers.dev
```

✅ Backend deployed!

---

## 🎨 Part 2: Deploy Frontend (3 minutes)

### Step 1: Go to Cloudflare Pages

Visit: https://dash.cloudflare.com/pages

### Step 2: Create Project

1. Click **"Create a project"**
2. Click **"Connect to Git"**
3. Select **GitHub**
4. Authorize Cloudflare
5. Select repository: **`Vibhor2702/pr_review`**

### Step 3: Configure Build

```
Project name: pr-review
Branch: master
Build command: cd frontend && npm install && npm run build
Output directory: frontend/dist
```

### Step 4: Add Environment Variable

Click **"Add variable"**:
```
Name:  VITE_API_URL
Value: https://pr-review-worker.your-username.workers.dev
```

⚠️ **Important**: Use YOUR actual Worker URL from Part 1!

### Step 5: Deploy

Click **"Save and Deploy"**

Wait ~2 minutes... ✅ Done!

**Your site**: `https://pr-review.pages.dev`

---

## 🧪 Test Your Deployment

### Test Backend

```powershell
# Health check
curl https://pr-review-worker.your-username.workers.dev/api/status

# Expected: {"ok": true, "service": "PR Review API"}
```

### Test Frontend

1. Visit: `https://pr-review.pages.dev`
2. Open DevTools (F12) → Console
3. Should see: `🔗 API Base URL: https://pr-review-worker...`
4. Try **"Try Demo"** button
5. Should see AI-generated review!

✅ **Everything working!**

---

## 🛠️ Local Development

### Run Backend Locally

```powershell
cd workers
npm run dev
```

Runs at: `http://localhost:8787`

### Run Frontend Locally

```powershell
cd frontend
npm install
npm run dev
```

Runs at: `http://localhost:5173`

Update `frontend/.env.local`:
```
VITE_API_URL=http://localhost:8787
```

---

## 📊 Monitor Your App

### View Analytics

- **Workers**: https://dash.cloudflare.com/workers
- **Pages**: https://dash.cloudflare.com/pages

### Live Logs

```powershell
cd workers
npm run tail
```

Streams real-time logs from your Worker!

---

## 🔄 Update & Redeploy

### Update Backend

```powershell
cd workers
# Make your changes...
npm run deploy
```

Deploys in ~30 seconds!

### Update Frontend

```powershell
# Make your changes...
git add .
git commit -m "Update feature"
git push origin master
```

Cloudflare Pages auto-deploys in ~2 minutes!

---

## 🐛 Troubleshooting

### "GEMINI_API_KEY not configured"

```powershell
cd workers
npx wrangler secret put GEMINI_API_KEY
```

### "API Connection Failed" in Frontend

1. Go to Cloudflare Pages → Your project
2. Settings → Environment Variables
3. Check `VITE_API_URL` is correct
4. Redeploy: Deployments → Retry deployment

### CORS Errors

Edit `workers/wrangler.toml`:
```toml
[vars]
ALLOWED_ORIGINS = "https://pr-review.pages.dev,https://*.pages.dev"
```

Then redeploy:
```powershell
npm run deploy
```

### Worker Not Updating

```powershell
npx wrangler deploy --no-cache
```

---

## 📝 API Endpoints

### Health Check
```
GET /api/status
```

### Code Review
```
POST /api/review
Body: {
  "diff": "+code changes here",
  "repo": "username/repo",
  "author": "developer"
}
```

---

## 💰 Free Tier Limits

| Service | Free Tier | Typical Usage | Cost |
|---------|-----------|---------------|------|
| **Workers** | 100K req/day | ~500/day | $0 |
| **Pages** | Unlimited | 10GB/month | $0 |
| **Gemini** | 60 req/min | ~100/day | $0 |
| **Total** | | | **$0/month** ✨ |

---

## ✅ Deployment Checklist

### Backend
- [ ] `cd workers && npm install`
- [ ] `npx wrangler login`
- [ ] `npx wrangler secret put GEMINI_API_KEY`
- [ ] `npm run deploy`
- [ ] Copy Worker URL
- [ ] Test: `curl <worker-url>/api/status`

### Frontend
- [ ] Go to dash.cloudflare.com/pages
- [ ] Connect GitHub repository
- [ ] Configure build settings
- [ ] Add `VITE_API_URL` environment variable
- [ ] Deploy
- [ ] Test site loads
- [ ] Test API connection works

### Verification
- [ ] Backend returns `{"ok": true}`
- [ ] Frontend loads without errors
- [ ] Demo review works
- [ ] No CORS errors in console

---

## 🎯 Quick Commands Reference

```powershell
# Backend
cd workers
npm install                          # Install dependencies
npm run dev                          # Run locally (port 8787)
npx wrangler login                   # Login to Cloudflare
npx wrangler secret put GEMINI_KEY   # Set API key
npm run deploy                       # Deploy to production
npm run tail                         # View live logs

# Frontend
cd frontend
npm install                          # Install dependencies
npm run dev                          # Run locally (port 5173)
npm run build                        # Build for production

# Git
git add .
git commit -m "Update"
git push origin master               # Auto-deploys frontend
```

---

## 🎉 Success!

Your PR Review Agent is now:
- ✅ **Live globally** on Cloudflare's edge network
- ✅ **Serverless** - no servers to manage
- ✅ **Free forever** - $0/month
- ✅ **Auto-scaling** - handles any traffic
- ✅ **SSL secured** - automatic HTTPS
- ✅ **Fast** - < 50ms response time worldwide

### Your Live URLs

| Service | URL |
|---------|-----|
| **Frontend** | https://pr-review.pages.dev |
| **Backend** | https://pr-review-worker.*.workers.dev |
| **GitHub** | https://github.com/Vibhor2702/pr_review |

---

## 📞 Need Help?

- **Cloudflare Docs**: https://developers.cloudflare.com/workers/
- **Gemini API**: https://ai.google.dev/docs
- **GitHub Issues**: https://github.com/Vibhor2702/pr_review/issues

---

**Total deployment time: ~6 minutes** ⚡

Made with ❤️ using Cloudflare Workers + Pages + Google Gemini AI
