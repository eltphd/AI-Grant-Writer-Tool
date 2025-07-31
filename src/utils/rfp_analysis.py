import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from .storage_utils import OrganizationInfo, RFPDocument, ProjectResponse, db_manager

class RFPAnalyzer:
    """Analyzes RFP documents and aligns with organization information"""
    
    def __init__(self):
        self.keywords = {
            'eligibility': ['eligible', 'eligibility', 'qualify', 'qualification', 'requirements'],
            'funding': ['funding', 'grant', 'award', 'budget', 'cost', 'amount'],
            'deadline': ['deadline', 'due date', 'submission', 'closing'],
            'scope': ['scope', 'purpose', 'objective', 'goal', 'target'],
            'evaluation': ['evaluation', 'criteria', 'scoring', 'review', 'assessment']
        }
    
    def analyze_rfp_content(self, content: str) -> Dict[str, Any]:
        """Extract key information from RFP content"""
        analysis = {
            'requirements': [],
            'eligibility_criteria': [],
            'funding_amount': None,
            'deadline': None,
            'key_themes': [],
            'evaluation_criteria': []
        }
        
        # Extract requirements
        requirement_patterns = [
            r'requirement[s]?\s*:?\s*([^.\n]+)',
            r'must\s+([^.\n]+)',
            r'shall\s+([^.\n]+)',
            r'required\s+([^.\n]+)'
        ]
        
        for pattern in requirement_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            analysis['requirements'].extend([match.strip() for match in matches])
        
        # Extract eligibility criteria
        eligibility_patterns = [
            r'eligible\s+([^.\n]+)',
            r'qualification[s]?\s*:?\s*([^.\n]+)',
            r'eligibility\s+criteria[:\s]*([^.\n]+)'
        ]
        
        for pattern in eligibility_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            analysis['eligibility_criteria'].extend([match.strip() for match in matches])
        
        # Extract funding amount
        funding_patterns = [
            r'\$[\d,]+(?:\.\d{2})?',
            r'[\d,]+(?:\.\d{2})?\s*dollars?',
            r'funding\s+amount[:\s]*([^.\n]+)',
            r'grant\s+amount[:\s]*([^.\n]+)'
        ]
        
        for pattern in funding_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                analysis['funding_amount'] = matches[0]
                break
        
        # Extract deadline
        deadline_patterns = [
            r'deadline[:\s]*([^.\n]+)',
            r'due\s+date[:\s]*([^.\n]+)',
            r'submission\s+deadline[:\s]*([^.\n]+)',
            r'closing\s+date[:\s]*([^.\n]+)'
        ]
        
        for pattern in deadline_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                analysis['deadline'] = matches[0]
                break
        
        return analysis
    
    def align_org_with_rfp(self, org: OrganizationInfo, rfp: RFPDocument) -> Dict[str, Any]:
        """Analyze alignment between organization and RFP requirements"""
        
        alignment = {
            'overall_score': 0,
            'org_fit_score': 0,
            'strengths': [],
            'weaknesses': [],
            'recommendations': [],
            'narrative_suggestions': []
        }
        
        # Analyze organization strengths against RFP requirements
        org_text = f"{org.mission} {org.description} {' '.join(org.key_accomplishments)} {' '.join(org.partnerships)}"
        
        # Check for keyword matches
        requirement_matches = 0
        total_requirements = len(rfp.requirements)
        
        for requirement in rfp.requirements:
            if any(keyword.lower() in org_text.lower() for keyword in requirement.split()):
                requirement_matches += 1
                alignment['strengths'].append(f"Matches requirement: {requirement}")
        
        # Calculate alignment scores
        if total_requirements > 0:
            alignment['org_fit_score'] = int((requirement_matches / total_requirements) * 100)
        
        # Overall score based on multiple factors
        alignment['overall_score'] = min(100, alignment['org_fit_score'] + 20)  # Bonus for good structure
        
        # Generate recommendations
        if alignment['org_fit_score'] < 70:
            alignment['recommendations'].append("Consider strengthening alignment with RFP requirements")
            alignment['recommendations'].append("Highlight relevant experience and partnerships")
        else:
            alignment['recommendations'].append("Strong alignment - emphasize key strengths")
        
        # Narrative suggestions
        alignment['narrative_suggestions'].append("Focus on measurable outcomes and impact")
        alignment['narrative_suggestions'].append("Include specific examples of success")
        alignment['narrative_suggestions'].append("Emphasize partnerships and collaborations")
        
        return alignment
    
    def generate_response_narrative(self, org: OrganizationInfo, rfp: RFPDocument, alignment: Dict[str, Any]) -> str:
        """Generate a tailored narrative based on RFP and organization alignment"""
        
        narrative_parts = []
        
        # Introduction
        narrative_parts.append(f"Based on our analysis of the {rfp.filename} requirements and {org.name}'s capabilities, we believe our organization is well-positioned to deliver exceptional results.")
        
        # Alignment summary
        if alignment['org_fit_score'] >= 80:
            narrative_parts.append(f"Our organization demonstrates strong alignment with the RFP requirements, with a {alignment['org_fit_score']}% fit score based on our experience and capabilities.")
        else:
            narrative_parts.append(f"While we acknowledge areas for growth, our organization brings valuable experience that aligns with {alignment['org_fit_score']}% of the RFP requirements.")
        
        # Key strengths
        if alignment['strengths']:
            narrative_parts.append("Our key strengths include:")
            for strength in alignment['strengths'][:3]:  # Top 3 strengths
                narrative_parts.append(f"• {strength}")
        
        # Recommendations
        if alignment['recommendations']:
            narrative_parts.append("To maximize our impact, we recommend:")
            for rec in alignment['recommendations']:
                narrative_parts.append(f"• {rec}")
        
        return "\n\n".join(narrative_parts)
    
    def create_project_response(self, org: OrganizationInfo, rfp: RFPDocument, alignment: Dict[str, Any]) -> ProjectResponse:
        """Create a complete project response"""
        
        from datetime import datetime
        
        response_id = f"response_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        narrative = self.generate_response_narrative(org, rfp, alignment)
        
        # Create sections based on RFP requirements
        sections = {
            "executive_summary": narrative[:500] + "...",
            "organization_profile": org.description,
            "project_approach": "Tailored approach based on RFP requirements",
            "timeline": "12-month implementation timeline",
            "budget": "Detailed budget aligned with RFP funding",
            "evaluation": "Comprehensive evaluation and reporting plan"
        }
        
        return ProjectResponse(
            id=response_id,
            project_id=rfp.project_id,
            rfp_id=rfp.id,
            org_id=org.id,
            narrative=narrative,
            sections=sections,
            alignment_score=alignment['org_fit_score'],
            recommendations=alignment['recommendations'],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

# Global analyzer instance
rfp_analyzer = RFPAnalyzer() 