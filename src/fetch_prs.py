"""PR fetchers for different git providers (GitHub, GitLab, Bitbucket)."""

import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin

import requests
from src.config import config

logger = logging.getLogger(__name__)


class PRFetcher(ABC):
    """Abstract base class for PR fetchers."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize fetcher with optional token."""
        self.token = token
        self.session = requests.Session()
        if token:
            self._configure_auth()
    
    @abstractmethod
    def _configure_auth(self):
        """Configure authentication for the session."""
        pass
    
    @abstractmethod
    def get_pr_info(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """
        Get PR information including files and metadata.
        
        Returns:
            {
                "provider": "github",
                "owner": "...",
                "repo": "...",
                "pr_number": 123,
                "head_ref": "branch-name",
                "base_ref": "main",
                "diff_url": "...",
                "files": [{"path": "a.py", "additions": 10, "deletions": 2}, ...]
            }
        """
        pass
    
    def _make_request(self, url: str, method: str = "GET", **kwargs) -> requests.Response:
        """Make authenticated request with error handling."""
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise


class GitHubFetcher(PRFetcher):
    """GitHub PR fetcher using GitHub REST API."""
    
    def __init__(self, token: Optional[str] = None):
        super().__init__(token or config.github_token)
        self.base_url = "https://api.github.com"
    
    def _configure_auth(self):
        """Configure GitHub authentication."""
        if self.token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            })
    
    def get_pr_info(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Get GitHub PR information."""
        # Get PR details
        pr_url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        pr_response = self._make_request(pr_url)
        pr_data = pr_response.json()
        
        # Get PR files
        files_url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        files_response = self._make_request(files_url)
        files_data = files_response.json()
        
        # Format files data
        files = []
        for file_info in files_data:
            files.append({
                "path": file_info["filename"],
                "additions": file_info["additions"],
                "deletions": file_info["deletions"],
                "status": file_info["status"],
                "patch": file_info.get("patch", "")
            })
        
        return {
            "provider": "github",
            "owner": owner,
            "repo": repo,
            "pr_number": pr_number,
            "head_ref": pr_data["head"]["ref"],
            "base_ref": pr_data["base"]["ref"],
            "head_sha": pr_data["head"]["sha"],
            "base_sha": pr_data["base"]["sha"],
            "diff_url": pr_data["diff_url"],
            "repo_url": pr_data["head"]["repo"]["clone_url"],
            "files": files,
            "title": pr_data["title"],
            "body": pr_data["body"] or ""
        }


class GitLabFetcher(PRFetcher):
    """GitLab PR (Merge Request) fetcher using GitLab REST API."""
    
    def __init__(self, token: Optional[str] = None, base_url: str = "https://gitlab.com"):
        super().__init__(token or config.gitlab_token)
        self.base_url = f"{base_url}/api/v4"
    
    def _configure_auth(self):
        """Configure GitLab authentication."""
        if self.token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            })
    
    def get_pr_info(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Get GitLab MR information."""
        project_path = f"{owner}/{repo}".replace("/", "%2F")
        
        # Get MR details
        mr_url = f"{self.base_url}/projects/{project_path}/merge_requests/{pr_number}"
        mr_response = self._make_request(mr_url)
        mr_data = mr_response.json()
        
        # Get MR changes
        changes_url = f"{self.base_url}/projects/{project_path}/merge_requests/{pr_number}/changes"
        changes_response = self._make_request(changes_url)
        changes_data = changes_response.json()
        
        # Format files data
        files = []
        for change in changes_data.get("changes", []):
            files.append({
                "path": change["new_path"] or change["old_path"],
                "additions": 0,  # GitLab doesn't provide line counts in changes API
                "deletions": 0,
                "status": "modified" if change["new_path"] and change["old_path"] else "added" if change["new_path"] else "deleted",
                "patch": change.get("diff", "")
            })
        
        return {
            "provider": "gitlab",
            "owner": owner,
            "repo": repo,
            "pr_number": pr_number,
            "head_ref": mr_data["source_branch"],
            "base_ref": mr_data["target_branch"],
            "head_sha": mr_data["sha"],
            "base_sha": mr_data["merge_commit_sha"] or "",
            "diff_url": f"{mr_data['web_url']}.diff",
            "repo_url": mr_data["source_project"]["http_url_to_repo"],
            "files": files,
            "title": mr_data["title"],
            "body": mr_data["description"] or ""
        }


class BitbucketFetcher(PRFetcher):
    """Bitbucket PR fetcher using Bitbucket REST API."""
    
    def __init__(self, token: Optional[str] = None):
        super().__init__(token or config.bitbucket_token)
        self.base_url = "https://api.bitbucket.org/2.0"
    
    def _configure_auth(self):
        """Configure Bitbucket authentication."""
        if self.token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json"
            })
    
    def get_pr_info(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Get Bitbucket PR information."""
        # Get PR details
        pr_url = f"{self.base_url}/repositories/{owner}/{repo}/pullrequests/{pr_number}"
        pr_response = self._make_request(pr_url)
        pr_data = pr_response.json()
        
        # Get PR diff
        diff_url = f"{self.base_url}/repositories/{owner}/{repo}/pullrequests/{pr_number}/diff"
        try:
            diff_response = self._make_request(diff_url)
            diff_content = diff_response.text
        except Exception as e:
            logger.warning(f"Failed to get diff: {e}")
            diff_content = ""
        
        # Parse files from diff (simplified parsing)
        files = self._parse_diff_files(diff_content)
        
        return {
            "provider": "bitbucket",
            "owner": owner,
            "repo": repo,
            "pr_number": pr_number,
            "head_ref": pr_data["source"]["branch"]["name"],
            "base_ref": pr_data["destination"]["branch"]["name"],
            "head_sha": pr_data["source"]["commit"]["hash"],
            "base_sha": pr_data["destination"]["commit"]["hash"],
            "diff_url": diff_url,
            "repo_url": pr_data["source"]["repository"]["links"]["clone"][0]["href"],
            "files": files,
            "title": pr_data["title"],
            "body": pr_data["description"] or ""
        }
    
    def _parse_diff_files(self, diff_content: str) -> List[Dict[str, Any]]:
        """Parse files from diff content."""
        files = []
        current_file = None
        additions = 0
        deletions = 0
        
        for line in diff_content.split('\n'):
            if line.startswith('diff --git'):
                if current_file:
                    files.append({
                        "path": current_file,
                        "additions": additions,
                        "deletions": deletions,
                        "status": "modified",
                        "patch": ""
                    })
                # Extract filename from "diff --git a/file.py b/file.py"
                parts = line.split()
                if len(parts) >= 4:
                    current_file = parts[2][2:]  # Remove "a/" prefix
                additions = 0
                deletions = 0
            elif line.startswith('+') and not line.startswith('+++'):
                additions += 1
            elif line.startswith('-') and not line.startswith('---'):
                deletions += 1
        
        # Add last file
        if current_file:
            files.append({
                "path": current_file,
                "additions": additions,
                "deletions": deletions,
                "status": "modified",
                "patch": ""
            })
        
        return files


def get_fetcher(provider: str, token: Optional[str] = None) -> PRFetcher:
    """Factory function to get the appropriate PR fetcher."""
    fetchers = {
        "github": GitHubFetcher,
        "gitlab": GitLabFetcher,
        "bitbucket": BitbucketFetcher
    }
    
    if provider.lower() not in fetchers:
        raise ValueError(f"Unsupported provider: {provider}")
    
    return fetchers[provider.lower()](token)