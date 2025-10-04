#!/bin/bash

# 🚀 Quick Deploy Script for Cloudflare Workers
# This script automates the deployment of your PR Review Worker

set -e  # Exit on error

echo "🚀 PR Review Agent - Cloudflare Workers Deployment"
echo "=================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found"
    echo "💡 Make sure you're in the workers/ directory"
    echo "   Run: cd workers && ./deploy.sh"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    echo "💡 Install from: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js found: $(node --version)"
echo ""

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo "✅ Dependencies installed"
    echo ""
fi

# Check if logged in to Cloudflare
echo "🔐 Checking Cloudflare authentication..."
if ! npx wrangler whoami &> /dev/null; then
    echo "❌ Not logged in to Cloudflare"
    echo "🔓 Opening browser for login..."
    npx wrangler login
    echo "✅ Login successful"
    echo ""
fi

# Get account info
echo "👤 Cloudflare Account Info:"
npx wrangler whoami
echo ""

# Check if GEMINI_API_KEY is set
echo "🔑 Checking secrets..."
read -p "Have you set GEMINI_API_KEY secret? (y/n): " has_secret

if [ "$has_secret" != "y" ]; then
    echo ""
    echo "📝 Setting GEMINI_API_KEY secret..."
    echo "💡 Paste your Google Gemini API key when prompted"
    echo "   Get one at: https://aistudio.google.com/app/apikey"
    echo ""
    npx wrangler secret put GEMINI_API_KEY
    echo "✅ Secret set successfully"
    echo ""
fi

# Confirm deployment
echo "🚀 Ready to deploy!"
echo ""
echo "This will deploy your Worker to Cloudflare's global network."
echo ""
read -p "Continue with deployment? (y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "❌ Deployment cancelled"
    exit 0
fi

echo ""
echo "🚀 Deploying to Cloudflare Workers..."
echo ""

# Deploy
npm run deploy

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🎉 Your Worker is now live!"
echo ""
echo "📋 Next Steps:"
echo "1. Copy your Worker URL (shown above)"
echo "2. Add it to Cloudflare Pages environment variables"
echo "   Variable: VITE_API_URL"
echo "   Value: https://pr-review-worker.your-username.workers.dev"
echo "3. Redeploy your frontend on Cloudflare Pages"
echo ""
echo "🧪 Test your API:"
echo "   curl https://pr-review-worker.your-username.workers.dev/api/status"
echo ""
echo "📊 View analytics:"
echo "   https://dash.cloudflare.com/workers"
echo ""
echo "Happy deploying! 🎊"
