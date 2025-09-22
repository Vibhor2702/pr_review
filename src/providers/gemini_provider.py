"""Google Gemini provider implementation for LLM services."""

import json
import logging
from typing import Dict, Any, List, Optional

import google.generativeai as genai  # type: ignore
from google.generativeai.types import HarmCategory, HarmBlockThreshold  # type: ignore
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import config
from src.providers.llm_provider import LLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """Google Gemini provider for code review generation."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash", temperature: Optional[float] = None):
        """Initialize Gemini provider."""
        self.api_key = api_key or config.gemini_api_key
        self.model_name = model
        self.temperature = temperature or config.llm_temperature
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            
            # Configure the model with safety settings
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
        else:
            self.model = None
            logger.warning("Gemini API key not provided")
    
    def is_available(self) -> bool:
        """Check if Gemini is properly configured."""
        return self.model is not None and self.api_key is not None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_review(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code review using Google Gemini."""
        if not self.is_available():
            raise ValueError("Gemini provider not properly configured")
        
        # Build the review prompt
        full_prompt = self._build_review_prompt(prompt, context)
        
        try:
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=800,
                response_mime_type="application/json"
            )
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            if not response.text:
                logger.warning("Empty response from Gemini")
                return self._fallback_response("Empty response from Gemini")
            
            try:
                result = json.loads(response.text)
            except json.JSONDecodeError:
                # Sometimes Gemini returns JSON with extra text, try to extract JSON
                text = response.text.strip()
                if text.startswith('```json'):
                    text = text[7:]
                if text.endswith('```'):
                    text = text[:-3]
                text = text.strip()
                result = json.loads(text)
            
            # Validate and normalize response
            return self._normalize_response(result)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Raw response: {response.text}")
            return self._fallback_response("Failed to parse LLM response")
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._fallback_response(f"LLM service error: {str(e)}")
    
    def summarize_findings(self, findings: List[Dict[str, Any]]) -> str:
        """Summarize multiple findings into a coherent review."""
        if not self.is_available():
            return "LLM not available for summarization"
        
        if not findings:
            return "No significant issues found in this PR."
        
        # Group findings by severity
        errors = [f for f in findings if f.get("severity") == "error"]
        warnings = [f for f in findings if f.get("severity") == "warning"]
        infos = [f for f in findings if f.get("severity") == "info"]
        
        summary_prompt = self._build_summary_prompt(errors, warnings, infos)
        
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=500
            )
            
            response = self.model.generate_content(
                summary_prompt,
                generation_config=generation_config
            )
            
            return response.text.strip() if response.text else "Unable to generate summary"
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return f"Found {len(findings)} issues: {len(errors)} errors, {len(warnings)} warnings, {len(infos)} suggestions."
    
    def _build_review_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Build the complete prompt for code review."""
        system_instructions = """You are an expert code reviewer. Your job is to review code changes and provide constructive feedback.

Focus on:
- Code quality and readability
- Potential bugs or security issues
- Performance considerations
- Best practices and conventions
- Maintainability

Provide responses in JSON format with these fields:
- "comment": Brief, actionable feedback
- "suggestion": Specific code improvement (if applicable)
- "severity": "error", "warning", or "info"
- "confidence": Number between 0 and 1
- "reasoning": Brief explanation of the issue

Be constructive and helpful. Avoid nitpicking trivial issues."""
        
        file_path = context.get("file_path", "unknown")
        diff = context.get("diff", "")
        static_findings = context.get("static_findings", [])
        
        prompt_parts = [
            system_instructions,
            "",
            f"Please review this code change in file: {file_path}",
            "",
            "Code diff:",
            diff,
        ]
        
        if static_findings:
            prompt_parts.extend([
                "",
                "Static analysis findings:",
                json.dumps(static_findings, indent=2)
            ])
        
        if prompt:
            prompt_parts.extend([
                "",
                "Additional context:",
                prompt
            ])
        
        prompt_parts.append("\nProvide your review as JSON only, no additional text.")
        
        return "\n".join(prompt_parts)
    
    def _build_summary_prompt(self, errors: List, warnings: List, infos: List) -> str:
        """Build prompt for summarizing findings."""
        parts = [
            "You are a code review assistant. Summarize the findings concisely.",
            "",
            "Please provide a concise summary of these code review findings:",
            ""
        ]
        
        if errors:
            parts.append(f"ERRORS ({len(errors)}):")
            for error in errors[:3]:  # Limit to first 3
                parts.append(f"- {error.get('comment', 'Unknown error')}")
            if len(errors) > 3:
                parts.append(f"- ... and {len(errors) - 3} more errors")
            parts.append("")
        
        if warnings:
            parts.append(f"WARNINGS ({len(warnings)}):")
            for warning in warnings[:3]:
                parts.append(f"- {warning.get('comment', 'Unknown warning')}")
            if len(warnings) > 3:
                parts.append(f"- ... and {len(warnings) - 3} more warnings")
            parts.append("")
        
        if infos:
            parts.append(f"SUGGESTIONS ({len(infos)}):")
            for info in infos[:2]:
                parts.append(f"- {info.get('comment', 'Unknown suggestion')}")
            if len(infos) > 2:
                parts.append(f"- ... and {len(infos) - 2} more suggestions")
        
        parts.extend([
            "",
            "Provide a 2-3 sentence summary focusing on the most important issues."
        ])
        
        return "\n".join(parts)
    
    def _normalize_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize and validate LLM response."""
        normalized = {
            "comment": response.get("comment", "No comment provided"),
            "suggestion": response.get("suggestion", ""),
            "severity": response.get("severity", "info").lower(),
            "confidence": float(response.get("confidence", 0.5)),
            "reasoning": response.get("reasoning", "")
        }
        
        # Validate severity
        if normalized["severity"] not in ["error", "warning", "info"]:
            normalized["severity"] = "info"
        
        # Clamp confidence
        normalized["confidence"] = max(0.0, min(1.0, normalized["confidence"]))
        
        return normalized
    
    def _fallback_response(self, error_message: str) -> Dict[str, Any]:
        """Create fallback response when LLM fails."""
        return {
            "comment": "Unable to generate LLM review",
            "suggestion": "",
            "severity": "info",
            "confidence": 0.0,
            "reasoning": error_message
        }