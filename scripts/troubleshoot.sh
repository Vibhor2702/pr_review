#!/bin/bash
# GitHub Actions Troubleshooting Script for Job 50920448307

echo "🔍 PR Review Agent - Troubleshooting Script"
echo "=========================================="

# Check environment variables
echo "📊 Environment Check:"
echo "GEMINI_API_KEY: ${GEMINI_API_KEY:+SET}" "${GEMINI_API_KEY:-NOT_SET}"
echo "GITHUB_TOKEN: ${GITHUB_TOKEN:+SET}" "${GITHUB_TOKEN:-NOT_SET}"
echo "CI_POST_REVIEW: ${CI_POST_REVIEW:-NOT_SET}"

# Check Python version
echo "🐍 Python Environment:"
python --version
pip --version

# Check installed packages
echo "📦 Installed Packages:"
pip list | grep -E "(google|flask|requests|gitpython)"

# Check if module can be imported
echo "🔧 Module Import Test:"
python -c "
try:
    import src.main
    print('✅ src.main imported successfully')
except Exception as e:
    print(f'❌ Failed to import src.main: {e}')

try:
    from src.config import config
    print('✅ Config imported successfully')
    print(f'   Gemini API Key: {\"SET\" if config.gemini_api_key else \"NOT_SET\"}')
except Exception as e:
    print(f'❌ Failed to import config: {e}')
"

# Check if artifacts directory exists
echo "📁 Directory Structure:"
ls -la . || true
ls -la src/ || true
mkdir -p artifacts
echo "✅ Created artifacts directory"

# Test basic functionality
echo "🧪 Basic Functionality Test:"
python -c "
try:
    from src.main import main
    print('✅ Main function accessible')
except Exception as e:
    print(f'❌ Main function not accessible: {e}')
"

echo "=========================================="
echo "✅ Troubleshooting complete"