"""PR quality scoring system."""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from src.config import config

logger = logging.getLogger(__name__)


class PRScorer:
    """Calculates PR quality scores based on various metrics."""
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """Initialize scorer with custom weights."""
        self.weights = weights or config.scoring_weights
    
    def calculate_score(self, findings: List[Dict[str, Any]], pr_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate PR quality score.
        
        Args:
            findings: List of analysis findings
            pr_context: PR context information
            
        Returns:
            {
                "score": 85,
                "breakdown": {...},
                "grade": "B+",
                "recommendations": [...]
            }
        """
        # Initialize scores
        base_score = self.weights.get("base_score", 100.0)
        
        # Calculate penalties
        style_penalty = self._calculate_style_penalty(findings)
        security_penalty = self._calculate_security_penalty(findings)
        complexity_penalty = self._calculate_complexity_penalty(findings)
        coverage_penalty = self._calculate_test_coverage_penalty(pr_context)
        size_penalty = self._calculate_size_penalty(pr_context)
        
        # Calculate final score
        total_penalty = (
            style_penalty + 
            security_penalty + 
            complexity_penalty + 
            coverage_penalty + 
            size_penalty
        )
        
        final_score = max(0, base_score - total_penalty)
        
        # Create breakdown
        breakdown = {
            "base_score": base_score,
            "style_penalty": style_penalty,
            "security_penalty": security_penalty,
            "complexity_penalty": complexity_penalty,
            "test_coverage_penalty": coverage_penalty,
            "size_penalty": size_penalty,
            "total_penalty": total_penalty,
            "final_score": final_score
        }
        
        # Calculate grade
        grade = self._score_to_grade(final_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(findings, breakdown)
        
        return {
            "score": round(final_score, 1),
            "breakdown": breakdown,
            "grade": grade,
            "recommendations": recommendations,
            "metrics": self._calculate_metrics(findings, pr_context)
        }
    
    def _calculate_style_penalty(self, findings: List[Dict[str, Any]]) -> float:
        """Calculate penalty for style issues."""
        style_issues = [f for f in findings if f.get("tool") == "style" or f.get("code", "").startswith("E") or f.get("code", "").startswith("W")]
        
        if not style_issues:
            return 0.0
        
        # Minor penalty for style issues
        penalty = len(style_issues) * self.weights.get("style_issues", 1.0)
        return min(penalty, 15.0)  # Cap at 15 points
    
    def _calculate_security_penalty(self, findings: List[Dict[str, Any]]) -> float:
        """Calculate penalty for security issues."""
        security_issues = [f for f in findings if f.get("tool") == "security" or f.get("severity") == "error"]
        
        if not security_issues:
            return 0.0
        
        # Heavier penalty for security issues
        penalty = 0.0
        for issue in security_issues:
            if issue.get("severity") == "error":
                penalty += self.weights.get("security_findings", 10.0)
            elif issue.get("severity") == "warning":
                penalty += self.weights.get("security_findings", 10.0) * 0.5
            else:
                penalty += self.weights.get("security_findings", 10.0) * 0.2
        
        return min(penalty, 30.0)  # Cap at 30 points
    
    def _calculate_complexity_penalty(self, findings: List[Dict[str, Any]]) -> float:
        """Calculate penalty for complexity issues."""
        complexity_issues = [f for f in findings if f.get("tool") == "complexity" or "COMPLEXITY" in f.get("code", "")]
        
        if not complexity_issues:
            return 0.0
        
        # Moderate penalty for complexity
        penalty = 0.0
        for issue in complexity_issues:
            # Extract complexity score if available
            code = issue.get("code", "")
            if "COMPLEXITY_" in code:
                try:
                    complexity_value = int(code.split("_")[1])
                    if complexity_value > 20:
                        penalty += 8.0
                    elif complexity_value > 15:
                        penalty += 5.0
                    else:
                        penalty += 2.0
                except (ValueError, IndexError):
                    penalty += 3.0
            else:
                penalty += 3.0
        
        return min(penalty, 20.0)  # Cap at 20 points
    
    def _calculate_test_coverage_penalty(self, pr_context: Dict[str, Any]) -> float:
        """Calculate penalty for lack of test coverage."""
        files = pr_context.get("files", [])
        
        if not files:
            return 0.0
        
        # Check if any test files are included
        test_files = [f for f in files if self._is_test_file(f.get("path", ""))]
        code_files = [f for f in files if self._is_code_file(f.get("path", "")) and not self._is_test_file(f.get("path", ""))]
        
        if not code_files:
            return 0.0  # No code files to test
        
        if not test_files:
            # No tests for code changes
            penalty = len(code_files) * self.weights.get("test_coverage", 3.0)
            return min(penalty, 15.0)  # Cap at 15 points
        
        return 0.0  # Tests are present
    
    def _calculate_size_penalty(self, pr_context: Dict[str, Any]) -> float:
        """Calculate penalty for large PRs."""
        files = pr_context.get("files", [])
        
        if not files:
            return 0.0
        
        # Count total lines changed
        total_additions = sum(f.get("additions", 0) for f in files)
        total_deletions = sum(f.get("deletions", 0) for f in files)
        total_changes = total_additions + total_deletions
        
        # Penalty for very large PRs
        if total_changes > 1000:
            return 10.0
        elif total_changes > 500:
            return 5.0
        elif total_changes > 200:
            return 2.0
        
        return 0.0
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "A-"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "B-"
        elif score >= 65:
            return "C+"
        elif score >= 60:
            return "C"
        elif score >= 55:
            return "C-"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def _generate_recommendations(self, findings: List[Dict[str, Any]], breakdown: Dict[str, float]) -> List[str]:
        """Generate recommendations based on score breakdown."""
        recommendations = []
        
        # Security recommendations
        if breakdown["security_penalty"] > 10:
            recommendations.append("🔒 Address security issues before merging")
        elif breakdown["security_penalty"] > 0:
            recommendations.append("Review security findings")
        
        # Complexity recommendations
        if breakdown["complexity_penalty"] > 10:
            recommendations.append("Simplify complex functions to improve maintainability")
        elif breakdown["complexity_penalty"] > 0:
            recommendations.append("Consider refactoring complex code sections")
        
        # Style recommendations
        if breakdown["style_penalty"] > 10:
            recommendations.append("🎨 Fix style issues for better code consistency")
        elif breakdown["style_penalty"] > 5:
            recommendations.append("✨ Address major style violations")
        
        # Test coverage recommendations
        if breakdown["test_coverage_penalty"] > 0:
            recommendations.append("🧪 Add tests for new code changes")
        
        # Size recommendations
        if breakdown["size_penalty"] > 5:
            recommendations.append("📏 Consider breaking large PR into smaller chunks")
        
        # Overall recommendations
        if breakdown["final_score"] >= 90:
            recommendations.append("✅ Excellent code quality!")
        elif breakdown["final_score"] >= 80:
            recommendations.append("👍 Good code quality with minor improvements needed")
        elif breakdown["final_score"] >= 70:
            recommendations.append("⚠️ Moderate issues that should be addressed")
        else:
            recommendations.append("❌ Significant issues that need attention before merging")
        
        return recommendations
    
    def _calculate_metrics(self, findings: List[Dict[str, Any]], pr_context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate additional metrics."""
        files = pr_context.get("files", [])
        
        return {
            "total_findings": len(findings),
            "files_changed": len(files),
            "lines_added": sum(f.get("additions", 0) for f in files),
            "lines_removed": sum(f.get("deletions", 0) for f in files),
            "net_lines": sum(f.get("additions", 0) for f in files) - sum(f.get("deletions", 0) for f in files),
            "error_count": len([f for f in findings if f.get("severity") == "error"]),
            "warning_count": len([f for f in findings if f.get("severity") == "warning"]),
            "info_count": len([f for f in findings if f.get("severity") == "info"]),
        }
    
    def _is_test_file(self, file_path: str) -> bool:
        """Check if file is a test file."""
        test_patterns = [
            "test_",
            "_test.",
            "/tests/",
            "/test/",
            "spec_",
            "_spec.",
            "/specs/",
            "/spec/"
        ]
        
        file_path_lower = file_path.lower()
        return any(pattern in file_path_lower for pattern in test_patterns)
    
    def _is_code_file(self, file_path: str) -> bool:
        """Check if file is a code file."""
        code_extensions = {".py", ".js", ".ts", ".java", ".go", ".rs", ".cpp", ".c", ".cs", ".php", ".rb"}
        return any(file_path.endswith(ext) for ext in code_extensions)


def calculate_pr_score(findings: List[Dict[str, Any]], pr_context: Dict[str, Any], weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """Convenience function to calculate PR score."""
    scorer = PRScorer(weights)
    return scorer.calculate_score(findings, pr_context)