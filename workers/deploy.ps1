# 🚀 Quick Deploy Script for Cloudflare Workers
# This script automates the deployment of your PR Review Worker

Write-Host "🚀 PR Review Agent - Cloudflare Workers Deployment" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "package.json")) {
    Write-Host "❌ Error: package.json not found" -ForegroundColor Red
    Write-Host "💡 Make sure you're in the workers\ directory" -ForegroundColor Yellow
    Write-Host "   Run: cd workers; .\deploy.ps1" -ForegroundColor Yellow
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ Error: Node.js is not installed" -ForegroundColor Red
    Write-Host "💡 Install from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
    Write-Host ""
}

# Check if logged in to Cloudflare
Write-Host "🔐 Checking Cloudflare authentication..." -ForegroundColor Yellow
try {
    npx wrangler whoami 2>&1 | Out-Null
    $loggedIn = $true
} catch {
    $loggedIn = $false
}

if (-not $loggedIn) {
    Write-Host "❌ Not logged in to Cloudflare" -ForegroundColor Red
    Write-Host "🔓 Opening browser for login..." -ForegroundColor Yellow
    npx wrangler login
    Write-Host "✅ Login successful" -ForegroundColor Green
    Write-Host ""
}

# Get account info
Write-Host "👤 Cloudflare Account Info:" -ForegroundColor Cyan
npx wrangler whoami
Write-Host ""

# Check if GEMINI_API_KEY is set
Write-Host "🔑 Checking secrets..." -ForegroundColor Yellow
$hasSecret = Read-Host "Have you set GEMINI_API_KEY secret? (y/n)"

if ($hasSecret -ne "y") {
    Write-Host ""
    Write-Host "📝 Setting GEMINI_API_KEY secret..." -ForegroundColor Yellow
    Write-Host "💡 Paste your Google Gemini API key when prompted" -ForegroundColor Yellow
    Write-Host "   Get one at: https://aistudio.google.com/app/apikey" -ForegroundColor Yellow
    Write-Host ""
    npx wrangler secret put GEMINI_API_KEY
    Write-Host "✅ Secret set successfully" -ForegroundColor Green
    Write-Host ""
}

# Confirm deployment
Write-Host "🚀 Ready to deploy!" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will deploy your Worker to Cloudflare's global network."
Write-Host ""
$confirm = Read-Host "Continue with deployment? (y/n)"

if ($confirm -ne "y") {
    Write-Host "❌ Deployment cancelled" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "🚀 Deploying to Cloudflare Workers..." -ForegroundColor Cyan
Write-Host ""

# Deploy
npm run deploy

Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 Your Worker is now live!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Copy your Worker URL (shown above)"
Write-Host "2. Add it to Cloudflare Pages environment variables"
Write-Host "   Variable: VITE_API_URL"
Write-Host "   Value: https://pr-review-worker.your-username.workers.dev"
Write-Host "3. Redeploy your frontend on Cloudflare Pages"
Write-Host ""
Write-Host "🧪 Test your API:" -ForegroundColor Cyan
Write-Host "   curl https://pr-review-worker.your-username.workers.dev/api/status"
Write-Host ""
Write-Host "📊 View analytics:" -ForegroundColor Cyan
Write-Host "   https://dash.cloudflare.com/workers"
Write-Host ""
Write-Host "Happy deploying! 🎊" -ForegroundColor Green
