"""Code analysis module with static checks and LLM integration."""

import ast
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from src.providers.llm_provider import LLMProvider
from src.providers.gemini_provider import GeminiProvider
from src.utils import is_python_file, is_text_file, read_file_safe

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """Code analyzer that combines static analysis with intelligent reviews."""
    
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        """Initialize code analyzer."""
        self.llm_provider = llm_provider or GeminiProvider()
        self.static_analyzers = {
            'syntax': SyntaxAnalyzer(),
            'security': SecurityAnalyzer(),
            'style': StyleAnalyzer(),
            'complexity': ComplexityAnalyzer()
        }
    
    def analyze_files(self, repo_path: str, changed_files: List[str], pr_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze changed files in a PR.
        
        Args:
            repo_path: Path to the repository
            changed_files: List of changed file paths
            pr_context: PR context information
            
        Returns:
            List of findings
        """
        all_findings = []
        
        for file_path in changed_files:
            full_path = Path(repo_path) / file_path
            
            if not full_path.exists():
                continue
            
            if not is_text_file(file_path):
                logger.debug(f"Skipping non-text file: {file_path}")
                continue
            
            logger.info(f"Analyzing file: {file_path}")
            
            # Get file content
            content = read_file_safe(str(full_path))
            if not content:
                continue
            
            # Run static analysis
            static_findings = self._run_static_analysis(str(full_path), content)
            
            # Get file diff for context
            file_diff = pr_context.get('files', {}).get(file_path, {}).get('patch', '')
            
            # Run LLM analysis if available
            llm_findings = []
            if self.llm_provider and self.llm_provider.is_available():
                llm_findings = self._run_llm_analysis(file_path, content, file_diff, static_findings)
            
            # Combine findings
            file_findings = static_findings + llm_findings
            
            # Add file context to each finding
            for finding in file_findings:
                finding['file'] = file_path
                finding['full_path'] = str(full_path)
            
            all_findings.extend(file_findings)
        
        return all_findings
    
    def _run_static_analysis(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Run all static analyzers on a file."""
        findings = []
        
        for analyzer_name, analyzer in self.static_analyzers.items():
            try:
                analyzer_findings = analyzer.analyze(file_path, content)
                for finding in analyzer_findings:
                    finding['tool'] = analyzer_name
                findings.extend(analyzer_findings)
            except Exception as e:
                logger.error(f"Static analyzer {analyzer_name} failed for {file_path}: {e}")
        
        return findings
    
    def _run_llm_analysis(self, file_path: str, content: str, diff: str, static_findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run LLM analysis on a file."""
        try:
            # Build context for LLM
            context = {
                'file_path': file_path,
                'diff': diff,
                'static_findings': static_findings,
                'content_length': len(content)
            }
            
            # Generate review
            prompt = f"Review this code change for quality, security, and best practices."
            llm_result = self.llm_provider.generate_review(prompt, context)
            
            # Convert to finding format
            finding = {
                'line': self._extract_line_from_diff(diff),
                'code': 'LLM_REVIEW',
                'message': llm_result.get('comment', 'LLM review'),
                'tool': 'llm',
                'severity': llm_result.get('severity', 'info'),
                'suggestion': llm_result.get('suggestion', ''),
                'confidence': llm_result.get('confidence', 0.5),
                'reasoning': llm_result.get('reasoning', '')
            }
            
            return [finding]
            
        except Exception as e:
            logger.error(f"LLM analysis failed for {file_path}: {e}")
            return []
    
    def _extract_line_from_diff(self, diff: str) -> int:
        """Extract a representative line number from diff."""
        for line in diff.split('\n'):
            if line.startswith('@@'):
                # Parse hunk header like "@@ -1,3 +1,4 @@"
                try:
                    parts = line.split()
                    if len(parts) >= 3:
                        new_range = parts[2][1:]  # Remove '+'
                        line_num = int(new_range.split(',')[0])
                        return line_num
                except (ValueError, IndexError):
                    pass
        return 1


class StaticAnalyzer:
    """Base class for static analyzers."""
    
    def analyze(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Analyze file and return findings."""
        raise NotImplementedError


class SyntaxAnalyzer(StaticAnalyzer):
    """Syntax analyzer for Python files."""
    
    def analyze(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Check for syntax errors."""
        if not is_python_file(file_path):
            return []
        
        findings = []
        try:
            ast.parse(content)
        except SyntaxError as e:
            findings.append({
                'line': e.lineno or 1,
                'code': 'SYNTAX_ERROR',
                'message': f"Syntax error: {e.msg}",
                'severity': 'error'
            })
        except Exception as e:
            findings.append({
                'line': 1,
                'code': 'PARSE_ERROR',
                'message': f"Failed to parse file: {str(e)}",
                'severity': 'error'
            })
        
        return findings


class SecurityAnalyzer(StaticAnalyzer):
    """Security analyzer using bandit."""
    
    def analyze(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Run bandit security analysis."""
        if not is_python_file(file_path):
            return []
        
        findings = []
        
        try:
            # Write content to temporary file for bandit
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
                tmp_file.write(content)
                tmp_path = tmp_file.name
            
            # Run bandit
            result = subprocess.run(
                ['bandit', '-f', 'json', tmp_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Clean up
            Path(tmp_path).unlink(missing_ok=True)
            
            if result.returncode == 0 or result.stdout:
                try:
                    bandit_output = json.loads(result.stdout)
                    for issue in bandit_output.get('results', []):
                        findings.append({
                            'line': issue.get('line_number', 1),
                            'code': issue.get('test_id', 'BANDIT'),
                            'message': issue.get('issue_text', 'Security issue'),
                            'severity': self._map_bandit_severity(issue.get('issue_severity', 'LOW'))
                        })
                except json.JSONDecodeError:
                    pass
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.debug("Bandit not available or timed out")
        except Exception as e:
            logger.error(f"Bandit analysis failed: {e}")
        
        return findings
    
    def _map_bandit_severity(self, bandit_severity: str) -> str:
        """Map bandit severity to our severity levels."""
        mapping = {
            'HIGH': 'error',
            'MEDIUM': 'warning',
            'LOW': 'info'
        }
        return mapping.get(bandit_severity.upper(), 'info')


class StyleAnalyzer(StaticAnalyzer):
    """Style analyzer using flake8."""
    
    def analyze(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Run flake8 style analysis."""
        if not is_python_file(file_path):
            return []
        
        findings = []
        
        try:
            # Write content to temporary file for flake8
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
                tmp_file.write(content)
                tmp_path = tmp_file.name
            
            # Run flake8
            result = subprocess.run(
                ['flake8', '--format=json', tmp_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Clean up
            Path(tmp_path).unlink(missing_ok=True)
            
            if result.stdout:
                try:
                    # flake8 JSON format isn't standard, parse line by line
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            # Format: filename:line:col: code message
                            parts = line.split(':', 3)
                            if len(parts) >= 4:
                                findings.append({
                                    'line': int(parts[1]),
                                    'code': parts[3].split()[0],
                                    'message': parts[3].split(' ', 1)[1] if ' ' in parts[3] else parts[3],
                                    'severity': 'warning'
                                })
                except (ValueError, IndexError):
                    pass
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.debug("Flake8 not available or timed out")
        except Exception as e:
            logger.error(f"Flake8 analysis failed: {e}")
        
        return findings


class ComplexityAnalyzer(StaticAnalyzer):
    """Complexity analyzer using radon."""
    
    def analyze(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Run radon complexity analysis."""
        if not is_python_file(file_path):
            return []
        
        findings = []
        
        try:
            # Write content to temporary file for radon
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
                tmp_file.write(content)
                tmp_path = tmp_file.name
            
            # Run radon
            result = subprocess.run(
                ['radon', 'cc', '-j', tmp_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Clean up
            Path(tmp_path).unlink(missing_ok=True)
            
            if result.returncode == 0 and result.stdout:
                try:
                    radon_output = json.loads(result.stdout)
                    for file_data in radon_output.values():
                        for func_data in file_data:
                            complexity = func_data.get('complexity', 0)
                            if complexity > 10:  # High complexity threshold
                                findings.append({
                                    'line': func_data.get('lineno', 1),
                                    'code': f'COMPLEXITY_{complexity}',
                                    'message': f"High cyclomatic complexity ({complexity}) in {func_data.get('name', 'function')}",
                                    'severity': 'warning' if complexity > 15 else 'info'
                                })
                except json.JSONDecodeError:
                    pass
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.debug("Radon not available or timed out")
        except Exception as e:
            logger.error(f"Radon analysis failed: {e}")
        
        return findings


def analyze_code(repo_path: str, changed_files: List[str], pr_context: Dict[str, Any], llm_provider: Optional[LLMProvider] = None) -> List[Dict[str, Any]]:
    """Convenience function to analyze code."""
    analyzer = CodeAnalyzer(llm_provider)
    return analyzer.analyze_files(repo_path, changed_files, pr_context)