"""Repository checkout functionality using gitpython."""

import logging
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Tuple
from contextlib import contextmanager

import git
from git import Repo, GitCommandError

logger = logging.getLogger(__name__)


class RepoCheckout:
    """Handles repository cloning and PR branch checkout."""
    
    def __init__(self, temp_dir: Optional[str] = None):
        """Initialize checkout manager."""
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.active_repos = {}  # Track active repository paths
    
    def checkout_pr(self, repo_url: str, pr_head_ref: str, pr_base_ref: str = "main") -> str:
        """
        Clone repository and checkout PR branch.
        
        Args:
            repo_url: Git repository URL
            pr_head_ref: PR head branch name
            pr_base_ref: PR base branch name (default: main)
            
        Returns:
            Path to the checked out repository
        """
        repo_name = self._extract_repo_name(repo_url)
        checkout_path = Path(self.temp_dir) / f"pr_review_{repo_name}_{pr_head_ref}"
        
        try:
            # Remove existing directory if it exists
            if checkout_path.exists():
                shutil.rmtree(checkout_path)
            
            logger.info(f"Cloning repository: {repo_url}")
            repo = Repo.clone_from(repo_url, checkout_path, depth=1, no_single_branch=True)
            
            # Fetch the specific branches we need
            origin = repo.remotes.origin
            
            try:
                # Try to fetch and checkout the PR branch
                origin.fetch(f"refs/heads/{pr_head_ref}:refs/remotes/origin/{pr_head_ref}")
                repo.git.checkout(f"origin/{pr_head_ref}", b=pr_head_ref)
                logger.info(f"Checked out PR branch: {pr_head_ref}")
            except GitCommandError as e:
                logger.warning(f"Failed to checkout PR branch {pr_head_ref}: {e}")
                # Fall back to default branch
                try:
                    repo.git.checkout(f"origin/{pr_base_ref}", b=pr_base_ref)
                    logger.info(f"Checked out base branch: {pr_base_ref}")
                except GitCommandError:
                    # Use whatever branch is available
                    current_branch = repo.active_branch.name
                    logger.info(f"Using current branch: {current_branch}")
            
            # Store the repo path for cleanup
            self.active_repos[str(checkout_path)] = repo
            
            return str(checkout_path)
            
        except Exception as e:
            logger.error(f"Failed to checkout repository: {e}")
            # Clean up on failure
            if checkout_path.exists():
                shutil.rmtree(checkout_path)
            raise
    
    def get_changed_files(self, repo_path: str, base_ref: str = "main", head_ref: Optional[str] = None) -> list:
        """
        Get list of changed files between base and head.
        
        Args:
            repo_path: Path to the repository
            base_ref: Base branch reference
            head_ref: Head branch reference (current if None)
            
        Returns:
            List of changed file paths
        """
        try:
            repo = Repo(repo_path)
            
            if head_ref:
                # Compare specific branches
                try:
                    diff = repo.git.diff(f"origin/{base_ref}...origin/{head_ref}", name_only=True)
                except GitCommandError:
                    # Fall back to comparing current branch with base
                    diff = repo.git.diff(f"origin/{base_ref}", name_only=True)
            else:
                # Compare current branch with base
                try:
                    diff = repo.git.diff(f"origin/{base_ref}", name_only=True)
                except GitCommandError:
                    # If no base branch, get all files that have been modified
                    diff = repo.git.diff("HEAD~1", name_only=True) if repo.head.commit.parents else ""
            
            changed_files = [f.strip() for f in diff.split('\n') if f.strip()]
            logger.info(f"Found {len(changed_files)} changed files")
            return changed_files
            
        except Exception as e:
            logger.error(f"Failed to get changed files: {e}")
            return []
    
    def get_file_diff(self, repo_path: str, file_path: str, base_ref: str = "main") -> str:
        """
        Get diff for a specific file.
        
        Args:
            repo_path: Path to the repository
            file_path: Path to the file within the repository
            base_ref: Base branch reference
            
        Returns:
            Diff content for the file
        """
        try:
            repo = Repo(repo_path)
            try:
                diff = repo.git.diff(f"origin/{base_ref}", file_path)
            except GitCommandError:
                # Fall back to HEAD~1 if base_ref doesn't exist
                diff = repo.git.diff("HEAD~1", file_path) if repo.head.commit.parents else ""
            
            return diff
            
        except Exception as e:
            logger.error(f"Failed to get file diff for {file_path}: {e}")
            return ""
    
    def cleanup(self, repo_path: Optional[str] = None):
        """Clean up repository checkouts with Windows compatibility."""
        if repo_path:
            # Clean up specific repository
            if repo_path in self.active_repos:
                try:
                    if Path(repo_path).exists():
                        self._force_remove_readonly(repo_path)
                    del self.active_repos[repo_path]
                    logger.info(f"Cleaned up repository: {repo_path}")
                except Exception as e:
                    logger.error(f"Failed to cleanup {repo_path}: {e}")
                    # Don't fail the entire process due to cleanup issues
        else:
            # Clean up all repositories
            for path in list(self.active_repos.keys()):
                self.cleanup(path)
    
    def _force_remove_readonly(self, path):
        """Force remove directory with read-only files (Windows compatible)."""
        import os
        import stat
        
        def handle_remove_readonly(func, path, exc):
            """Error handler for removing read-only files."""
            if os.path.exists(path):
                os.chmod(path, stat.S_IWRITE)
                func(path)
        
        try:
            shutil.rmtree(path, onerror=handle_remove_readonly)
        except Exception as e:
            logger.warning(f"Could not fully clean up {path}: {e}")
            # Try alternative cleanup
            try:
                import subprocess
                subprocess.run(['rmdir', '/s', '/q', str(path)], shell=True, capture_output=True)
            except Exception:
                pass  # Ignore if this also fails
    
    def _extract_repo_name(self, repo_url: str) -> str:
        """Extract repository name from URL."""
        # Handle various URL formats
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]
        
        parts = repo_url.split('/')
        return parts[-1] if parts else "unknown_repo"
    
    @contextmanager
    def temporary_checkout(self, repo_url: str, pr_head_ref: str, pr_base_ref: str = "main"):
        """Context manager for temporary repository checkout."""
        repo_path = None
        try:
            repo_path = self.checkout_pr(repo_url, pr_head_ref, pr_base_ref)
            yield repo_path
        finally:
            if repo_path:
                self.cleanup(repo_path)


# Convenience functions
def checkout_pr(repo_url: str, pr_head_ref: str, pr_base_ref: str = "main") -> str:
    """Convenience function to checkout a PR."""
    checkout_manager = RepoCheckout()
    return checkout_manager.checkout_pr(repo_url, pr_head_ref, pr_base_ref)


def get_changed_files(repo_path: str, base_ref: str = "main", head_ref: Optional[str] = None) -> list:
    """Convenience function to get changed files."""
    checkout_manager = RepoCheckout()
    return checkout_manager.get_changed_files(repo_path, base_ref, head_ref)