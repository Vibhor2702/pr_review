"""Flask HTTP server for the PR review agent."""

import logging
import os
from typing import Dict, Any

from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest

from src.config import config
from src.utils import setup_logging
from src.fetch_prs import get_fetcher
from src.repo_checkout import RepoCheckout
from src.analyze_code import analyze_code
from src.review_generator import generate_review
from src.scoring import calculate_pr_score
from src.ci_integration import save_review_artifacts, post_comments_to_github
from src.providers.gemini_provider import GeminiProvider

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Enable CORS for all routes
    from flask_cors import CORS
    CORS(app, origins=[
        "http://localhost:3002",
        "https://*.vercel.app",
        "https://*.netlify.app",
        "https://*.pages.dev",
        "https://pr-review.pages.dev"
    ])
    
    # Setup logging
    setup_logging()
    
    @app.route("/", methods=["GET"])
    def root():
        """Root endpoint - API information."""
        return {
            "name": "PR Review Agent API",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "health": "/health",
                "config": "/config",
                "review": "/review_pr",
                "demo": "/demo"
            },
            "description": "Professional Pull Request Review API powered by Google Gemini AI"
        }
    
    @app.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "version": "1.0.0"}
    
    @app.route("/review_pr", methods=["POST"])
    def review_pr():
        """Review PR endpoint."""
        try:
            # Parse request
            data = request.get_json()
            if not data:
                raise BadRequest("JSON body required")
            
            provider = data.get("provider")
            owner = data.get("owner")
            repo = data.get("repo")
            pr_number = data.get("pr_number")
            token = data.get("token")
            no_llm = data.get("no_llm", False)
            post_comments = data.get("post_comments", False)
            
            # Validate required fields
            if not all([provider, owner, repo, pr_number]):
                raise BadRequest("Missing required fields: provider, owner, repo, pr_number")
            
            if provider not in ["github", "gitlab", "bitbucket"]:
                raise BadRequest("Invalid provider. Must be github, gitlab, or bitbucket")
            
            logger.info(f"Starting review for {provider}/{owner}/{repo}#{pr_number}")
            
            # Check configuration
            missing_config = config.validate_required_config([provider])
            if no_llm:
                missing_config = [c for c in missing_config if c != "GEMINI_API_KEY"]
            
            if missing_config:
                return jsonify({
                    "error": "Configuration error",
                    "missing_config": missing_config
                }), 500
            
            # Fetch PR information
            fetcher = get_fetcher(provider, token)
            pr_context = fetcher.get_pr_info(owner, repo, pr_number)
            
            # Checkout repository
            checkout_manager = RepoCheckout()
            repo_path = None
            
            try:
                repo_path = checkout_manager.checkout_pr(
                    pr_context['repo_url'],
                    pr_context['head_ref'],
                    pr_context['base_ref']
                )
                
                # Analyze code
                changed_files = [f['path'] for f in pr_context['files']]
                llm_provider = None if no_llm else GeminiProvider()
                findings = analyze_code(repo_path, changed_files, pr_context, llm_provider)
                
                # Generate review
                review_data = generate_review(findings, pr_context)
                score_data = calculate_pr_score(findings, pr_context)
                review_data["score"] = score_data
                
                # Save artifacts
                artifact_path = save_review_artifacts(review_data, pr_context)
                
                # Post comments if requested
                if post_comments and provider == "github":
                    comments_posted = post_comments_to_github(
                        owner, repo, pr_number, review_data.get("comments", []), token
                    )
                    review_data["comments_posted"] = comments_posted
                
                logger.info(f"Review completed for {provider}/{owner}/{repo}#{pr_number}")
                
                # Return response
                response_data = {
                    "status": "success",
                    "pr_context": {
                        "provider": pr_context["provider"],
                        "owner": pr_context["owner"],
                        "repo": pr_context["repo"],
                        "pr_number": pr_context["pr_number"],
                        "title": pr_context["title"],
                        "files_changed": len(pr_context["files"])
                    },
                    "review": {
                        "score": score_data.get("score", 0),
                        "grade": score_data.get("grade", "F"),
                        "total_findings": len(findings),
                        "summary": review_data.get("summary", ""),
                        "comments": review_data.get("comments", [])
                    },
                    "metadata": review_data.get("metadata", {}),
                    "artifact_path": artifact_path
                }
                
                return jsonify(response_data)
                
            finally:
                # Cleanup
                if repo_path:
                    checkout_manager.cleanup(repo_path)
                    
        except BadRequest as e:
            logger.error(f"Bad request: {e}")
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error(f"Review failed: {e}", exc_info=True)
            return jsonify({
                "error": "Internal server error",
                "message": str(e)
            }), 500
    
    @app.route("/providers", methods=["GET"])
    def list_providers():
        """List available providers and their configuration status."""
        providers = {}
        
        for provider in ["github", "gitlab", "bitbucket"]:
            token = config.get_token_for_provider(provider)
            providers[provider] = {
                "configured": token is not None,
                "token_length": len(token) if token else 0
            }
        
        return jsonify({
            "providers": providers,
            "llm_configured": config.gemini_api_key is not None
        })
    
    @app.route("/demo/review", methods=["POST"])
    def demo_review():
        """Demo review endpoint with mock data."""
        try:
            data = request.get_json()
            if not data:
                raise BadRequest("JSON body required")
            
            provider = data.get("provider", "github")
            owner = data.get("owner", "example")
            repo = data.get("repo", "demo")
            pr_number = data.get("pr_number", 1)
            
            # Simulate processing time
            import time
            time.sleep(1)
            
            # Return realistic demo data
            demo_response = {
                "status": "success",
                "pr_context": {
                    "provider": provider,
                    "owner": owner,
                    "repo": repo,
                    "pr_number": pr_number,
                    "title": "feat: Add new authentication system",
                    "files_changed": 8,
                    "head_ref": "feature/auth-system",
                    "base_ref": "main"
                },
                "review": {
                    "score": 85,
                    "grade": "B+",
                    "total_findings": 12,
                    "summary": "Good overall code quality with some areas for improvement. The authentication implementation is solid but could benefit from additional error handling and test coverage.",
                    "comments": [
                        {
                            "file": "src/auth/authentication.py",
                            "line": 42,
                            "side": "right",
                            "message": "Consider adding input validation for email format",
                            "suggestion": "Use a proper email validation library like email-validator",
                            "severity": "warning",
                            "rule": "input-validation",
                            "confidence": 0.8
                        },
                        {
                            "file": "src/models/user.py",
                            "line": 15,
                            "side": "right",
                            "message": "Missing docstring for User class",
                            "suggestion": "Add comprehensive docstring explaining the User model",
                            "severity": "info",
                            "rule": "documentation",
                            "confidence": 0.9
                        },
                        {
                            "file": "src/auth/password.py",
                            "line": 28,
                            "side": "right",
                            "message": "Password hashing could be more secure",
                            "suggestion": "Consider using bcrypt with higher cost factor",
                            "severity": "warning",
                            "rule": "security",
                            "confidence": 0.85
                        }
                    ]
                },
                "metadata": {
                    "total_findings": 12,
                    "severity_breakdown": {
                        "error": 1,
                        "warning": 7,
                        "info": 4
                    },
                    "timestamp": "2025-09-22T13:52:00Z"
                },
                "artifact_path": "/tmp/demo_review_artifacts"
            }
            
            return jsonify(demo_response)
            
        except BadRequest as e:
            logger.error(f"Bad request: {e}")
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error(f"Demo review failed: {e}", exc_info=True)
            return jsonify({
                "error": "Internal server error",
                "message": str(e)
            }), 500

    @app.route("/config", methods=["GET"])
    def get_config():
        """Get current configuration (without sensitive data)."""
        return jsonify({
            "server_host": config.server_host,
            "server_port": config.server_port,
            "llm_temperature": config.llm_temperature,
            "ci_post_review": config.ci_post_review,
            "scoring_weights": config.scoring_weights,
            "providers_configured": {
                "github": config.github_token is not None,
                "gitlab": config.gitlab_token is not None,
                "bitbucket": config.bitbucket_token is not None,
            },
            "llm_configured": config.gemini_api_key is not None
        })
    
    @app.errorhandler(404)
    def not_found(error):
        """404 error handler."""
        return jsonify({"error": "Endpoint not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500 error handler."""
        logger.error(f"Internal server error: {error}")
        return jsonify({"error": "Internal server error"}), 500
    
    return app


def main():
    """Run the server directly."""
    app = create_app()
    port = int(os.environ.get("PORT", config.server_port))
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()