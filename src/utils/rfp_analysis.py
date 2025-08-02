"""RFP Analysis utilities for grant writing tool."""

import re
from typing import Dict, List, Any
from datetime import datetime

def analyze_rfp_content(content: str) -> Dict[str, Any]:
    """Analyze RFP content to extract key information."""
    analysis = {
        'requirements': [],
        'eligibility_criteria': [],
        'funding_amount': None,
        'deadline': None,
        'key_dates': [],
        'evaluation_criteria': []
    }
    
    # Extract funding amount
    funding_patterns = [
        r'\$[\d,]+(?:\.\d{2})?',
        r'funding.*?\$[\d,]+(?:\.\d{2})?',
        r'grant.*?\$[\d,]+(?:\.\d{2})?',
        r'budget.*?\$[\d,]+(?:\.\d{2})?'
    ]
    
    for pattern in funding_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            analysis['funding_amount'] = matches[0]
            break
    
    # Extract deadlines
    deadline_patterns = [
        r'deadline.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'due.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'submission.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
    ]
    
    for pattern in deadline_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            analysis['deadline'] = matches[0]
            break
    
    # Extract requirements (basic pattern matching)
    requirement_keywords = ['must', 'shall', 'required', 'requirement', 'criteria']
    lines = content.split('\n')
    
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in requirement_keywords):
            if len(line.strip()) > 10:  # Avoid very short lines
                analysis['requirements'].append(line.strip())
    
    # Extract eligibility criteria
    eligibility_keywords = ['eligible', 'eligibility', 'qualify', 'qualification']
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in eligibility_keywords):
            if len(line.strip()) > 10:
                analysis['eligibility_criteria'].append(line.strip())
    
    return analysis

def analyze_organization_rfp_alignment(org_data: Dict[str, Any], rfp_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze alignment between organization profile and RFP requirements."""
    
    # Simple scoring algorithm
    org_fit_score = 0
    overall_score = 0
    
    # Check if organization has required capabilities
    org_description = org_data.get('description', '').lower()
    org_mission = org_data.get('mission', '').lower()
    
    # Count matching requirements
    requirements = rfp_data.get('requirements', [])
    matching_requirements = 0
    
    for req in requirements:
        req_lower = req.lower()
        if any(keyword in org_description or keyword in org_mission 
               for keyword in req_lower.split()[:5]):  # Check first 5 words
            matching_requirements += 1
    
    if requirements:
        org_fit_score = min(100, (matching_requirements / len(requirements)) * 100)
    
    # Overall score based on multiple factors
    factors = [
        org_fit_score * 0.6,  # 60% weight on requirement match
        80 if rfp_data.get('funding_amount') else 60,  # 20% weight on funding info
        90 if rfp_data.get('deadline') else 70  # 20% weight on deadline info
    ]
    
    overall_score = sum(factors)
    
    return {
        'org_fit_score': round(org_fit_score, 1),
        'overall_score': round(overall_score, 1),
        'matching_requirements': matching_requirements,
        'total_requirements': len(requirements),
        'analysis_date': datetime.now().isoformat()
    } 