"""Review generator that converts analysis results into structured inline comments."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ReviewGenerator:
    """Generates structured review comments from analysis findings."""
    
    def __init__(self):
        """Initialize review generator."""
        pass
    
    def generate_review(self, findings: List[Dict[str, Any]], pr_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate structured review from findings.
        
        Args:
            findings: List of analysis findings
            pr_context: PR context information
            
        Returns:
            {
                "comments": [...],
                "summary": "...",
                "metadata": {...}
            }
        """
        # Convert findings to inline comments
        comments = self._convert_findings_to_comments(findings)
        
        # Generate summary
        summary = self._generate_summary(findings, pr_context)
        
        # Create metadata
        metadata = self._create_metadata(findings, pr_context)
        
        return {
            "comments": comments,
            "summary": summary,
            "metadata": metadata
        }
    
    def _convert_findings_to_comments(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert analysis findings to inline comment format."""
        comments = []
        
        for finding in findings:
            comment = {
                "file": finding.get("file", "unknown"),
                "line": finding.get("line", 1),
                "side": "right",  # Standard for new code
                "message": finding.get("message", "No message"),
                "severity": finding.get("severity", "info"),
                "tool": finding.get("tool", "unknown"),
                "code": finding.get("code", ""),
            }
            
            # Add suggestion if available
            suggestion = finding.get("suggestion", "")
            if suggestion:
                comment["suggestion"] = suggestion
            
            # Add rule/code reference
            if finding.get("code"):
                comment["rule"] = finding["code"]
            
            # Add confidence if available (from LLM)
            if "confidence" in finding:
                comment["confidence"] = finding["confidence"]
            
            # Add reasoning if available (from LLM)
            if "reasoning" in finding:
                comment["reasoning"] = finding["reasoning"]
            
            comments.append(comment)
        
        return comments
    
    def _generate_summary(self, findings: List[Dict[str, Any]], pr_context: Dict[str, Any]) -> str:
        """Generate a summary of the review."""
        if not findings:
            return "✅ No issues found. This PR looks good!"
        
        # Count findings by severity
        severity_counts = {"error": 0, "warning": 0, "info": 0}
        tool_counts = {}
        
        for finding in findings:
            severity = finding.get("severity", "info")
            tool = finding.get("tool", "unknown")
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
        
        # Build summary
        summary_parts = []
        
        # Overall assessment
        total_issues = len(findings)
        if severity_counts["error"] > 0:
            summary_parts.append(f"❌ Found {total_issues} issues ({severity_counts['error']} errors)")
        elif severity_counts["warning"] > 0:
            summary_parts.append(f"⚠️ Found {total_issues} issues ({severity_counts['warning']} warnings)")
        else:
            summary_parts.append(f"ℹ️ Found {total_issues} suggestions")
        
        # Breakdown by severity
        breakdown = []
        if severity_counts["error"] > 0:
            breakdown.append(f"{severity_counts['error']} errors")
        if severity_counts["warning"] > 0:
            breakdown.append(f"{severity_counts['warning']} warnings")
        if severity_counts["info"] > 0:
            breakdown.append(f"{severity_counts['info']} suggestions")
        
        if breakdown:
            summary_parts.append(f"Breakdown: {', '.join(breakdown)}")
        
        # Tool breakdown
        if len(tool_counts) > 1:
            tool_breakdown = [f"{tool}: {count}" for tool, count in tool_counts.items()]
            summary_parts.append(f"Sources: {', '.join(tool_breakdown)}")
        
        # Recommendations
        if severity_counts["error"] > 0:
            summary_parts.append("Please address all errors before merging.")
        elif severity_counts["warning"] > 5:
            summary_parts.append("Consider addressing the warnings for better code quality.")
        
        return "\n\n".join(summary_parts)
    
    def _create_metadata(self, findings: List[Dict[str, Any]], pr_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create metadata for the review."""
        # Count findings by severity and tool
        severity_counts = {"error": 0, "warning": 0, "info": 0}
        tool_counts = {}
        file_counts = {}
        
        for finding in findings:
            severity = finding.get("severity", "info")
            tool = finding.get("tool", "unknown")
            file_path = finding.get("file", "unknown")
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
            file_counts[file_path] = file_counts.get(file_path, 0) + 1
        
        # Calculate confidence score (if LLM findings present)
        confidence_scores = [f.get("confidence", 0) for f in findings if "confidence" in f]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else None
        
        return {
            "total_findings": len(findings),
            "severity_breakdown": severity_counts,
            "tool_breakdown": tool_counts,
            "file_breakdown": file_counts,
            "most_problematic_files": self._get_top_files(file_counts, 5),
            "avg_llm_confidence": avg_confidence,
            "timestamp": datetime.utcnow().isoformat(),
            "pr_info": {
                "provider": pr_context.get("provider", "unknown"),
                "pr_number": pr_context.get("pr_number"),
                "files_changed": len(pr_context.get("files", []))
            }
        }
    
    def _get_top_files(self, file_counts: Dict[str, int], limit: int) -> List[Dict[str, Any]]:
        """Get files with most issues."""
        sorted_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"file": file, "issues": count} for file, count in sorted_files[:limit]]
    
    def generate_markdown_report(self, review_data: Dict[str, Any]) -> str:
        """Generate a markdown report from review data."""
        lines = []
        
        # Title
        lines.append("# 🔍 PR Review Report")
        lines.append("")
        
        # Summary
        lines.append("## Summary")
        lines.append(review_data["summary"])
        lines.append("")
        
        # Statistics
        metadata = review_data["metadata"]
        lines.append("## 📊 Statistics")
        lines.append(f"- **Total Issues:** {metadata['total_findings']}")
        
        severity_breakdown = metadata["severity_breakdown"]
        lines.append(f"- **Errors:** {severity_breakdown.get('error', 0)}")
        lines.append(f"- **Warnings:** {severity_breakdown.get('warning', 0)}")
        lines.append(f"- **Suggestions:** {severity_breakdown.get('info', 0)}")
        lines.append("")
        
        # Most problematic files
        if metadata.get("most_problematic_files"):
            lines.append("## 📁 Files with Most Issues")
            for file_info in metadata["most_problematic_files"]:
                lines.append(f"- `{file_info['file']}`: {file_info['issues']} issues")
            lines.append("")
        
        # Detailed findings
        if review_data["comments"]:
            lines.append("## 🔍 Detailed Findings")
            lines.append("")
            
            # Group by file
            files_dict = {}
            for comment in review_data["comments"]:
                file_path = comment["file"]
                if file_path not in files_dict:
                    files_dict[file_path] = []
                files_dict[file_path].append(comment)
            
            for file_path, file_comments in files_dict.items():
                lines.append(f"### 📄 `{file_path}`")
                lines.append("")
                
                for comment in file_comments:
                    severity_emoji = {
                        "error": "❌",
                        "warning": "⚠️",
                        "info": "ℹ️"
                    }.get(comment["severity"], "📝")
                    
                    lines.append(f"**Line {comment['line']}** {severity_emoji} {comment['severity'].upper()}")
                    lines.append(f"- **Issue:** {comment['message']}")
                    
                    if comment.get("rule"):
                        lines.append(f"- **Rule:** `{comment['rule']}`")
                    
                    if comment.get("suggestion"):
                        lines.append(f"- **Suggestion:** {comment['suggestion']}")
                    
                    if comment.get("tool"):
                        lines.append(f"- **Tool:** {comment['tool']}")
                    
                    lines.append("")
        
        # Footer
        lines.append("---")
        lines.append(f"*Report generated on {metadata['timestamp']}*")
        
        return "\n".join(lines)


def generate_review(findings: List[Dict[str, Any]], pr_context: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to generate review."""
    generator = ReviewGenerator()
    return generator.generate_review(findings, pr_context)