# PR Review Agent Demo (Google Gemini Edition)

## Quick Start

### 1. Environment Setup
```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies (already done)
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file with your API keys:
```env
# Google Gemini API Key (required for intelligent reviews)
GEMINI_API_KEY=your_gemini_api_key_here

# Git provider tokens (optional but recommended)
GITHUB_TOKEN=your_github_token_here
GITLAB_TOKEN=your_gitlab_token_here
BITBUCKET_TOKEN=your_bitbucket_token_here

# Gemini model selection (optional)
GEMINI_MODEL=gemini-1.5-flash

# Webhook secret (for CI integration)
WEBHOOK_SECRET=your_webhook_secret_here
```

### 3. Getting Your Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key and add it to your `.env` file

### 3. CLI Usage Examples

#### Review a GitHub Pull Request
```bash
python -m src.main review \
  --provider github \
  --owner microsoft \
  --repo vscode \
  --pr 12345
```

#### Review a GitLab Merge Request
```bash
python -m src.main review \
  --provider gitlab \
  --owner gitlab-org \
  --repo gitlab \
  --pr 45678
```

#### Review with Custom Configuration
```bash
python -m src.main review \
  --provider github \
  --owner myorg \
  --repo myrepo \
  --pr 123 \
  --config custom_config.yaml \
  --output-format json \
  --output-file review_results.json
```

### 4. API Server Usage

#### Start the Server
```bash
python -m src.main serve --port 8080
```

#### Make API Requests
```bash
# Review PR via API
curl -X POST http://localhost:8080/review_pr \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "github",
    "owner": "microsoft",
    "repo": "vscode",
    "pr_number": 12345
  }'

# Health check
curl http://localhost:8080/health

# Get configuration
curl http://localhost:8080/config
```

### 5. CI Integration

The GitHub Actions workflow is already set up in `.github/workflows/pr_review.yml`.

To use it:
1. Add your `GEMINI_API_KEY` and `GITHUB_TOKEN` to repository secrets
2. The workflow will automatically run on every pull request
3. Review results will be posted as PR comments and saved as artifacts

### 6. Expected Output

The tool generates comprehensive reviews including:

#### JSON Format
```json
{
  "comments": [
    {
      "file": "src/example.py",
      "line": 42,
      "message": "Consider using a more descriptive variable name",
      "severity": "info",
      "tool": "flake8",
      "suggestion": "Use 'user_count' instead of 'n'"
    }
  ],
  "metadata": {
    "total_comments": 5,
    "files_analyzed": 12,
    "score": 85,
    "grade": "B+",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

#### Markdown Format
```markdown
# Code Review Summary

**Overall Score:** 85/100 (B+)
**Files Analyzed:** 12
**Total Issues Found:** 5

## Issues by Severity
- 🔴 Critical: 0
- 🟡 Warning: 2  
- 🔵 Info: 3

## Most Problematic Files
1. `src/main.py` - 3 issues
2. `src/utils.py` - 2 issues

## Detailed Findings

### src/main.py:42
**Severity:** Info | **Tool:** flake8
Consider using a more descriptive variable name
```

### 7. Testing

Run the test suite:
```bash
pytest tests/ -v
```

All 27 tests should pass!

## Features

- ✅ Multi-provider support (GitHub, GitLab, Bitbucket)
- ✅ Static analysis (flake8, bandit, radon)
- ✅ Intelligent code reviews with Google Gemini
- ✅ Quality scoring (0-100 with letter grades)
- ✅ CLI and API interfaces
- ✅ CI/CD integration
- ✅ Rich terminal output
- ✅ Comprehensive test suite
- ✅ JSON and Markdown output formats

## Next Steps

1. Add your Gemini API key to `.env`
2. Try reviewing a real pull request
3. Integrate with your CI/CD pipeline
4. Customize the configuration for your needs

**Note:** This version uses Google Gemini exclusively for intelligent code reviews. Gemini offers competitive performance with potentially lower costs and different rate limits.

Happy reviewing! 🚀