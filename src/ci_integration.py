"""CI integration helpers for posting reviews and managing artifacts."""

import logging
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

import requests
from src.config import config

logger = logging.getLogger(__name__)


class CIIntegration:
    """Handles CI-specific integrations and comment posting."""
    
    def __init__(self):
        """Initialize CI integration."""
        pass
    
    def post_comments_to_github(self, owner: str, repo: str, pr_number: int, comments: List[Dict[str, Any]], token: Optional[str] = None) -> bool:
        """
        Post review comments to GitHub PR.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: PR number
            comments: List of review comments
            token: GitHub token (optional, uses config if not provided)
            
        Returns:
            True if successful, False otherwise
        """
        github_token = token or config.github_token
        
        if not github_token:
            logger.error("GitHub token not available")
            return False
        
        if not config.ci_post_review:
            logger.info("CI review posting disabled")
            return False
        
        session = requests.Session()
        session.headers.update({
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        })
        
        # Get PR details to get the commit SHA
        pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
        try:
            pr_response = session.get(pr_url)
            pr_response.raise_for_status()
            pr_data = pr_response.json()
            commit_sha = pr_data["head"]["sha"]
        except Exception as e:
            logger.error(f"Failed to get PR details: {e}")
            return False
        
        # Post review comments
        review_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        
        # Group comments for batch posting
        review_comments = []
        for comment in comments:
            if comment.get("severity") == "info" and len(comments) > 10:
                continue  # Skip info comments for large reviews
            
            review_comment = {
                "path": comment["file"],
                "line": comment["line"],
                "body": self._format_comment_body(comment),
                "side": "RIGHT"
            }
            review_comments.append(review_comment)
        
        if not review_comments:
            logger.info("No comments to post")
            return True
        
        # Create review
        review_data = {
            "commit_id": commit_sha,
            "body": "Automated code review by PR Review Agent",
            "event": "COMMENT",
            "comments": review_comments[:20]  # GitHub limits to 20 comments per review
        }
        
        try:
            response = session.post(review_url, json=review_data)
            response.raise_for_status()
            logger.info(f"Successfully posted {len(review_comments)} comments to GitHub PR")
            return True
        except Exception as e:
            logger.error(f"Failed to post review comments: {e}")
            return False
    
    def post_comments_to_gitlab(self, project_id: str, mr_number: int, comments: List[Dict[str, Any]], token: Optional[str] = None) -> bool:
        """
        Post review comments to GitLab MR.
        
        Args:
            project_id: GitLab project ID
            mr_number: MR number
            comments: List of review comments
            token: GitLab token (optional, uses config if not provided)
            
        Returns:
            True if successful, False otherwise
        """
        gitlab_token = token or config.gitlab_token
        
        if not gitlab_token:
            logger.error("GitLab token not available")
            return False
        
        if not config.ci_post_review:
            logger.info("CI review posting disabled")
            return False
        
        session = requests.Session()
        session.headers.update({
            "Authorization": f"Bearer {gitlab_token}",
            "Content-Type": "application/json"
        })
        
        # Post individual comments (GitLab doesn't have batch review API like GitHub)
        success_count = 0
        for comment in comments:
            if comment.get("severity") == "info" and len(comments) > 10:
                continue  # Skip info comments for large reviews
            
            comment_url = f"https://gitlab.com/api/v4/projects/{project_id}/merge_requests/{mr_number}/discussions"
            comment_data = {
                "body": self._format_comment_body(comment),
                "position": {
                    "position_type": "text",
                    "new_path": comment["file"],
                    "new_line": comment["line"]
                }
            }
            
            try:
                response = session.post(comment_url, json=comment_data)
                response.raise_for_status()
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to post comment to GitLab: {e}")
        
        logger.info(f"Posted {success_count} comments to GitLab MR")
        return success_count > 0
    
    def _format_comment_body(self, comment: Dict[str, Any]) -> str:
        """Format comment body for posting."""
        severity_emoji = {
            "error": "❌",
            "warning": "⚠️", 
            "info": "ℹ️"
        }
        
        emoji = severity_emoji.get(comment.get("severity", "info"), "📝")
        message = comment.get("message", "No message")
        tool = comment.get("tool", "unknown")
        
        body_parts = [f"{emoji} **{comment.get('severity', 'info').upper()}**", "", message]
        
        if comment.get("suggestion"):
            body_parts.extend(["", "**Suggestion:**", comment["suggestion"]])
        
        if comment.get("rule"):
            body_parts.extend(["", f"**Rule:** `{comment['rule']}`"])
        
        body_parts.extend(["", f"*Found by: {tool}*"])
        
        return "\n".join(body_parts)
    
    def save_artifacts(self, review_data: Dict[str, Any], pr_context: Dict[str, Any], output_dir: str = "artifacts") -> str:
        """
        Save review artifacts to files.
        
        Args:
            review_data: Review results
            pr_context: PR context
            output_dir: Output directory
            
        Returns:
            Path to the main artifact file
        """
        artifacts_dir = Path(output_dir)
        artifacts_dir.mkdir(exist_ok=True)
        
        # Generate artifact filename
        provider = pr_context.get("provider", "unknown")
        pr_number = pr_context.get("pr_number", "unknown")
        artifact_filename = f"review_{provider}_{pr_number}.json"
        artifact_path = artifacts_dir / artifact_filename
        
        # Combine all data
        artifact_data = {
            "pr_context": pr_context,
            "review": review_data,
            "timestamp": review_data.get("metadata", {}).get("timestamp"),
            "version": "1.0"
        }
        
        # Save main artifact
        try:
            with open(artifact_path, 'w', encoding='utf-8') as f:
                json.dump(artifact_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved review artifact to {artifact_path}")
        except Exception as e:
            logger.error(f"Failed to save artifact: {e}")
            return ""
        
        # Save markdown report
        markdown_path = artifacts_dir / f"review_{provider}_{pr_number}.md"
        try:
            from src.review_generator import ReviewGenerator
            generator = ReviewGenerator()
            markdown_content = generator.generate_markdown_report(review_data)
            
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            logger.info(f"Saved markdown report to {markdown_path}")
        except Exception as e:
            logger.error(f"Failed to save markdown report: {e}")
        
        return str(artifact_path)
    
    def setup_github_actions_output(self, review_data: Dict[str, Any]) -> None:
        """Set up GitHub Actions outputs."""
        try:
            import os
            
            # Set outputs for GitHub Actions
            if "GITHUB_OUTPUT" in os.environ:
                with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                    score = review_data.get("metadata", {}).get("score", 0)
                    grade = review_data.get("metadata", {}).get("grade", "F")
                    total_findings = review_data.get("metadata", {}).get("total_findings", 0)
                    
                    f.write(f"score={score}\n")
                    f.write(f"grade={grade}\n")
                    f.write(f"total_findings={total_findings}\n")
            
            # Set step summary
            if "GITHUB_STEP_SUMMARY" in os.environ:
                with open(os.environ["GITHUB_STEP_SUMMARY"], "w") as f:
                    from src.review_generator import ReviewGenerator
                    generator = ReviewGenerator()
                    markdown_content = generator.generate_markdown_report(review_data)
                    f.write(markdown_content)
                    
        except Exception as e:
            logger.error(f"Failed to setup GitHub Actions output: {e}")


def post_comments_to_github(owner: str, repo: str, pr_number: int, comments: List[Dict[str, Any]], token: Optional[str] = None) -> bool:
    """Convenience function to post comments to GitHub."""
    ci = CIIntegration()
    return ci.post_comments_to_github(owner, repo, pr_number, comments, token)


def save_review_artifacts(review_data: Dict[str, Any], pr_context: Dict[str, Any], output_dir: str = "artifacts") -> str:
    """Convenience function to save review artifacts."""
    ci = CIIntegration()
    return ci.save_artifacts(review_data, pr_context, output_dir)