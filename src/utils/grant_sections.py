"""Grant sections management and template utilities.

This module handles the six core grant application sections with structured
data storage, template generation, and RAG-enabled retrieval.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import markdown
from pathlib import Path

@dataclass
class GrantSection:
    """Represents a grant application section."""
    id: str
    title: str
    content: str
    target_length: str
    word_count: int = 0
    last_updated: str = ""
    status: str = "draft"  # draft, complete, reviewed
    
    def update_content(self, new_content: str):
        """Update section content and metadata."""
        self.content = new_content
        self.word_count = len(new_content.split())
        self.last_updated = datetime.now().isoformat()
        if self.word_count > 0:
            self.status = "complete" if self.word_count >= 50 else "draft"

@dataclass
class GrantDocument:
    """Represents a complete grant application document."""
    project_id: str
    sections: Dict[str, GrantSection]
    created_at: str
    last_updated: str
    total_word_count: int = 0
    
    def update_section(self, section_id: str, content: str):
        """Update a specific section."""
        if section_id in self.sections:
            self.sections[section_id].update_content(content)
            self._update_metadata()
    
    def _update_metadata(self):
        """Update document metadata."""
        self.last_updated = datetime.now().isoformat()
        self.total_word_count = sum(section.word_count for section in self.sections.values())
    
    def get_section(self, section_id: str) -> Optional[GrantSection]:
        """Get a specific section."""
        return self.sections.get(section_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "project_id": self.project_id,
            "sections": {k: asdict(v) for k, v in self.sections.items()},
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "total_word_count": self.total_word_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GrantDocument':
        """Create from dictionary."""
        sections = {}
        for section_id, section_data in data.get("sections", {}).items():
            sections[section_id] = GrantSection(**section_data)
        
        return cls(
            project_id=data["project_id"],
            sections=sections,
            created_at=data["created_at"],
            last_updated=data["last_updated"],
            total_word_count=data.get("total_word_count", 0)
        )

class GrantSectionManager:
    """Manages grant sections and templates."""
    
    # Core sections schema
    CORE_SECTIONS = {
        "exec_summary": {
            "id": "exec_summary",
            "title": "Executive Summary / Cover Sheet",
            "target_length": "250–400 words",
            "description": "Concise snapshot of the project: who you are, what you want to do, funding request, and expected impact.",
            "placeholder": "Describe your organization, the project goals, funding amount requested, and expected impact in 250-400 words..."
        },
        "org_background": {
            "id": "org_background",
            "title": "Organization Background & Capacity",
            "target_length": "300–500 words",
            "description": "Mission, history, leadership, key accomplishments, and infrastructure that prove you can deliver.",
            "placeholder": "Describe your organization's mission, history, leadership team, key accomplishments, and capacity to deliver this project..."
        },
        "need_statement": {
            "id": "need_statement",
            "title": "Statement of Need / Problem Analysis",
            "target_length": "400–600 words",
            "description": "Data-rich justification for why the project matters. Include quantitative evidence and community voices.",
            "placeholder": "Describe the problem or need your project addresses. Include data, statistics, and community input to justify the urgency..."
        },
        "project_design": {
            "id": "project_design",
            "title": "Project/Program Design & Objectives",
            "target_length": "600–800 words",
            "description": "The 'how.' Break into SMART objectives, activities, timelines, staffing, and partnerships.",
            "placeholder": "Detail your project design, SMART objectives, activities, timeline, staffing plan, and key partnerships..."
        },
        "evaluation_plan": {
            "id": "evaluation_plan",
            "title": "Evaluation & Impact Measurement",
            "target_length": "300–500 words",
            "description": "Outcomes, KPIs, data-collection methods, and reporting cadence.",
            "placeholder": "Describe your evaluation plan, key performance indicators, data collection methods, and reporting schedule..."
        },
        "budget_sustainability": {
            "id": "budget_sustainability",
            "title": "Budget & Sustainability Plan",
            "target_length": "250–400 words",
            "description": "Itemized budget, justification notes, and post-grant funding strategy.",
            "placeholder": "Provide your detailed budget breakdown, cost justifications, and sustainability plan for post-grant funding..."
        }
    }
    
    def __init__(self):
        self.documents: Dict[str, GrantDocument] = {}
    
    def create_grant_document(self, project_id: str) -> GrantDocument:
        """Create a new grant document with all six sections."""
        sections = {}
        for section_id, section_info in self.CORE_SECTIONS.items():
            sections[section_id] = GrantSection(
                id=section_id,
                title=section_info["title"],
                content=section_info["placeholder"],
                target_length=section_info["target_length"]
            )
        
        document = GrantDocument(
            project_id=project_id,
            sections=sections,
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat()
        )
        
        self.documents[project_id] = document
        return document
    
    def get_grant_document(self, project_id: str) -> Optional[GrantDocument]:
        """Get an existing grant document."""
        return self.documents.get(project_id)
    
    def update_section(self, project_id: str, section_id: str, content: str) -> Dict[str, Any]:
        """Update a section and return the updated document state."""
        document = self.get_grant_document(project_id)
        if not document:
            document = self.create_grant_document(project_id)
        
        document.update_section(section_id, content)
        
        return {
            "doc_state": {section_id: section.content for section_id, section in document.sections.items()},
            "delta_note": f"Updated {document.sections[section_id].title}",
            "section_updated": section_id,
            "word_count": document.sections[section_id].word_count,
            "status": document.sections[section_id].status
        }
    
    def regenerate_section(self, project_id: str, section_id: str, context: str) -> Dict[str, Any]:
        """Regenerate a section based on context."""
        # This would integrate with OpenAI to regenerate content
        # For now, return the current state
        document = self.get_grant_document(project_id)
        if document:
            return {
                "doc_state": {section_id: section.content for section_id, section in document.sections.items()},
                "delta_note": f"Regenerated {document.sections[section_id].title}",
                "section_updated": section_id
            }
        return {}
    
    def export_to_markdown(self, project_id: str) -> str:
        """Export grant document to markdown format."""
        document = self.get_grant_document(project_id)
        if not document:
            return ""
        
        markdown_content = f"# Grant Application\n\n"
        markdown_content += f"**Project ID:** {project_id}\n"
        markdown_content += f"**Last Updated:** {document.last_updated}\n"
        markdown_content += f"**Total Word Count:** {document.total_word_count}\n\n"
        
        for section_id, section in document.sections.items():
            markdown_content += f"## {section.title}\n\n"
            markdown_content += f"*Target Length: {section.target_length}*\n\n"
            markdown_content += f"{section.content}\n\n"
            markdown_content += f"---\n\n"
        
        return markdown_content
    
    def export_to_docx(self, project_id: str) -> bytes:
        """Export grant document to DOCX format."""
        # This would use python-docx to create a Word document
        # For now, return markdown as placeholder
        markdown_content = self.export_to_markdown(project_id)
        return markdown_content.encode('utf-8')
    
    def get_section_templates(self) -> Dict[str, Any]:
        """Get section templates for UI initialization."""
        return {
            "sections": self.CORE_SECTIONS,
            "total_sections": len(self.CORE_SECTIONS)
        }
    
    def get_document_stats(self, project_id: str) -> Dict[str, Any]:
        """Get document statistics."""
        document = self.get_grant_document(project_id)
        if not document:
            return {}
        
        section_stats = {}
        for section_id, section in document.sections.items():
            section_stats[section_id] = {
                "title": section.title,
                "word_count": section.word_count,
                "target_length": section.target_length,
                "status": section.status,
                "last_updated": section.last_updated
            }
        
        return {
            "project_id": project_id,
            "total_word_count": document.total_word_count,
            "sections": section_stats,
            "completion_percentage": self._calculate_completion(document),
            "last_updated": document.last_updated
        }
    
    def _calculate_completion(self, document: GrantDocument) -> float:
        """Calculate document completion percentage."""
        completed_sections = sum(1 for section in document.sections.values() if section.status == "complete")
        return (completed_sections / len(document.sections)) * 100

# Global instance
grant_section_manager = GrantSectionManager() 