# 🚀 Quick Deployment Reference Card

## ⚡ Fastest Deployment Path

### 1. Railway Backend (2 minutes)
```bash
1. Visit: https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select: Vibhor2702/pr_review
4. Add variable: GEMINI_API_KEY = your_key_here
5. Deploy! ✅
6. Copy URL: https://pr-review-production.up.railway.app
```

### 2. Cloudflare Pages Frontend (3 minutes)
```bash
1. Visit: https://dash.cloudflare.com
2. Workers & Pages → Create → Pages → Connect to Git
3. Select: Vibhor2702/pr_review
4. Configure:
   Build command: cd frontend && npm install && npm run build
   Output directory: frontend/dist
5. Add environment variable:
   VITE_API_URL = https://pr-review-production.up.railway.app
6. Save and Deploy! ✅
7. Your URL: https://pr-review.pages.dev
```

---

## 📋 Deployment Checklist

### Before Deployment
- [ ] GitHub repository created and code pushed
- [ ] Google Gemini API key obtained
- [ ] Railway account created (no credit card)
- [ ] Cloudflare account created (no credit card)

### Backend (Railway)
- [ ] Project connected to GitHub
- [ ] `GEMINI_API_KEY` environment variable set
- [ ] Health endpoint returns 200: `/health`
- [ ] API info endpoint works: `/`
- [ ] Demo endpoint works: `/demo/review`

### Frontend (Cloudflare Pages)
- [ ] Project connected to GitHub
- [ ] `VITE_API_URL` environment variable set to Railway URL
- [ ] Build completes successfully
- [ ] Site loads at `https://pr-review.pages.dev`
- [ ] Can navigate through all tabs
- [ ] No CORS errors in console

### Integration
- [ ] Frontend can call backend API
- [ ] Demo mode works without errors
- [ ] Real PR review works (with valid token)
- [ ] No console errors
- [ ] All features functional

---

## 🔧 Essential Environment Variables

### Railway (Backend)
```bash
GEMINI_API_KEY=your_gemini_api_key_here  # REQUIRED
PORT=8080                                 # Auto-set by Railway
FLASK_ENV=production                      # Recommended
```

### Cloudflare Pages (Frontend)
```bash
VITE_API_URL=https://pr-review-production.up.railway.app  # REQUIRED
```

---

## 🔗 Live URLs Template

Once deployed, your URLs will be:

```
Frontend: https://pr-review.pages.dev
Backend:  https://pr-review-production.up.railway.app
Health:   https://pr-review-production.up.railway.app/health
API Docs: https://pr-review-production.up.railway.app/
```

---

## 🧪 Quick Test Commands

### Test Backend
```bash
# Health check
curl https://pr-review-production.up.railway.app/health

# API information
curl https://pr-review-production.up.railway.app/

# Demo review
curl -X POST https://pr-review-production.up.railway.app/demo/review \
  -H "Content-Type: application/json" \
  -d '{"provider":"github","owner":"test","repo":"demo","pr_number":1}'
```

### Test Frontend
1. Open: https://pr-review.pages.dev
2. Open DevTools (F12) → Console
3. Check for errors (should be none)
4. Try demo mode
5. Try real PR review

---

## 🐛 Quick Troubleshooting

### Backend Issues
| Problem | Solution |
|---------|----------|
| 500 Error | Check Railway logs, verify `GEMINI_API_KEY` is set |
| App not starting | Check `railway.json` and `Procfile` are committed |
| Slow first request | Railway free tier sleeps after inactivity (~30s wake) |

### Frontend Issues
| Problem | Solution |
|---------|----------|
| CORS errors | Verify `VITE_API_URL` in Cloudflare matches Railway URL |
| Build fails | Check `package.json` and build command in Cloudflare |
| Blank page | Check browser console for errors, verify dist/ built |

### Integration Issues
| Problem | Solution |
|---------|----------|
| API calls fail | Verify CORS settings in `src/server.py` |
| 404 on API | Check Railway URL is correct in Cloudflare env vars |
| Mixed content | Ensure both URLs use HTTPS |

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `DEPLOYMENT_GUIDE.md` | Complete deployment walkthrough |
| `README.md` | Project overview with deployment badges |
| `railway.json` | Railway deployment configuration |
| `Procfile` | Railway start command |
| `wrangler.toml` | Cloudflare Pages configuration |
| `.github/workflows/deploy.yml` | CI/CD automation |

---

## 🎯 Success Indicators

✅ **Backend Deployed** when:
- Railway dashboard shows "Active"
- Health endpoint returns `{"status":"healthy"}`
- No errors in Railway logs

✅ **Frontend Deployed** when:
- Cloudflare Pages shows "Active"
- Site loads at pages.dev URL
- No errors in browser console

✅ **Integration Working** when:
- Demo mode works in frontend
- Real PR review completes
- No CORS or network errors

---

## 🚀 Auto-Deploy

Both platforms auto-deploy on git push to `main`:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Railway: ~2 minutes to redeploy
Cloudflare: ~1 minute to redeploy

---

## 📞 Quick Help

- **Railway Logs**: Railway Dashboard → Project → Deployments → View Logs
- **Cloudflare Build Logs**: Cloudflare → Site → View Build
- **GitHub Actions**: Repository → Actions tab
- **Full Guide**: See `DEPLOYMENT_GUIDE.md`

---

## 💡 Pro Tips

1. **Test Locally First**: Run frontend and backend locally before deploying
2. **Check Logs**: Always check deployment logs for errors
3. **Environment Variables**: Double-check spelling and values
4. **CORS**: Ensure backend allows frontend domain
5. **API URL**: Make sure frontend has correct backend URL
6. **Cache**: Clear browser cache if changes don't appear
7. **Railway Sleep**: First request may be slow (wakes from sleep)
8. **Gemini API**: Verify your Gemini API key is active

---

**Need more help?** See `DEPLOYMENT_GUIDE.md` for detailed instructions.

---

**Deployment Time Estimate**: 5-7 minutes total (once accounts are created)
