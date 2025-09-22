"""Tests for review schema and comment format validation."""

import pytest
from pydantic import BaseModel, ValidationError, Field
from typing import List, Optional
from src.review_generator import ReviewGenerator, generate_review


class ReviewComment(BaseModel):
    """Pydantic model for review comment validation."""
    file: str
    line: int = Field(ge=1, description="Line number must be positive")
    side: str = "right"
    message: str
    severity: str
    tool: str
    code: Optional[str] = None
    suggestion: Optional[str] = None
    rule: Optional[str] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None


class ReviewSummary(BaseModel):
    """Pydantic model for review summary validation."""
    comments: List[ReviewComment]
    summary: str
    metadata: dict


class TestReviewSchema:
    """Test cases for review schema validation."""
    
    def test_valid_comment_schema(self):
        """Test valid comment format."""
        comment_data = {
            "file": "src/module.py",
            "line": 42,
            "side": "right",
            "message": "This function has high complexity",
            "severity": "warning",
            "tool": "complexity",
            "code": "COMPLEXITY_15",
            "suggestion": "Consider breaking into smaller functions",
            "rule": "CC_HIGH",
        }
        
        comment = ReviewComment(**comment_data)
        assert comment.file == "src/module.py"
        assert comment.line == 42
        assert comment.severity == "warning"
        assert comment.tool == "complexity"
    
    def test_minimal_comment_schema(self):
        """Test minimal required fields for comment."""
        comment_data = {
            "file": "test.py",
            "line": 1,
            "message": "Test message",
            "severity": "info",
            "tool": "test"
        }
        
        comment = ReviewComment(**comment_data)
        assert comment.file == "test.py"
        assert comment.line == 1
        assert comment.side == "right"  # Default value
        assert comment.code is None  # Optional field
    
    def test_invalid_comment_missing_required(self):
        """Test validation fails with missing required fields."""
        comment_data = {
            "file": "test.py",
            # Missing line, message, severity, tool
        }
        
        with pytest.raises(ValidationError):
            ReviewComment(**comment_data)
    
    def test_invalid_line_number(self):
        """Test validation fails with invalid line number."""
        with pytest.raises(ValidationError):
            # Test negative line number
            ReviewComment(
                file="test.py",
                line=-1,
                message="Test message",
                severity="info",
                tool="test"
            )
    
    def test_valid_severity_values(self):
        """Test valid severity values."""
        valid_severities = ["error", "warning", "info"]
        
        for severity in valid_severities:
            comment_data = {
                "file": "test.py",
                "line": 1,
                "message": "Test message",
                "severity": severity,
                "tool": "test"
            }
            comment = ReviewComment(**comment_data)
            assert comment.severity == severity
    
    def test_confidence_range(self):
        """Test confidence value validation."""
        # Valid confidence values
        for confidence in [0.0, 0.5, 1.0]:
            comment_data = {
                "file": "test.py",
                "line": 1,
                "message": "Test message",
                "severity": "info",
                "tool": "llm",
                "confidence": confidence
            }
            comment = ReviewComment(**comment_data)
            assert comment.confidence == confidence
    
    def test_complete_review_schema(self):
        """Test complete review response schema."""
        review_data = {
            "comments": [
                {
                    "file": "src/module.py",
                    "line": 10,
                    "message": "Style issue",
                    "severity": "warning",
                    "tool": "flake8",
                    "code": "E302"
                },
                {
                    "file": "src/utils.py",
                    "line": 5,
                    "message": "Security issue",
                    "severity": "error",
                    "tool": "bandit",
                    "code": "B101"
                }
            ],
            "summary": "Found 2 issues: 1 error, 1 warning",
            "metadata": {
                "total_findings": 2,
                "severity_breakdown": {"error": 1, "warning": 1, "info": 0},
                "timestamp": "2023-01-01T00:00:00"
            }
        }
        
        review = ReviewSummary(**review_data)
        assert len(review.comments) == 2
        assert review.summary == "Found 2 issues: 1 error, 1 warning"
        assert review.metadata["total_findings"] == 2


class TestReviewGenerator:
    """Test cases for ReviewGenerator class."""
    
    def test_empty_findings(self):
        """Test review generation with no findings."""
        generator = ReviewGenerator()
        findings = []
        pr_context = {"provider": "github", "pr_number": 123, "files": []}
        
        result = generator.generate_review(findings, pr_context)
        
        assert result["comments"] == []
        assert "No issues found" in result["summary"]
        assert result["metadata"]["total_findings"] == 0
    
    def test_single_finding(self):
        """Test review generation with single finding."""
        generator = ReviewGenerator()
        findings = [
            {
                "file": "test.py",
                "line": 10,
                "message": "Style issue",
                "severity": "warning",
                "tool": "flake8",
                "code": "E302"
            }
        ]
        pr_context = {"provider": "github", "pr_number": 123, "files": []}
        
        result = generator.generate_review(findings, pr_context)
        
        assert len(result["comments"]) == 1
        comment = result["comments"][0]
        assert comment["file"] == "test.py"
        assert comment["line"] == 10
        assert comment["severity"] == "warning"
        assert comment["rule"] == "E302"
    
    def test_multiple_findings_different_severity(self):
        """Test review generation with multiple findings of different severity."""
        generator = ReviewGenerator()
        findings = [
            {
                "file": "test.py",
                "line": 10,
                "message": "Security issue",
                "severity": "error",
                "tool": "bandit",
                "code": "B101"
            },
            {
                "file": "test.py",
                "line": 20,
                "message": "Style issue",
                "severity": "warning",
                "tool": "flake8",
                "code": "E302"
            },
            {
                "file": "utils.py",
                "line": 5,
                "message": "Suggestion",
                "severity": "info",
                "tool": "llm",
                "suggestion": "Consider using list comprehension"
            }
        ]
        pr_context = {"provider": "github", "pr_number": 123, "files": []}
        
        result = generator.generate_review(findings, pr_context)
        
        assert len(result["comments"]) == 3
        assert "3 issues" in result["summary"]
        assert "1 errors" in result["summary"]
        assert "1 warnings" in result["summary"]
        assert "1 suggestions" in result["summary"]
        
        # Check metadata
        metadata = result["metadata"]
        assert metadata["total_findings"] == 3
        assert metadata["severity_breakdown"]["error"] == 1
        assert metadata["severity_breakdown"]["warning"] == 1
        assert metadata["severity_breakdown"]["info"] == 1
    
    def test_llm_finding_with_confidence(self):
        """Test LLM finding with confidence and reasoning."""
        generator = ReviewGenerator()
        findings = [
            {
                "file": "test.py",
                "line": 15,
                "message": "Complex function",
                "severity": "warning",
                "tool": "llm",
                "suggestion": "Break into smaller functions",
                "confidence": 0.85,
                "reasoning": "Function has many nested conditions"
            }
        ]
        pr_context = {"provider": "github", "pr_number": 123, "files": []}
        
        result = generator.generate_review(findings, pr_context)
        
        comment = result["comments"][0]
        assert comment["confidence"] == 0.85
        assert comment["reasoning"] == "Function has many nested conditions"
        assert comment["suggestion"] == "Break into smaller functions"
    
    def test_metadata_creation(self):
        """Test metadata creation."""
        generator = ReviewGenerator()
        findings = [
            {"file": "file1.py", "severity": "error", "tool": "bandit"},
            {"file": "file1.py", "severity": "warning", "tool": "flake8"},
            {"file": "file2.py", "severity": "info", "tool": "llm"},
        ]
        pr_context = {
            "provider": "github",
            "pr_number": 123,
            "files": [{"path": "file1.py"}, {"path": "file2.py"}]
        }
        
        result = generator.generate_review(findings, pr_context)
        metadata = result["metadata"]
        
        assert metadata["total_findings"] == 3
        assert metadata["severity_breakdown"]["error"] == 1
        assert metadata["severity_breakdown"]["warning"] == 1
        assert metadata["severity_breakdown"]["info"] == 1
        assert metadata["tool_breakdown"]["bandit"] == 1
        assert metadata["tool_breakdown"]["flake8"] == 1
        assert metadata["tool_breakdown"]["llm"] == 1
        assert metadata["file_breakdown"]["file1.py"] == 2
        assert metadata["file_breakdown"]["file2.py"] == 1
        assert metadata["pr_info"]["provider"] == "github"
        assert metadata["pr_info"]["pr_number"] == 123
    
    def test_most_problematic_files(self):
        """Test identification of most problematic files."""
        generator = ReviewGenerator()
        findings = [
            {"file": "problematic.py", "severity": "error"},
            {"file": "problematic.py", "severity": "warning"},
            {"file": "problematic.py", "severity": "warning"},
            {"file": "okay.py", "severity": "info"},
        ]
        pr_context = {"provider": "github", "pr_number": 123, "files": []}
        
        result = generator.generate_review(findings, pr_context)
        most_problematic = result["metadata"]["most_problematic_files"]
        
        assert len(most_problematic) >= 1
        assert most_problematic[0]["file"] == "problematic.py"
        assert most_problematic[0]["issues"] == 3
    
    def test_markdown_report_generation(self):
        """Test markdown report generation."""
        generator = ReviewGenerator()
        review_data = {
            "summary": "Found 2 issues",
            "comments": [
                {
                    "file": "test.py",
                    "line": 10,
                    "message": "Test issue",
                    "severity": "warning",
                    "tool": "test_tool",
                    "rule": "TEST001"
                }
            ],
            "metadata": {
                "total_findings": 2,
                "severity_breakdown": {"error": 0, "warning": 2, "info": 0},
                "most_problematic_files": [{"file": "test.py", "issues": 1}],
                "timestamp": "2023-01-01T00:00:00"
            }
        }
        
        markdown = generator.generate_markdown_report(review_data)
        
        assert "# 🔍 PR Review Report" in markdown
        assert "Found 2 issues" in markdown
        assert "**Total Issues:** 2" in markdown
        assert "**Warnings:** 2" in markdown
        assert "test.py" in markdown
        assert "TEST001" in markdown
        assert "2023-01-01T00:00:00" in markdown


def test_generate_review_convenience_function():
    """Test the convenience function."""
    findings = [
        {
            "file": "test.py",
            "line": 1,
            "message": "Test finding",
            "severity": "info",
            "tool": "test"
        }
    ]
    pr_context = {"provider": "github", "pr_number": 123, "files": []}
    
    result = generate_review(findings, pr_context)
    
    assert "comments" in result
    assert "summary" in result
    assert "metadata" in result
    assert len(result["comments"]) == 1


if __name__ == "__main__":
    pytest.main([__file__])