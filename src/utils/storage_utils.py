"""Data models for the AI Grant Writer tool.

This module provides dataclass models for the application entities.
All database operations are now handled directly by supabase_utils.py.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

@dataclass
class OrganizationInfo:
    """Secure organization information"""
    id: str
    name: str
    mission: str
    description: str
    key_accomplishments: List[str]
    partnerships: List[str]
    impact_metrics: Dict[str, Any]
    created_at: str
    updated_at: str

@dataclass
class RFPDocument:
    """RFP document with analysis"""
    id: str
    project_id: str
    filename: str
    content: str
    requirements: List[str]
    eligibility_criteria: List[str]
    funding_amount: Optional[str]
    deadline: Optional[str]
    analysis_result: Dict[str, Any]
    created_at: str

@dataclass
class ProjectResponse:
    """Project-specific response to RFP"""
    id: str
    project_id: str
    rfp_id: str
    org_id: str
    narrative: str
    sections: Dict[str, str]
    alignment_score: int
    recommendations: List[str]
    created_at: str
    updated_at: str

@dataclass
class SecureData:
    """Securely stored sensitive information"""
    id: str
    file_chunk_id: int
    original_text: str
    redactions: List[Dict[str, Any]]
    created_at: str

# All database operations are now handled directly by supabase_utils.py
# This file only contains data models for type safety and documentation