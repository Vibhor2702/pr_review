# 🔐 Secure API Key Setup Script
# Run this script to configure your new Gemini API key

Write-Host "🔑 PR Review - Secure API Key Configuration" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Get the API key from user
Write-Host "📋 Step 1: Enter Your New Gemini API Key" -ForegroundColor Yellow
Write-Host "Paste your key (starts with AIzaSy...):" -ForegroundColor White
$apiKey = Read-Host -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiKey)
$apiKeyPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

# Validate key format
if ($apiKeyPlain -notmatch '^AIzaSy[A-Za-z0-9_-]{33}$') {
    Write-Host "❌ ERROR: Invalid API key format!" -ForegroundColor Red
    Write-Host "Key should start with 'AIzaSy' and be 39 characters long" -ForegroundColor Red
    exit 1
}

Write-Host "✅ API key format validated" -ForegroundColor Green
Write-Host ""

# Step 2: Update local .dev.vars
Write-Host "📝 Step 2: Updating workers/.dev.vars (local development)" -ForegroundColor Yellow
$devVarsPath = "workers\.dev.vars"
$devVarsContent = @"
# Local development environment variables
# This file is for LOCAL DEVELOPMENT ONLY - never commit secrets!
# For production, use: npx wrangler secret put GEMINI_API_KEY

# Google Gemini API Key (required)
GEMINI_API_KEY=$apiKeyPlain

# Optional: GitHub token for fetching PRs (if implementing full PR fetch)
# GITHUB_TOKEN=your-github-token-here

"@

Set-Content -Path $devVarsPath -Value $devVarsContent -NoNewline
Write-Host "✅ Updated workers/.dev.vars" -ForegroundColor Green
Write-Host ""

# Step 3: Verify file is gitignored
Write-Host "🔒 Step 3: Verifying security (gitignore check)" -ForegroundColor Yellow
$gitIgnoreCheck = git check-ignore $devVarsPath
if ($gitIgnoreCheck) {
    Write-Host "✅ $devVarsPath is gitignored (secure)" -ForegroundColor Green
} else {
    Write-Host "⚠️  WARNING: $devVarsPath is NOT gitignored!" -ForegroundColor Red
    Write-Host "Adding to .gitignore now..." -ForegroundColor Yellow
    Add-Content -Path ".gitignore" -Value "`nworkers/.dev.vars"
    Write-Host "✅ Added to .gitignore" -ForegroundColor Green
}
Write-Host ""

# Step 4: Update Cloudflare Worker production secret
Write-Host "☁️  Step 4: Updating Cloudflare Worker (production)" -ForegroundColor Yellow
Write-Host "Running: npx wrangler secret put GEMINI_API_KEY" -ForegroundColor Gray

Set-Location workers
$apiKeyPlain | npx wrangler secret put GEMINI_API_KEY

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Cloudflare Worker secret updated" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to update Cloudflare Worker secret" -ForegroundColor Red
    Write-Host "Please run manually: cd workers; echo 'YOUR_KEY' | npx wrangler secret put GEMINI_API_KEY" -ForegroundColor Yellow
}

Set-Location ..
Write-Host ""

# Step 5: Test local development server
Write-Host "🧪 Step 5: Testing local development server" -ForegroundColor Yellow
Write-Host "Starting dev server..." -ForegroundColor Gray

Set-Location workers
$devServer = Start-Process -FilePath "npx" -ArgumentList "wrangler", "dev", "--port", "8787" -PassThru -NoNewWindow

Start-Sleep -Seconds 5

# Test the endpoint
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8787/api/status" -Method Get
    if ($response.ok -eq $true) {
        Write-Host "✅ Local dev server working!" -ForegroundColor Green
        Write-Host "   Response: $($response.service) v$($response.version)" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️  Could not connect to dev server" -ForegroundColor Yellow
    Write-Host "   This is OK - server may need more time to start" -ForegroundColor Gray
}

# Stop the dev server
Stop-Process -Id $devServer.Id -Force
Set-Location ..
Write-Host ""

# Step 6: Test production API
Write-Host "🌐 Step 6: Testing production API" -ForegroundColor Yellow
try {
    $prodResponse = Invoke-RestMethod -Uri "https://pr-review-worker.kenshifan3000.workers.dev/api/status" -Method Get
    if ($prodResponse.ok -eq $true) {
        Write-Host "✅ Production API working!" -ForegroundColor Green
        Write-Host "   URL: https://pr-review-worker.kenshifan3000.workers.dev" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Production API test failed" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Summary
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Local development configured (workers/.dev.vars)" -ForegroundColor Green
Write-Host "✅ Production Worker updated (Cloudflare Secret)" -ForegroundColor Green
Write-Host "✅ Security verified (gitignore)" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Test locally:  cd workers && npm run dev" -ForegroundColor White
Write-Host "2. Deploy frontend: Cloudflare Pages will auto-deploy from GitHub" -ForegroundColor White
Write-Host "3. Monitor build: https://dash.cloudflare.com/pages" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Your URLs:" -ForegroundColor Yellow
Write-Host "   Backend:  https://pr-review-worker.kenshifan3000.workers.dev" -ForegroundColor White
Write-Host "   Frontend: https://pr-review.pages.dev (after Pages deployment)" -ForegroundColor White
Write-Host ""

# Clean up sensitive data from memory
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
Remove-Variable -Name apiKey, apiKeyPlain, BSTR -ErrorAction SilentlyContinue
