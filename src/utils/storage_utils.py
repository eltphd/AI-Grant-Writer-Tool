"""Storage utilities for the AI Grant Writer tool using Supabase.

This module provides functions for storing files and context data in Supabase,
which is much more reliable than local file storage on Railway.
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests
from pathlib import Path

# Import config
try:
    from . import config
except ImportError:
    import config

def _build_headers() -> dict[str, str]:
    """Construct the headers required for Supabase REST requests."""
    return {
        "apikey": config.SUPABASE_KEY,
        "Authorization": f"Bearer {config.SUPABASE_KEY}",
        "Content-Type": "application/json",
    }

def _request(method: str, path: str, **kwargs: Any) -> Optional[Any]:
    """Helper to make an HTTP request to the Supabase REST API."""
    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        print("❌ Supabase configuration missing; cannot perform request")
        return None
    
    url = config.SUPABASE_URL.rstrip("/") + path
    headers = _build_headers()
    custom_headers = kwargs.pop("headers", {})
    headers.update(custom_headers)
    
    try:
        response = requests.request(method, url, headers=headers, **kwargs)
        if response.ok:
            if response.text:
                try:
                    return response.json()
                except Exception:
                    return response.text
            return True
        else:
            print(f"❌ Supabase request failed: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"❌ Supabase request exception: {e}")
        return None

def save_uploaded_file(file_content: bytes, filename: str, project_id: str) -> Dict[str, Any]:
    """Save an uploaded file to Supabase storage and extract text content.
    
    Args:
        file_content: The file content as bytes
        filename: Original filename
        project_id: Project ID for organization
        
    Returns:
        Dictionary with file info and extracted text
    """
    try:
        # Generate unique filename
        file_hash = hashlib.md5(file_content).hexdigest()
        file_ext = Path(filename).suffix.lower()
        unique_filename = f"{file_hash}{file_ext}"
        
        # Extract text content
        extracted_text = extract_text_from_bytes(file_content, file_ext)
        
        # Save file metadata to Supabase
        file_data = {
            "filename": filename,
            "file_hash": file_hash,
            "project_id": project_id,
            "uploaded_at": datetime.now().isoformat(),
            "extracted_text": extracted_text,
            "file_size": len(file_content),
            "file_type": file_ext,
            "file_content": file_content.hex()  # Store as hex string
        }
        
        # Insert into files table
        result = _request("POST", "/rest/v1/files", json=file_data)
        
        if result:
            return {
                "success": True,
                "filename": filename,
                "file_hash": file_hash,
                "extracted_text_length": len(extracted_text),
                "uploaded_at": file_data["uploaded_at"]
            }
        else:
            return {"success": False, "error": "Failed to save file to database"}
        
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return {"success": False, "error": str(e)}

def extract_text_from_bytes(file_content: bytes, file_ext: str) -> str:
    """Extract text content from file bytes."""
    try:
        if file_ext == ".pdf":
            return extract_pdf_text_from_bytes(file_content)
        elif file_ext in [".docx", ".doc"]:
            return extract_docx_text_from_bytes(file_content)
        elif file_ext in [".txt", ".md"]:
            return file_content.decode('utf-8')
        else:
            return f"Unsupported file type: {file_ext}"
            
    except Exception as e:
        print(f"❌ Error extracting text: {e}")
        return f"Error extracting text: {str(e)}"

def extract_pdf_text_from_bytes(file_content: bytes) -> str:
    """Extract text from PDF bytes."""
    try:
        import PyPDF2
        from io import BytesIO
        
        pdf_file = BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_docx_text_from_bytes(file_content: bytes) -> str:
    """Extract text from DOCX bytes."""
    try:
        import docx
        from io import BytesIO
        
        doc_file = BytesIO(file_content)
        doc = docx.Document(doc_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def save_context(project_id: str, context_data: Dict[str, Any]) -> bool:
    """Save context data to Supabase.
    
    Args:
        project_id: Project ID
        context_data: Context data to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get existing context or create new
        existing_context = get_project_context(project_id)
        
        if existing_context.get("error"):
            # Create new context
            context_data["project_id"] = project_id
            context_data["created_at"] = datetime.now().isoformat()
            context_data["updated_at"] = datetime.now().isoformat()
            
            result = _request("POST", "/rest/v1/project_contexts", json=context_data)
        else:
            # Update existing context
            context_data["updated_at"] = datetime.now().isoformat()
            result = _request("PATCH", f"/rest/v1/project_contexts?project_id=eq.{project_id}", json=context_data)
        
        return result is not None
        
    except Exception as e:
        print(f"❌ Error saving context: {e}")
        return False

def get_project_context(project_id: str) -> Dict[str, Any]:
    """Get all context data for a project from Supabase.
    
    Args:
        project_id: Project ID
        
    Returns:
        Dictionary with project context
    """
    try:
        result = _request("GET", f"/rest/v1/project_contexts?project_id=eq.{project_id}")
        
        if result and isinstance(result, list) and len(result) > 0:
            return result[0]
        else:
            return {
                "project_id": project_id,
                "files": [],
                "organization_info": "",
                "initiative_description": "",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
    except Exception as e:
        print(f"❌ Error loading context: {e}")
        return {"error": str(e)}

def update_project_info(project_id: str, organization_info: str = "", initiative_description: str = "") -> bool:
    """Update project information in Supabase.
    
    Args:
        project_id: Project ID
        organization_info: Organization description
        initiative_description: Initiative description
        
    Returns:
        True if successful, False otherwise
    """
    try:
        context = get_project_context(project_id)
        
        if context.get("error"):
            # Create new context
            context_data = {
                "project_id": project_id,
                "organization_info": organization_info,
                "initiative_description": initiative_description,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            result = _request("POST", "/rest/v1/project_contexts", json=context_data)
        else:
            # Update existing context
            update_data = {
                "organization_info": organization_info,
                "initiative_description": initiative_description,
                "updated_at": datetime.now().isoformat()
            }
            result = _request("PATCH", f"/rest/v1/project_contexts?project_id=eq.{project_id}", json=update_data)
        
        return result is not None
        
    except Exception as e:
        print(f"❌ Error updating project info: {e}")
        return False

def get_context_summary(project_id: str) -> str:
    """Get a summary of project context for AI prompts.
    
    Args:
        project_id: Project ID
        
    Returns:
        Formatted context summary
    """
    try:
        context = get_project_context(project_id)
        
        if context.get("error"):
            return "Error retrieving context."
        
        summary_parts = []
        
        # Add organization info
        if context.get("organization_info"):
            summary_parts.append(f"Organization Information: {context['organization_info']}")
        
        # Add initiative description
        if context.get("initiative_description"):
            summary_parts.append(f"Initiative Description: {context['initiative_description']}")
        
        # Add file summaries
        if context.get("files"):
            summary_parts.append("Uploaded Documents:")
            for file_info in context["files"]:
                filename = file_info.get("filename", "Unknown")
                text_length = len(file_info.get("extracted_text", ""))
                summary_parts.append(f"- {filename} ({text_length} characters)")
        
        return "\n\n".join(summary_parts) if summary_parts else "No context available."
        
    except Exception as e:
        print(f"❌ Error getting context summary: {e}")
        return "Error retrieving context."

def delete_project_context(project_id: str) -> bool:
    """Delete all context data for a project from Supabase.
    
    Args:
        project_id: Project ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Delete context
        context_result = _request("DELETE", f"/rest/v1/project_contexts?project_id=eq.{project_id}")
        
        # Delete files
        files_result = _request("DELETE", f"/rest/v1/files?project_id=eq.{project_id}")
        
        return context_result is not None and files_result is not None
        
    except Exception as e:
        print(f"❌ Error deleting context: {e}")
        return False 