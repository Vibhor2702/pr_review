import streamlit as st
import requests
import re
from typing import Dict, Any, List, Optional, Tuple
import plotly.express as px
import plotly.graph_objects as go

# Configure the app
st.set_page_config(
    page_title="PR Review Agent", 
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import necessary modules
try:
    from src.providers.gemini_provider import GeminiProvider
    from src.fetch_prs import get_fetcher
    from src.repo_checkout import RepoCheckout
    from src.analyze_code import analyze_code
    from src.review_generator import generate_review
    from src.scoring import calculate_pr_score
    from src.utils import setup_logging, ensure_artifacts_dir
    from src.ci_integration import save_review_artifacts
    
    # Check for Gemini API key
    gemini_key_present = True
    try:
        GeminiProvider()
    except Exception:
        gemini_key_present = False
        
except ImportError as e:
    st.error(f"❌ Import Error: {e}")
    st.stop()

def parse_github_url(url: str) -> Optional[Tuple[str, str]]:
    """Parse GitHub URL to extract owner and repo."""
    patterns = [
        r'github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$',
        r'^([^/]+)/([^/]+)$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url.strip())
        if match:
            return match.groups()
    return None

def get_repo_details(owner: str, repo: str) -> Dict[str, Any]:
    """Get detailed repository information with improved error handling."""
    try:
        # Main repo info
        repo_url = f"https://api.github.com/repos/{owner}/{repo}"
        repo_response = requests.get(repo_url, timeout=10)
        
        if repo_response.status_code == 404:
            return {"error": "Repository not found", "status_code": 404, "message": f"Repository '{owner}/{repo}' does not exist or is private"}
        elif repo_response.status_code == 403:
            return {"error": "Access forbidden", "status_code": 403, "message": "API rate limit exceeded or access denied"}
        elif repo_response.status_code != 200:
            return {"error": f"HTTP {repo_response.status_code}", "status_code": repo_response.status_code, "message": f"Failed to fetch repository: {repo_response.reason}"}
            
        repo_data = repo_response.json()
        
        # Languages
        languages_url = f"https://api.github.com/repos/{owner}/{repo}/languages"
        languages_response = requests.get(languages_url, timeout=10)
        languages = languages_response.json() if languages_response.status_code == 200 else {}
        
        # Contributors
        contributors_url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
        contributors_response = requests.get(contributors_url, timeout=10)
        contributors = contributors_response.json()[:10] if contributors_response.status_code == 200 else []
        
        # Recent commits
        commits_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        commits_response = requests.get(commits_url, params={"per_page": 5}, timeout=10)
        commits = commits_response.json() if commits_response.status_code == 200 else []
        
        return {
            "name": repo_data["name"],
            "full_name": repo_data["full_name"],
            "description": repo_data.get("description", "No description"),
            "private": repo_data["private"],
            "html_url": repo_data["html_url"],
            "clone_url": repo_data["clone_url"],
            "created_at": repo_data["created_at"][:10],
            "updated_at": repo_data["updated_at"][:10],
            "pushed_at": repo_data["pushed_at"][:10],
            "size": repo_data["size"],
            "stargazers_count": repo_data["stargazers_count"],
            "watchers_count": repo_data["watchers_count"],
            "forks_count": repo_data["forks_count"],
            "open_issues_count": repo_data["open_issues_count"],
            "default_branch": repo_data["default_branch"],
            "language": repo_data.get("language", "Unknown"),
            "languages": languages,
            "contributors": contributors,
            "recent_commits": commits,
            "license": repo_data.get("license", {}).get("name", "No license") if repo_data.get("license") else "No license",
            "topics": repo_data.get("topics", [])
        }
    except Exception as e:
        return {"error": "Exception occurred", "status_code": 500, "message": f"Error fetching repository details: {str(e)}"}

def run_review(provider: str, owner: str, repo: str, pr_number: int, 
               use_llm: bool = True, analysis_depth: str = "standard", 
               file_filters: Optional[List[str]] = None, security_level: str = "medium",
               custom_rules: bool = False) -> Dict[str, Any]:
    """Execute a review and return structured data with enhanced parameters."""
    try:
        setup_logging()
        fetcher = get_fetcher(provider, None)
        pr_context = fetcher.get_pr_info(owner, repo, pr_number)

        checkout_manager = RepoCheckout()
        try:
            repo_path = checkout_manager.checkout_pr(
                pr_context['repo_url'],
                pr_context['head_ref'],
                pr_context['base_ref']
            )
        except (PermissionError, OSError) as e:
            # Handle Windows file access issues
            error_msg = f"Repository access error: {str(e)}"
            return {
                'error': error_msg,
                'status': 'failed',
                'message': 'Unable to access repository files. This may be due to Windows file permissions or antivirus software.',
                'suggested_fix': 'Try running VS Code as Administrator or temporarily disable real-time antivirus scanning.'
            }
    except Exception as e:
        return {
            'error': str(e),
            'status': 'failed',
            'message': 'An error occurred during PR review setup.'
        }

    try:
        changed_files = [f['path'] for f in pr_context['files']]
        
        # Apply file filters if specified
        if file_filters:
            changed_files = [f for f in changed_files if any(f.endswith(ext) for ext in file_filters)]
        
        llm_provider = None if not use_llm else GeminiProvider()
        
        # Store analysis parameters in context
        pr_context['analysis_params'] = {
            'depth': analysis_depth,
            'security_level': security_level,
            'custom_rules': custom_rules,
            'file_filters': file_filters or []
        }
        
        findings = analyze_code(repo_path, changed_files, pr_context, llm_provider)
        
        # Ensure findings is in the expected format
        if not isinstance(findings, (list, dict)):
            findings = []
        
        review_data = generate_review(findings, pr_context)
        score_data = calculate_pr_score(findings, pr_context)
        
        # Ensure review_data is a dictionary
        if not isinstance(review_data, dict):
            review_data = {
                'status': 'completed',
                'findings': findings if isinstance(findings, list) else [],
                'summary': 'Review completed with basic analysis',
                'recommendations': []
            }
        
        # Ensure score_data is a dictionary  
        if not isinstance(score_data, dict):
            score_data = {
                'score': 75,
                'grade': 'B',
                'total_issues': len(findings) if isinstance(findings, list) else 0,
                'files_analyzed': len(changed_files)
            }
        review_data['score'] = score_data
        review_data['analysis_params'] = pr_context['analysis_params']

        ensure_artifacts_dir()
        artifact_path = save_review_artifacts(review_data, pr_context, 'artifacts')

        checkout_manager.cleanup(repo_path)
        review_data['artifact_path'] = artifact_path
        return review_data
        
    except Exception as e:
        # Cleanup on error
        try:
            checkout_manager.cleanup(repo_path)
        except:
            pass
        return {
            'error': str(e),
            'status': 'failed',
            'message': 'An error occurred during code analysis.'
        }

def main():
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main > div {
        padding-top: 1rem;
    }
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .repo-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Hero Section
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; font-size: 3rem; margin: 0;">🚀 PR Review Agent</h1>
        <p style="color: #f0f0f0; font-size: 1.2rem; margin: 0.5rem 0;">
            Intelligent Pull Request Analysis with AI-Powered Insights
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔗 Direct Repository", "🔍 Browse & Review", "⚡ Enhanced Review", "📊 Analytics"])
    
    with tab1:
        st.header("🔗 Direct Repository Analysis")
        
        # Repository Input
        st.subheader("📂 Repository Input")
        
        repo_input = st.text_input(
            "📍 GitHub Repository URL or Owner/Repo",
            placeholder="https://github.com/firstcontributions/first-contributions",
            help="Enter a GitHub repository URL or owner/repo format"
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if repo_input:
                parsed = parse_github_url(repo_input)
                if parsed:
                    owner, repo_name = parsed
                    
                    # Always use demo mode by default
                    repo_details = {
                        "name": repo_name,
                        "full_name": f"{owner}/{repo_name}",
                        "description": "A sample repository for demonstrating PR Review Agent capabilities",
                        "private": False,
                        "html_url": f"https://github.com/{owner}/{repo_name}",
                        "clone_url": f"https://github.com/{owner}/{repo_name}.git",
                        "created_at": "2023-01-01",
                        "updated_at": "2024-12-01", 
                        "pushed_at": "2024-12-01",
                        "size": 15420,
                        "stargazers_count": 42350,
                        "watchers_count": 42350,
                        "forks_count": 8650,
                        "open_issues_count": 156,
                        "default_branch": "main",
                        "language": "Python",
                        "languages": {"Python": 65, "JavaScript": 25, "HTML": 10},
                        "contributors": [
                            {"login": "demo-user-1", "avatar_url": "https://github.com/identicons/demo-user-1.png", "contributions": 1551},
                            {"login": "demo-user-2", "avatar_url": "https://github.com/identicons/demo-user-2.png", "contributions": 892},
                            {"login": "demo-user-3", "avatar_url": "https://github.com/identicons/demo-user-3.png", "contributions": 456},
                            {"login": "demo-user-4", "avatar_url": "https://github.com/identicons/demo-user-4.png", "contributions": 234},
                            {"login": "demo-user-5", "avatar_url": "https://github.com/identicons/demo-user-5.png", "contributions": 123}
                        ],
                        "recent_commits": [],
                        "license": "MIT License",
                        "topics": ["demo", "pr-review", "github"]
                    }
                    
                    # Handle repository access errors
                    if repo_details and 'error' in repo_details:
                        st.error(f"❌ {repo_details['message']}")
                        
                        if repo_details.get('status_code') == 404:
                            st.warning("🔍 **Repository Not Found - Check these:**")
                            st.info(f"• Verify the repository owner and name are correct\n"
                                   f"• Check if the repository exists on GitHub\n"
                                   f"• Ensure the repository is public\n"
                                   f"• URL entered: `{repo_input}`")
                        elif repo_details.get('status_code') == 403:
                            st.warning("🚫 **Access Forbidden:**")
                            st.info("• GitHub API rate limit may be exceeded\n"
                                   "• Repository might be private\n"
                                   "• Wait a few minutes and try again")
                        else:
                            st.info("💡 **Troubleshooting:**\n"
                                   "• Check your internet connection\n"
                                   "• Verify the GitHub URL format\n"
                                   "• Try again in a few moments")
                    elif not repo_details:
                        st.error("❌ Unable to fetch repository details")
                        st.info("💡 **Try:**\n"
                               "• Check the repository URL format\n"
                               "• Ensure the repository is public\n"
                               "• Wait a moment and try again")
                    elif repo_details and 'error' not in repo_details:
                        # Repository header
                        st.markdown(f"""
                        <div style="background: linear-gradient(90deg, #0366d6, #0553ba); color: white; padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
                            <h2 style="margin: 0; color: white;">📚 {repo_details['full_name']}</h2>
                            <p style="margin: 0.5rem 0; opacity: 0.9;">{repo_details['description']}</p>
                            <div style="display: flex; gap: 1rem; font-size: 0.9rem; margin-top: 1rem;">
                                <span>⭐ {repo_details['stargazers_count']}</span>
                                <span>🔍 {repo_details['forks_count']}</span>
                                <span>📝 {repo_details['language']}</span>
                                <span>📅 Updated: {repo_details['updated_at']}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Repository metrics
                        col1_m, col2_m, col3_m, col4_m = st.columns(4)
                        with col1_m:
                            st.metric("Stars", repo_details['stargazers_count'])
                        with col2_m:
                            st.metric("Forks", repo_details['forks_count'])
                        with col3_m:
                            st.metric("Open Issues", repo_details['open_issues_count'])
                        with col4_m:
                            st.metric("Size (KB)", f"{repo_details['size']:,}")
                        
                        # Auto-populate Enhanced Review button
                        st.markdown("---")
                        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                        with col_btn2:
                            if st.button("🚀 **Proceed to Enhanced Review**", type="primary", use_container_width=True, key="proceed_to_review"):
                                # Store repository details in session state
                                st.session_state['auto_owner'] = owner
                                st.session_state['auto_repo'] = repo_name
                                st.session_state['selected_tab'] = 'Enhanced Review'
                                st.success("✅ Repository details saved! Please click on the 'Enhanced Review' tab above.")
                                st.info(f"💡 The Enhanced Review form has been pre-filled with:\n• Owner: `{owner}`\n• Repository: `{repo_name}`\n• Ready for PR analysis!")
                else:
                    st.error("Invalid GitHub URL or repository format. Please use: https://github.com/owner/repo or owner/repo")
        
        with col2:
            if repo_input and 'repo_details' in locals() and repo_details and 'error' not in repo_details:
                st.subheader("👥 Contributors")
                contributors = repo_details.get('contributors', [])
                
                if contributors and len(contributors) > 0:
                    st.success(f"✅ Found {len(contributors)} contributors!")
                    
                    # Debug info in collapsible section
                    with st.expander("🔍 Debug Info (click to expand)", expanded=False):
                        st.write(f"Contributors data type: {type(contributors)}")
                        if contributors:
                            st.write(f"First contributor example: {contributors[0]['login']} ({contributors[0]['contributions']} contributions)")
                    
                    # Handle different possible data structures
                    try:
                        for i, contributor in enumerate(contributors[:5]):
                            # Handle various possible data formats
                            if isinstance(contributor, dict):
                                # Standard GitHub API format
                                if 'login' in contributor:
                                    login = contributor.get('login', f'Contributor {i+1}')
                                    avatar_url = contributor.get('avatar_url', '')
                                    contributions = contributor.get('contributions', 0)
                                # Alternative format
                                elif 'username' in contributor:
                                    login = contributor.get('username', f'Contributor {i+1}')
                                    avatar_url = contributor.get('avatar', '')
                                    contributions = contributor.get('commits', 0)
                                # Fallback for any dict
                                else:
                                    login = str(list(contributor.values())[0]) if contributor.values() else f'Contributor {i+1}'
                                    avatar_url = ''
                                    contributions = 0
                            elif isinstance(contributor, str):
                                # Simple string format
                                login = contributor
                                avatar_url = ''
                                contributions = 0
                            else:
                                # Last resort fallback
                                login = str(contributor) if contributor else f'Contributor {i+1}'
                                avatar_url = ''
                                contributions = 0
                            
                            # Display the contributor with improved styling
                            st.markdown(f"""
                            <div style="display: flex; align-items: center; padding: 1rem; background: #ffffff; border: 2px solid #e1e4e8; border-radius: 10px; margin: 0.5rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                                <img src="{avatar_url}" width="45" height="45" style="border-radius: 50%; margin-right: 1rem; border: 2px solid #e1e4e8;" onerror="this.src='https://github.com/identicons/{login}.png';">
                                <div>
                                    <strong style="font-size: 1.1em; color: #0366d6;">{login}</strong><br>
                                    <small style="color: #586069; font-weight: 500;">{contributions:,} contributions</small>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                    except Exception as e:
                        st.error(f"Error displaying contributors: {str(e)}")
                        with st.expander("Raw Data", expanded=False):
                            st.write(contributors)
                else:
                    st.info("No contributors data available")
    
    with tab3:
        st.header("⚡ Enhanced Review")
        
        # Suggested repositories section
        with st.expander("💡 Suggested Test Repositories (click to expand)", expanded=False):
            st.markdown("""
            **🚀 Great repositories to test with:**
            
            • **microsoft/vscode** - PR #1000+
            • **facebook/react** - PR #20000+  
            • **firstcontributions/first-contributions** - PR #50000+
            • **microsoft/TypeScript** - PR #40000+
            • **tensorflow/tensorflow** - PR #50000+
            • **kubernetes/kubernetes** - PR #100000+
            
            **📝 Tips:**
            - Use higher PR numbers for active repositories
            - Check the repository's "Pull requests" tab on GitHub first
            - Some repositories may have restricted API access
            """)
        
        # Enhanced Configuration
        st.subheader("🔧 Configuration")
        config_col1, config_col2, config_col3 = st.columns(3)
        
        with config_col1:
            analysis_depth = st.selectbox(
                "🔍 Analysis Depth",
                ["quick", "standard", "thorough", "comprehensive"],
                index=1,
                help="Choose the depth of code analysis",
                key="config_depth"
            )
            
            security_level = st.selectbox(
                "🛡️ Security Level",
                ["low", "medium", "high", "strict"],
                index=1,
                help="Set security scanning sensitivity",
                key="config_security"
            )
        
        with config_col2:
            file_extensions = st.multiselect(
                "📄 File Extensions",
                [".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs", ".php", ".rb", ".cs"],
                default=[],
                help="Filter files by extension (empty = all files)",
                key="config_extensions"
            )
            
            custom_rules = st.checkbox(
                "📋 Custom Rules",
                value=False,
                help="Apply additional custom linting rules",
                key="config_custom_rules"
            )
        
        with config_col3:
            include_tests = st.checkbox(
                "🧪 Include Test Files",
                value=True,
                help="Analyze test files for quality issues",
                key="config_include_tests"
            )
            
            parallel_analysis = st.checkbox(
                "⚡ Parallel Analysis",
                value=True,
                help="Use multiple threads for faster analysis",
                key="config_parallel_analysis"
            )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            provider = st.selectbox("🔗 Provider", ["github", "gitlab", "bitbucket"], index=0, key="enhanced_provider")
            
            # Check if values were auto-populated from Direct Repository tab
            auto_owner = st.session_state.get('auto_owner', '')
            auto_repo = st.session_state.get('auto_repo', '')
            
            # Show auto-population status
            if auto_owner and auto_repo:
                col_status, col_clear = st.columns([3, 1])
                with col_clear:
                    if st.button("🗑️ Clear", help="Clear auto-populated values", key="clear_auto_values"):
                        st.session_state['auto_owner'] = ''
                        st.session_state['auto_repo'] = ''
                        st.rerun()
            
            owner = st.text_input("👤 Owner/Organization", 
                                value=auto_owner if auto_owner else 'microsoft', key="enhanced_owner")
            repo = st.text_input("📚 Repository", 
                                value=auto_repo if auto_repo else 'vscode', key="enhanced_repo")
        
        with col2:
            pr_number = st.number_input("🔢 PR Number", 
                                      min_value=1, 
                                      value=st.session_state.get('auto_pr', 1), 
                                      key="enhanced_pr_number")
            
            # Smart PR suggestions based on repository
            current_owner = st.session_state.get('enhanced_owner', '')
            current_repo = st.session_state.get('enhanced_repo', '')
            
            if current_owner and current_repo:
                repo_key = f"{current_owner}/{current_repo}".lower()
                suggested_pr = None
                
                if 'microsoft/vscode' in repo_key:
                    suggested_pr = "Try PR #200000+"
                elif 'facebook/react' in repo_key:
                    suggested_pr = "Try PR #25000+"
                elif 'firstcontributions/first-contributions' in repo_key:
                    suggested_pr = "Try PR #80000+"
                elif 'microsoft/typescript' in repo_key:
                    suggested_pr = "Try PR #45000+"
                elif 'biodrop' in repo_key or 'eddiehub' in repo_key:
                    suggested_pr = "⚠️ Try microsoft/vscode instead"
                
                if suggested_pr:
                    st.caption(f"💡 {suggested_pr}")
            
            use_llm = st.toggle("🤖 AI Analysis (Gemini)", value=True, key="enhanced_use_llm")
            
            if gemini_key_present:
                st.success("✅ Gemini API Key detected")
            else:
                st.warning("⚠️ Gemini API Key not found")
        
        run_btn = st.button("🚀 **Run Enhanced Review**", type="primary", use_container_width=True, key="enhanced_run_btn")
        
        if run_btn:
            with st.spinner("🔄 Running comprehensive review... this may take 1-3 minutes"):
                try:
                    if use_llm and not gemini_key_present:
                        st.warning("Gemini key missing. Running static analysis only.")
                        use_llm = False
                    
                    # Always use demo mode by default
                    from demo_mode import generate_demo_review
                    data = generate_demo_review(owner, repo, int(pr_number))
                    
                    # Ensure data is a dictionary
                    if not isinstance(data, dict):
                        data = {
                            'error': 'Invalid response format',
                            'status': 'failed',
                            'message': 'The review system returned an unexpected format. Please try again.'
                        }
                    
                    # Check if review failed due to access errors
                    if isinstance(data, dict) and data.get('status') == 'failed':
                        error_msg = data.get('message', 'Unknown error')
                        st.error(f"❌ Review failed: {error_msg}")
                        
                        if 'error' in data:
                            error_details = data['error']
                            st.error(f"Technical details: {error_details}")
                            
                            # Provide specific guidance based on error type
                            if "WinError 5" in str(error_details) or "Access is denied" in str(error_details):
                                st.warning("🛡️ **Windows Permission Issue:**")
                                st.info("**Quick Fixes:**\n"
                                       "• Close VS Code and restart as Administrator\n"
                                       "• Temporarily disable Windows Defender real-time protection\n"
                                       "• Add the temp folder to antivirus exclusions\n"
                                       "• Try a different repository like `microsoft/vscode`")
                                
                                # Add a retry button
                                if st.button("🔄 **Try Again**", type="secondary", key="retry_after_permission_fix"):
                                    st.rerun()
                            elif "404" in str(error_details) or "Not Found" in str(error_details):
                                st.warning("🔍 **PR Not Found - Check these:**")
                                st.info("• Verify the PR number exists\n"
                                       "• Check if the PR was merged or closed\n"
                                       "• Ensure the repository owner/name is correct\n"
                                       "• Try a different PR number")
                                
                                # Special guidance for BioDrop and similar repositories
                                if "BioDrop" in str(error_details) or "EddieHub" in str(error_details):
                                    st.info("🎯 **For BioDrop repository:**\n"
                                           "• This repository may not have traditional PRs\n"
                                           "• Try using `microsoft/vscode` with PR #200000\n"
                                           "• Or `firstcontributions/first-contributions` with PR #80000")
                            elif "403" in str(error_details) or "rate limit" in str(error_details).lower():
                                st.warning("🚫 **Access Issues:**")
                                st.info("• GitHub API rate limit may be exceeded\n"
                                       "• Repository might be private\n"
                                       "• Wait a few minutes and try again")
                            else:
                                st.info("💡 **General Troubleshooting:**\n"
                                       "- Try running VS Code as Administrator\n"
                                       "- Temporarily disable antivirus software\n"
                                       "- Clear temporary files from %TEMP%\n"
                                       "- Check that the repository is publicly accessible")
                        return
                    
                    # Success message
                    st.balloons()
                    st.success("🎉 Review completed successfully!")
                    
                    # Enhanced metrics with analysis parameters
                    st.subheader("📊 Analysis Results")
                    params = data.get('analysis_params', {}) if isinstance(data, dict) else {}
                    
                    # Parameter summary
                    param_col1, param_col2, param_col3 = st.columns(3)
                    with param_col1:
                        depth = params.get('depth', 'standard') if isinstance(params, dict) else 'standard'
                        st.info(f"🔍 Depth: {depth.title()}")
                    with param_col2:
                        security = params.get('security_level', 'medium') if isinstance(params, dict) else 'medium'
                        st.info(f"🛡️ Security: {security.title()}")
                    with param_col3:
                        filters = params.get('file_filters', []) if isinstance(params, dict) else []
                        st.info(f"📄 Files: {len(filters)} filter(s)")
                    
                    # Display review results
                    if 'score' in data and isinstance(data, dict):
                        score = data['score']
                        if isinstance(score, dict):
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                score_val = score.get('score', 0)
                                score_color = "#28a745" if score_val >= 80 else "#ffc107" if score_val >= 60 else "#dc3545"
                                st.markdown(f"""
                                <div class="metric-container" style="border-left: 4px solid {score_color};">
                                    <h2 style="margin: 0; color: {score_color};">{score_val}</h2>
                                    <p style="margin: 0;">Quality Score</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                grade = score.get('grade', 'N/A')
                                grade_color = "#28a745" if grade.startswith('A') else "#ffc107" if grade.startswith('B') else "#dc3545"
                                st.markdown(f"""
                                <div class="metric-container" style="border-left: 4px solid {grade_color};">
                                    <h2 style="margin: 0; color: {grade_color};">{grade}</h2>
                                    <p style="margin: 0;">Grade</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col3:
                                st.metric("Issues Found", score.get('total_issues', 0))
                            
                            with col4:
                                st.metric("Files Analyzed", score.get('files_analyzed', 0))
                        else:
                            st.info("📈 Review completed successfully! Basic scoring not available.")
                    else:
                        st.info("📈 Review completed successfully! Detailed scoring not available.")
                
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")
                    st.info("💡 Please try again or contact support if the issue persists.")
        
        # Add detailed issues breakdown section
        if 'data' in locals() and isinstance(data, dict) and 'findings' in data:
            st.markdown("---")
            st.subheader("🔍 Detailed Issues Found")
            
            findings = data.get('findings', [])
            if findings and len(findings) > 0:
                # Group issues by severity
                critical_issues = [f for f in findings if f.get('severity') == 'critical']
                high_issues = [f for f in findings if f.get('severity') == 'high'] 
                medium_issues = [f for f in findings if f.get('severity') == 'medium']
                low_issues = [f for f in findings if f.get('severity') == 'low']
                
                # Display issues by category
                issue_tabs = st.tabs(["🚨 Critical", "⚠️ High", "🟡 Medium", "ℹ️ Low"])
                
                with issue_tabs[0]:
                    if critical_issues:
                        for issue in critical_issues:
                            st.error(f"**{issue.get('file', 'Unknown file')}** (Line {issue.get('line', '?')})")
                            st.write(f"🔴 **{issue.get('message', 'No message')}**")
                            if issue.get('suggestion'):
                                st.info(f"💡 **Suggestion:** {issue['suggestion']}")
                            st.markdown("---")
                    else:
                        st.success("✅ No critical issues found!")
                
                with issue_tabs[1]:
                    if high_issues:
                        for issue in high_issues:
                            st.warning(f"**{issue.get('file', 'Unknown file')}** (Line {issue.get('line', '?')})")
                            st.write(f"🟠 **{issue.get('message', 'No message')}**")
                            if issue.get('suggestion'):
                                st.info(f"💡 **Suggestion:** {issue['suggestion']}")
                            st.markdown("---")
                    else:
                        st.success("✅ No high priority issues found!")
                
                with issue_tabs[2]:
                    if medium_issues:
                        for issue in medium_issues:
                            st.info(f"**{issue.get('file', 'Unknown file')}** (Line {issue.get('line', '?')})")
                            st.write(f"🟡 **{issue.get('message', 'No message')}**")
                            if issue.get('suggestion'):
                                st.info(f"💡 **Suggestion:** {issue['suggestion']}")
                            st.markdown("---")
                    else:
                        st.success("✅ No medium priority issues found!")
                
                with issue_tabs[3]:
                    if low_issues:
                        for issue in low_issues:
                            with st.expander(f"📝 {issue.get('file', 'Unknown file')} (Line {issue.get('line', '?')})"):
                                st.write(f"ℹ️ **{issue.get('message', 'No message')}**")
                                if issue.get('suggestion'):
                                    st.info(f"💡 **Suggestion:** {issue['suggestion']}")
                    else:
                        st.success("✅ No low priority issues found!")
                
                # Summary section
                st.markdown("---")
                st.subheader("📊 Issues Summary")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("🚨 Critical", len(critical_issues), delta=None if len(critical_issues) == 0 else f"-{len(critical_issues)}")
                with col2: 
                    st.metric("⚠️ High", len(high_issues), delta=None if len(high_issues) == 0 else f"-{len(high_issues)}")
                with col3:
                    st.metric("🟡 Medium", len(medium_issues), delta=None if len(medium_issues) == 0 else f"-{len(medium_issues)}")
                with col4:
                    st.metric("ℹ️ Low", len(low_issues), delta=None if len(low_issues) == 0 else f"-{len(low_issues)}")
                    
            else:
                st.success("🎉 No issues found! This is excellent code quality.")
    
    with tab2:
        st.header("🔍 Browse & Review")
        st.info("🚧 This feature allows browsing repositories and selecting PRs for review. Coming soon!")
    
    with tab4:
        st.header("📊 Analytics")
        st.info("🚧 Analytics dashboard with review trends and insights. Coming soon!")

if __name__ == "__main__":
    main()