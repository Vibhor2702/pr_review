"""Utility functions for the PR review agent."""

import logging
import tempfile
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import colorlog


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Set up colored logging for the application."""
    # Create formatter
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler
    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def create_temp_dir(prefix: str = "pr_review_") -> str:
    """Create a temporary directory."""
    return tempfile.mkdtemp(prefix=prefix)


def safe_json_load(file_path: str) -> Optional[Dict[str, Any]]:
    """Safely load JSON from file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError) as e:
        logging.getLogger(__name__).error(f"Failed to load JSON from {file_path}: {e}")
        return None


def safe_json_save(data: Dict[str, Any], file_path: str) -> bool:
    """Safely save data as JSON to file."""
    try:
        # Create directory if it doesn't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except (PermissionError, OSError) as e:
        logging.getLogger(__name__).error(f"Failed to save JSON to {file_path}: {e}")
        return False


def read_file_safe(file_path: str) -> Optional[str]:
    """Safely read file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
        logging.getLogger(__name__).error(f"Failed to read file {file_path}: {e}")
        return None


def is_python_file(file_path: str) -> bool:
    """Check if file is a Python file."""
    return file_path.endswith(('.py', '.pyi', '.pyx'))


def is_text_file(file_path: str) -> bool:
    """Check if file is a text file that can be analyzed."""
    text_extensions = {
        '.py', '.pyi', '.pyx',  # Python
        '.js', '.ts', '.jsx', '.tsx',  # JavaScript/TypeScript
        '.java', '.kt',  # Java/Kotlin
        '.go',  # Go
        '.rs',  # Rust
        '.cpp', '.c', '.h', '.hpp',  # C/C++
        '.cs',  # C#
        '.php',  # PHP
        '.rb',  # Ruby
        '.swift',  # Swift
        '.scala',  # Scala
        '.r', '.R',  # R
        '.sql',  # SQL
        '.sh', '.bash',  # Shell
        '.yaml', '.yml',  # YAML
        '.json',  # JSON
        '.xml',  # XML
        '.md', '.rst',  # Documentation
        '.txt',  # Text
    }
    
    return any(file_path.endswith(ext) for ext in text_extensions)


def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    try:
        return os.path.getsize(file_path)
    except (FileNotFoundError, PermissionError):
        return 0


def truncate_text(text: str, max_length: int = 1000) -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    size = float(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def extract_function_names(python_code: str) -> List[str]:
    """Extract function names from Python code using AST."""
    import ast
    
    try:
        tree = ast.parse(python_code)
        function_names = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_names.append(node.name)
        
        return function_names
    except SyntaxError:
        return []


def extract_class_names(python_code: str) -> List[str]:
    """Extract class names from Python code using AST."""
    import ast
    
    try:
        tree = ast.parse(python_code)
        class_names = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_names.append(node.name)
        
        return class_names
    except SyntaxError:
        return []


def calculate_lines_of_code(file_path: str) -> Dict[str, int]:
    """Calculate lines of code statistics."""
    content = read_file_safe(file_path)
    if not content:
        return {"total": 0, "code": 0, "comments": 0, "blank": 0}
    
    lines = content.split('\n')
    total_lines = len(lines)
    code_lines = 0
    comment_lines = 0
    blank_lines = 0
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            blank_lines += 1
        elif stripped.startswith('#'):
            comment_lines += 1
        else:
            code_lines += 1
    
    return {
        "total": total_lines,
        "code": code_lines,
        "comments": comment_lines,
        "blank": blank_lines
    }


def normalize_path(path: str) -> str:
    """Normalize path separators for cross-platform compatibility."""
    return str(Path(path))


def ensure_artifacts_dir(base_path: str = ".") -> str:
    """Ensure artifacts directory exists and return its path."""
    artifacts_dir = Path(base_path) / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    return str(artifacts_dir)