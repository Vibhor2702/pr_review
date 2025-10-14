#!/bin/bash

# PR Review Agent - Quick Deployment Setup Script
# This script helps you deploy to Railway and Cloudflare Pages

set -e

echo "🚀 PR Review Agent - Deployment Setup"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found. Please run this script from the project root."
    exit 1
fi

print_info "Checking deployment configuration..."
echo ""

# Check if railway.json exists
if [ -f "railway.json" ]; then
    print_success "Railway configuration found (railway.json)"
else
    print_error "railway.json not found"
    exit 1
fi

# Check if Procfile exists
if [ -f "Procfile" ]; then
    print_success "Procfile found"
else
    print_error "Procfile not found"
    exit 1
fi

# Check if wrangler.toml exists
if [ -f "wrangler.toml" ]; then
    print_success "Cloudflare configuration found (wrangler.toml)"
else
    print_error "wrangler.toml not found"
    exit 1
fi

# Check if frontend build configuration exists
if [ -f "frontend/package.json" ]; then
    print_success "Frontend package.json found"
else
    print_error "frontend/package.json not found"
    exit 1
fi

# Check if GitHub Actions workflow exists
if [ -f ".github/workflows/deploy.yml" ]; then
    print_success "GitHub Actions workflow found"
else
    print_warning "GitHub Actions workflow not found (optional)"
fi

echo ""
print_success "All deployment files are in place!"
echo ""

# Print deployment instructions
echo "📋 Next Steps:"
echo "=============="
echo ""
echo "1️⃣  Backend Deployment (Railway):"
echo "   • Visit: https://railway.app/new"
echo "   • Connect GitHub repository: Vibhor2702/pr_review"
echo "   • Add environment variable: GEMINI_API_KEY=your_key"
echo "   • Railway will auto-deploy using railway.json"
echo "   • Copy your Railway URL (e.g., https://pr-review-production.up.railway.app)"
echo ""
echo "2️⃣  Frontend Deployment (Cloudflare Pages):"
echo "   • Visit: https://dash.cloudflare.com"
echo "   • Go to Workers & Pages → Create Application → Pages"
echo "   • Connect GitHub repository: Vibhor2702/pr_review"
echo "   • Build command: cd frontend && npm install && npm run build"
echo "   • Build output: frontend/dist"
echo "   • Add environment variable: VITE_API_URL=<your_railway_url>"
echo "   • Deploy!"
echo ""
echo "3️⃣  Verify Deployment:"
echo "   • Backend health: curl https://your-railway-url/health"
echo "   • Frontend: Open https://pr-review.pages.dev in browser"
echo "   • Test integration: Create a review in the frontend"
echo ""

# Ask if user wants to see the deployment guide
read -p "Do you want to open the detailed deployment guide? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "DEPLOYMENT_GUIDE.md" ]; then
        if command -v code &> /dev/null; then
            code DEPLOYMENT_GUIDE.md
            print_success "Opened DEPLOYMENT_GUIDE.md in VS Code"
        elif command -v cat &> /dev/null; then
            cat DEPLOYMENT_GUIDE.md
        else
            print_info "Please open DEPLOYMENT_GUIDE.md manually"
        fi
    else
        print_warning "DEPLOYMENT_GUIDE.md not found"
    fi
fi

echo ""
print_success "Deployment setup complete! Follow the steps above to deploy."
echo ""
print_info "For detailed instructions, see DEPLOYMENT_GUIDE.md"
print_info "For questions, open an issue on GitHub"
echo ""
