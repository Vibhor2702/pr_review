"""Tests for the scoring system."""

import pytest
from src.scoring import PRScorer, calculate_pr_score


class TestPRScorer:
    """Test cases for PRScorer class."""
    
    def test_perfect_score(self):
        """Test perfect score with no issues."""
        scorer = PRScorer()
        findings = []
        pr_context = {"files": []}
        
        result = scorer.calculate_score(findings, pr_context)
        
        assert result["score"] == 100.0
        assert result["grade"] == "A+"
        assert result["breakdown"]["final_score"] == 100.0
        assert "✅ Excellent code quality!" in result["recommendations"]
    
    def test_style_penalty(self):
        """Test style issue penalties."""
        scorer = PRScorer()
        findings = [
            {"tool": "style", "code": "E302", "severity": "warning"},
            {"tool": "style", "code": "W291", "severity": "warning"},
        ]
        pr_context = {"files": []}
        
        result = scorer.calculate_score(findings, pr_context)
        
        assert result["score"] < 100.0
        assert result["breakdown"]["style_penalty"] > 0
        assert result["grade"] in ["A", "A-", "B+"]
    
    def test_security_penalty(self):
        """Test security issue penalties."""
        scorer = PRScorer()
        findings = [
            {"tool": "security", "code": "B101", "severity": "error"},
            {"tool": "security", "code": "B201", "severity": "warning"},
        ]
        pr_context = {"files": []}
        
        result = scorer.calculate_score(findings, pr_context)
        
        assert result["score"] < 85.0  # Should have significant penalty
        assert result["breakdown"]["security_penalty"] > 0
        assert "🔒 Address security issues" in result["recommendations"][0]
    
    def test_complexity_penalty(self):
        """Test complexity issue penalties."""
        scorer = PRScorer()
        findings = [
            {"tool": "complexity", "code": "COMPLEXITY_25", "severity": "warning"},
            {"tool": "complexity", "code": "COMPLEXITY_15", "severity": "warning"},
        ]
        pr_context = {"files": []}
        
        result = scorer.calculate_score(findings, pr_context)
        
        assert result["breakdown"]["complexity_penalty"] > 0
        assert any("complex" in rec.lower() for rec in result["recommendations"])
    
    def test_test_coverage_penalty(self):
        """Test test coverage penalties."""
        scorer = PRScorer()
        findings = []
        pr_context = {
            "files": [
                {"path": "src/module.py", "additions": 50},
                {"path": "src/utils.py", "additions": 30},
            ]
        }
        
        result = scorer.calculate_score(findings, pr_context)
        
        assert result["breakdown"]["test_coverage_penalty"] > 0
        assert any("test" in rec.lower() for rec in result["recommendations"])
    
    def test_size_penalty(self):
        """Test size penalties for large PRs."""
        scorer = PRScorer()
        findings = []
        pr_context = {
            "files": [
                {"path": "file1.py", "additions": 300, "deletions": 200},
                {"path": "file2.py", "additions": 400, "deletions": 300},
                {"path": "file3.py", "additions": 200, "deletions": 100},
            ]
        }
        
        result = scorer.calculate_score(findings, pr_context)
        
        assert result["breakdown"]["size_penalty"] > 0
        assert any("large" in rec.lower() or "break" in rec.lower() for rec in result["recommendations"])
    
    def test_custom_weights(self):
        """Test custom scoring weights."""
        custom_weights = {
            "base_score": 100.0,
            "style_issues": 10.0,  # Higher penalty
            "security_findings": 5.0,  # Lower penalty
            "complexity": 15.0,
            "test_coverage": 2.0
        }
        
        scorer = PRScorer(custom_weights)
        findings = [
            {"tool": "style", "code": "E302", "severity": "warning"},
            {"tool": "security", "code": "B101", "severity": "error"},
        ]
        pr_context = {"files": []}
        
        result = scorer.calculate_score(findings, pr_context)
        
        # Style penalty should be higher due to custom weight
        assert result["breakdown"]["style_penalty"] >= 10.0
    
    def test_grade_calculation(self):
        """Test grade calculation from scores."""
        scorer = PRScorer()
        
        # Test different score ranges
        test_cases = [
            (95, "A+"),
            (90, "A"),
            (85, "A-"),
            (80, "B+"),
            (75, "B"),
            (70, "B-"),
            (65, "C+"),
            (60, "C"),
            (55, "C-"),
            (50, "D"),
            (45, "F")
        ]
        
        for score, expected_grade in test_cases:
            grade = scorer._score_to_grade(score)
            assert grade == expected_grade
    
    def test_metrics_calculation(self):
        """Test metrics calculation."""
        scorer = PRScorer()
        findings = [
            {"severity": "error"},
            {"severity": "warning"},
            {"severity": "warning"},
            {"severity": "info"},
        ]
        pr_context = {
            "files": [
                {"path": "file1.py", "additions": 10, "deletions": 5},
                {"path": "file2.py", "additions": 20, "deletions": 0},
            ]
        }
        
        result = scorer.calculate_score(findings, pr_context)
        metrics = result["metrics"]
        
        assert metrics["total_findings"] == 4
        assert metrics["files_changed"] == 2
        assert metrics["lines_added"] == 30
        assert metrics["lines_removed"] == 5
        assert metrics["net_lines"] == 25
        assert metrics["error_count"] == 1
        assert metrics["warning_count"] == 2
        assert metrics["info_count"] == 1
    
    def test_is_test_file(self):
        """Test test file detection."""
        scorer = PRScorer()
        
        test_files = [
            "test_module.py",
            "module_test.py",
            "tests/test_utils.py",
            "test/integration_test.py",
            "spec_module.py",
            "module_spec.py",
            "specs/api_spec.py",
        ]
        
        non_test_files = [
            "module.py",
            "utils.py",
            "src/main.py",
            "setup.py",
        ]
        
        for file_path in test_files:
            assert scorer._is_test_file(file_path), f"{file_path} should be detected as test file"
        
        for file_path in non_test_files:
            assert not scorer._is_test_file(file_path), f"{file_path} should not be detected as test file"
    
    def test_is_code_file(self):
        """Test code file detection."""
        scorer = PRScorer()
        
        code_files = [
            "module.py",
            "script.js",
            "component.ts",
            "Main.java",
            "main.go",
            "lib.rs",
            "utils.cpp",
            "header.c",
            "service.cs",
            "controller.php",
            "model.rb"
        ]
        
        non_code_files = [
            "README.md",
            "config.json",
            "style.css",
            "template.html",
            "data.xml"
        ]
        
        for file_path in code_files:
            assert scorer._is_code_file(file_path), f"{file_path} should be detected as code file"
        
        for file_path in non_code_files:
            assert not scorer._is_code_file(file_path), f"{file_path} should not be detected as code file"


def test_calculate_pr_score_convenience_function():
    """Test the convenience function."""
    findings = [{"tool": "style", "severity": "warning"}]
    pr_context = {"files": []}
    
    result = calculate_pr_score(findings, pr_context)
    
    assert "score" in result
    assert "grade" in result
    assert "breakdown" in result
    assert "recommendations" in result
    assert "metrics" in result


if __name__ == "__main__":
    pytest.main([__file__])