"""Storage utilities for the AI Grant Writer tool using Supabase.

This module provides functions for storing files and context data in Supabase,
which is much more reliable than local file storage on Railway.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Import Supabase utility functions
try:
    from .supabase_utils import (
        insert_organization, get_organization, insert_rfp, get_rfp,
        insert_project_response, get_project_response, insert_file_chunks_into_db,
        insert_secure_data, get_all_projects_from_db
    ) # type: ignore
except ImportError:
    from utils.supabase_utils import (
        insert_organization, get_organization, insert_rfp, get_rfp,
        insert_project_response, get_project_response, insert_file_chunks_into_db,
        insert_secure_data, get_all_projects_from_db
    ) # type: ignore

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

class DatabaseManager:
    """Manages all database operations with security"""
    
    def save_organization(self, org: OrganizationInfo) -> bool:
        """Save organization information to Supabase"""
        try:
            return insert_organization(asdict(org))
        except Exception as e:
            print(f"Error saving organization to Supabase: {e}")
            return False
    
    def get_organization(self, org_id: str) -> Optional[OrganizationInfo]:
        """Get organization information from Supabase"""
        try:
            data = get_organization(org_id)
            if data:
                return OrganizationInfo(**data)
            return None
        except Exception as e:
            print(f"Error getting organization from Supabase: {e}")
            return None
    
    def save_rfp(self, rfp: RFPDocument) -> bool:
        """Save RFP document with analysis to Supabase"""
        try:
            return insert_rfp(asdict(rfp))
        except Exception as e:
            print(f"Error saving RFP to Supabase: {e}")
            return False
    
    def get_rfp(self, rfp_id: str) -> Optional[RFPDocument]:
        """Get RFP document from Supabase"""
        try:
            data = get_rfp(rfp_id)
            if data:
                return RFPDocument(**data)
            return None
        except Exception as e:
            print(f"Error getting RFP from Supabase: {e}")
            return None
    
    def save_project_response(self, response: ProjectResponse) -> bool:
        """Save project response to Supabase"""
        try:
            return insert_project_response(asdict(response))
        except Exception as e:
            print(f"Error saving project response to Supabase: {e}")
            return False
    
    def get_project_response(self, response_id: str) -> Optional[ProjectResponse]:
        """Get project response from Supabase"""
        try:
            data = get_project_response(response_id)
            if data:
                return ProjectResponse(**data)
            return None
        except Exception as e:
            print(f"Error getting project response from Supabase: {e}")
            return None

    def insert_file_chunk(self, file_name: str, chunk_text: str, embedding: List[float]) -> Optional[int]:
        """Insert a file chunk into the file_chunks table in Supabase.
        Returns the ID of the inserted chunk.
        """
        try:
            # insert_file_chunks_into_db expects a list of tuples
            chunk_id = insert_file_chunks_into_db([(file_name, chunk_text, embedding)])
            return chunk_id
        except Exception as e:
            print(f"Error inserting file chunk into Supabase: {e}")
            return None

    def insert_secure_data(self, file_chunk_id: int, original_text: str, redactions: List[Dict[str, Any]]) -> bool:
        """Save sensitive data to the secure_storage table in Supabase."""
        try:
            return insert_secure_data(file_chunk_id, original_text, redactions)
        except Exception as e:
            print(f"Error saving secure data to Supabase: {e}")
            return False
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get all projects from Supabase"""
        try:
            return get_all_projects_from_db()
        except Exception as e:
            print(f"Error getting all projects from Supabase: {e}")
            return []

# Global database manager instance
db_manager = DatabaseManager()