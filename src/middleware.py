"""Middleware for logging and debugging AI requests.

This module provides middleware for logging final prompts and debugging
context injection issues in the AI workflow.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptLoggingMiddleware:
    """Middleware for logging AI prompts and context"""
    
    def __init__(self):
        self.log_file = "prompt_logs.jsonl"
    
    def log_prompt(self, prompt_data: Dict[str, Any]):
        """Log prompt data for debugging"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "prompt_type": prompt_data.get("type", "unknown"),
                "message": prompt_data.get("message", ""),
                "context_keys": list(prompt_data.get("context", {}).keys()),
                "has_context": bool(prompt_data.get("context")),
                "context_size": len(str(prompt_data.get("context", ""))),
                "grant_type": prompt_data.get("grant_type", "unknown"),
                "organization_id": prompt_data.get("organization_id", "unknown")
            }
            
            # Log to file
            with open(self.log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
            
            # Log to console for debugging
            logger.info(f"Prompt logged: {log_entry['prompt_type']} - Context: {log_entry['has_context']} - Size: {log_entry['context_size']}")
            
        except Exception as e:
            logger.error(f"Error logging prompt: {e}")
    
    def check_context_injection(self, prompt: str) -> Dict[str, Any]:
        """Check for missing context placeholders"""
        issues = []
        
        # Check for common context placeholders
        context_placeholders = [
            "{{context}}",
            "{context}",
            "CONTEXT:",
            "ORGANIZATION:",
            "COMMUNITY:"
        ]
        
        missing_placeholders = []
        for placeholder in context_placeholders:
            if placeholder not in prompt:
                missing_placeholders.append(placeholder)
        
        if missing_placeholders:
            issues.append(f"Missing context placeholders: {missing_placeholders}")
        
        # Check for empty context sections
        if "CONTEXT:" in prompt and "CONTEXT:\n" in prompt:
            issues.append("Empty context section detected")
        
        return {
            "has_issues": len(issues) > 0,
            "issues": issues,
            "context_injected": len(issues) == 0
        }

# Global middleware instance
prompt_logger = PromptLoggingMiddleware() 