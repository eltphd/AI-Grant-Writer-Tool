"""Specialized 7B LLM approach with cultural competency for grant writing.

This module implements a specialized approach using smaller, efficient models
with cultural competency features and advanced prompt engineering.
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

# Import the advanced RAG system
try:
    from .advanced_rag_utils import advanced_rag_db, CulturalKnowledgeItem
except ImportError:
    from advanced_rag_utils import advanced_rag_db, CulturalKnowledgeItem

class SpecializedLLMApproach:
    """Specialized 7B-like approach with cultural competency"""
    
    def __init__(self):
        self.cultural_prompts = self._load_cultural_prompts()
        self.grant_writing_prompts = self._load_grant_writing_prompts()
        self.community_contexts = self._load_community_contexts()
    
    def _load_cultural_prompts(self) -> Dict[str, Any]:
        """Load culturally sensitive prompt templates"""
        return {
            "executive_summary": {
                "system_prompt": """You are a culturally sensitive grant writing expert specializing in community-based organizations.

CULTURAL COMPETENCY GUIDELINES:
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

RESPONSE FORMAT:
- Start with a compelling community-focused opening
- Include specific cultural context and community strengths
- Use clear headings and bullet points
- End with measurable impact and community benefits""",
                
                "user_prompt_template": """Write a culturally sensitive executive summary for a grant proposal.

ORGANIZATION CONTEXT: {organization_info}
COMMUNITY FOCUS: {community_focus}
UPLOADED DOCUMENTS: {uploaded_files}
RFP REQUIREMENTS: {rfp_requirements}

Please create an executive summary that:
1. Respects and honors the community's cultural context
2. Highlights community strengths and resilience
3. Addresses specific community needs and priorities
4. Uses inclusive, accessible language
5. Provides concrete, measurable goals
6. Shows cultural competency and sensitivity

Focus on community impact and cultural appropriateness."""
            },
            
            "organization_profile": {
                "system_prompt": """You are a culturally sensitive grant writing expert helping organizations create compelling profiles.

CULTURAL COMPETENCY GUIDELINES:
- Emphasize community connections and cultural relevance
- Highlight diverse partnerships and collaborations
- Show respect for traditional knowledge and practices
- Include cultural competency in organizational strengths
- Address community-specific challenges and solutions
- Use culturally appropriate success metrics

RESPONSE FORMAT:
- Start with mission and cultural connection
- Include community partnerships and cultural expertise
- Highlight cultural competency and community trust
- Show measurable impact with cultural context
- Use clear, accessible language""",
                
                "user_prompt_template": """Create a culturally sensitive organization profile for grant writing.

ORGANIZATION INFO: {organization_info}
COMMUNITY CONTEXT: {community_focus}
CULTURAL GUIDELINES: {cultural_guidelines}

Please write a profile that:
1. Shows cultural competency and community trust
2. Highlights diverse partnerships and collaborations
3. Emphasizes community-driven approaches
4. Includes culturally appropriate success metrics
5. Demonstrates understanding of community needs
6. Uses inclusive, respectful language"""
            },
            
            "project_description": {
                "system_prompt": """You are a culturally sensitive project planning expert.

CULTURAL COMPETENCY GUIDELINES:
- Emphasize community-driven project design
- Include cultural context in project goals
- Address community-specific barriers and solutions
- Show respect for traditional knowledge and practices
- Include culturally appropriate evaluation methods
- Consider cultural concepts of time and planning

RESPONSE FORMAT:
- Start with community needs and cultural context
- Include community participation in design
- Address cultural barriers and solutions
- Show culturally appropriate outcomes
- Use clear, accessible language""",
                
                "user_prompt_template": """Write a culturally sensitive project description for grant writing.

PROJECT CONTEXT: {project_context}
COMMUNITY FOCUS: {community_focus}
CULTURAL GUIDELINES: {cultural_guidelines}

Please create a project description that:
1. Shows community-driven design and participation
2. Addresses cultural context and community needs
3. Includes culturally appropriate methods and outcomes
4. Demonstrates cultural competency and sensitivity
5. Uses inclusive, accessible language
6. Provides concrete, measurable goals"""
            }
        }
    
    def _load_grant_writing_prompts(self) -> Dict[str, Any]:
        """Load specialized grant writing prompts"""
        return {
            "budget_section": {
                "cultural_considerations": [
                    "Include culturally appropriate cost considerations",
                    "Address cultural barriers to resource access",
                    "Consider community-specific budget priorities",
                    "Include cultural competency training costs",
                    "Address language access and translation needs"
                ],
                "prompt_template": """Create a culturally sensitive budget section for grant writing.

PROJECT SCOPE: {project_scope}
COMMUNITY CONTEXT: {community_focus}
CULTURAL NEEDS: {cultural_needs}

Include culturally appropriate budget items such as:
- Cultural competency training and materials
- Language access and translation services
- Community engagement and outreach costs
- Culturally appropriate evaluation methods
- Cultural consultation and advisory services"""
            },
            
            "timeline_section": {
                "cultural_considerations": [
                    "Respect cultural concepts of time and planning",
                    "Include community consultation periods",
                    "Consider cultural events and traditions",
                    "Allow for community decision-making processes",
                    "Include cultural competency development time"
                ],
                "prompt_template": """Create a culturally sensitive timeline for grant implementation.

PROJECT SCOPE: {project_scope}
COMMUNITY CONTEXT: {community_focus}
CULTURAL EVENTS: {cultural_events}

Consider cultural factors such as:
- Community consultation and decision-making time
- Cultural events and traditional practices
- Seasonal and cultural calendar considerations
- Community relationship-building periods
- Cultural competency development phases"""
            },
            
            "evaluation_section": {
                "cultural_considerations": [
                    "Include culturally appropriate evaluation methods",
                    "Consider community-defined success metrics",
                    "Address cultural barriers to participation",
                    "Include qualitative cultural impact measures",
                    "Respect cultural concepts of success and progress"
                ],
                "prompt_template": """Create a culturally sensitive evaluation plan for grant writing.

PROJECT GOALS: {project_goals}
COMMUNITY CONTEXT: {community_focus}
CULTURAL METRICS: {cultural_metrics}

Include culturally appropriate evaluation methods:
- Community-defined success indicators
- Cultural impact and competency measures
- Qualitative community feedback methods
- Culturally appropriate data collection
- Community participation in evaluation"""
            }
        }
    
    def _load_community_contexts(self) -> Dict[str, Any]:
        """Load community-specific cultural contexts"""
        return {
            "urban_communities": {
                "cultural_values": ["diversity", "resilience", "community", "innovation"],
                "communication_style": "direct and inclusive",
                "success_metrics": ["community engagement", "diversity representation", "accessibility"],
                "cultural_considerations": [
                    "Address diverse cultural backgrounds",
                    "Consider language access needs",
                    "Include multiple cultural perspectives",
                    "Address systemic barriers and inequities"
                ]
            },
            "rural_communities": {
                "cultural_values": ["tradition", "self_reliance", "community", "stewardship"],
                "communication_style": "personal and trust-based",
                "success_metrics": ["community ownership", "sustainability", "local capacity"],
                "cultural_considerations": [
                    "Respect traditional knowledge and practices",
                    "Consider seasonal and agricultural cycles",
                    "Include local leadership and expertise",
                    "Address geographic and resource barriers"
                ]
            },
            "indigenous_communities": {
                "cultural_values": ["spirituality", "land_connection", "tradition", "community"],
                "communication_style": "respectful and traditional",
                "success_metrics": ["cultural preservation", "community sovereignty", "traditional knowledge"],
                "cultural_considerations": [
                    "Respect traditional knowledge and practices",
                    "Include cultural ceremonies and protocols",
                    "Address historical trauma and systemic barriers",
                    "Support community sovereignty and self-determination"
                ]
            }
        }
    
    def generate_culturally_sensitive_response(self, prompt_type: str, context: Dict[str, Any], 
                                            community_context: Optional[str] = None) -> str:
        """Generate culturally sensitive response using specialized approach"""
        
        try:
            # Get cultural prompts for the specific type
            if prompt_type in self.cultural_prompts:
                system_prompt = self.cultural_prompts[prompt_type]["system_prompt"]
                user_prompt_template = self.cultural_prompts[prompt_type]["user_prompt_template"]
                
                # Enhance context with community-specific information
                enhanced_context = self._enhance_context_with_cultural_info(context, community_context)
                
                # Format user prompt
                user_prompt = user_prompt_template.format(**enhanced_context)
                
                # Use OpenAI with specialized prompts
                from .openai_utils import get_culturally_sensitive_response
                return get_culturally_sensitive_response(user_prompt, community_context)
            
            else:
                # Fallback to general culturally sensitive response
                from .openai_utils import chat_grant_assistant
                return chat_grant_assistant(
                    f"Help with {prompt_type}",
                    str(context),
                    community_context
                )
                
        except Exception as e:
            print(f"Error generating culturally sensitive response: {e}")
            return self._generate_fallback_response(prompt_type, context, community_context)
    
    def _enhance_context_with_cultural_info(self, context: Dict[str, Any], 
                                          community_context: Optional[str] = None) -> Dict[str, Any]:
        """Enhance context with cultural information"""
        enhanced_context = context.copy()
        
        # Add community-specific cultural information
        if community_context and community_context in self.community_contexts:
            community_info = self.community_contexts[community_context]
            enhanced_context["cultural_values"] = ", ".join(community_info["cultural_values"])
            enhanced_context["communication_style"] = community_info["communication_style"]
            enhanced_context["cultural_considerations"] = "\n".join(community_info["cultural_considerations"])
        
        # Add cultural guidelines from RAG system
        try:
            cultural_guidelines = advanced_rag_db.get_cultural_guidelines(community_context)
            if cultural_guidelines:
                enhanced_context["cultural_guidelines"] = "\n".join(cultural_guidelines[0].guidelines[:5])
        except Exception as e:
            print(f"Error getting cultural guidelines: {e}")
            enhanced_context["cultural_guidelines"] = "Use inclusive, respectful language"
        
        return enhanced_context
    
    def _generate_fallback_response(self, prompt_type: str, context: Dict[str, Any], 
                                  community_context: Optional[str] = None) -> str:
        """Generate fallback response when specialized approach fails"""
        
        base_response = f"""📋 **{prompt_type.replace('_', ' ').title()}**

Based on your organization's information and community context, here's a culturally sensitive approach:

**Community Focus:**
Your project serves {community_context or 'diverse communities'} with respect for cultural values and traditions.

**Key Considerations:**
• Use inclusive, respectful language throughout
• Highlight community strengths and resilience
• Address cultural barriers and solutions
• Include community voice and perspectives
• Show cultural competency and sensitivity

**Next Steps:**
Please review this approach and let me know if you'd like me to adjust the focus, tone, or add specific cultural considerations for your community."""
        
        return base_response
    
    def generate_grant_section_with_cultural_context(self, section_type: str, 
                                                   organization_info: str,
                                                   project_context: str,
                                                   community_context: Optional[str] = None) -> str:
        """Generate grant section with cultural context awareness"""
        
        # Build context
        context = {
            "organization_info": organization_info,
            "project_context": project_context,
            "community_focus": community_context or "diverse communities",
            "uploaded_files": "Based on uploaded documents",
            "rfp_requirements": "Based on RFP analysis"
        }
        
        # Generate culturally sensitive response
        return self.generate_culturally_sensitive_response(section_type, context, community_context)
    
    def analyze_cultural_alignment(self, organization_info: str, 
                                 community_context: Optional[str] = None) -> Dict[str, Any]:
        """Analyze cultural alignment of organization with community context"""
        
        try:
            # Get community context information
            community_info = {}
            if community_context and community_context in self.community_contexts:
                community_info = self.community_contexts[community_context]
            
            # Analyze alignment
            alignment_analysis = {
                "cultural_values_match": [],
                "communication_style_alignment": "",
                "cultural_competency_indicators": [],
                "recommendations": [],
                "community_context": community_context,
                "analysis_date": datetime.now().isoformat()
            }
            
            # Check for cultural competency indicators
            cultural_indicators = [
                "diverse", "inclusive", "community", "cultural", "multicultural",
                "partnership", "collaboration", "respect", "traditional", "heritage"
            ]
            
            for indicator in cultural_indicators:
                if indicator.lower() in organization_info.lower():
                    alignment_analysis["cultural_competency_indicators"].append(indicator)
            
            # Generate recommendations
            if community_context:
                if community_context == "urban_communities":
                    alignment_analysis["recommendations"].extend([
                        "Emphasize diversity and inclusion in all sections",
                        "Include multiple cultural perspectives and languages",
                        "Address systemic barriers and inequities",
                        "Show commitment to accessibility and representation"
                    ])
                elif community_context == "rural_communities":
                    alignment_analysis["recommendations"].extend([
                        "Highlight local expertise and traditional knowledge",
                        "Show respect for community traditions and practices",
                        "Address geographic and resource barriers",
                        "Emphasize community ownership and sustainability"
                    ])
                elif community_context == "indigenous_communities":
                    alignment_analysis["recommendations"].extend([
                        "Respect traditional knowledge and cultural practices",
                        "Include cultural protocols and community consultation",
                        "Address historical trauma and systemic barriers",
                        "Support community sovereignty and self-determination"
                    ])
            
            return alignment_analysis
            
        except Exception as e:
            print(f"Error analyzing cultural alignment: {e}")
            return {
                "error": "Unable to analyze cultural alignment",
                "recommendations": ["Use inclusive, respectful language", "Consider community cultural context"]
            }

# Initialize the specialized LLM approach
specialized_llm = SpecializedLLMApproach() 