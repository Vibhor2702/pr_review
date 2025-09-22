@echo off
echo 🚀 Setting up PR Review Agent Frontend...

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js detected

REM Navigate to frontend directory
cd /d "%~dp0"

REM Install dependencies
echo 📦 Installing dependencies...
call npm install

REM Create environment file
if not exist ".env" (
    echo 📝 Creating environment file...
    (
        echo # Frontend Configuration
        echo VITE_API_URL=http://localhost:5000
        echo VITE_APP_TITLE=PR Review Agent
        echo VITE_APP_DESCRIPTION=Professional Pull Request Review Dashboard
        echo VITE_ENABLE_ANALYTICS=true
        echo VITE_ENABLE_REALTIME=true
        echo.
        echo # Optional: Custom branding
        echo VITE_COMPANY_NAME=Your Company
        echo VITE_SUPPORT_EMAIL=support@yourcompany.com
    ) > .env
    echo ✅ Created .env file - customize as needed
) else (
    echo ✅ .env file already exists
)

REM Create public directory
if not exist "public" mkdir public

REM Build the project to check for errors
echo 🔨 Building project...
call npm run build

if %ERRORLEVEL% EQU 0 (
    echo ✅ Frontend setup complete!
    echo.
    echo 🎯 Next steps:
    echo 1. Start the backend: cd .. ^&^& python -m src.main serve
    echo 2. Start the frontend: npm run dev
    echo 3. Open http://localhost:3000
    echo.
    echo 🛠️  Development commands:
    echo    npm run dev        - Start development server
    echo    npm run build      - Build for production
    echo    npm run preview    - Preview production build
    echo    npm run lint       - Run linting
) else (
    echo ❌ Build failed. Please check the errors above.
    pause
    exit /b 1
)

pause