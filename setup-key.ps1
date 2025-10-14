# Secure API Key Setup for PR Review
# This script configures your Gemini API key for local and production use

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " PR Review - API Key Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Get API key from user
Write-Host "Enter your Gemini API key (starts with AIzaSy...):" -ForegroundColor Yellow
$apiKey = Read-Host

# Validate key format
if ($apiKey -notmatch '^AIzaSy[A-Za-z0-9_-]{33}$') {
    Write-Host ""
    Write-Host "ERROR: Invalid API key format!" -ForegroundColor Red
    Write-Host "Key should start with 'AIzaSy' and be 39 characters total" -ForegroundColor Red
    exit 1
}

Write-Host "Valid API key format" -ForegroundColor Green
Write-Host ""

# Update workers/.dev.vars
Write-Host "Updating workers/.dev.vars..." -ForegroundColor Yellow
$devVarsContent = @"
# Local development environment variables
GEMINI_API_KEY=$apiKey

"@

Set-Content -Path "workers\.dev.vars" -Value $devVarsContent -NoNewline
Write-Host "Updated workers/.dev.vars" -ForegroundColor Green
Write-Host ""

# Verify gitignore
$gitCheck = git check-ignore "workers/.dev.vars" 2>$null
if ($gitCheck) {
    Write-Host "Security verified: workers/.dev.vars is gitignored" -ForegroundColor Green
} else {
    Write-Host "WARNING: workers/.dev.vars is NOT gitignored!" -ForegroundColor Red
}
Write-Host ""

# Update Cloudflare Worker secret
Write-Host "Updating Cloudflare Worker secret..." -ForegroundColor Yellow
Set-Location workers
$apiKey | npx wrangler secret put GEMINI_API_KEY

if ($LASTEXITCODE -eq 0) {
    Write-Host "Cloudflare Worker secret updated successfully" -ForegroundColor Green
} else {
    Write-Host "Failed to update Cloudflare Worker secret" -ForegroundColor Red
}

Set-Location ..
Write-Host ""

# Test production API
Write-Host "Testing production API..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "https://pr-review-worker.kenshifan3000.workers.dev/api/status" -Method Get -ErrorAction Stop
    if ($response.ok -eq $true) {
        Write-Host "Production API is working!" -ForegroundColor Green
        Write-Host "Service: $($response.service) v$($response.version)" -ForegroundColor Gray
    }
} catch {
    Write-Host "Production API test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " Setup Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Local dev key: workers/.dev.vars (secured)" -ForegroundColor White
Write-Host "Production key: Cloudflare Secrets (encrypted)" -ForegroundColor White
Write-Host ""
Write-Host "Test locally:  cd workers && npm run dev" -ForegroundColor Yellow
Write-Host "Backend URL:   https://pr-review-worker.kenshifan3000.workers.dev" -ForegroundColor Yellow
Write-Host ""
