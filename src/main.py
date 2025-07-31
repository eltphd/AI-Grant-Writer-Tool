import os
import sys
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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

# Simple test endpoints
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

# Project endpoints (simplified for now)
@app.get("/projects")
async def get_projects():
    """Get all projects"""
    try:
        # Return empty list for now
        return {"success": True, "projects": []}
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
        
        return {"success": True, "project": project_data}
    except Exception as e:
        print(f"❌ Error creating project: {e}")
        return {"success": False, "error": str(e)}

@app.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get a specific project"""
    try:
        # Return mock project for now
        project = {
            "id": project_id,
            "name": f"Project {project_id[:8]}",
            "description": "Mock project",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        return {"success": True, "project": project}
    except Exception as e:
        print(f"❌ Error getting project: {e}")
        return {"success": False, "error": str(e)}

@app.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    try:
        return {"success": True}
    except Exception as e:
        print(f"❌ Error deleting project: {e}")
        return {"success": False, "error": str(e)}

# File upload endpoint (simplified)
@app.post("/upload")
async def upload_file(project_id: str, file: UploadFile):
    """Upload a file for a project"""
    try:
        return {"success": True, "filename": file.filename}
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return {"success": False, "error": str(e)}

# Chat endpoints (simplified)
@app.post("/chat/send_message")
async def send_message(project_id: str, message: dict):
    """Send a chat message for a project"""
    try:
        return {
            "success": True,
            "response": "This is a mock response. Backend is working!",
            "project_id": project_id
        }
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return {"success": False, "error": str(e)}

@app.get("/chat/history/{project_id}")
async def get_chat_history(project_id: str):
    """Get chat history for a project"""
    try:
        return {"success": True, "messages": []}
    except Exception as e:
        print(f"❌ Error getting chat history: {e}")
        return {"success": False, "error": str(e)}

# Context endpoint (simplified)
@app.post("/context/{project_id}")
async def update_project_context(project_id: str, context_data: dict):
    """Update project context"""
    try:
        return {"success": True}
    except Exception as e:
        print(f"❌ Error updating project context: {e}")
        return {"success": False, "error": str(e)}

# Grant sections endpoints (simplified)
@app.get("/grant/sections/{project_id}")
async def get_grant_sections(project_id: str):
    """Get grant sections for a project"""
    try:
        return {
            "success": True,
            "sections": {},
            "stats": {"total_words": 0, "completion_percentage": 0},
            "chat_summary": "",
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        print(f"❌ Error getting grant sections: {e}")
        return {"success": False, "error": str(e)}

@app.post("/grant/sections/{project_id}/auto-populate")
async def auto_populate_sections(project_id: str):
    """Auto-populate grant sections from chat conversation"""
    try:
        return {
            "success": True,
            "populated_sections": 0,
            "total_sections": 0
        }
    except Exception as e:
        print(f"❌ Error auto-populating sections: {e}")
        return {"success": False, "error": str(e)}

@app.get("/grant/sections/{project_id}/export/markdown")
async def export_grant_markdown(project_id: str):
    """Export grant document as markdown"""
    try:
        markdown_content = "# Grant Application\n\nNo content available."
        
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
        # Return empty document for now
        from fastapi.responses import Response
        return Response(
            content=b"Empty document",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename=grant-application-{project_id}.docx"}
        )
    except Exception as e:
        print(f"❌ Error exporting DOCX: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error exporting document"
        )

# Legacy endpoints
@app.post("/generate")
async def generate_response(request: dict):
    """Generate AI response (legacy endpoint)"""
    try:
        return {"response": "Mock AI response"}
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        return {"error": str(e)}

@app.post("/analyze")
async def analyze_content(request: dict):
    """Analyze content (legacy endpoint)"""
    try:
        return {"analysis": "Mock analysis"}
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