# PR Review Agent

[![Frontend Live](https://img.shields.io/badge/Cloudflare-Pages-orange?style=for-the-badge&logo=cloudflare)](https://pr-review.pages.dev)
[![Backend API](https://img.shields.io/badge/Cloudflare-Workers-orange?style=for-the-badge&logo=cloudflare)](https://pr-review.pages.dev)
[![Cost](https://img.shields.io/badge/Cost-$0%2Fmonth-success?style=for-the-badge)](DEPLOY.md)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB?style=flat-square&logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

A professional automated Pull Request Review Agent that analyzes code changes, provides comprehensive feedback, and generates quality scores for pull requests across GitHub, GitLab, and Bitbucket.

## 🌐 Live Deployment

Your application is **LIVE** on Cloudflare - completely free, forever!

- **Frontend**: [https://pr-review.pages.dev](https://pr-review.pages.dev) ⚡ Cloudflare Pages
- **Backend**: [https://pr-review-worker.kenshifan3000.workers.dev](https://pr-review-worker.kenshifan3000.workers.dev) ⚡ Cloudflare Workers
- **Cost**: $0/month forever
- **Status**: ✅ Both deployed and running

## 🚀 Quick Deploy (6 minutes)

```bash
# 1. Deploy backend
cd workers
npm install
npx wrangler login
npx wrangler secret put GEMINI_API_KEY
npm run deploy

# 2. Deploy frontend (via Cloudflare Dashboard)
# See DEPLOY.md for complete guide
```

**📚 Full Guide**: [DEPLOY.md](DEPLOY.md) - Complete step-by-step deployment

### ⚡ Why Cloudflare?

- ✅ **Forever Free**: 100,000 requests/day
- ✅ **Global Edge Network**: 300+ locations worldwide
- ✅ **Zero Maintenance**: No servers to manage
- ✅ **Auto-Scaling**: Handles any traffic
- ✅ **Fast**: < 50ms response time globally

## ✨ Features

- **Multi-Platform Support**: Works with GitHub, GitLab, and Bitbucket
- **Comprehensive Analysis**: Uses Google Gemini for advanced code review suggestions
- **Static Code Analysis**: Integrates bandit, flake8, and radon for comprehensive checks
- **Quality Scoring**: Provides 0-100 quality scores with letter grades
- **CI/CD Integration**: Automated reviews via GitHub Actions
- **Multiple Interfaces**: CLI tool, HTTP API, and modern web dashboard
- **Professional Frontend**: Competition-level React TypeScript interface
- **Structured Output**: JSON artifacts and markdown reports

## 🎨 **NEW: Professional Web Dashboard**

**Competition-level React TypeScript frontend** with modern design and real-time features:

- 📊 **Real-time Dashboard** - Live metrics and activity monitoring
- 🎯 **Interactive Analytics** - Charts, graphs, and data visualization  
- 📱 **Progressive Web App** - Install as native app with offline support
- 🌙 **Dark/Light Theme** - Professional theming system
- ⚡ **Real-time Updates** - WebSocket integration for live data
- 📲 **Mobile-First Design** - Perfect on all devices

### Quick Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Windows setup
setup.bat

# Or manual setup
npm install && npm run dev
```

**Frontend**: http://localhost:3000 | **Backend**: http://localhost:5000

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Git
- Google Gemini API key (for comprehensive features)
- Git provider tokens (GitHub/GitLab/Bitbucket)

### Installation

1. **Clone and setup the repository:**

```bash
git clone <repository-url>
cd pr_review_agent
```

2. **Create and activate virtual environment:**

**Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows PowerShell:**
```powershell
python -m venv venv
# If you get execution policy errors, run this first:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**

```bash
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables:
```bash
# Language Model Provider (required for comprehensive features)
GEMINI_API_KEY=your_gemini_api_key_here

# Git Providers (at least one required)
GITHUB_TOKEN=your_github_token_here
GITLAB_TOKEN=your_gitlab_token_here
BITBUCKET_TOKEN=your_bitbucket_token_here

# Optional settings
CI_POST_REVIEW=false
LLM_TEMPERATURE=0.3
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
```

### PowerShell Execution Policy Fix

If you encounter PowerShell execution policy errors on Windows:

```powershell
# Temporary fix (for current session)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Or permanent fix (requires admin)
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## 📖 Usage

### Command Line Interface

**Review a GitHub PR:**
```bash
python -m src.main review --provider github --owner microsoft --repo vscode --pr 123
```

**Review a GitLab MR:**
```bash
python -m src.main review --provider gitlab --owner gitlab-org --repo gitlab --pr 456
```

**Review with custom output directory:**
```bash
python -m src.main review --provider github --owner owner --repo repo --pr 123 --output ./my-reviews
```

**Skip comprehensive analysis (static only):**
```bash
python -m src.main review --provider github --owner owner --repo repo --pr 123 --no-llm
```

**Start HTTP server:**
```bash
python -m src.main serve --host 0.0.0.0 --port 5000
```

### HTTP API

**Start the server:**
```bash
python -m src.main serve
```

**Access the web dashboard:**
- **Modern Frontend**: http://localhost:3000 (see `frontend/` directory)
- **API Endpoints**: http://localhost:5000

**Review a PR via API:**
```bash
curl -X POST http://localhost:5000/review_pr \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "github",
    "owner": "microsoft",
    "repo": "vscode",
    "pr_number": 123,
    "post_comments": false
  }'
```

**Check server health:**
```bash
curl http://localhost:5000/health
```

**Get configuration status:**
```bash
curl http://localhost:5000/config
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/review_pr` | POST | Review a pull request |
| `/providers` | GET | List provider configuration status |
| `/config` | GET | Get current configuration |

### API Request Format

```json
{
  "provider": "github|gitlab|bitbucket",
  "owner": "repository-owner",
  "repo": "repository-name", 
  "pr_number": 123,
  "token": "optional-custom-token",
  "no_llm": false,
  "post_comments": false
}
```

### API Response Format

```json
{
  "status": "success",
  "pr_context": {
    "provider": "github",
    "owner": "microsoft", 
    "repo": "vscode",
    "pr_number": 123,
    "title": "Fix syntax highlighting bug",
    "files_changed": 3
  },
  "review": {
    "score": 85,
    "grade": "B+",
    "total_findings": 4,
    "summary": "⚠️ Found 4 issues (2 warnings, 2 suggestions)",
    "comments": [
      {
        "file": "src/module.py",
        "line": 42,
        "side": "right",
        "message": "This function has high cyclomatic complexity",
        "suggestion": "Consider breaking into smaller functions",
        "severity": "warning",
        "rule": "COMPLEXITY_15"
      }
    ]
  },
  "metadata": {
    "total_findings": 4,
    "severity_breakdown": {"error": 0, "warning": 2, "info": 2},
    "timestamp": "2023-01-01T12:00:00Z"
  },
  "artifact_path": "artifacts/review_github_123.json"
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes* | - | Google Gemini API key for comprehensive features |
| `GITHUB_TOKEN` | No | - | GitHub personal access token |
| `GITLAB_TOKEN` | No | - | GitLab personal access token |
| `BITBUCKET_TOKEN` | No | - | Bitbucket app password |
| `CI_POST_REVIEW` | No | `false` | Enable CI comment posting |
| `LLM_TEMPERATURE` | No | `0.3` | Model creativity level (0-1) |
| `SERVER_HOST` | No | `0.0.0.0` | Server bind address |
| `SERVER_PORT` | No | `5000` | Server port |

*Required only if using comprehensive features

### Scoring Weights

Customize scoring weights via environment variables:

```bash
WEIGHT_STYLE=5.0          # Style issue penalty per issue
WEIGHT_SECURITY=15.0      # Security issue penalty per issue  
WEIGHT_COMPLEXITY=10.0    # Complexity penalty per issue
WEIGHT_TEST_COVERAGE=8.0  # Test coverage penalty per missing test
BASE_SCORE=100.0          # Starting score
```

## 🚦 GitHub Actions Integration

Add automated PR reviews to your repository:

1. **Copy the workflow file:**
```bash
mkdir -p .github/workflows
cp .github/workflows/pr_review.yml .github/workflows/
```

2. **Add repository secrets:**
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `GITHUB_TOKEN`: Automatically provided by GitHub

3. **Customize the workflow** (optional):
```yaml
# In .github/workflows/pr_review.yml
- name: Run PR Review
  run: |
    python -m src.main review \
      --provider github \
      --owner ${{ github.repository_owner }} \
      --repo ${{ github.event.repository.name }} \
      --pr ${{ github.event.pull_request.number }} \
      --no-llm  # Add this to skip comprehensive analysis
```

The workflow will:
- ✅ Run on every PR (open, update, reopen)
- 🔍 Analyze changed files
- 📊 Generate quality scores
- 💬 Post summary comments
- 📁 Upload detailed reports as artifacts
- ❌ Fail if quality is below threshold (configurable)

## 📊 Understanding Results

### Quality Scores

| Score Range | Grade | Meaning |
|-------------|-------|---------|
| 95-100 | A+ | Excellent code quality |
| 90-94 | A | Very good quality |
| 85-89 | A- | Good quality |
| 80-84 | B+ | Above average |
| 75-79 | B | Average |
| 70-74 | B- | Below average |
| 65-69 | C+ | Needs improvement |
| 60-64 | C | Poor quality |
| 55-59 | C- | Very poor |
| 50-54 | D | Failing |
| 0-49 | F | Critical issues |

### Severity Levels

- **Error** ❌: Critical issues that should block merging
- **Warning** ⚠️: Important issues that should be addressed
- **Info** ℹ️: Suggestions for improvement

### Analysis Tools

1. **Syntax Checker**: Python AST parsing for syntax errors
2. **Bandit**: Security vulnerability scanning
3. **Flake8**: Style and convention checking  
4. **Radon**: Cyclomatic complexity analysis
5. **Advanced Reviewer**: Google Gemini for comprehensive suggestions

## 📁 Output Files

The tool generates several output files in the `artifacts/` directory:

- `review_{provider}_{pr_number}.json`: Complete review data
- `review_{provider}_{pr_number}.md`: Human-readable markdown report

### Sample JSON Output

```json
{
  "pr_context": {
    "provider": "github",
    "owner": "microsoft",
    "repo": "vscode", 
    "pr_number": 123,
    "title": "Add new feature",
    "files": [...]
  },
  "review": {
    "comments": [...],
    "summary": "Found 3 issues: 1 warning, 2 suggestions",
    "metadata": {...},
    "score": {
      "score": 82,
      "grade": "B+",
      "breakdown": {...},
      "recommendations": [...]
    }
  },
  "timestamp": "2023-01-01T12:00:00Z",
  "version": "1.0"
}
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_scoring.py

# Run with coverage
pytest --cov=src tests/

# Run with verbose output
pytest -v tests/
```

### Test Coverage

The test suite covers:
- ✅ Scoring algorithm validation
- ✅ Review schema validation
- ✅ Configuration loading
- ✅ Edge cases and error handling

## 🛠️ Development

### Project Structure

```
pr_review_agent/
├── .github/workflows/       # GitHub Actions workflows
├── frontend/                # 🆕 React TypeScript Web Dashboard
│   ├── src/                 # Frontend source code
│   ├── public/              # Static assets
│   ├── setup.bat/.sh        # Platform setup scripts
│   └── README.md            # Frontend documentation
├── src/                     # Backend source code
│   ├── providers/           # LLM provider implementations
│   ├── main.py              # CLI entrypoint  
│   ├── server.py            # Flask HTTP server
│   ├── config.py            # Configuration management
│   ├── fetch_prs.py         # Git provider adapters
│   ├── repo_checkout.py     # Repository management
│   ├── analyze_code.py      # Code analysis orchestration
│   ├── review_generator.py  # Review formatting
│   ├── scoring.py           # Quality scoring
│   ├── ci_integration.py    # CI/CD helpers
│   └── utils.py             # Utility functions
├── tests/                   # Test suite
├── artifacts/               # Generated reports
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

### Adding New Providers

1. **Extend the base fetcher:**
```python
# In src/fetch_prs.py
class CustomFetcher(PRFetcher):
    def get_pr_info(self, owner, repo, pr_number):
        # Implement provider-specific logic
        pass
```

2. **Register the provider:**
```python
# In get_fetcher() function
fetchers["custom"] = CustomFetcher
```

3. **Add configuration:**
```python
# In src/config.py
self.custom_token = os.getenv("CUSTOM_TOKEN")
```

### Adding New Analysis Tools

1. **Create analyzer class:**
```python
# In src/analyze_code.py
class CustomAnalyzer(StaticAnalyzer):
    def analyze(self, file_path, content):
        # Implement analysis logic
        return findings
```

2. **Register analyzer:**
```python
# In CodeAnalyzer.__init__()
self.static_analyzers['custom'] = CustomAnalyzer()
```

## 🚨 Troubleshooting

### Common Issues

**1. PowerShell Execution Policy Error**
```
Solution: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

**2. Missing OpenAI API Key**
```
Error: Configuration error, missing_config: ['OPENAI_API_KEY']
Solution: Add OPENAI_API_KEY to your .env file
```

**3. Git Authentication Failed**
```
Error: Failed to get PR details
Solution: Verify your git provider token has correct permissions
```

**4. Static Analysis Tools Not Found**
```
Warning: Bandit not available or timed out
Solution: Ensure all tools are installed: pip install bandit flake8 radon
```

**5. Large Repository Timeout**
```
Error: Repository checkout failed
Solution: Try with smaller PRs or increase timeout settings
```

### Debug Mode

Enable verbose logging:
```bash
python -m src.main review --provider github --owner owner --repo repo --pr 123 --verbose
```

### Required Permissions

**GitHub Token Permissions:**
- `repo` (for private repos) or `public_repo` (for public repos)
- `pull_requests:write` (for posting comments)

**GitLab Token Permissions:**
- `api` scope
- `read_repository` 
- `write_repository` (for comments)

**Bitbucket App Password:**
- `Repositories: Read`
- `Pull requests: Write` (for comments)

## � Deployment

### Free Hosting Setup (No Credit Card Required)

The application is deployed using:
- **Backend**: [Railway.app](https://railway.app) (Free Tier)
- **Frontend**: [Cloudflare Pages](https://pages.cloudflare.com) (Free Tier)

**Quick Deploy:**

1. **Backend (Railway)**
   ```bash
   # Fork this repository
   # Connect to Railway: https://railway.app/new
   # Add environment variable: GEMINI_API_KEY=your_key
   # Railway auto-deploys from main branch
   ```

2. **Frontend (Cloudflare Pages)**
   ```bash
   # Connect to Cloudflare Pages: https://pages.cloudflare.com
   # Build command: cd frontend && npm install && npm run build
   # Output directory: frontend/dist
   # Add environment variable: VITE_API_URL=https://your-railway-app.up.railway.app
   ```

**For detailed deployment instructions**, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

### Deployment Architecture

```
GitHub (main branch)
     │
     ├─────────────────────┐
     │                     │
     ▼                     ▼
Railway.app          Cloudflare Pages
(Backend API)        (React Frontend)
     │                     │
     └──────── API ────────┘
        (CORS Enabled)
```

### Environment Variables

**Backend (Railway)**:
```bash
GEMINI_API_KEY=your_gemini_key
PORT=8080  # Auto-set by Railway
FLASK_ENV=production
```

**Frontend (Cloudflare Pages)**:
```bash
VITE_API_URL=https://pr-review-production.up.railway.app
```

### CI/CD Pipeline

Automated deployment via GitHub Actions:
- ✅ Tests run on every push
- ✅ Auto-deploy to Railway (backend)
- ✅ Auto-deploy to Cloudflare Pages (frontend)
- ✅ Deployment status in README badges

## �📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`) 
5. Open a Pull Request

## 📞 Support

- 📚 Documentation: Check this README
- 🐛 Issues: Open a GitHub issue
- 💬 Discussions: Use GitHub Discussions
- 📧 Email: [Your contact email]

## 🔮 Future Enhancements

- [ ] Support for more programming languages
- [ ] Integration with more static analysis tools
- [ ] Custom rule configuration
- [ ] Web dashboard for review management
- [ ] Slack/Teams notifications
- [ ] Performance benchmarking
- [ ] Code quality trends over time

---

**Made with ❤️ by the PR Review Agent team**