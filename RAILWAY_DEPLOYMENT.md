# Railway Deployment Guide

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Google Gemini API Key**: Get one from [Google AI Studio](https://makersuite.google.com/)
3. **GitHub Token** (optional): For private repository access

## Quick Deploy to Railway

### Option 1: Deploy from GitHub (Recommended)

1. **Push your code to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. **Deploy to Railway**:
   - Go to [railway.app](https://railway.app) and log in
   - Click "New Project"
   - Choose "Deploy from GitHub repo"
   - Select your repository
   - Railway will automatically detect it's a Python app

3. **Set Environment Variables**:
   Go to your project settings and add these variables:
   ```
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   GITHUB_TOKEN=your_github_token_here (optional)
   ```

### Option 2: Deploy from Local

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize and Deploy**:
   ```bash
   railway link
   railway up
   ```

4. **Set Environment Variables**:
   ```bash
   railway variables set GEMINI_API_KEY=your_actual_gemini_api_key_here
   railway variables set GITHUB_TOKEN=your_github_token_here
   ```

## Configuration Files Created

### 1. `Procfile`
Tells Railway how to start your app:
```
web: gunicorn --bind 0.0.0.0:$PORT src.server:create_app()
```

### 2. `railway.json`
Railway-specific configuration:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn --bind 0.0.0.0:$PORT src.server:create_app()",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 3. `runtime.txt`
Specifies Python version:
```
python-3.11.5
```

### 4. `.railwayignore`
Excludes unnecessary files from deployment

### 5. Updated `requirements.txt`
Added production dependencies:
- `gunicorn>=21.0.0` - Production WSGI server
- `flask-cors>=4.0.0` - Cross-origin resource sharing

## Environment Variables

Set these in your Railway project dashboard:

### Required:
- `GEMINI_API_KEY` - Your Google Gemini API key

### Optional:
- `GITHUB_TOKEN` - For private GitHub repositories
- `GITLAB_TOKEN` - For GitLab repositories  
- `BITBUCKET_TOKEN` - For Bitbucket repositories
- `GEMINI_MODEL` - AI model (default: gemini-1.5-flash)
- `LLM_TEMPERATURE` - AI temperature (default: 0.3)

## Testing Your Deployment

1. **Check Health Endpoint**:
   Visit: `https://your-app-name.up.railway.app/health`
   
2. **Test API**:
   ```bash
   curl https://your-app-name.up.railway.app/config
   ```

3. **Test Demo Review**:
   ```bash
   curl -X POST https://your-app-name.up.railway.app/demo/review \
     -H "Content-Type: application/json" \
     -d '{}'
   ```

## Frontend Deployment (Next Steps)

After your backend is deployed:

1. **Update Frontend API URL**:
   In `frontend/src/lib/api.ts`, update the base URL:
   ```typescript
   const BASE_URL = 'https://your-app-name.up.railway.app'
   ```

2. **Deploy Frontend to Vercel**:
   ```bash
   cd frontend
   npm run build
   npx vercel --prod
   ```

## Troubleshooting

### Common Issues:

1. **Build Fails**: 
   - Check `requirements.txt` for any missing dependencies
   - Ensure Python version is compatible

2. **App Crashes**:
   - Check Railway logs for error messages
   - Verify environment variables are set correctly
   - Ensure GEMINI_API_KEY is valid

3. **CORS Issues**:
   - Backend includes CORS headers for common frontend domains
   - Add your specific domain if needed

4. **Port Issues**:
   - Railway automatically sets the PORT environment variable
   - App is configured to use Railway's PORT

### Viewing Logs:
```bash
railway logs
```

### Redeploying:
```bash
railway up --detach
```

## Database (If Needed Later)

Railway offers PostgreSQL databases:
```bash
railway add postgresql
```

## Custom Domain (Optional)

In Railway dashboard:
1. Go to Settings → Domains
2. Add your custom domain
3. Configure DNS records as shown

## Support

- Railway Docs: https://docs.railway.app/
- Railway Discord: https://discord.gg/railway
- Project Issues: Check Railway dashboard logs

Your backend should now be accessible at: `https://your-app-name.up.railway.app`