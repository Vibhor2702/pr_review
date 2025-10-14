# 🚀 Quick Setup Guide

## ✅ What's Fixed
- Removed 8+ unnecessary documentation files
- Created working `setup-key.ps1` script
- Fixed PowerShell syntax errors
- Cleaned up repository

## 🔑 Configure Your API Key

Run this command and paste your Gemini API key:

```powershell
.\setup-key.ps1
```

The script will:
1. Validate your API key format
2. Update `workers/.dev.vars` (local development)
3. Update Cloudflare Worker secret (production)
4. Verify security (gitignore check)
5. Test production API

## 📚 Documentation

- **README.md** - Project overview
- **DEPLOY.md** - Full deployment guide
- **USAGE_GUIDE.md** - How to use the app
- **DEMO.md** - Demo and examples

## 🌐 Your URLs

**Backend:** https://pr-review-worker.kenshifan3000.workers.dev
**Frontend:** https://pr-review.pages.dev (deploying now)

## 🧪 Test After Setup

```powershell
# Test local
cd workers
npm run dev
# Visit http://localhost:8787/api/status

# Test production
curl https://pr-review-worker.kenshifan3000.workers.dev/api/status
```

---

**That's it! Run `.\setup-key.ps1` now!** 🎉
