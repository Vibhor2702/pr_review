@echo off
REM PR Review Agent - Quick Deployment Setup Script (Windows)
REM This script helps you deploy to Railway and Cloudflare Pages

echo.
echo ======================================
echo    PR Review Agent - Deployment Setup
echo ======================================
echo.

REM Check if we're in the right directory
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found. Please run this script from the project root.
    exit /b 1
)

echo [INFO] Checking deployment configuration...
echo.

REM Check if railway.json exists
if exist "railway.json" (
    echo [OK] Railway configuration found ^(railway.json^)
) else (
    echo [ERROR] railway.json not found
    exit /b 1
)

REM Check if Procfile exists
if exist "Procfile" (
    echo [OK] Procfile found
) else (
    echo [ERROR] Procfile not found
    exit /b 1
)

REM Check if wrangler.toml exists
if exist "wrangler.toml" (
    echo [OK] Cloudflare configuration found ^(wrangler.toml^)
) else (
    echo [ERROR] wrangler.toml not found
    exit /b 1
)

REM Check if frontend build configuration exists
if exist "frontend\package.json" (
    echo [OK] Frontend package.json found
) else (
    echo [ERROR] frontend\package.json not found
    exit /b 1
)

REM Check if GitHub Actions workflow exists
if exist ".github\workflows\deploy.yml" (
    echo [OK] GitHub Actions workflow found
) else (
    echo [WARNING] GitHub Actions workflow not found ^(optional^)
)

echo.
echo [SUCCESS] All deployment files are in place!
echo.

REM Print deployment instructions
echo ========================================
echo    Next Steps
echo ========================================
echo.
echo 1. Backend Deployment ^(Railway^):
echo    - Visit: https://railway.app/new
echo    - Connect GitHub repository: Vibhor2702/pr_review
echo    - Add environment variable: GEMINI_API_KEY=your_key
echo    - Railway will auto-deploy using railway.json
echo    - Copy your Railway URL ^(e.g., https://pr-review-production.up.railway.app^)
echo.
echo 2. Frontend Deployment ^(Cloudflare Pages^):
echo    - Visit: https://dash.cloudflare.com
echo    - Go to Workers ^& Pages -^> Create Application -^> Pages
echo    - Connect GitHub repository: Vibhor2702/pr_review
echo    - Build command: cd frontend ^&^& npm install ^&^& npm run build
echo    - Build output: frontend/dist
echo    - Add environment variable: VITE_API_URL=^<your_railway_url^>
echo    - Deploy!
echo.
echo 3. Verify Deployment:
echo    - Backend health: curl https://your-railway-url/health
echo    - Frontend: Open https://pr-review.pages.dev in browser
echo    - Test integration: Create a review in the frontend
echo.

REM Ask if user wants to open the deployment guide
set /p REPLY="Do you want to open the detailed deployment guide? (y/n): "
if /i "%REPLY%"=="y" (
    if exist "DEPLOYMENT_GUIDE.md" (
        if exist "C:\Program Files\Microsoft VS Code\Code.exe" (
            start "" "C:\Program Files\Microsoft VS Code\Code.exe" "DEPLOYMENT_GUIDE.md"
            echo [SUCCESS] Opened DEPLOYMENT_GUIDE.md in VS Code
        ) else (
            start "" "DEPLOYMENT_GUIDE.md"
            echo [INFO] Opened DEPLOYMENT_GUIDE.md with default application
        )
    ) else (
        echo [WARNING] DEPLOYMENT_GUIDE.md not found
    )
)

echo.
echo [SUCCESS] Deployment setup complete! Follow the steps above to deploy.
echo.
echo [INFO] For detailed instructions, see DEPLOYMENT_GUIDE.md
echo [INFO] For questions, open an issue on GitHub
echo.

pause
