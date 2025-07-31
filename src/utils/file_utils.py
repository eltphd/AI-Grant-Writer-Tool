"""File utilities for the AI Grant Writer tool.

This module provides functions for handling file uploads, text extraction,
and context management for personalized AI responses.
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
import PyPDF2
import docx
from pathlib import Path

# Create uploads directory if it doesn't exist
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

# Create context storage directory
CONTEXT_DIR = Path("context")
CONTEXT_DIR.mkdir(exist_ok=True)

# Create chat history storage directory
CHAT_DIR = Path("chat_history")
CHAT_DIR.mkdir(exist_ok=True)

def save_uploaded_file(file_content: bytes, filename: str, project_id: str) -> Dict[str, Any]:
    """Save an uploaded file and extract its text content.
    
    Args:
        file_content: The file content as bytes
        filename: Original filename
        project_id: Project ID for organization
        
    Returns:
        Dictionary with file info and extracted text
    """
    try:
        # Create project directory
        project_dir = UPLOADS_DIR / project_id
        project_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        file_hash = hashlib.md5(file_content).hexdigest()
        file_ext = Path(filename).suffix.lower()
        unique_filename = f"{file_hash}{file_ext}"
        file_path = project_dir / unique_filename
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Extract text based on file type
        extracted_text = extract_text_from_file(file_path, file_ext)
        
        # Save context
        context_data = {
            "filename": filename,
            "file_path": str(file_path),
            "file_hash": file_hash,
            "project_id": project_id,
            "uploaded_at": datetime.now().isoformat(),
            "extracted_text": extracted_text,
            "file_size": len(file_content),
            "file_type": file_ext
        }
        
        save_context(project_id, context_data)
        
        return {
            "success": True,
            "filename": filename,
            "file_hash": file_hash,
            "extracted_text_length": len(extracted_text),
            "uploaded_at": context_data["uploaded_at"]
        }
        
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return {"success": False, "error": str(e)}

def extract_text_from_file(file_path: Path, file_ext: str) -> str:
    """Extract text content from various file types.
    
    Args:
        file_path: Path to the file
        file_ext: File extension
        
    Returns:
        Extracted text content
    """
    try:
        if file_ext == ".pdf":
            return extract_pdf_text(file_path)
        elif file_ext in [".docx", ".doc"]:
            return extract_docx_text(file_path)
        elif file_ext in [".txt", ".md"]:
            return extract_txt_text(file_path)
        else:
            return f"Unsupported file type: {file_ext}"
            
    except Exception as e:
        print(f"❌ Error extracting text from {file_path}: {e}")
        return f"Error extracting text: {str(e)}"

def extract_pdf_text(file_path: Path) -> str:
    """Extract text from PDF file."""
    try:
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_docx_text(file_path: Path) -> str:
    """Extract text from DOCX file."""
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def extract_txt_text(file_path: Path) -> str:
    """Extract text from TXT file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        return f"Error reading text file: {str(e)}"

def save_context(project_id: str, context_data: Dict[str, Any]) -> bool:
    """Save context data for a project.
    
    Args:
        project_id: Project ID
        context_data: Context data to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        context_file = CONTEXT_DIR / f"{project_id}_context.json"
        
        # Load existing context or create new
        if context_file.exists():
            with open(context_file, "r") as f:
                context = json.load(f)
        else:
            context = {
                "project_id": project_id,
                "files": [],
                "organization_info": "",
                "initiative_description": "",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        
        # Add new file context
        context["files"].append(context_data)
        context["updated_at"] = datetime.now().isoformat()
        
        # Save updated context
        with open(context_file, "w") as f:
            json.dump(context, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving context: {e}")
        return False

def get_project_context(project_id: str) -> Dict[str, Any]:
    """Get all context data for a project.
    
    Args:
        project_id: Project ID
        
    Returns:
        Dictionary with project context
    """
    try:
        context_file = CONTEXT_DIR / f"{project_id}_context.json"
        
        if context_file.exists():
            with open(context_file, "r") as f:
                return json.load(f)
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
    """Update project information.
    
    Args:
        project_id: Project ID
        organization_info: Organization description
        initiative_description: Initiative description
        
    Returns:
        True if successful, False otherwise
    """
    try:
        context = get_project_context(project_id)
        
        if organization_info:
            context["organization_info"] = organization_info
        if initiative_description:
            context["initiative_description"] = initiative_description
            
        context["updated_at"] = datetime.now().isoformat()
        
        context_file = CONTEXT_DIR / f"{project_id}_context.json"
        with open(context_file, "w") as f:
            json.dump(context, f, indent=2)
        
        return True
        
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
    """Delete all context data for a project.
    
    Args:
        project_id: Project ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Delete context file
        context_file = CONTEXT_DIR / f"{project_id}_context.json"
        if context_file.exists():
            context_file.unlink()
        
        # Delete uploaded files
        project_dir = UPLOADS_DIR / project_id
        if project_dir.exists():
            for file_path in project_dir.iterdir():
                file_path.unlink()
            project_dir.rmdir()
        
        return True
        
    except Exception as e:
        print(f"❌ Error deleting context: {e}")
        return False 

def save_chat_message(project_id: str, conversation_data: Dict[str, Any]) -> bool:
    """Save a chat message for RAG context.
    
    Args:
        project_id: Project ID
        conversation_data: Dictionary with user_message, ai_response, and timestamp
        
    Returns:
        True if successful, False otherwise
    """
    try:
        chat_file = CHAT_DIR / f"{project_id}_chat.json"
        
        # Load existing chat history or create new
        if chat_file.exists():
            with open(chat_file, "r") as f:
                chat_history = json.load(f)
        else:
            chat_history = {
                "project_id": project_id,
                "messages": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        
        # Add new message
        chat_history["messages"].append(conversation_data)
        chat_history["updated_at"] = datetime.now().isoformat()
        
        # Keep only last 50 messages to prevent file from getting too large
        if len(chat_history["messages"]) > 50:
            chat_history["messages"] = chat_history["messages"][-50:]
        
        # Save updated chat history
        with open(chat_file, "w") as f:
            json.dump(chat_history, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving chat message: {e}")
        return False

def get_chat_history(project_id: str) -> str:
    """Get chat history for RAG context.
    
    Args:
        project_id: Project ID
        
    Returns:
        Formatted chat history string
    """
    try:
        chat_file = CHAT_DIR / f"{project_id}_chat.json"
        
        if chat_file.exists():
            with open(chat_file, "r") as f:
                chat_history = json.load(f)
            
            # Format recent messages for context
            recent_messages = chat_history.get("messages", [])[-10:]  # Last 10 messages
            
            formatted_history = []
            for msg in recent_messages:
                user_msg = msg.get("user_message", "")
                ai_msg = msg.get("ai_response", "")
                if user_msg and ai_msg:
                    formatted_history.append(f"User: {user_msg}\nAI: {ai_msg}")
            
            return "\n\n".join(formatted_history) if formatted_history else ""
        else:
            return ""
            
    except Exception as e:
        print(f"❌ Error loading chat history: {e}")
        return ""

def get_chat_messages(project_id: str) -> List[Dict[str, Any]]:
    """Get all chat messages for a project.
    
    Args:
        project_id: Project ID
        
    Returns:
        List of chat messages
    """
    try:
        chat_file = CHAT_DIR / f"{project_id}_chat.json"
        
        if chat_file.exists():
            with open(chat_file, "r") as f:
                chat_history = json.load(f)
            return chat_history.get("messages", [])
        else:
            return []
            
    except Exception as e:
        print(f"❌ Error loading chat messages: {e}")
        return []

def delete_chat_history(project_id: str) -> bool:
    """Delete chat history for a project.
    
    Args:
        project_id: Project ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        chat_file = CHAT_DIR / f"{project_id}_chat.json"
        if chat_file.exists():
            chat_file.unlink()
        return True
        
    except Exception as e:
        print(f"❌ Error deleting chat history: {e}")
        return False 