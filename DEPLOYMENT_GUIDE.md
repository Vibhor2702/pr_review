# 🚀 Complete Free Hosting Deployment Guide

This guide will walk you through deploying the **PR Review Agent** using:
- **Backend**: Railway.app (Free Tier - No Credit Card)
- **Frontend**: Cloudflare Pages (Free Tier - No Credit Card)

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Deployment (Railway)](#backend-deployment-railway)
3. [Frontend Deployment (Cloudflare Pages)](#frontend-deployment-cloudflare-pages)
4. [Environment Configuration](#environment-configuration)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)
7. [Portfolio Integration](#portfolio-integration)

---

## 🔧 Prerequisites

### Required Accounts (All Free, No Credit Card)
- ✅ GitHub account with this repository
- ✅ Railway.app account (sign up at https://railway.app)
- ✅ Cloudflare account (sign up at https://cloudflare.com)
- ✅ Google Gemini API key (get from https://makersuite.google.com/app/apikey)

### Repository Setup
```bash
git clone https://github.com/Vibhor2702/pr_review.git
cd pr_review
```

---

## 🔹 Backend Deployment (Railway)

### Step 1: Create Railway Project

1. **Go to Railway Dashboard**
   - Visit https://railway.app/dashboard
   - Click **"New Project"**

2. **Deploy from GitHub**
   - Select **"Deploy from GitHub repo"**
   - Choose **`Vibhor2702/pr_review`**
   - Railway will automatically detect it's a Python project

3. **Configure Build Settings**
   - Railway automatically uses `railway.json` configuration
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn --bind 0.0.0.0:$PORT 'src.server:create_app()'`

### Step 2: Set Environment Variables

In Railway Dashboard → Your Project → Variables, add:

```bash
# Required
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Auto-set by Railway
PORT=8080

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=0

# Optional Git Provider Tokens
GITHUB_TOKEN=your_github_token_if_needed
GITLAB_TOKEN=your_gitlab_token_if_needed
BITBUCKET_TOKEN=your_bitbucket_token_if_needed

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8080

# LLM Configuration
LLM_TEMPERATURE=0.3
LLM_MODEL=gemini-1.5-flash

# CORS Configuration
CORS_ORIGINS=https://pr-review.pages.dev,https://*.pages.dev
```

### Step 3: Get Your Railway URL

1. After deployment completes, go to **"Settings"** → **"Domains"**
2. Railway will provide a URL like: `https://pr-review-production.up.railway.app`
3. **Save this URL** - you'll need it for frontend configuration

### Step 4: Verify Backend

Test your API:
```bash
curl https://pr-review-production.up.railway.app/health
# Should return: {"status":"healthy","version":"1.0.0"}
```

---

## 🌐 Frontend Deployment (Cloudflare Pages)

### Step 1: Connect to Cloudflare Pages

1. **Go to Cloudflare Dashboard**
   - Visit https://dash.cloudflare.com
   - Navigate to **"Workers & Pages"** → **"Create Application"**
   - Select **"Pages"** → **"Connect to Git"**

2. **Select Repository**
   - Choose **`Vibhor2702/pr_review`**
   - Grant Cloudflare access to your repository

### Step 2: Configure Build Settings

Set the following in Cloudflare Pages:

```yaml
Framework preset: None (or Vite)
Build command: cd frontend && npm install && npm run build
Build output directory: frontend/dist
Root directory: /
```

### Step 3: Set Environment Variables

In Cloudflare Pages → Settings → Environment Variables:

```bash
# Production Environment
VITE_API_URL=https://pr-review-production.up.railway.app

# Preview Environment (optional)
VITE_API_URL=https://pr-review-production.up.railway.app
```

**Important**: Use your actual Railway URL from Step 3 above!

### Step 4: Configure Custom Domain (Optional)

1. In Cloudflare Pages → **"Custom domains"**
2. Default domain: `https://pr-review.pages.dev`
3. You can add custom domain if you have one

### Step 5: Deploy

1. Click **"Save and Deploy"**
2. Cloudflare will automatically:
   - Install dependencies
   - Build the React app
   - Deploy to global CDN
3. Deployment usually takes 2-3 minutes

---

## 🔐 Environment Configuration

### Backend (.env.railway)
Already configured in Railway dashboard. The app reads from environment variables.

### Frontend (.env.production)
Created automatically during build with `VITE_API_URL` from Cloudflare environment variables.

---

## ✅ Verification

### 1. Test Backend API

```bash
# Health check
curl https://pr-review-production.up.railway.app/health

# API info
curl https://pr-review-production.up.railway.app/

# Demo review
curl -X POST https://pr-review-production.up.railway.app/demo/review \
  -H "Content-Type: application/json" \
  -d '{"provider":"github","owner":"test","repo":"demo","pr_number":1}'
```

### 2. Test Frontend

1. Visit: `https://pr-review.pages.dev`
2. Try the demo mode first (no API calls needed)
3. Test a real PR review with your GitHub token

### 3. Test Integration

1. Open browser DevTools → Network tab
2. Create a new review in the frontend
3. Verify API calls go to your Railway backend
4. Check for CORS errors (should be none)

---

## 🚨 Troubleshooting

### Backend Issues

**Problem**: 500 Error on Railway
```bash
# Check logs in Railway Dashboard
# Common issues:
- Missing GEMINI_API_KEY
- Python dependencies not installed
- Port binding issues
```

**Solution**:
```bash
# Verify environment variables are set
# Check Railway logs for specific errors
# Ensure requirements.txt includes all dependencies
```

### Frontend Issues

**Problem**: API calls failing (CORS errors)
```bash
# Check browser console for errors like:
# "Access to fetch at '...' from origin '...' has been blocked by CORS"
```

**Solution**:
```bash
# Verify VITE_API_URL is correctly set in Cloudflare
# Ensure Railway backend has correct CORS_ORIGINS
# Check that your Railway URL is correct
```

**Problem**: Build fails on Cloudflare
```bash
# Common issues:
- Build command incorrect
- Node version mismatch
- Missing dependencies
```

**Solution**:
```bash
# In Cloudflare build settings:
Build command: cd frontend && npm install && npm run build
Output directory: frontend/dist
Node version: 20 (set in Environment Variables: NODE_VERSION=20)
```

### Integration Issues

**Problem**: Frontend can't connect to backend

**Solution**:
1. Check `VITE_API_URL` in Cloudflare Pages settings
2. Verify Railway backend is running (check health endpoint)
3. Test API directly with curl
4. Check browser DevTools → Network tab for failed requests

---

## 🎯 Portfolio Integration

### Add to Your Portfolio

Once deployed, add this to your `projects.json`:

```json
{
  "id": "pr-review-agent",
  "title": "PR Review Agent",
  "description": "Professional automated Pull Request Review Agent using Google Gemini AI. Analyzes code quality, security, and provides actionable feedback across GitHub, GitLab, and Bitbucket.",
  "longDescription": "Full-stack application that leverages Google Gemini AI and static analysis tools to provide comprehensive pull request reviews. Features real-time analytics, multi-provider support, and automated CI/CD integration.",
  "tech": [
    "Python",
    "Flask",
    "React",
    "TypeScript",
    "Google Gemini AI",
    "Tailwind CSS",
    "Railway",
    "Cloudflare Pages",
    "GitHub Actions"
  ],
  "features": [
    "AI-powered code review using Google Gemini",
    "Static code analysis (Bandit, Radon, Flake8)",
    "Multi-provider support (GitHub, GitLab, Bitbucket)",
    "Real-time PR scoring and grading",
    "Automated CI/CD integration",
    "Professional React dashboard with analytics"
  ],
  "links": {
    "demo": "https://pr-review.pages.dev",
    "api": "https://pr-review-production.up.railway.app",
    "source": "https://github.com/Vibhor2702/pr_review",
    "documentation": "https://github.com/Vibhor2702/pr_review#readme"
  },
  "images": {
    "thumbnail": "/projects/pr-review/thumbnail.png",
    "screenshots": [
      "/projects/pr-review/dashboard.png",
      "/projects/pr-review/review.png",
      "/projects/pr-review/analytics.png"
    ]
  },
  "status": "production",
  "featured": true,
  "category": "Full Stack",
  "date": "2025-09-22",
  "badges": [
    {
      "label": "Frontend",
      "url": "https://img.shields.io/badge/Cloudflare-Pages-orange",
      "link": "https://pr-review.pages.dev"
    },
    {
      "label": "Backend",
      "url": "https://img.shields.io/badge/Railway-API-blue",
      "link": "https://pr-review-production.up.railway.app"
    },
    {
      "label": "CI/CD",
      "url": "https://github.com/Vibhor2702/pr_review/actions/workflows/deploy.yml/badge.svg",
      "link": "https://github.com/Vibhor2702/pr_review/actions"
    }
  ]
}
```

### Add Badges to README

Add these to your `README.md`:

```markdown
# PR Review Agent

[![Frontend Live](https://img.shields.io/badge/Cloudflare-Pages-orange)](https://pr-review.pages.dev)
[![Backend API](https://img.shields.io/badge/Railway-API-blue)](https://pr-review-production.up.railway.app)
[![Deploy Status](https://github.com/Vibhor2702/pr_review/actions/workflows/deploy.yml/badge.svg)](https://github.com/Vibhor2702/pr_review/actions)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

🚀 **Live Demo**: [https://pr-review.pages.dev](https://pr-review.pages.dev)
🔌 **API Endpoint**: [https://pr-review-production.up.railway.app](https://pr-review-production.up.railway.app)
```

---

## 📊 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Repository                        │
│              github.com/Vibhor2702/pr_review                │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ (Git Push to main)
                 │
         ┌───────┴────────┐
         │                │
         ▼                ▼
┌─────────────────┐  ┌──────────────────┐
│  Railway.app    │  │ Cloudflare Pages │
│   (Backend)     │  │   (Frontend)     │
├─────────────────┤  ├──────────────────┤
│ Python Flask    │  │ React + Vite     │
│ Gunicorn        │  │ TypeScript       │
│ Google Gemini   │  │ Tailwind CSS     │
│ Static Analysis │  │ Radix UI         │
└────────┬────────┘  └────────┬─────────┘
         │                    │
         │    API Calls       │
         │◄───────────────────┤
         │   (CORS Enabled)   │
         │                    │
         ▼                    ▼
┌─────────────────────────────────────┐
│          Global Users               │
│  https://pr-review.pages.dev        │
└─────────────────────────────────────┘
```

---

## 🎉 Success Checklist

- [x] Railway backend deployed and responding
- [x] Cloudflare Pages frontend deployed
- [x] API calls working between frontend and backend
- [x] No CORS errors
- [x] Health endpoint returns 200 OK
- [x] Demo mode working in frontend
- [x] Real PR review working (with valid tokens)
- [x] GitHub Actions workflow running
- [x] Badges added to README
- [x] Portfolio entry created

---

## 📞 Support

If you encounter issues:

1. **Check Railway Logs**: Railway Dashboard → Your Project → Deployments → View Logs
2. **Check Cloudflare Build Logs**: Cloudflare Pages → Your Site → View Build
3. **Test API Directly**: Use curl or Postman to test backend endpoints
4. **Browser DevTools**: Check Network and Console tabs for errors
5. **GitHub Issues**: Open an issue at https://github.com/Vibhor2702/pr_review/issues

---

## 🔄 Continuous Deployment

Both Railway and Cloudflare Pages support automatic deployments:

- **Railway**: Auto-deploys on push to `main` branch
- **Cloudflare Pages**: Auto-deploys on push to `main` branch
- **GitHub Actions**: Runs tests on every push and PR

To trigger a deployment:
```bash
git add .
git commit -m "Update deployment configuration"
git push origin main
```

Both platforms will automatically detect the changes and redeploy within 2-3 minutes.

---

## 🌟 Next Steps

1. **Custom Domain**: Add your own domain in Cloudflare Pages settings
2. **Analytics**: Add Cloudflare Web Analytics (free)
3. **Monitoring**: Set up Railway webhooks for deployment notifications
4. **CI/CD**: Enhance GitHub Actions workflow with more tests
5. **Documentation**: Add API documentation with Swagger/OpenAPI

---

## 📝 Notes

- **Railway Free Tier**: 500 hours/month, $5 credit (sufficient for development)
- **Cloudflare Pages**: Unlimited bandwidth and requests
- **No Credit Card Required**: Both services offer generous free tiers
- **Auto-Sleep**: Railway may sleep after inactivity, first request wakes it up (~30s)
- **CDN**: Cloudflare Pages uses global CDN for fast loading worldwide

---

**Happy Deploying! 🚀**

For questions or issues, please open an issue on GitHub or contact the maintainers.
