"""Storage utilities for the AI Grant Writer tool using Supabase.

This module provides functions for storing files and context data in Supabase,
which is much more reliable than local file storage on Railway.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import os

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
    org_id: str
    data_type: str  # 'financial', 'personal', 'confidential'
    encrypted_data: str
    redacted_summary: str
    created_at: str

class DatabaseManager:
    """Manages all database operations with security"""
    
    def __init__(self):
        self.data_dir = "data"
        self.secure_dir = "secure_data"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.secure_dir, exist_ok=True)
    
    def _get_file_path(self, filename: str, secure: bool = False) -> str:
        """Get file path for data storage"""
        base_dir = self.secure_dir if secure else self.data_dir
        return os.path.join(base_dir, f"{filename}.json")
    
    def save_organization(self, org: OrganizationInfo) -> bool:
        """Save organization information"""
        try:
            file_path = self._get_file_path(f"org_{org.id}")
            with open(file_path, 'w') as f:
                json.dump(asdict(org), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving organization: {e}")
            return False
    
    def get_organization(self, org_id: str) -> Optional[OrganizationInfo]:
        """Get organization information"""
        try:
            file_path = self._get_file_path(f"org_{org_id}")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return OrganizationInfo(**data)
            return None
        except Exception as e:
            print(f"Error getting organization: {e}")
            return None
    
    def save_rfp(self, rfp: RFPDocument) -> bool:
        """Save RFP document with analysis"""
        try:
            file_path = self._get_file_path(f"rfp_{rfp.id}")
            with open(file_path, 'w') as f:
                json.dump(asdict(rfp), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving RFP: {e}")
            return False
    
    def get_rfp(self, rfp_id: str) -> Optional[RFPDocument]:
        """Get RFP document"""
        try:
            file_path = self._get_file_path(f"rfp_{rfp_id}")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return RFPDocument(**data)
            return None
        except Exception as e:
            print(f"Error getting RFP: {e}")
            return None
    
    def save_project_response(self, response: ProjectResponse) -> bool:
        """Save project response"""
        try:
            file_path = self._get_file_path(f"response_{response.id}")
            with open(file_path, 'w') as f:
                json.dump(asdict(response), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving project response: {e}")
            return False
    
    def get_project_response(self, response_id: str) -> Optional[ProjectResponse]:
        """Get project response"""
        try:
            file_path = self._get_file_path(f"response_{response_id}")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return ProjectResponse(**data)
            return None
        except Exception as e:
            print(f"Error getting project response: {e}")
            return None
    
    def save_secure_data(self, secure_data: SecureData) -> bool:
        """Save sensitive data securely"""
        try:
            file_path = self._get_file_path(f"secure_{secure_data.id}", secure=True)
            with open(file_path, 'w') as f:
                json.dump(asdict(secure_data), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving secure data: {e}")
            return False
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get all projects"""
        try:
            projects = []
            for filename in os.listdir(self.data_dir):
                if filename.startswith("response_") and filename.endswith(".json"):
                    response_id = filename.replace("response_", "").replace(".json", "")
                    response = self.get_project_response(response_id)
                    if response:
                        projects.append({
                            "id": response.project_id,
                            "name": f"Project {response.project_id}",
                            "description": f"RFP Response - {response.rfp_id}",
                            "created_at": response.created_at
                        })
            return projects
        except Exception as e:
            print(f"Error getting projects: {e}")
            return []

# Global database manager instance
db_manager = DatabaseManager() 