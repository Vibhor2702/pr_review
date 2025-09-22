"""Abstract LLM provider interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate_review(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a code review using the LLM.
        
        Args:
            prompt: The review prompt
            context: Additional context (file info, diff, etc.)
            
        Returns:
            {
                "comment": "Review comment text",
                "suggestion": "Suggested code or improvement",
                "severity": "info|warning|error",
                "confidence": 0.95,
                "reasoning": "Brief explanation"
            }
        """
        pass
    
    @abstractmethod
    def summarize_findings(self, findings: List[Dict[str, Any]]) -> str:
        """
        Summarize multiple findings into a coherent review.
        
        Args:
            findings: List of individual findings
            
        Returns:
            Summary text
        """
        pass
    
    def is_available(self) -> bool:
        """Check if the provider is properly configured and available."""
        return True