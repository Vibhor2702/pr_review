"""Demo mode functionality for PR Review Agent."""

import random
from typing import Dict, Any

def generate_demo_review(owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
    """Generate a realistic demo review without actually cloning repositories."""
    
    # Generate more comprehensive demo findings
    demo_findings = [
        {
            "type": "security",
            "severity": "high",
            "file": "src/auth/login.py",
            "line": 67,
            "message": "Potential SQL injection vulnerability in user authentication",
            "suggestion": "Use parameterized queries instead of string concatenation. Consider using ORM like SQLAlchemy.",
            "code_snippet": "query = f\"SELECT * FROM users WHERE email='{email}'\""
        },
        {
            "type": "security", 
            "severity": "medium",
            "file": "api/endpoints.py",
            "line": 156,
            "message": "Hardcoded API key found in source code",
            "suggestion": "Move sensitive credentials to environment variables or secure vault",
            "code_snippet": "api_key = 'sk-1234567890abcdef'"
        },
        {
            "type": "performance",
            "severity": "medium", 
            "file": "utils/data_processor.py",
            "line": 89,
            "message": "Inefficient nested loop operation O(n²) complexity",
            "suggestion": "Consider using dictionary lookup or set operations for O(1) complexity",
            "code_snippet": "for item in list1:\n    for match in list2:\n        if item.id == match.id:"
        },
        {
            "type": "style",
            "severity": "low",
            "file": "src/main.py",
            "line": 42,
            "message": "Variable name does not follow PEP 8 naming conventions",
            "suggestion": "Replace 'userData' with 'user_data' to follow snake_case convention",
            "code_snippet": "userData = get_user_info()"
        },
        {
            "type": "maintainability",
            "severity": "medium",
            "file": "services/payment.py", 
            "line": 234,
            "message": "Function exceeds recommended length (85 lines)",
            "suggestion": "Break down into smaller, more focused functions for better readability",
            "code_snippet": "def process_payment(...):"
        },
        {
            "type": "documentation",
            "severity": "low",
            "file": "models/user.py",
            "line": 12,
            "message": "Missing docstring for public method",
            "suggestion": "Add comprehensive docstring explaining parameters, return values, and exceptions",
            "code_snippet": "def update_profile(self, data):"
        },
        {
            "type": "error_handling",
            "severity": "medium",
            "file": "api/file_upload.py",
            "line": 78,
            "message": "Bare except clause catches all exceptions",
            "suggestion": "Catch specific exceptions and handle them appropriately",
            "code_snippet": "try:\n    process_file()\nexcept:\n    pass"
        },
        {
            "type": "performance",
            "severity": "low",
            "file": "templates/dashboard.html",
            "line": 45,
            "message": "Large inline CSS should be moved to external stylesheet",
            "suggestion": "Extract CSS to separate file for better caching and maintainability",
            "code_snippet": "<style>/* 200+ lines of CSS */</style>"
        }
    ]
    
    # Generate realistic scores
    base_score = random.randint(75, 92)
    grade_map = {
        (90, 100): "A+",
        (85, 89): "A", 
        (80, 84): "A-",
        (75, 79): "B+",
        (70, 74): "B",
        (0, 69): "C"
    }
    
    grade = "B"
    for score_range, letter_grade in grade_map.items():
        if score_range[0] <= base_score <= score_range[1]:
            grade = letter_grade
            break
    
    # Count issues by severity
    security_issues = len([f for f in demo_findings if f["type"] == "security"])
    performance_issues = len([f for f in demo_findings if f["type"] == "performance"]) 
    style_issues = len([f for f in demo_findings if f["type"] in ["style", "documentation"]])
    
    return {
        "status": "completed",
        "findings": demo_findings,
        "summary": f"Analyzed PR #{pr_number} from {owner}/{repo}. Found {len(demo_findings)} issues across {len(set(f['type'] for f in demo_findings))} categories. Key concerns include security vulnerabilities and performance optimizations.",
        "recommendations": [
            "🔒 Address the SQL injection vulnerability in authentication system immediately",
            "⚡ Optimize data processing algorithms to improve performance by ~60%",
            "📚 Add comprehensive documentation for public API methods", 
            "🧪 Increase test coverage for payment processing modules",
            "🔧 Implement proper error handling with specific exception types",
            "📐 Follow PEP 8 style guidelines consistently across the codebase"
        ],
        "score": {
            "score": base_score,
            "grade": grade,
            "total_issues": len(demo_findings),
            "files_analyzed": random.randint(12, 18),
            "security_issues": security_issues,
            "style_issues": style_issues, 
            "performance_issues": performance_issues,
            "lines_of_code": random.randint(2500, 4200),
            "test_coverage": random.randint(65, 85)
        },
        "analysis_params": {
            "depth": "standard",
            "security_level": "medium", 
            "custom_rules": False,
            "file_filters": []
        },
        "artifact_path": "demo_artifacts/review_summary.json",
        "files_changed": [
            "src/auth/login.py",
            "api/endpoints.py", 
            "utils/data_processor.py",
            "src/main.py",
            "services/payment.py",
            "models/user.py",
            "api/file_upload.py",
            "templates/dashboard.html"
        ]
    }

def is_demo_mode_enabled() -> bool:
    """Check if demo mode should be enabled (for problematic repositories)."""
    import os
    return os.environ.get("PR_REVIEW_DEMO_MODE", "false").lower() == "true"