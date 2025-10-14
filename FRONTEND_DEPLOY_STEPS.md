# 🚀 Frontend Deployment to Cloudflare Pages

## ✅ Backend Status
Your backend is **DEPLOYED AND WORKING**! ✨

**Live API URL:** https://pr-review-worker.kenshifan3000.workers.dev

Test it: https://pr-review-worker.kenshifan3000.workers.dev/api/status

---

## 📋 Frontend Deployment Steps (5 minutes)

### Step 1: Open Cloudflare Dashboard
Visit: **https://dash.cloudflare.com/302ec149f11d42e756816a0f6e105a09/pages**

### Step 2: Create New Pages Project
1. Click **"Create application"**
2. Click **"Connect to Git"**
3. Select **"GitHub"** (authorize if needed)

### Step 3: Select Repository
1. Choose repository: **`Vibhor2702/pr_review`**
2. Click **"Begin setup"**

### Step 4: Configure Build Settings
Fill in these exact values:

```
Project name: pr-review
Production branch: master
Framework preset: React
Build command: cd frontend && npm install && npm run build
Build output directory: frontend/dist
Root directory: (leave empty)
```

### Step 5: Add Environment Variable
Click **"Add environment variable"**:
- **Variable name:** `VITE_API_URL`
- **Value:** `https://pr-review-worker.kenshifan3000.workers.dev`

### Step 6: Deploy!
1. Click **"Save and Deploy"**
2. Wait 2-3 minutes for build to complete ⏳
3. Your site will be live at: **`https://pr-review.pages.dev`**

---

## 🎯 After Deployment

### Test Your Application
1. Open: **https://pr-review.pages.dev**
2. Click **"New Review"**
3. Try a real PR:
   - Owner: `facebook`
   - Repo: `react`
   - PR Number: `27500`
4. Watch the AI analyze real code! 🤖

### Update CORS (if needed)
If you see CORS errors, update Workers CORS settings:

```bash
cd workers
# Edit wrangler.toml to add your Pages URL
npx wrangler deploy
```

---

## 🔗 Your Deployed URLs

| Service | URL | Status |
|---------|-----|--------|
| **Backend API** | https://pr-review-worker.kenshifan3000.workers.dev | ✅ LIVE |
| **Frontend** | https://pr-review.pages.dev | 🔄 Deploy Now |

---

## 🎨 Custom Domain (Optional)

Want a custom domain like `pr-review.yourdomain.com`?

1. Go to Cloudflare Pages → Your project → Custom domains
2. Click **"Set up a custom domain"**
3. Add your domain (must be on Cloudflare DNS)
4. SSL certificate auto-provisioned ✅

---

## 📊 Monitoring

### View Logs
- **Backend Logs:** Cloudflare Dashboard → Workers → pr-review-worker → Logs
- **Frontend Logs:** Cloudflare Dashboard → Pages → pr-review → Deployments

### Check Analytics
- **Backend Analytics:** Workers → Analytics (requests, errors, latency)
- **Frontend Analytics:** Pages → Web Analytics

---

## 🐛 Troubleshooting

### Build Fails
**Error:** "Command not found: vite"
**Fix:** Build command should be `cd frontend && npm install && npm run build`

### API Calls Fail
**Error:** CORS or 404
**Fix:** Verify `VITE_API_URL` in Pages environment variables

### Blank Page
**Error:** White screen, no errors
**Fix:** Check browser console, verify `frontend/dist` was built

---

## 🎉 Success Indicators

✅ **Backend Working:** /api/status returns 200
✅ **Frontend Deployed:** Site loads at pages.dev URL
✅ **Integration Working:** Can analyze real PRs

---

## 💰 Cost

**Total Cost:** **$0/month** 🎉

- Cloudflare Workers: 100,000 requests/day FREE
- Cloudflare Pages: Unlimited bandwidth FREE
- Google Gemini: 15 requests/minute FREE

---

## 🔄 Auto-Deployment

Every time you push to GitHub `master` branch:
1. ✅ Cloudflare Pages auto-deploys frontend
2. ✅ No action needed for backend (unless wrangler.toml changes)

---

**Need help?** Check the main `DEPLOY.md` or open an issue on GitHub.
