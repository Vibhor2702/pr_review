#!/bin/bash

# Frontend Setup Script for PR Review Agent

echo "🚀 Setting up PR Review Agent Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

# Check Node version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js $(node -v) detected"

# Navigate to frontend directory
cd "$(dirname "$0")"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Create environment file
if [ ! -f ".env" ]; then
    echo "📝 Creating environment file..."
    cat > .env << EOL
# Frontend Configuration
VITE_API_URL=http://localhost:5000
VITE_APP_TITLE=PR Review Agent
VITE_APP_DESCRIPTION=Professional Pull Request Review Dashboard
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_REALTIME=true

# Optional: Custom branding
VITE_COMPANY_NAME=Your Company
VITE_SUPPORT_EMAIL=support@yourcompany.com
EOL
    echo "✅ Created .env file - customize as needed"
else
    echo "✅ .env file already exists"
fi

# Create public directory and assets
mkdir -p public
if [ ! -f "public/icon-192.png" ]; then
    echo "📱 Creating app icons..."
    # Create placeholder icons (you can replace with real ones)
    echo "Add your 192x192 and 512x512 app icons to public/ directory"
fi

# Build the project to check for errors
echo "🔨 Building project..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Frontend setup complete!"
    echo ""
    echo "🎯 Next steps:"
    echo "1. Start the backend: cd .. && python -m src.main serve"
    echo "2. Start the frontend: npm run dev"
    echo "3. Open http://localhost:3000"
    echo ""
    echo "🛠️  Development commands:"
    echo "   npm run dev        - Start development server"
    echo "   npm run build      - Build for production"
    echo "   npm run preview    - Preview production build"
    echo "   npm run lint       - Run linting"
else
    echo "❌ Build failed. Please check the errors above."
    exit 1
fi