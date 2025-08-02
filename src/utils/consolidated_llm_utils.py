"""Consolidated LLM approach using one powerful model for both content generation and cultural alignment.

This module implements a sequential workflow using GPT-4/Claude 3 with structured system prompts
to handle both content generation and cultural sensitivity in a single LLM call.
"""

import os
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import OpenAI utilities
try:
    from .openai_utils import get_openai_client
    OPENAI_AVAILABLE = True
except ImportError:
    try:
        from openai_utils import get_openai_client
        OPENAI_AVAILABLE = True
    except ImportError:
        print("⚠️ OpenAI utilities not available")
        OPENAI_AVAILABLE = False

class ConsolidatedLLMApproach:
    """Consolidated approach using one powerful model for both content and cultural alignment"""
    
    def __init__(self):
        self.client = get_openai_client() if OPENAI_AVAILABLE else None
        self.cultural_prompts = self._load_cultural_prompts()
        self.grant_templates = self._load_grant_templates()
        
    def _load_cultural_prompts(self) -> Dict[str, Any]:
        """Load culturally sensitive prompt templates"""
        return {
            "system_prompt_template": """You are a grant assistant for {organization_name}. Adhere to:

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
RESPONSE FORMAT:
- Start with a compelling community-focused opening
- Include specific cultural context and community strengths
- Use clear headings and bullet points
- End with measurable impact and community benefits""",
            
            "community_context_template": """COMMUNITY CONTEXT: {community_focus}
CULTURAL GUIDELINES: {cultural_guidelines}
ORGANIZATION PROFILE: {organization_info}"""
        }
    
    def _load_grant_templates(self) -> Dict[str, Any]:
        """Load grant-specific templates for different types"""
        return {
            "nih": {
                "tone": "Scientific and community-focused",
                "emphasis": "Research methodology and community impact",
                "cultural_notes": "Emphasize community partnership in research"
            },
            "nsf": {
                "tone": "Innovation and broader impact",
                "emphasis": "Novel approaches and educational outreach",
                "cultural_notes": "Highlight diverse participation and inclusion"
            },
            "community": {
                "tone": "Community-driven and collaborative",
                "emphasis": "Local partnerships and sustainable impact",
                "cultural_notes": "Center community voice and traditional knowledge"
            },
            "federal": {
                "tone": "Comprehensive and evidence-based",
                "emphasis": "Measurable outcomes and systematic approach",
                "cultural_notes": "Demonstrate cultural competency in implementation"
            }
        }
    
    def generate_consolidated_response(self, 
                                    message: str, 
                                    context: Dict[str, Any], 
                                    grant_type: str = "community",
                                    community_context: Optional[str] = None) -> str:
        """Generate culturally sensitive response using consolidated LLM approach"""
        
        if not self.client:
            return "⚠️ OpenAI client not available. Please configure API key."
        
        try:
            # Build dynamic system prompt
            organization_name = context.get('organization_info', 'the organization').split()[0] if context.get('organization_info') else 'the organization'
            system_prompt = self.cultural_prompts["system_prompt_template"].format(
                organization_name=organization_name
            )
            
            # Add grant-specific cultural notes
            grant_template = self.grant_templates.get(grant_type, self.grant_templates["community"])
            system_prompt += f"\n\nGRANT TYPE: {grant_type.upper()}"
            system_prompt += f"\nTONE: {grant_template['tone']}"
            system_prompt += f"\nEMPHASIS: {grant_template['emphasis']}"
            system_prompt += f"\nCULTURAL NOTES: {grant_template['cultural_notes']}"
            
            # Build context string
            context_string = self.cultural_prompts["community_context_template"].format(
                community_focus=community_context or context.get('community_focus', ''),
                cultural_guidelines=context.get('cultural_guidelines', ''),
                organization_info=context.get('organization_info', '')
            )
            
            # Add uploaded content context
            if context.get('uploaded_content'):
                context_string += f"\n\nUPLOADED CONTENT:\n" + "\n".join(context.get('uploaded_content', []))
            
            # Add RFP requirements
            if context.get('rfp_requirements'):
                context_string += f"\n\nRFP REQUIREMENTS:\n" + ", ".join(context.get('rfp_requirements', []))
            
            # Build user message with context
            user_message = f"""
{context_string}

USER REQUEST: {message}

Please provide a culturally sensitive, community-focused response that addresses the user's request while maintaining the appropriate tone and emphasis for this grant type.
"""
            
            # Make single LLM call
            response = self.client.chat.completions.create(
                model="gpt-4",  # Use GPT-4 for best cultural competency
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Error in consolidated LLM approach: {e}")
            return f"⚠️ Error generating response: {str(e)}"
    
    def generate_grant_section(self, 
                             section_type: str, 
                             context: Dict[str, Any], 
                             grant_type: str = "community",
                             community_context: Optional[str] = None) -> str:
        """Generate specific grant sections using consolidated approach"""
        
        section_prompts = {
            "executive_summary": "Write a compelling executive summary that highlights community impact and cultural sensitivity.",
            "organization_profile": "Create an organization profile that emphasizes community connections and cultural competency.",
            "project_description": "Describe the project with focus on community-driven solutions and measurable impact.",
            "budget": "Create a budget section that shows responsible resource allocation and community benefit.",
            "timeline": "Develop a timeline that respects cultural concepts of time and community planning.",
            "evaluation": "Design evaluation metrics that capture both quantitative outcomes and cultural impact."
        }
        
        prompt = section_prompts.get(section_type, "Provide guidance on this grant section.")
        
        return self.generate_consolidated_response(prompt, context, grant_type, community_context)
    
    def evaluate_cultural_alignment(self, 
                                 content: str, 
                                 context: Dict[str, Any], 
                                 community_context: Optional[str] = None) -> Dict[str, Any]:
        """Evaluate cultural alignment using the same consolidated model"""
        
        if not self.client:
            return {"error": "OpenAI client not available"}
        
        try:
            evaluation_prompt = f"""
Evaluate the following content for cultural competency and sensitivity:

CONTENT TO EVALUATE:
{content}

COMMUNITY CONTEXT: {community_context or context.get('community_focus', '')}

Please evaluate on these dimensions:
1. Cultural Sensitivity (0-100)
2. Community Focus (0-100)
3. Cognitive Friendliness (0-100)
4. Overall Quality (0-100)

Provide scores and specific recommendations for improvement.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a cultural competency evaluator. Provide structured evaluation with scores and recommendations."},
                    {"role": "user", "content": evaluation_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse evaluation response
            eval_text = response.choices[0].message.content.strip()
            
            # Extract scores using regex
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
            
        except Exception as e:
            print(f"❌ Error in cultural evaluation: {e}")
            return {"error": str(e)}
    
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
consolidated_llm = ConsolidatedLLMApproach() 