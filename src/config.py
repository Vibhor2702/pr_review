"""Configuration loader for the PR review agent."""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Config:
    """Configuration class for the PR review agent."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        # API Keys and tokens
        self.gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
        self.github_token: Optional[str] = os.getenv("GITHUB_TOKEN")
        self.gitlab_token: Optional[str] = os.getenv("GITLAB_TOKEN")
        self.bitbucket_token: Optional[str] = os.getenv("BITBUCKET_TOKEN")
        
        # Server configuration
        self.server_host: str = os.getenv("SERVER_HOST", "0.0.0.0")
        self.server_port: int = int(os.getenv("SERVER_PORT", "5000"))
        
        # LLM configuration (Gemini)
        self.llm_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))
        
        # CI configuration
        self.ci_post_review: bool = os.getenv("CI_POST_REVIEW", "false").lower() == "true"
        
        # Scoring weights
        self.scoring_weights = self._get_scoring_weights()
    
    def _get_scoring_weights(self) -> Dict[str, float]:
        """Get scoring weights with defaults."""
        return {
            "style_issues": float(os.getenv("WEIGHT_STYLE", "5.0")),
            "security_findings": float(os.getenv("WEIGHT_SECURITY", "15.0")),
            "complexity": float(os.getenv("WEIGHT_COMPLEXITY", "10.0")),
            "test_coverage": float(os.getenv("WEIGHT_TEST_COVERAGE", "8.0")),
            "base_score": float(os.getenv("BASE_SCORE", "100.0"))
        }
    
    def get_token_for_provider(self, provider: str) -> Optional[str]:
        """Get the appropriate token for a git provider."""
        provider_tokens = {
            "github": self.github_token,
            "gitlab": self.gitlab_token,
            "bitbucket": self.bitbucket_token
        }
        return provider_tokens.get(provider.lower())
    
    def validate_required_config(self, providers: Optional[list] = None) -> list:
        """Validate required configuration and return missing items."""
        missing = []
        
        if not self.gemini_api_key:
            missing.append("GEMINI_API_KEY")
        
        if providers:
            for provider in providers:
                if not self.get_token_for_provider(provider):
                    missing.append(f"{provider.upper()}_TOKEN")
        
        return missing


# Global configuration instance
config = Config()