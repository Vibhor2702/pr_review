# 🚀 Streamlit UI for PR Review Agent

This guide shows how to run the PR Review Agent with a **Streamlit web interface** for interactive PR reviews.

## 🎯 Quick Start

### 1. Install Dependencies
```powershell
cd "C:\Users\versu\OneDrive\Desktop\PR@REVIEW\pr_review_agent"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Set Environment Variables (Optional)
```powershell
# For AI-powered analysis (optional)
$env:GEMINI_API_KEY = "your_gemini_api_key_here"

# For private repos (optional)
$env:GITHUB_TOKEN = "your_github_token_here"
```

### 3. Launch Streamlit App
```powershell
streamlit run streamlit_app.py
```

The app will open at: **http://localhost:8501**

---

## 🖥️ Interface Features

### Sidebar Controls
- **Provider**: Choose GitHub, GitLab, or Bitbucket
- **Owner/Org**: Repository owner (e.g., "microsoft")
- **Repository**: Repository name (e.g., "vscode") 
- **PR Number**: Pull request number to review
- **Enable LLM**: Toggle AI-powered analysis (requires API key)

### Results Display
- **Metrics**: Score, Grade, Error/Warning counts
- **Summary**: Overall assessment text
- **Findings**: Detailed list of issues with:
  - File path and line number
  - Severity level (ERROR/WARNING/INFO)
  - Analysis tool used
  - Detailed message and suggestions

### Download Options
- **JSON Artifact**: Complete review data for CI integration

---

## 🎨 Example Usage

### 1. Public Repository Review
```
Provider: github
Owner: microsoft  
Repository: vscode
PR Number: 123
Enable LLM: ✅ (if API key available)
```

### 2. Quick Style Check
```
Provider: github
Owner: your-org
Repository: your-repo
PR Number: 42
Enable LLM: ❌ (static analysis only)
```

---

## 🔧 Configuration

### Environment Variables
| Variable | Required | Purpose |
|----------|----------|---------|
| `GEMINI_API_KEY` | Optional | AI-powered analysis |
| `GITHUB_TOKEN` | Optional | Private repo access |
| `GITLAB_TOKEN` | Optional | GitLab integration |
| `BITBUCKET_TOKEN` | Optional | Bitbucket integration |

### Without API Keys
The app works with **static analysis only**:
- Security scanning (Bandit)
- Code style checks (Flake8)  
- Complexity analysis (Radon)
- Syntax validation

---

## 🚀 Deployment Options

### Local Development
```powershell
streamlit run streamlit_app.py --server.port 8501
```

### Production Deployment
```powershell
# With custom host/port
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8080

# Headless mode (no browser auto-open)
$env:STREAMLIT_SERVER_HEADLESS="true"
streamlit run streamlit_app.py
```

### Cloud Deployment
The app can be deployed to:
- **Streamlit Cloud** (streamlit.io)
- **Heroku** with Streamlit buildpack
- **Railway** with streamlit run command
- **Docker** with streamlit base image

---

## 🔍 Troubleshooting

### Common Issues

#### "Module not found" errors
```powershell
# Ensure you're in the right directory and venv is activated
cd pr_review_agent
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### App won't start
```powershell
# Check if port is in use
netstat -an | findstr 8501

# Try different port
streamlit run streamlit_app.py --server.port 8502
```

#### Review fails without API keys
- Disable "Enable LLM" checkbox
- App will run static analysis only
- Still provides valuable code quality insights

#### Empty results
- Check that PR number exists
- Verify repository is public (or token provided for private)
- Ensure PR has code changes (not just docs)

---

## 🎯 Comparison with Other Interfaces

| Interface | Best For | Pros | Cons |
|-----------|----------|------|------|
| **Streamlit** | Interactive exploration | Visual, user-friendly | Single-user sessions |
| **CLI** | Automation, scripts | Fast, scriptable | Terminal-only |
| **REST API** | CI/CD integration | Programmatic access | Requires HTTP client |
| **React Dashboard** | Team dashboards | Professional UI | More complex setup |

---

## 📊 Performance Notes

- **Startup**: ~3-5 seconds
- **Review Time**: 30-60 seconds per PR
- **Memory Usage**: ~150MB base + repo size
- **Concurrent Users**: Single session per instance

---

## 🛠️ Development Tips

### Custom Styling
```python
# Add to streamlit_app.py
st.markdown("""
<style>
.stApp > header[data-testid="stHeader"] {
    background-color: transparent;
}
</style>
""", unsafe_allow_html=True)
```

### Add New Metrics
```python
# In main() function
col1, col2 = st.columns(2)
col1.metric("Custom Metric", value)
col2.metric("Another Metric", value2)
```

---

## 🎉 Success!

Your PR Review Agent Streamlit interface is ready! 

Open **http://localhost:8501** and start reviewing pull requests with an intuitive web interface.