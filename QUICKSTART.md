# ⚡ Quick Start - 5 Minute Deployment

Deploy your PR Review Agent to Cloudflare in 5 minutes!

## 🎯 What You'll Get

- ✅ Serverless API on Cloudflare Workers (100K requests/day FREE)
- ✅ React frontend on Cloudflare Pages (Unlimited bandwidth FREE)
- ✅ Google Gemini AI integration (60 requests/min FREE)
- ✅ Global CDN with 300+ edge locations
- ✅ Automatic SSL/HTTPS
- ✅ Zero maintenance, auto-scaling

**Total Cost: $0/month forever!** 💰

---

## 📋 Prerequisites (2 minutes)

1. **Cloudflare Account**: https://dash.cloudflare.com/sign-up (FREE)
2. **Google Gemini API Key**: https://aistudio.google.com/app/apikey (FREE)
3. **Node.js 18+**: https://nodejs.org/ (if not installed)

---

## 🚀 Deploy Backend (2 minutes)

```bash
# 1. Go to workers directory
cd workers

# 2. Install dependencies
npm install

# 3. Login to Cloudflare (opens browser)
npx wrangler login

# 4. Set your Gemini API key (paste when prompted)
npx wrangler secret put GEMINI_API_KEY

# 5. Deploy! 🎉
npm run deploy
```

**Copy the Worker URL** shown after deployment (looks like):
```
https://pr-review-worker.your-username.workers.dev
```

✅ Backend is live!

---

## 🎨 Deploy Frontend (2 minutes)

### Via Cloudflare Dashboard (Recommended)

1. Go to: https://dash.cloudflare.com/pages
2. Click **"Create a project"**
3. Connect GitHub repository: `Vibhor2702/pr_review`
4. Configure:
   ```
   Project name: pr-review
   Branch: master
   Build command: cd frontend && npm install && npm run build
   Output directory: frontend/dist
   ```

5. Add Environment Variable:
   ```
   VITE_API_URL = https://pr-review-worker.your-username.workers.dev
   ```
   (Use your actual Worker URL from above!)

6. Click **"Save and Deploy"**

Your site will be at:
```
https://pr-review.pages.dev
```

✅ Frontend is live!

---

## 🧪 Test It Works

### 1. Test Backend API

```bash
curl https://pr-review-worker.your-username.workers.dev/api/status
```

Should return:
```json
{
  "ok": true,
  "service": "PR Review API",
  "version": "1.0.0"
}
```

### 2. Test Frontend

Visit: `https://pr-review.pages.dev`

- Should load React app
- Open browser console (F12)
- Should see: `🔗 API Base URL: https://pr-review-worker...`

### 3. Test Full Review

1. Click **"New Review"** or **"Try Demo"**
2. Enter test data
3. Click **"Review PR"**
4. See AI-generated review! 🎉

---

## 🎯 That's It!

Your PR Review Agent is now:
- ✅ Live globally on Cloudflare
- ✅ Serverless and auto-scaling
- ✅ Running forever for FREE
- ✅ SSL secured with HTTPS
- ✅ Backed by Google Gemini AI

### Your Live URLs

| Service | URL |
|---------|-----|
| **Frontend** | https://pr-review.pages.dev |
| **Backend API** | https://pr-review-worker.*.workers.dev |
| **GitHub** | https://github.com/Vibhor2702/pr_review |

---

## 📚 What's Next?

### Local Development

```bash
# Backend (Workers)
cd workers
npm run dev              # Runs at localhost:8787

# Frontend
cd frontend
npm install
npm run dev             # Runs at localhost:5173
```

### Monitor Your App

- **Analytics**: https://dash.cloudflare.com/workers
- **Logs**: `cd workers && npm run tail`
- **Pages Dashboard**: https://dash.cloudflare.com/pages

### Customize

- **Edit AI prompts**: `workers/src/index.ts` → `analyzeWithGemini()`
- **Add features**: Edit React components in `frontend/src/`
- **Configure**: Update `workers/wrangler.toml`

---

## 🐛 Troubleshooting

### "GEMINI_API_KEY not configured"
```bash
cd workers
npx wrangler secret put GEMINI_API_KEY
```

### "API Connection Failed" in frontend
1. Check Cloudflare Pages → Environment Variables
2. Verify `VITE_API_URL` is your Worker URL
3. Redeploy frontend

### CORS errors
Update `workers/wrangler.toml`:
```toml
[vars]
ALLOWED_ORIGINS = "https://pr-review.pages.dev,https://*.pages.dev"
```

---

## 📖 Full Documentation

- **Complete Guide**: `CLOUDFLARE_COMPLETE_GUIDE.md`
- **Workers Details**: `workers/README.md`
- **Architecture**: See main `README.md`

---

## 💡 Pro Tips

1. **Custom Domain**: Add `api.your-domain.com` in Workers dashboard
2. **Rate Limiting**: Enable in Cloudflare → Security → WAF
3. **Caching**: Add cache headers for faster responses
4. **Monitoring**: Set up alerts in Cloudflare dashboard

---

## ✅ Deployment Checklist

- [ ] Cloudflare account created
- [ ] Google Gemini API key obtained
- [ ] Workers deployed: `npm run deploy`
- [ ] Worker URL copied
- [ ] Pages project created
- [ ] Environment variable `VITE_API_URL` set
- [ ] Frontend deployed
- [ ] Tested `/api/status` endpoint
- [ ] Tested frontend loads
- [ ] Tested AI review works

---

**Questions?** See `CLOUDFLARE_COMPLETE_GUIDE.md` or open an issue on GitHub!

Made with ❤️ using Cloudflare Workers + Pages + Google Gemini AI
