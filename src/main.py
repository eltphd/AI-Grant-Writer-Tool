import os
import sys
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.utils import file_utils, openai_utils, storage_utils, postgres_storage, supabase_utils, privacy_utils, embedding_utils, grant_sections, config

# Initialize FastAPI app
app = FastAPI(title="GWAT API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Project endpoints (no auth required)
@app.get("/projects")
async def get_projects():
    """Get all projects"""
    try:
        if config.USE_SUPABASE:
            projects = supabase_utils.get_all_projects()
        else:
            projects = postgres_storage.get_all_projects()
        
        return {"success": True, "projects": projects}
    except Exception as e:
        print(f"❌ Error getting projects: {e}")
        return {"success": False, "error": str(e)}

@app.post("/projects")
async def create_project(project_data: dict):
    """Create a new project"""
    try:
        project_data["id"] = str(uuid.uuid4())
        project_data["created_at"] = datetime.utcnow()
        project_data["updated_at"] = datetime.utcnow()
        
        if config.USE_SUPABASE:
            project = supabase_utils.create_project(project_data)
        else:
            project = postgres_storage.create_project(project_data)
        
        return {"success": True, "project": project}
    except Exception as e:
        print(f"❌ Error creating project: {e}")
        return {"success": False, "error": str(e)}

@app.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get a specific project"""
    try:
        if config.USE_SUPABASE:
            project = supabase_utils.get_project(project_id)
        else:
            project = postgres_storage.get_project(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        return {"success": True, "project": project}
    except Exception as e:
        print(f"❌ Error getting project: {e}")
        return {"success": False, "error": str(e)}

@app.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    try:
        if config.USE_SUPABASE:
            success = supabase_utils.delete_project(project_id)
        else:
            success = postgres_storage.delete_project(project_id)
        
        return {"success": success}
    except Exception as e:
        print(f"❌ Error deleting project: {e}")
        return {"success": False, "error": str(e)}

# File upload endpoint (no auth required)
@app.post("/upload")
async def upload_file(project_id: str, file: UploadFile):
    """Upload a file for a project"""
    try:
        # Verify project exists
        if config.USE_SUPABASE:
            project = supabase_utils.get_project(project_id)
        else:
            project = postgres_storage.get_project(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Process file upload
        file_content = await file.read()
        file_info = {
            "filename": file.filename,
            "file_size": len(file_content),
            "content_type": file.content_type,
            "project_id": project_id
        }
        
        # Save file and process
        if config.USE_SUPABASE:
            result = supabase_utils.save_file(file_info, file_content)
        else:
            result = file_utils.save_file(file_info, file_content)
        
        # Process for privacy and embeddings
        if result["success"]:
            # Privacy processing
            privacy_result = privacy_utils.privacy_manager.process_text_for_storage(
                result["text_content"], project_id
            )
            
            # Embedding processing
            embedding_result = embedding_utils.embedding_manager.create_embeddings_for_text(
                privacy_result["redacted_text"], project_id
            )
        
        return result
        
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return {"success": False, "error": str(e)}

# Chat endpoints (no auth required)
@app.post("/chat/send_message")
async def send_message(project_id: str, message: dict):
    """Send a chat message for a project"""
    try:
        # Verify project exists
        if config.USE_SUPABASE:
            project = supabase_utils.get_project(project_id)
        else:
            project = postgres_storage.get_project(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Save message
        message_data = {
            "project_id": project_id,
            "message": message.get("message", ""),
            "timestamp": datetime.utcnow(),
            "message_type": "user"
        }
        
        if config.USE_SUPABASE:
            supabase_utils.save_chat_message(message_data)
        else:
            postgres_storage.save_chat_message(message_data)
        
        # Get context for AI response
        project_context = ""
        if config.USE_SUPABASE:
            context_data = supabase_utils.get_project_context(project_id)
        else:
            context_data = postgres_storage.get_project_context(project_id)
        
        if context_data:
            if "organization_info" in context_data:
                project_context += f"Organization: {context_data['organization_info']}\n"
            if "initiative_description" in context_data:
                project_context += f"Initiative: {context_data['initiative_description']}"
        
        # Get chat history and semantic context
        if config.USE_SUPABASE:
            chat_history = supabase_utils.get_chat_history(project_id)
            semantic_context = embedding_utils.embedding_manager.create_context_for_ai(
                project_id, message.get("message", "")
            )
        else:
            chat_history = postgres_storage.get_chat_history(project_id)
            semantic_context = embedding_utils.embedding_manager.create_context_for_ai(
                project_id, message.get("message", "")
            )
        
        # Combine context for AI
        full_context = f"{project_context}\n\nChat History: {chat_history}\n\nSemantic Context: {semantic_context}"
        
        # Get AI response
        ai_response = openai_utils.chat_grant_assistant(
            message.get("message", ""), 
            project_id, 
            full_context
        )
        
        # Save AI response
        ai_message_data = {
            "project_id": project_id,
            "message": ai_response,
            "timestamp": datetime.utcnow(),
            "message_type": "ai"
        }
        
        if config.USE_SUPABASE:
            supabase_utils.save_chat_message(ai_message_data)
        else:
            postgres_storage.save_chat_message(ai_message_data)
        
        return {
            "success": True,
            "response": ai_response,
            "project_id": project_id
        }
        
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return {"success": False, "error": str(e)}

@app.get("/chat/history/{project_id}")
async def get_chat_history(project_id: str):
    """Get chat history for a project"""
    try:
        # Verify project exists
        if config.USE_SUPABASE:
            project = supabase_utils.get_project(project_id)
        else:
            project = postgres_storage.get_project(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if config.USE_SUPABASE:
            messages = supabase_utils.get_chat_messages(project_id)
        else:
            messages = postgres_storage.get_chat_messages(project_id)
        
        return {"success": True, "messages": messages}
        
    except Exception as e:
        print(f"❌ Error getting chat history: {e}")
        return {"success": False, "error": str(e)}

# Context endpoint (no auth required)
@app.post("/context/{project_id}")
async def update_project_context(project_id: str, context_data: dict):
    """Update project context"""
    try:
        # Verify project exists
        if config.USE_SUPABASE:
            project = supabase_utils.get_project(project_id)
        else:
            project = postgres_storage.get_project(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        context_data["updated_at"] = datetime.utcnow()
        
        if config.USE_SUPABASE:
            result = supabase_utils.update_project_context(project_id, context_data)
        else:
            result = postgres_storage.update_project_context(project_id, context_data)
        
        return result
        
    except Exception as e:
        print(f"❌ Error updating project context: {e}")
        return {"success": False, "error": str(e)}

# Grant sections endpoints (no auth required)
@app.get("/grant/sections/{project_id}")
async def get_grant_sections(project_id: str):
    """Get grant sections for a project"""
    try:
        # Verify project exists
        if config.USE_SUPABASE:
            project = supabase_utils.get_project(project_id)
        else:
            project = postgres_storage.get_project(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Get or create grant document
        document = grant_sections.grant_section_manager.get_grant_document(project_id)
        if not document:
            document = grant_sections.grant_section_manager.create_grant_document(project_id)
        
        # Get chat messages for auto-population
        if config.USE_SUPABASE:
            chat_messages = supabase_utils.get_chat_messages(project_id)
        else:
            chat_messages = postgres_storage.get_chat_messages(project_id)
        
        # Auto-populate sections from chat if document is empty
        if document.total_words == 0 and chat_messages:
            grant_sections.grant_section_manager.auto_populate_from_chat(project_id, chat_messages)
            document = grant_sections.grant_section_manager.get_grant_document(project_id)
        
        # Prepare response
        sections = {}
        for section_id, section in document.sections.items():
            sections[section_id] = {
                "id": section.id,
                "title": section.title,
                "content": section.content,
                "target_length": section.target_length,
                "description": section.description,
                "word_count": section.word_count,
                "status": section.status,
                "last_updated": section.last_updated
            }
        
        stats = grant_sections.grant_section_manager.get_document_stats(project_id)
        
        return {
            "success": True,
            "sections": sections,
            "stats": stats,
            "chat_summary": document.chat_summary,
            "last_updated": document.last_updated
        }
        
    except Exception as e:
        print(f"❌ Error getting grant sections: {e}")
        return {"success": False, "error": str(e)}

@app.post("/grant/sections/{project_id}/auto-populate")
async def auto_populate_sections(project_id: str):
    """Auto-populate grant sections from chat conversation"""
    try:
        # Verify project exists
        if config.USE_SUPABASE:
            project = supabase_utils.get_project(project_id)
        else:
            project = postgres_storage.get_project(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Get chat messages
        if config.USE_SUPABASE:
            chat_messages = supabase_utils.get_chat_messages(project_id)
        else:
            chat_messages = postgres_storage.get_chat_messages(project_id)
        
        # Auto-populate sections
        result = grant_sections.grant_section_manager.auto_populate_from_chat(project_id, chat_messages)
        
        return {
            "success": True,
            "populated_sections": result["populated_sections"],
            "total_sections": result["total_sections"]
        }
        
    except Exception as e:
        print(f"❌ Error auto-populating sections: {e}")
        return {"success": False, "error": str(e)}

@app.get("/grant/sections/{project_id}/export/markdown")
async def export_grant_markdown(project_id: str):
    """Export grant document as markdown"""
    try:
        # Verify project exists
        if config.USE_SUPABASE:
            project = supabase_utils.get_project(project_id)
        else:
            project = postgres_storage.get_project(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        markdown_content = grant_sections.grant_section_manager.export_to_markdown(project_id)
        
        from fastapi.responses import Response
        return Response(
            content=markdown_content,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=grant-application-{project_id}.md"}
        )
        
    except Exception as e:
        print(f"❌ Error exporting markdown: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error exporting document"
        )

@app.get("/grant/sections/{project_id}/export/docx")
async def export_grant_docx(project_id: str):
    """Export grant document as DOCX"""
    try:
        # Verify project exists
        if config.USE_SUPABASE:
            project = supabase_utils.get_project(project_id)
        else:
            project = postgres_storage.get_project(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        docx_content = grant_sections.grant_section_manager.export_to_docx(project_id)
        
        from fastapi.responses import Response
        return Response(
            content=docx_content,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename=grant-application-{project_id}.docx"}
        )
        
    except Exception as e:
        print(f"❌ Error exporting DOCX: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error exporting document"
        )

# Keep existing endpoints for backward compatibility
@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "message": "GWAT API is running!",
        "timestamp": datetime.utcnow(),
        "api_key_status": "configured" if os.getenv("OPENAI_API_KEY") else "not configured",
        "environment_vars": {
            "OPENAI_API_KEY": "set" if os.getenv("OPENAI_API_KEY") else "not set",
            "USE_SUPABASE": os.getenv("USE_SUPABASE", "false"),
            "SUPABASE_URL": "set" if os.getenv("SUPABASE_URL") else "not set",
            "DB_HOSTNAME": "set" if os.getenv("DB_HOSTNAME") else "not set",
            "PORT": os.getenv("PORT", "8080")
        }
    }

@app.get("/simple")
async def simple_test():
    """Simple test endpoint"""
    return {"status": "ok", "message": "Simple endpoint working - updated", "deployment": "latest", "memory": "32gb"}

@app.post("/generate")
async def generate_response(request: dict):
    """Generate AI response (legacy endpoint)"""
    try:
        question = request.get("question", "")
        project_id = request.get("project_id", "default")
        
        # Get AI response
        response = openai_utils.chat_grant_assistant(question, project_id)
        
        return {"response": response}
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        return {"error": str(e)}

@app.post("/analyze")
async def analyze_content(request: dict):
    """Analyze content (legacy endpoint)"""
    try:
        content = request.get("content", "")
        analysis_type = request.get("type", "general")
        
        # Get AI analysis
        response = openai_utils.analyze_content(content, analysis_type)
        
        return {"analysis": response}
    except Exception as e:
        print(f"❌ Error analyzing content: {e}")
        return {"error": str(e)}

# Startup event
@app.on_event("startup")
async def startup_event():
    print("🚀 FastAPI startup event triggered")
    print(f"🔧 Startup - OPENAI_API_KEY: {'set' if os.getenv('OPENAI_API_KEY') else 'not set'}")
    print(f"🔧 Startup - PORT: {os.getenv('PORT', '8080')}")
    print(f"🔧 Startup - RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'development')}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))