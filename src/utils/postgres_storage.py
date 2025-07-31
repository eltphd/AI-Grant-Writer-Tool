"""PostgreSQL storage utilities for the AI Grant Writer tool.

This module provides functions for storing files and context data in PostgreSQL,
which is more reliable than local file storage on Railway.
"""

import os
import json
import hashlib
import psycopg2
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Import config
try:
    from . import config
except ImportError:
    import config

def get_db_connection():
    """Get a database connection."""
    try:
        conn = psycopg2.connect(
            host=config.DB_HOSTNAME,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

def init_database():
    """Initialize database tables if they don't exist."""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Create files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id SERIAL PRIMARY KEY,
                filename TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                project_id TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                extracted_text TEXT,
                file_size INTEGER,
                file_type TEXT,
                file_content BYTEA
            )
        """)
        
        # Create project_contexts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_contexts (
                id SERIAL PRIMARY KEY,
                project_id TEXT UNIQUE NOT NULL,
                organization_info TEXT,
                initiative_description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create chat_messages table for RAG functionality
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id SERIAL PRIMARY KEY,
                project_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_type TEXT DEFAULT 'chat',
                metadata JSONB DEFAULT '{}'::jsonb
            )
        """)
        
        # Create embeddings table for future vector search
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id SERIAL PRIMARY KEY,
                project_id TEXT NOT NULL,
                content_type TEXT NOT NULL,
                content_id TEXT NOT NULL,
                embedding_vector VECTOR(1536),
                content_text TEXT,
                metadata JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create redactions table for sensitive data management
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS redactions (
                id SERIAL PRIMARY KEY,
                project_id TEXT NOT NULL,
                file_id INTEGER REFERENCES files(id),
                original_text TEXT NOT NULL,
                redacted_text TEXT NOT NULL,
                redaction_type TEXT NOT NULL,
                confidence_score FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_project_id ON files(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_project_id ON chat_messages(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_embeddings_project_id ON embeddings(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_redactions_project_id ON redactions(project_id)")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database tables initialized")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        return False

def save_uploaded_file(file_content: bytes, filename: str, project_id: str) -> Dict[str, Any]:
    """Save an uploaded file to PostgreSQL and extract text content.
    
    Args:
        file_content: The file content as bytes
        filename: Original filename
        project_id: Project ID for organization
        
    Returns:
        Dictionary with file info and extracted text
    """
    try:
        # Initialize database if needed
        init_database()
        
        # Generate unique filename
        file_hash = hashlib.md5(file_content).hexdigest()
        file_ext = Path(filename).suffix.lower()
        unique_filename = f"{file_hash}{file_ext}"
        
        # Extract text content
        extracted_text = extract_text_from_bytes(file_content, file_ext)
        
        # Save to database
        conn = get_db_connection()
        if not conn:
            return {"success": False, "error": "Database connection failed"}
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO files (filename, file_hash, project_id, extracted_text, file_size, file_type, file_content)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (filename, file_hash, project_id, extracted_text, len(file_content), file_ext, file_content))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "filename": filename,
            "file_hash": file_hash,
            "extracted_text_length": len(extracted_text),
            "uploaded_at": datetime.now().isoformat()
        }
        
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
    """Save context data to PostgreSQL.
    
    Args:
        project_id: Project ID
        context_data: Context data to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        init_database()
        conn = get_db_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Check if context exists
        cursor.execute("SELECT id FROM project_contexts WHERE project_id = %s", (project_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing context
            cursor.execute("""
                UPDATE project_contexts 
                SET organization_info = %s, initiative_description = %s, updated_at = CURRENT_TIMESTAMP
                WHERE project_id = %s
            """, (context_data.get('organization_info', ''), 
                  context_data.get('initiative_description', ''), project_id))
        else:
            # Create new context
            cursor.execute("""
                INSERT INTO project_contexts (project_id, organization_info, initiative_description)
                VALUES (%s, %s, %s)
            """, (project_id, context_data.get('organization_info', ''), 
                  context_data.get('initiative_description', '')))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error saving context: {e}")
        return False

def get_project_context(project_id: str) -> Dict[str, Any]:
    """Get all context data for a project from PostgreSQL.
    
    Args:
        project_id: Project ID
        
    Returns:
        Dictionary with project context
    """
    try:
        init_database()
        conn = get_db_connection()
        if not conn:
            return {"error": "Database connection failed"}
        
        cursor = conn.cursor()
        
        # Get project context
        cursor.execute("""
            SELECT project_id, organization_info, initiative_description, created_at, updated_at
            FROM project_contexts WHERE project_id = %s
        """, (project_id,))
        
        context_row = cursor.fetchone()
        
        # Get files for this project
        cursor.execute("""
            SELECT filename, file_hash, uploaded_at, extracted_text, file_size, file_type
            FROM files WHERE project_id = %s ORDER BY uploaded_at DESC
        """, (project_id,))
        
        files = []
        for row in cursor.fetchall():
            files.append({
                "filename": row[0],
                "file_hash": row[1],
                "uploaded_at": row[2].isoformat() if row[2] else None,
                "extracted_text": row[3],
                "file_size": row[4],
                "file_type": row[5]
            })
        
        cursor.close()
        conn.close()
        
        if context_row:
            return {
                "project_id": context_row[0],
                "organization_info": context_row[1] or "",
                "initiative_description": context_row[2] or "",
                "created_at": context_row[3].isoformat() if context_row[3] else None,
                "updated_at": context_row[4].isoformat() if context_row[4] else None,
                "files": files
            }
        else:
            return {
                "project_id": project_id,
                "organization_info": "",
                "initiative_description": "",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "files": files
            }
            
    except Exception as e:
        print(f"❌ Error loading context: {e}")
        return {"error": str(e)}

def update_project_info(project_id: str, organization_info: str = "", initiative_description: str = "") -> bool:
    """Update project information in PostgreSQL.
    
    Args:
        project_id: Project ID
        organization_info: Organization description
        initiative_description: Initiative description
        
    Returns:
        True if successful, False otherwise
    """
    try:
        init_database()
        conn = get_db_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Check if context exists
        cursor.execute("SELECT id FROM project_contexts WHERE project_id = %s", (project_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing context
            cursor.execute("""
                UPDATE project_contexts 
                SET organization_info = %s, initiative_description = %s, updated_at = CURRENT_TIMESTAMP
                WHERE project_id = %s
            """, (organization_info, initiative_description, project_id))
        else:
            # Create new context
            cursor.execute("""
                INSERT INTO project_contexts (project_id, organization_info, initiative_description)
                VALUES (%s, %s, %s)
            """, (project_id, organization_info, initiative_description))
        
        conn.commit()
        cursor.close()
        conn.close()
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
    """Delete all context data for a project from PostgreSQL.
    
    Args:
        project_id: Project ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        init_database()
        conn = get_db_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Delete files
        cursor.execute("DELETE FROM files WHERE project_id = %s", (project_id,))
        
        # Delete context
        cursor.execute("DELETE FROM project_contexts WHERE project_id = %s", (project_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
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
        init_database()
        conn = get_db_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO chat_messages (project_id, user_message, ai_response, timestamp, metadata)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            project_id,
            conversation_data.get("user_message", ""),
            conversation_data.get("ai_response", ""),
            conversation_data.get("timestamp", datetime.now().isoformat()),
            json.dumps(conversation_data.get("metadata", {}))
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
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
        init_database()
        conn = get_db_connection()
        if not conn:
            return ""
        
        cursor = conn.cursor()
        
        # Get last 10 messages for context
        cursor.execute("""
            SELECT user_message, ai_response 
            FROM chat_messages 
            WHERE project_id = %s 
            ORDER BY timestamp DESC 
            LIMIT 10
        """, (project_id,))
        
        messages = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Format messages for context
        formatted_history = []
        for user_msg, ai_msg in reversed(messages):  # Reverse to get chronological order
            if user_msg and ai_msg:
                formatted_history.append(f"User: {user_msg}\nAI: {ai_msg}")
        
        return "\n\n".join(formatted_history)
        
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
        init_database()
        conn = get_db_connection()
        if not conn:
            return []
        
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_message, ai_response, timestamp, message_type, metadata
            FROM chat_messages 
            WHERE project_id = %s 
            ORDER BY timestamp ASC
        """, (project_id,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                "user_message": row[0],
                "ai_response": row[1],
                "timestamp": row[2].isoformat() if row[2] else None,
                "message_type": row[3],
                "metadata": row[4] if row[4] else {}
            })
        
        cursor.close()
        conn.close()
        return messages
        
    except Exception as e:
        print(f"❌ Error loading chat messages: {e}")
        return []

def delete_chat_history(project_id: str) -> bool:
    """Delete all chat messages for a project."""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_messages WHERE project_id = %s", (project_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error deleting chat history: {e}")
        return False
    finally:
        conn.close()

# Project management functions
def get_all_projects() -> List[Dict[str, Any]]:
    """Get all projects."""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT project_id, 
                   MAX(created_at) as last_activity,
                   COUNT(*) as file_count
            FROM files 
            GROUP BY project_id
            ORDER BY last_activity DESC
        """)
        
        projects = []
        for row in cursor.fetchall():
            project_id, last_activity, file_count = row
            projects.append({
                "id": project_id,
                "name": f"Project {project_id[:8]}",
                "description": f"Project with {file_count} files",
                "created_at": last_activity,
                "updated_at": last_activity,
                "file_count": file_count
            })
        
        return projects
    except Exception as e:
        print(f"❌ Error getting all projects: {e}")
        return []
    finally:
        conn.close()

def create_project(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new project."""
    # For now, we'll create a project by saving a placeholder file
    # This ensures the project exists in the database
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
                "created_at": project_data.get("created_at", datetime.utcnow()),
                "updated_at": project_data.get("updated_at", datetime.utcnow())
            }
        else:
            return None
    except Exception as e:
        print(f"❌ Error creating project: {e}")
        return None

def get_project(project_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific project."""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT project_id, 
                   MAX(created_at) as last_activity,
                   COUNT(*) as file_count
            FROM files 
            WHERE project_id = %s
            GROUP BY project_id
        """, (project_id,))
        
        row = cursor.fetchone()
        if row:
            project_id, last_activity, file_count = row
            return {
                "id": project_id,
                "name": f"Project {project_id[:8]}",
                "description": f"Project with {file_count} files",
                "created_at": last_activity,
                "updated_at": last_activity,
                "file_count": file_count
            }
        return None
    except Exception as e:
        print(f"❌ Error getting project: {e}")
        return None
    finally:
        conn.close()

def delete_project(project_id: str) -> bool:
    """Delete a project and all its data."""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        # Delete all data associated with the project
        cursor.execute("DELETE FROM files WHERE project_id = %s", (project_id,))
        cursor.execute("DELETE FROM project_contexts WHERE project_id = %s", (project_id,))
        cursor.execute("DELETE FROM chat_messages WHERE project_id = %s", (project_id,))
        cursor.execute("DELETE FROM embeddings WHERE project_id = %s", (project_id,))
        cursor.execute("DELETE FROM redactions WHERE project_id = %s", (project_id,))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error deleting project: {e}")
        return False
    finally:
        conn.close() 