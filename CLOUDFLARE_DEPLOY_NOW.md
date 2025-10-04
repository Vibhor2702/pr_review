# 🚨 URGENT: Cloudflare Pages Deployment Steps

## The Issue
You're seeing `DNS_PROBE_FINISHED_NXDOMAIN` because the Cloudflare Pages site doesn't exist yet.

## ✅ Fix: Deploy to Cloudflare Pages (5 minutes)

### Step 1: Go to Cloudflare Dashboard
```
https://dash.cloudflare.com
```

### Step 2: Create Pages Project
1. Click **"Workers & Pages"** in the left sidebar
2. Click **"Create Application"** button
3. Select **"Pages"** tab
4. Click **"Connect to Git"**

### Step 3: Authorize GitHub
1. Click **"Connect GitHub"**
2. Authorize Cloudflare to access your repositories
3. Select **"Vibhor2702/pr_review"** repository

### Step 4: Configure Build Settings
```yaml
Project name: pr-review
Branch: master (or main)
Framework preset: None
Build command: cd frontend && npm install && npm run build
Build output directory: frontend/dist
Root directory: /
```

### Step 5: Environment Variables
Click **"Environment variables"** and add:
```bash
Variable name: VITE_API_URL
Value: https://pr-review-production.up.railway.app
```
(Or use your actual Railway URL if different)

### Step 6: Deploy!
1. Click **"Save and Deploy"**
2. Wait 2-3 minutes for build to complete
3. Your site will be live at: **https://pr-review.pages.dev**

---

## 🔍 Alternative: Check if Railway Backend is Deployed

Before deploying frontend, ensure your backend is working:

```bash
# Test Railway backend (if you've deployed it)
curl https://pr-review-production.up.railway.app/health
```

If this doesn't work, you need to deploy to Railway first:
1. Go to: https://railway.app/new
2. Deploy from GitHub: Vibhor2702/pr_review
3. Add environment variable: GEMINI_API_KEY=your_key
4. Wait for deployment (~2 minutes)
5. Copy your Railway URL

---

## 📋 Deployment Order

**Correct Order:**
1. ✅ Deploy Backend to Railway first
2. ✅ Get Railway URL
3. ✅ Deploy Frontend to Cloudflare with Railway URL in env vars

**Current Status:**
- [ ] Backend deployed to Railway?
- [ ] Frontend deployed to Cloudflare?

---

## 🎯 Quick Deployment Links

### Railway (Backend)
👉 **Start here:** https://railway.app/new

### Cloudflare Pages (Frontend)  
👉 **Then here:** https://dash.cloudflare.com

---

## 💡 Pro Tip

You can also deploy directly from Cloudflare CLI:

```bash
# Install Wrangler (Cloudflare CLI)
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Deploy pages (from project root)
wrangler pages deploy frontend/dist --project-name=pr-review
```

But the dashboard method is easier for first-time deployment!

---

## ✅ After Deployment

Once Cloudflare Pages finishes deploying:
1. You'll get a URL like: `https://pr-review.pages.dev`
2. Open it in your browser
3. It should connect to your Railway backend
4. No more DNS errors! 🎉

---

**Current Issue**: The site doesn't exist yet
**Solution**: Follow the steps above to create it!
**Time Required**: 5 minutes
