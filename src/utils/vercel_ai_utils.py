"""Vercel AI Gateway integration for unified model management and credit management.

This module provides a unified interface for AI model calls through Vercel's AI Gateway,
enabling model switching, credit management, and abuse protection.
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime

class VercelAIGateway:
    """Vercel AI Gateway integration for unified model management"""
    
    def __init__(self):
        self.api_key = os.getenv('VERCEL_AI_KEY')
        self.base_url = "https://api.vercel.ai/v1"
        self.rate_limit = 3  # requests per minute (free tier)
        self.last_request_time = None
        
    def _check_rate_limit(self):
        """Check rate limiting for free tier"""
        if self.last_request_time:
            time_diff = (datetime.now() - self.last_request_time).total_seconds()
            if time_diff < 60:  # 1 minute
                return False
        return True
    
    def _update_rate_limit(self):
        """Update rate limit tracking"""
        self.last_request_time = datetime.now()
    
    def chat_completion(self, 
                       messages: List[Dict[str, str]], 
                       model: str = "gpt-4",
                       max_tokens: int = 1500,
                       temperature: float = 0.7) -> Dict[str, Any]:
        """Make chat completion request through Vercel AI Gateway"""
        
        if not self.api_key:
            return {"error": "VERCEL_AI_KEY not configured"}
        
        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded. Please wait before making another request."}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                self._update_rate_limit()
                return response.json()
            else:
                return {"error": f"API request failed: {response.status_code} - {response.text}"}
                
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def generate_grant_response(self, 
                              message: str, 
                              context: Dict[str, Any], 
                              grant_type: str = "community") -> str:
        """Generate grant writing response using Vercel AI Gateway"""
        
        # Build system prompt for grant writing
        system_prompt = f"""You are a grant assistant for {context.get('organization_info', 'the organization').split()[0] if context.get('organization_info') else 'the organization'}. Adhere to:

CULTURAL COMPETENCY GUIDELINES:
- Tone: Formal yet inclusive
- Cultural priorities: Emphasize community impact, avoid jargon
- Use inclusive, respectful language that honors diverse communities
- Highlight community strengths and resilience, not deficits
- Avoid stereotypes and assumptions about cultural groups
- Emphasize community-driven solutions and local expertise
- Consider cultural concepts of time, planning, and success
- Use culturally appropriate examples and analogies
- Address historical context and systemic barriers
- Include community voice and perspectives

COGNITIVE FRIENDLINESS:
- Use clear, simple language that's easy to understand
- Provide concrete examples and specific details
- Use bullet points and numbered lists for easy scanning
- Break down complex concepts into simple steps
- Use positive, encouraging language throughout
- Avoid overwhelming with too much information at once

REQUIRED SECTIONS: Project Goals, Budget, Evaluation Metrics
GRANT TYPE: {grant_type.upper()}

RESPONSE FORMAT:
- Start with a compelling community-focused opening
- Include specific cultural context and community strengths
- Use clear headings and bullet points
- End with measurable impact and community benefits"""
        
        # Build user message with context
        context_string = f"""
COMMUNITY CONTEXT: {context.get('community_focus', '')}
ORGANIZATION PROFILE: {context.get('organization_info', '')}
UPLOADED CONTENT: {' '.join(context.get('uploaded_content', []))}
RFP REQUIREMENTS: {', '.join(context.get('rfp_requirements', []))}

USER REQUEST: {message}

Please provide a culturally sensitive, community-focused response that addresses the user's request while maintaining the appropriate tone and emphasis for this grant type.
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context_string}
        ]
        
        # Make request through Vercel AI Gateway
        result = self.chat_completion(messages, model="gpt-4")
        
        if "error" in result:
            return f"⚠️ Error: {result['error']}"
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"].strip()
        else:
            return "⚠️ No response generated"
    
    def evaluate_cultural_alignment(self, 
                                 content: str, 
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate cultural alignment using Vercel AI Gateway"""
        
        evaluation_prompt = f"""Evaluate the following content for cultural competency and sensitivity:

CONTENT TO EVALUATE:
{content}

COMMUNITY CONTEXT: {context.get('community_focus', '')}

Please evaluate on these dimensions and provide scores (0-100):
1. Cultural Sensitivity
2. Community Focus  
3. Cognitive Friendliness
4. Overall Quality

Provide scores and specific recommendations for improvement."""
        
        messages = [
            {"role": "system", "content": "You are a cultural competency evaluator. Provide structured evaluation with scores and recommendations."},
            {"role": "user", "content": evaluation_prompt}
        ]
        
        result = self.chat_completion(messages, model="gpt-4", max_tokens=500, temperature=0.3)
        
        if "error" in result:
            return {"error": result["error"]}
        
        if "choices" in result and len(result["choices"]) > 0:
            eval_text = result["choices"][0]["message"]["content"].strip()
            
            # Extract scores using regex
            import re
            scores = {
                "cultural_sensitivity": self._extract_score(eval_text, "Cultural Sensitivity"),
                "community_focus": self._extract_score(eval_text, "Community Focus"),
                "cognitive_friendliness": self._extract_score(eval_text, "Cognitive Friendliness"),
                "overall_quality": self._extract_score(eval_text, "Overall Quality")
            }
            
            return {
                "scores": scores,
                "recommendations": eval_text,
                "quality_level": self._get_quality_level(scores.get("overall_quality", 0))
            }
        else:
            return {"error": "No evaluation generated"}
    
    def _extract_score(self, text: str, dimension: str) -> int:
        """Extract score from evaluation text"""
        pattern = rf"{dimension}.*?(\d+)"
        match = re.search(pattern, text, re.IGNORECASE)
        return int(match.group(1)) if match else 0
    
    def _get_quality_level(self, score: int) -> str:
        """Convert score to quality level"""
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        else:
            return "needs_improvement"

# Global instance
vercel_ai_gateway = VercelAIGateway() 