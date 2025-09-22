# PR Review Agent - Complete Usage Guide

## Overview

The PR Review Agent is a sophisticated code analysis tool that automatically reviews pull requests across GitHub, GitLab, and Bitbucket. It combines static code analysis with intelligent feedback to provide comprehensive code reviews and quality scoring.

## How It Works

### 1. **Multi-Platform Integration**
- Connects to GitHub, GitLab, and Bitbucket APIs
- Fetches PR details, diffs, and file changes
- Supports both public and private repositories

### 2. **Static Code Analysis**
- **Syntax Validation**: Uses Python AST to check for syntax errors
- **Security Analysis**: Runs Bandit to identify security vulnerabilities
- **Style Checking**: Uses Flake8/PyFlakes for code style issues
- **Complexity Analysis**: Uses Radon to measure cyclomatic complexity

### 3. **Intelligent Review**
- **Language Model Integration**: Uses Google Gemini for intelligent code suggestions
- **Context-Aware Analysis**: Considers code context and best practices
- **Structured Feedback**: Provides actionable suggestions with confidence levels

### 4. **Quality Scoring**
- **Weighted Scoring**: Combines multiple metrics into a 0-100 score
- **Letter Grades**: A+ to F grading system
- **Detailed Breakdown**: Shows individual penalty categories
- **Recommendations**: Provides specific improvement suggestions

## Setup Instructions

### Prerequisites
- Python 3.10 or higher
- Git installed on your system
- API access to your target repositories

### Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd pr_review_agent
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   ```

3. **Activate Virtual Environment**
   
   **Windows PowerShell:**
   ```powershell
   # If you get execution policy error, run this first:
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   
   # Then activate:
   .\venv\Scripts\Activate.ps1
   ```
   
   **Windows Command Prompt:**
   ```cmd
   venv\Scripts\activate.bat
   ```
   
   **Linux/macOS:**
   ```bash
   source venv/bin/activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

### Required API Keys

#### Google Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key to your `.env` file:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

#### Git Provider Tokens (Optional but Recommended)

**GitHub:**
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Create a new token with `repo` and `pull_requests` permissions
3. Add to `.env`: `GITHUB_TOKEN=your_token_here`

**GitLab:**
1. Go to GitLab Settings → Access Tokens
2. Create token with `api` and `read_repository` scopes
3. Add to `.env`: `GITLAB_TOKEN=your_token_here`

**Bitbucket:**
1. Go to Bitbucket Settings → App passwords
2. Create password with `Repositories: Read` permission
3. Add to `.env`: `BITBUCKET_TOKEN=your_token_here`

## Usage Examples

### Command Line Interface

#### Basic PR Review
```bash
python -m src.main review \
  --provider github \
  --owner microsoft \
  --repo vscode \
  --pr 12345
```

#### Review with Custom Output
```bash
python -m src.main review \
  --provider gitlab \
  --owner myorg \
  --repo myproject \
  --pr 42 \
  --output ./custom-reviews \
  --verbose
```

#### Static Analysis Only (No Intelligent Features)
```bash
python -m src.main review \
  --provider github \
  --owner owner \
  --repo repo \
  --pr 123 \
  --no-llm
```

### HTTP API Server

#### Start the Server
```bash
python -m src.main serve --host 0.0.0.0 --port 5000
```

#### API Endpoints

**Review a Pull Request:**
```bash
curl -X POST http://localhost:5000/review_pr \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "github",
    "owner": "microsoft",
    "repo": "vscode",
    "pr_number": 12345
  }'
```

**Health Check:**
```bash
curl http://localhost:5000/health
```

**Configuration Status:**
```bash
curl http://localhost:5000/config
```

## Output Formats

### JSON Output Structure
```json
{
  "pr_context": {
    "provider": "github",
    "owner": "microsoft",
    "repo": "vscode",
    "pr_number": 12345,
    "head_ref": "feature-branch",
    "base_ref": "main"
  },
  "review": {
    "comments": [
      {
        "file": "src/example.py",
        "line": 42,
        "message": "Consider using a more descriptive variable name",
        "severity": "info",
        "tool": "flake8",
        "suggestion": "Replace 'n' with 'user_count'",
        "confidence": 0.8
      }
    ],
    "score": {
      "score": 85,
      "grade": "B+",
      "breakdown": {
        "style_penalty": 5,
        "security_penalty": 0,
        "complexity_penalty": 10,
        "total_files": 3,
        "total_lines": 156
      }
    },
    "metadata": {
      "total_comments": 5,
      "files_analyzed": 3,
      "timestamp": "2024-01-15T10:30:00Z"
    }
  }
}
```

### Markdown Report
The tool also generates human-readable markdown reports with:
- Executive summary
- Score breakdown
- Most problematic files
- Detailed findings by file
- Improvement recommendations

## CI/CD Integration

### GitHub Actions

The included workflow (`.github/workflows/pr_review.yml`) automatically:
1. Runs on every pull request
2. Analyzes the changes
3. Posts results as PR comments
4. Saves detailed reports as artifacts
5. Sets quality gates based on scores

**Setup:**
1. Add repository secrets:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `GITHUB_TOKEN`: Automatically provided by GitHub Actions
2. Commit the workflow file
3. The agent will run automatically on new PRs

### Custom CI Integration

For other CI systems, use the CLI:
```bash
# In your CI script
python -m src.main review \
  --provider github \
  --owner $CI_REPO_OWNER \
  --repo $CI_REPO_NAME \
  --pr $CI_PR_NUMBER \
  --output $CI_ARTIFACTS_DIR
```

## Configuration Options

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes* | - | Google Gemini API key |
| `GITHUB_TOKEN` | No | - | GitHub personal access token |
| `GITLAB_TOKEN` | No | - | GitLab access token |
| `BITBUCKET_TOKEN` | No | - | Bitbucket app password |
| `LLM_TEMPERATURE` | No | `0.3` | Model creativity (0-1) |
| `CI_POST_REVIEW` | No | `false` | Auto-post comments in CI |
| `SERVER_HOST` | No | `0.0.0.0` | Server bind address |
| `SERVER_PORT` | No | `5000` | Server port |

*Required only for intelligent features

### Scoring Weights

Customize scoring in your environment:
```env
WEIGHT_STYLE=5.0
WEIGHT_SECURITY=15.0
WEIGHT_COMPLEXITY=10.0
WEIGHT_TEST_COVERAGE=8.0
BASE_SCORE=100.0
```

## Quality Score Interpretation

| Score | Grade | Quality Level |
|-------|-------|---------------|
| 90-100 | A+ | Excellent |
| 85-89 | A | Very Good |
| 80-84 | A- | Good |
| 75-79 | B+ | Above Average |
| 70-74 | B | Average |
| 65-69 | B- | Below Average |
| 60-64 | C+ | Needs Improvement |
| 55-59 | C | Poor |
| 50-54 | D | Failing |
| 0-49 | F | Critical Issues |

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## Troubleshooting

### Common Issues

**ModuleNotFoundError: No module named 'google'**
- Ensure `google-generativeai` is installed: `pip install google-generativeai`

**403 Forbidden when accessing repositories**
- Check that your tokens have the required permissions
- Verify the repository exists and is accessible

**Empty review results**
- Ensure the PR has actual code changes
- Check that changed files are in supported languages (primarily Python)

**High memory usage**
- Large repositories may consume significant memory during analysis
- Consider using `--no-llm` for very large PRs to reduce processing time

### Debug Mode

Enable verbose logging:
```bash
python -m src.main review [...] --verbose
```

## Architecture

### Component Overview

- **`src/main.py`**: CLI interface and command routing
- **`src/server.py`**: HTTP API server using Flask
- **`src/fetch_prs.py`**: Git provider API adapters
- **`src/repo_checkout.py`**: Repository cloning and checkout management
- **`src/analyze_code.py`**: Static analysis orchestration
- **`src/providers/`**: Language model provider abstractions
- **`src/review_generator.py`**: Report generation and formatting
- **`src/scoring.py`**: Quality scoring algorithms
- **`src/ci_integration.py`**: CI/CD integration helpers

### Data Flow

1. **Fetch**: Get PR metadata from git provider API
2. **Checkout**: Clone repository and checkout PR branch
3. **Analyze**: Run static tools and intelligent analysis
4. **Generate**: Create structured review comments
5. **Score**: Calculate quality metrics
6. **Output**: Generate JSON/markdown reports
7. **Integrate**: Post to PR or save artifacts

## Best Practices

### For Development Teams

1. **Set Quality Gates**: Configure CI to fail below certain scores
2. **Regular Reviews**: Run on all PRs, not just large changes
3. **Team Standards**: Customize scoring weights for your team's priorities
4. **Incremental Adoption**: Start with static analysis, add intelligent features gradually

### For CI/CD

1. **Artifact Storage**: Always save detailed reports for later review
2. **Comment Management**: Use `CI_POST_REVIEW=true` judiciously to avoid spam
3. **Timeout Handling**: Set appropriate timeouts for large repositories
4. **Resource Limits**: Monitor memory/CPU usage in CI environments

### Security Considerations

1. **Token Management**: Use repository secrets, never commit tokens
2. **Least Privilege**: Grant minimal required permissions to tokens
3. **Network Security**: Consider firewall rules for self-hosted instances
4. **Code Sandboxing**: The tool only analyzes code, never executes it

## Support and Contributing

This tool is designed to be extensible. Key extension points:

- **New Git Providers**: Implement the `PRFetcher` interface
- **Additional Languages**: Extend static analyzers
- **Custom Scoring**: Modify scoring algorithms
- **New LLM Providers**: Implement the `LLMProvider` interface

The codebase follows professional development practices with comprehensive testing, type hints, and documentation.