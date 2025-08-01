
"""Utility functions for interacting with a Supabase backend via its REST API.

This module provides a drop‑in replacement for pgvector_utils when the
application is configured to talk to Supabase instead of a local
PostgreSQL database.  It uses the Supabase HTTP endpoints exposed via
PostgREST to perform basic CRUD operations.  Vector search (used for
Retrieval‑Augmented Generation) is not implemented here because the
Supabase REST API does not currently expose pgvector operators via HTTP.

Operations implemented include inserting and updating clients, projects,
files, file chunks, and questions.  Each function returns simple Python
objects (or True/False for writes) and should raise no exceptions — errors are logged and
rolled back internally.
"""

from __future__ import annotations

import json
import os
from typing import Any, Iterable, Optional, Dict, List

import requests
from openai import OpenAI

# Load Supabase configuration from config.py.  We import lazily to avoid
# circular dependencies when the FastAPI app determines which util module
# to use.  Relative import is attempted first for local execution and
# falls back to absolute import when running under the src package.
try:
    from src.utils import config  # type: ignore
except Exception:
    import config  # type: ignore

def get_openai_client() -> OpenAI:
    """Return an OpenAI client, caching it for future use."""
    if not getattr(get_openai_client, "client", None):
        openai_key = getattr(config, "OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise RuntimeError("OPENAI_API_KEY not configured in environment variables or config.py")
        get_openai_client.client = OpenAI(api_key=openai_key)  # type: ignore
    return get_openai_client.client  # type: ignore


def create_embeddings(chunks: list[str]) -> list[list[float]]:
    """Create embeddings for a list of text chunks using OpenAI."""
    client = get_openai_client()
    response = client.embeddings.create(model="text-embedding-ada-002", input=chunks)
    return [embedding.embedding for embedding in response.data]


def _build_headers() -> dict[str, str]:
    """Construct the headers required for Supabase REST requests."""
    return {
        "apikey": config.SUPABASE_KEY,
        "Authorization": f"Bearer {config.SUPABASE_KEY}",
        "Content-Type": "application/json",
    }


def _request(method: str, path: str, **kwargs: Any) -> Optional[Any]:
    """Helper to make an HTTP request to the Supabase REST API.

    Args:
        method: The HTTP method (GET, POST, PATCH, DELETE).
        path: The path to append to the base Supabase URL (should start
            with "/rest/v1/").
        kwargs: Additional arguments passed through to requests.request().

    Returns:
        The parsed JSON response if successful, or or the response text if not JSON, or None on error.
    """
    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        print("Supabase configuration missing; cannot perform request")
        return None
    url = config.SUPABASE_URL.rstrip("/") + path
    headers = _build_headers()
    # Merge custom headers but allow caller to override defaults
    custom_headers = kwargs.pop("headers", {})
    headers.update(custom_headers)
    try:
        response = requests.request(method, url, headers=headers, **kwargs)
        # 2xx responses indicate success
        if response.ok:
            # Return JSON if present; some operations (insert) may return
            # an empty body when Prefer=return=minimal is used.
            if response.text:
                try:
                    return response.json()
                except Exception:
                    return response.text
            return True
        else:
            # Print the error for debugging
            print(f"Supabase request failed: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"Supabase request exception: {e}")
        return None


# ---------------------------------------------------------------------------
# CRUD Functions
# ---------------------------------------------------------------------------

def query_data(table_name: str) -> Optional[Any]:
    """Return all rows from the specified table via Supabase REST API.

    Args:
        table_name: The name of the table to query.

    Returns:
        A list of rows (dictionaries) or None if an error occurred.
    """
    return _request("GET", f"/rest/v1/{table_name}?select=*")


def query_questions(project_id: str) -> Optional[Any]:
    """Return all question records for a given project ID via Supabase."""
    return _request(
        "GET",
        f"/rest/v1/questions?project_id=eq.{project_id}&select=*",
    )


def insert_file(filename: str) -> bool:
    """Insert a file record into the files table."""
    data = {"file_name": filename}
    # Prefer return=representation so we get the inserted row back
    res = _request(
        "POST",
        "/rest/v1/files",
        json=data,
        headers={"Prefer": "return=representation"},
    )
    return bool(res)


def insert_project(project_name: str, project_description: str, client_id: int | None = None) -> bool:
    """Insert a new project into the projects table."""
    data: dict[str, Any] = {
        "name": project_name,
        "description": project_description,
    }
    if client_id is not None:
        data["client_id"] = client_id
    res = _request(
        "POST",
        "/rest/v1/projects",
        json=data,
        headers={"Prefer": "return=representation"},
    )
    return bool(res)


def delete_questions_from_db(project_id: int) -> bool:
    """Remove all questions for the given project ID."""
    res = _request(
        "DELETE",
        f"/rest/v1/questions?project_id=eq.{project_id}",
    )
    # Supabase returns True on success when no body is returned
    return res is not None


def insert_questions_into_db(questions: Iterable[Any]) -> bool:
    """Insert a collection of question records into the questions table."""
    success = True
    for q in questions.questions:
        data = {
            "question": q.question,
            "answer": q.answer,
            "project_id": q.project_id,
            "embedding": q.embedding,
            "chat_history": q.chat_history,
        }
        res = _request(
            "POST",
            "/rest/v1/questions",
            json=data,
            headers={"Prefer": "return=representation"},
        )
        if res is None:
            success = False
    return success


def save_questions(project_id: int, questions: Any) -> bool:
    """Replace all questions for a project with the provided list."""
    if delete_questions_from_db(project_id):
        return insert_questions_into_db(questions)
    return False


def insert_file_chunks_into_db(chunks: Iterable[tuple[str, str]]) -> Optional[int]:
    """Insert file chunks and embeddings into the file_chunks table.
    Returns the ID of the inserted chunk.
    """
    # Create embeddings for all chunks in one go
    chunk_texts = [chunk_text for _, chunk_text in chunks]
    embeddings = create_embeddings(chunk_texts)

    # Supabase PostgREST can insert multiple rows at once if the data is a list of objects
    data_to_insert = []
    for i, (file_name, chunk_text) in enumerate(chunks):
        data_to_insert.append({
            "file_name": file_name,
            "chunk_text": chunk_text,
            "embedding": embeddings[i],
        })
    
    res = _request(
        "POST",
        "/rest/v1/file_chunks",
        json=data_to_insert,
        headers={"Prefer": "return=representation"},
    )
    
    if res and isinstance(res, list) and len(res) > 0:
        # Assuming we only insert one chunk at a time for now, return its ID
        return res[0].get("id")
    return None


def insert_client(client: Any) -> bool:
    """Insert a new client into the clients table."""
    data = {
        "name": client.name,
        "organization": client.organization,
        "contact_info": client.contact_info,
        "demographics": client.demographics,
        "goals": client.goals,
    }
    res = _request(
        "POST",
        "/rest/v1/clients",
        json=data,
        headers={"Prefer": "return=representation"},
    )
    return bool(res)


def update_client(client_id: int, client: Any) -> bool:
    """Update an existing client's details."""
    # Build a dict of only the provided fields
    data: dict[str, Any] = {}
    if getattr(client, "name", None):
        data["name"] = client.name
    if getattr(client, "organization", None):
        data["organization"] = client.organization
    if getattr(client, "contact_info", None):
        data["contact_info"] = client.contact_info
    if getattr(client, "demographics", None):
        data["demographics"] = client.demographics
    if getattr(client, "goals", None):
        data["goals"] = client.goals
    if not data:
        return True  # nothing to update
    res = _request(
        "PATCH",
        f"/rest/v1/clients?id=eq.{client_id}",
        json=data,
        headers={"Prefer": "return=representation"},
    )
    return bool(res)


def rag_context(question: str, files: list[str]) -> Optional[str]:
    """Return the best matching context chunk for a question.

    This function now calls a Supabase Edge Function to perform the vector search.
    """
    try:
        response = _request(
            "POST",
            f"/functions/v1/rag_context",
            json={"query": question, "files": files},
        )
        if response and isinstance(response, list) and len(response) > 0:
            return response[0].get("chunk_text")
        return None
    except Exception as e:
        print(f"Error calling rag_context Edge Function: {e}")
        return None

# ---------------------------------------------------------------------------
# Chat History Functions for RAG
# ---------------------------------------------------------------------------

def save_chat_message(project_id: str, conversation_data: dict[str, Any]) -> bool:
    """Save a chat message for RAG context.
    
    Args:
        project_id: Project ID
        conversation_data: Dictionary with user_message, ai_response, and timestamp
        
    Returns:
        True if successful, False otherwise
    """
    data = {
        "project_id": project_id,
        "user_message": conversation_data.get("user_message", ""),
        "ai_response": conversation_data.get("ai_response", ""),
        "timestamp": conversation_data.get("timestamp"),
        "message_type": conversation_data.get("message_type", "chat"),
        "metadata": conversation_data.get("metadata", {})
    }
    
    res = _request(
        "POST",
        "/rest/v1/chat_messages",
        json=data,
        headers={"Prefer": "return=representation"},
    )
    return bool(res)

def get_chat_history(project_id: str) -> str:
    """Get chat history for RAG context.
    
    Args:
        project_id: Project ID
        
    Returns:
        Formatted chat history string
    """
    # Get last 10 messages for context
    res = _request(
        "GET",
        f"/rest/v1/chat_messages?project_id=eq.{project_id}&order=timestamp.desc&limit=10&select=user_message,ai_response"
    )
    
    if not res:
        return ""
    
    # Format messages for context
    formatted_history = []
    for msg in reversed(res):  # Reverse to get chronological order
        user_msg = msg.get("user_message", "")
        ai_msg = msg.get("ai_response", "")
        if user_msg and ai_msg:
            formatted_history.append(f"User: {user_msg}\nAI: {ai_msg}")
    
    return "\n\n".join(formatted_history)

def get_chat_messages(project_id: str) -> list[dict[str, Any]]:
    """Get all chat messages for a project.
    
    Args:
        project_id: Project ID
        
    Returns:
        List of chat messages
    """
    res = _request(
        "GET",
        f"/rest/v1/chat_messages?project_id=eq.{project_id}&order=timestamp.asc&select=*"
    )
    
    if not res:
        return []
    
    return res

def delete_chat_history(project_id: str) -> bool:
    """Delete chat history for a project.
    
    Args:
        project_id: Project ID
        
    Returns:
        True if successful, False otherwise
    """
    res = _request(
        "DELETE",
        f"/rest/v1/chat_messages?project_id=eq.{project_id}"
    )
    return res is not None

# ---------------------------------------------------------------------------
# File and Context Management Functions
# ---------------------------------------------------------------------------

def save_uploaded_file(file_content: bytes, filename: str, project_id: str) -> dict[str, Any]:
    """Save an uploaded file to Supabase.
    
    Args:
        file_content: The file content as bytes
        filename: Original filename
        project_id: Project ID for organization
        
    Returns:
        Dictionary with file info and extracted text
    """
    try:
        # For now, we'll store basic file info
        # In a full implementation, you'd want to store the file content
        # in Supabase Storage and reference it here
        data = {
            "filename": filename,
            "project_id": project_id,
            "file_size": len(file_content),
            "file_type": filename.split('.')[-1].lower() if '.' in filename else "unknown"
        }
        
        res = _request(
            "POST",
            "/rest/v1/files",
            json=data,
            headers={"Prefer": "return=representation"},
        )
        
        if res:
            return {
                "success": True,
                "filename": filename,
                "file_size": len(file_content),
                "uploaded_at": res.get("created_at")
            }
        else:
            return {"success": False, "error": "Failed to save file"}
            
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return {"success": False, "error": str(e)}

def insert_secure_data(file_chunk_id: int, original_text: str, redactions: list) -> Optional[int]:
    """Insert sensitive data into the secure_storage table.
    Returns the ID of the inserted secure data record.
    """
    data = {
        "file_chunk_id": file_chunk_id,
        "original_text": original_text,
        "redactions": redactions,
    }
    res = _request(
        "POST",
        "/rest/v1/secure_storage",
        json=data,
        headers={"Prefer": "return=representation"},
    )
    if res and isinstance(res, list) and len(res) > 0:
        return res[0].get("id")
    return None


def get_project_context(project_id: str) -> dict[str, Any]:
    """Get all context data for a project from Supabase.
    
    Args:
        project_id: Project ID
        
    Returns:
        Dictionary with project context
    """
    res = _request(
        "GET",
        f"/rest/v1/project_contexts?project_id=eq.{project_id}&select=*"
    )
    
    if res and len(res) > 0:
        context = res[0]
        return {
            "project_id": context.get("project_id"),
            "organization_info": context.get("organization_info", ""),
            "initiative_description": context.get("initiative_description", ""),
            "created_at": context.get("created_at"),
            "updated_at": context.get("updated_at"),
            "files": []  # Would need separate query for files
        }
    else:
        return {
            "project_id": project_id,
            "organization_info": "",
            "initiative_description": "",
            "created_at": None,
            "updated_at": None,
            "files": []
        }

def update_project_info(project_id: str, organization_info: str = "", initiative_description: str = "") -> bool:
    """Update project information in Supabase.
    
    Args:
        project_id: Project ID
        organization_info: Organization description
        initiative_description: Initiative description
        
    Returns:
        True if successful, False otherwise
    """
    data = {
        "organization_info": organization_info,
        "initiative_description": initiative_description,
        "updated_at": "now()"
    }
    
    res = _request(
        "PATCH",
        f"/rest/v1/project_contexts?project_id=eq.{project_id}",
        json=data,
        headers={"Prefer": "return=representation"},
    )
    
    if not res:
        # Try to create new record if update failed
        data["project_id"] = project_id
        res = _request(
            "POST",
            "/rest/v1/project_contexts",
            json=data,
            headers={"Prefer": "return=representation"},
        )
    
    return bool(res)

def get_context_summary(project_id: str) -> str:
    """Get a summary of project context for AI prompts.
    
    Args:
        project_id: Project ID
        
    Returns:
        Formatted context summary
    """
    context = get_project_context(project_id)
    
    summary_parts = []
    
    # Add organization info
    if context.get("organization_info"):
        summary_parts.append(f"Organization Information: {context['organization_info']}")
    
    # Add initiative description
    if context.get("initiative_description"):
        summary_parts.append(f"Initiative Description: {context['initiative_description']}")
    
    return "\n\n".join(summary_parts) if summary_parts else "No context available."

def delete_project_context(project_id: str) -> bool:
    """Delete all context data for a project from Supabase.
    
    Args:
        project_id: Project ID
        
    Returns:
        True if successful, False otherwise
    """
    # Delete project context
    context_res = _request(
        "DELETE",
        f"/rest/v1/project_contexts?project_id=eq.{project_id}"
    )
    
    # Delete files
    files_res = _request(
        "DELETE",
        f"/rest/v1/files?project_id=eq.{project_id}"
    )
    
    # Delete chat messages
    chat_res = _request(
        "DELETE",
        f"/rest/v1/chat_messages?project_id=eq.{project_id}"
    )
    
    return context_res is not None and files_res is not None and chat_res is not None

# Project management functions
def get_all_projects() -> list[dict[str, Any]]:
    """Get all projects from Supabase."""
    try:
        # Get all files grouped by project_id
        res = _request(
            "GET",
            "/rest/v1/files?select=project_id,created_at&order=created_at.desc"
        )
        
        if not res:
            return []
        
        # Group by project_id and get the latest activity
        projects = {}
        for file_data in res:
            project_id = file_data.get("project_id")
            if project_id:
                if project_id not in projects:
                    projects[project_id] = {
                        "id": project_id,
                        "name": f"Project {project_id[:8]}",
                        "description": "Project with uploaded files",
                        "created_at": file_data.get("created_at"),
                        "updated_at": file_data.get("created_at"),
                        "file_count": 1
                    }
                else:
                    projects[project_id]["file_count"] += 1
        
        return list(projects.values())
    except Exception as e:
        print(f"❌ Error getting all projects: {e}")
        return []

def create_project(project_data: dict[str, Any]) -> dict[str, Any]:
    """Create a new project in Supabase."""
    try:
        # Create a placeholder file to establish the project
        placeholder_content = b"Project created"
        file_info = {
            "filename": "project_created.txt",
            "file_size": len(placeholder_content),
            "content_type": "text/plain",
            "project_id": project_data["id"]
        }
        
        result = save_uploaded_file(placeholder_content, file_info["filename"], project_data["id"])
        
        if result["success"]:
            return {
                "id": project_data["id"],
                "name": project_data.get("name", f"Project {project_data['id'][:8]}"),
                "description": project_data.get("description", "New project"),
                "created_at": project_data.get("created_at"),
                "updated_at": project_data.get("updated_at")
            }
        else:
            return None
    except Exception as e:
        print(f"❌ Error creating project: {e}")
        return None

def get_project(project_id: str) -> Optional[dict[str, Any]]:
    """Get a specific project from Supabase."""
    try:
        # Get files for this project
        res = _request(
            "GET",
            f"/rest/v1/files?project_id=eq.{project_id}&select=*&order=created_at.desc"
        )
        
        if res and len(res) > 0:
            latest_file = res[0]
            file_count = len(res)
            
            return {
                "id": project_id,
                "name": f"Project {project_id[:8]}",
                "description": f"Project with {file_count} files",
                "created_at": latest_file.get("created_at"),
                "updated_at": latest_file.get("created_at"),
                "file_count": file_count
            }
        return None
    except Exception as e:
        print(f"❌ Error getting project: {e}")
        return None

def delete_project(project_id: str) -> bool:
    """Delete a project and all its data from Supabase."""
    try:
        # Delete all data associated with the project
        context_res = _request(
            "DELETE",
            f"/rest/v1/project_contexts?project_id=eq.{project_id}"
        )
        
        files_res = _request(
            "DELETE",
            f"/rest/v1/files?project_id=eq.{project_id}"
        )
        
        chat_res = _request(
            "DELETE",
            f"/rest/v1/chat_messages?project_id=eq.{project_id}"
        )
        
        # Note: embeddings and redactions tables might not exist in Supabase
        # so we'll skip those for now
        
        return context_res is not None and files_res is not None and chat_res is not None
    except Exception as e:
        print(f"❌ Error deleting project: {e}")
        return False

# New functions for storage_utils integration
def insert_organization(org_data: Dict[str, Any]) -> bool:
    """Insert organization data into the 'organizations' table."""
    res = _request(
        "POST",
        "/rest/v1/organizations",
        json=org_data,
        headers={"Prefer": "return=representation"},
    )
    return bool(res)

def get_organization(org_id: str) -> Optional[Dict[str, Any]]:
    """Get organization data from the 'organizations' table."""
    res = _request(
        "GET",
        f"/rest/v1/organizations?id=eq.{org_id}&select=*",
    )
    if res and isinstance(res, list) and len(res) > 0:
        return res[0]
    return None

def insert_rfp(rfp_data: Dict[str, Any]) -> bool:
    """Insert RFP data into the 'rfp_documents' table."""
    res = _request(
        "POST",
        "/rest/v1/rfp_documents",
        json=rfp_data,
        headers={"Prefer": "return=representation"},
    )
    return bool(res)

def get_rfp(rfp_id: str) -> Optional[Dict[str, Any]]:
    """Get RFP data from the 'rfp_documents' table."""
    res = _request(
        "GET",
        f"/rest/v1/rfp_documents?id=eq.{rfp_id}&select=*",
    )
    if res and isinstance(res, list) and len(res) > 0:
        return res[0]
    return None

def insert_project_response(response_data: Dict[str, Any]) -> bool:
    """Insert project response data into the 'project_responses' table."""
    res = _request(
        "POST",
        "/rest/v1/project_responses",
        json=response_data,
        headers={"Prefer": "return=representation"},
    )
    return bool(res)

def get_project_response(response_id: str) -> Optional[Dict[str, Any]]:
    """Get project response data from the 'project_responses' table."""
    res = _request(
        "GET",
        f"/rest/v1/project_responses?id=eq.{response_id}&select=*",
    )
    if res and isinstance(res, list) and len(res) > 0:
        return res[0]
    return None

def get_all_projects_from_db() -> List[Dict[str, Any]]:
    """Get all projects from the 'projects' table."""
    res = _request(
        "GET",
        "/rest/v1/projects?select=*",
    )
    if res and isinstance(res, list):
        return res
    return []
