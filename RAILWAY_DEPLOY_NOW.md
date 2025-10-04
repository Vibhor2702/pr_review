# 🚀 RAILWAY DEPLOYMENT - START HERE!

## Why Deploy Railway First?
The frontend needs the backend URL to work. Deploy backend first, then frontend.

---

## 📋 Railway Deployment Steps (5 minutes)

### Step 1: Create Railway Account
1. Go to: **https://railway.app**
2. Click **"Login"** or **"Start a New Project"**
3. Sign in with **GitHub** (easiest method)
4. ✅ No credit card required!

### Step 2: Create New Project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. If this is your first time:
   - Click **"Configure GitHub App"**
   - Grant Railway access to your repositories
   - Select **"Only select repositories"**
   - Choose **"Vibhor2702/pr_review"**

### Step 3: Deploy Repository
1. Search for **"pr_review"** or **"Vibhor2702/pr_review"**
2. Click on the repository
3. Railway will automatically:
   - Detect it's a Python project
   - Read `railway.json` configuration
   - Read `Procfile` for start command
   - Install dependencies from `requirements.txt`

### Step 4: Add Environment Variable
1. In your Railway project, click **"Variables"** tab
2. Click **"+ New Variable"**
3. Add:
   ```
   Name: GEMINI_API_KEY
   Value: your_actual_gemini_api_key_here
   ```
4. Get Gemini key from: https://makersuite.google.com/app/apikey

### Step 5: Wait for Deployment
1. Railway will start building (watch the logs)
2. Wait ~2-3 minutes
3. Deployment status will show **"Active"** when ready

### Step 6: Get Your Railway URL
1. Click **"Settings"** tab
2. Scroll to **"Domains"** section
3. Click **"Generate Domain"**
4. Copy the generated URL (like: `pr-review-production-XXXX.up.railway.app`)

### Step 7: Test Your Backend
```bash
# Replace with your actual Railway URL
curl https://your-railway-url.up.railway.app/health

# Should return:
# {"status":"healthy","version":"1.0.0"}
```

---

## ✅ Success Checklist

- [ ] Railway account created
- [ ] GitHub connected to Railway
- [ ] Project deployed from repository
- [ ] GEMINI_API_KEY environment variable added
- [ ] Deployment status shows "Active"
- [ ] Domain generated
- [ ] Health endpoint returns 200 OK

---

## 🐛 Troubleshooting

### Build Fails
**Problem**: Deployment fails during build
**Solution**: 
- Check Railway logs for specific error
- Ensure `requirements.txt` is in root directory
- Verify all dependencies are listed

### Environment Variable Missing
**Problem**: App crashes with "Configuration error"
**Solution**:
- Add `GEMINI_API_KEY` in Railway Variables tab
- Restart deployment after adding variable

### Port Binding Error
**Problem**: "Error: Address already in use"
**Solution**:
- Railway auto-sets `PORT` environment variable
- Our code already handles this in `src/server.py`
- No action needed!

### 404 Error on Domain
**Problem**: Domain returns 404
**Solution**:
- Wait 1-2 minutes after "Generate Domain"
- Railway needs time to route the domain
- Try again after waiting

---

## 📝 After Successful Deployment

Once your Railway backend is working:

1. ✅ Save your Railway URL
2. ✅ Test the health endpoint
3. ✅ Test the API root endpoint
4. ✅ Now you're ready to deploy the frontend!

**Next Step**: Deploy frontend to Cloudflare Pages with your Railway URL

---

## 🎯 Common Railway URLs

Your Railway URL will look like one of these:
- `https://pr-review-production.up.railway.app`
- `https://pr-review-production-XXXX.up.railway.app`
- `https://your-project-name.up.railway.app`

Make note of your actual URL - you'll need it for Cloudflare Pages!

---

## 💡 Pro Tips

1. **Enable Auto-Deploy**: Railway auto-deploys on git push by default ✅
2. **Monitor Logs**: Click "Deployments" → "View Logs" to debug issues
3. **Environment Variables**: You can add more variables later (GitHub tokens, etc.)
4. **Metrics**: Railway shows CPU, Memory, and Network usage
5. **Free Tier**: You get $5 credit monthly (500 hours) - plenty for development!

---

## ⏱️ Deployment Timeline

- Account creation: 1 minute
- Repository connection: 1 minute
- Initial deployment: 2-3 minutes
- **Total**: ~5 minutes

---

## 🔗 Useful Links

- **Railway Dashboard**: https://railway.app/dashboard
- **Railway Docs**: https://docs.railway.app
- **Railway Status**: https://status.railway.app
- **Get Gemini Key**: https://makersuite.google.com/app/apikey

---

## ✅ Verification Commands

After deployment, test these endpoints:

```bash
# Replace YOUR_URL with actual Railway URL

# Health check
curl https://YOUR_URL/health

# API information
curl https://YOUR_URL/

# Providers status
curl https://YOUR_URL/providers

# Demo review
curl -X POST https://YOUR_URL/demo/review \
  -H "Content-Type: application/json" \
  -d '{"provider":"github","owner":"test","repo":"demo","pr_number":1}'
```

All should return valid JSON responses!

---

**Ready to deploy?** Go to https://railway.app/new and follow the steps above!
