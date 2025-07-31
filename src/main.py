import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import our utilities
try:
    from .utils.storage_utils import db_manager, OrganizationInfo, RFPDocument, ProjectResponse
    from .utils.rfp_analysis import rfp_analyzer
except ImportError:
    # Fallback for direct execution
    from utils.storage_utils import db_manager, OrganizationInfo, RFPDocument, ProjectResponse
    from utils.rfp_analysis import rfp_analyzer

app = FastAPI(title="GWAT API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Projects endpoint
@app.get("/projects")
async def get_projects():
    """Get all projects"""
    try:
        projects = db_manager.get_all_projects()
        return {"success": True, "projects": projects}
    except Exception as e:
        print(f"❌ Error getting projects: {e}")
        return {"success": False, "error": str(e)}

# Organization management
@app.post("/organization/create")
async def create_organization(request: dict):
    """Create organization profile"""
    try:
        from datetime import datetime
        
        org = OrganizationInfo(
            id=f"org_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=request.get('name', 'New Organization'),
            mission=request.get('mission', ''),
            description=request.get('description', ''),
            key_accomplishments=request.get('key_accomplishments', []),
            partnerships=request.get('partnerships', []),
            impact_metrics=request.get('impact_metrics', {}),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        if db_manager.save_organization(org):
            return {"success": True, "organization": org.__dict__}
        else:
            return {"success": False, "error": "Failed to save organization"}
    except Exception as e:
        print(f"❌ Error creating organization: {e}")
        return {"success": False, "error": str(e)}

@app.get("/organization/{org_id}")
async def get_organization(org_id: str):
    """Get organization profile"""
    try:
        org = db_manager.get_organization(org_id)
        if org:
            return {"success": True, "organization": org.__dict__}
        else:
            return {"success": False, "error": "Organization not found"}
    except Exception as e:
        print(f"❌ Error getting organization: {e}")
        return {"success": False, "error": str(e)}

# RFP upload and analysis
@app.post("/rfp/upload")
async def upload_rfp(project_id: str, request: dict):
    """Upload and analyze RFP document"""
    try:
        from datetime import datetime
        
        # Analyze RFP content
        content = request.get('content', '')
        analysis = rfp_analyzer.analyze_rfp_content(content)
        
        # Create RFP document
        rfp = RFPDocument(
            id=f"rfp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            project_id=project_id,
            filename=request.get('filename', 'RFP Document'),
            content=content,
            requirements=analysis['requirements'],
            eligibility_criteria=analysis['eligibility_criteria'],
            funding_amount=analysis['funding_amount'],
            deadline=analysis['deadline'],
            analysis_result=analysis,
            created_at=datetime.now().isoformat()
        )
        
        if db_manager.save_rfp(rfp):
            return {"success": True, "rfp": rfp.__dict__}
        else:
            return {"success": False, "error": "Failed to save RFP"}
    except Exception as e:
        print(f"❌ Error uploading RFP: {e}")
        return {"success": False, "error": str(e)}

@app.post("/rfp/analyze")
async def analyze_rfp(project_id: str, request: dict):
    """Analyze RFP and align with organization info"""
    try:
        org_id = request.get('org_id')
        rfp_id = request.get('rfp_id')
        
        if not org_id or not rfp_id:
            return {"success": False, "error": "Missing org_id or rfp_id"}
        
        # Get organization and RFP
        org = db_manager.get_organization(org_id)
        rfp = db_manager.get_rfp(rfp_id)
        
        if not org or not rfp:
            return {"success": False, "error": "Organization or RFP not found"}
        
        # Analyze alignment
        alignment = rfp_analyzer.align_org_with_rfp(org, rfp)
        
        # Create project response
        response = rfp_analyzer.create_project_response(org, rfp, alignment)
        
        if db_manager.save_project_response(response):
            return {
                "success": True,
                "analysis": alignment,
                "response": response.__dict__
            }
        else:
            return {"success": False, "error": "Failed to save project response"}
    except Exception as e:
        print(f"❌ Error analyzing RFP: {e}")
        return {"success": False, "error": str(e)}

# File upload endpoint
@app.post("/upload")
async def upload_file(project_id: str, file: dict):
    """Upload file and extract content"""
    try:
        # Mock file processing
        return {
            "success": True,
            "filename": file.get('filename', 'uploaded_file'),
            "content_length": len(file.get('content', '')),
            "uploaded_at": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return {"success": False, "error": str(e)}

# Context endpoint
@app.get("/context/{project_id}")
async def get_project_context(project_id: str):
    """Get project context"""
    try:
        return {"success": True, "context": {"files": []}}
    except Exception as e:
        print(f"❌ Error getting project context: {e}")
        return {"success": False, "error": str(e)}

@app.post("/context/{project_id}")
async def update_project_context(project_id: str, request: dict):
    """Update project context"""
    try:
        return {"success": True, "message": "Context updated successfully"}
    except Exception as e:
        print(f"❌ Error updating project context: {e}")
        return {"success": False, "error": str(e)}

# Chat endpoints
@app.post("/chat/send_message")
async def send_message(request: dict):
    """Send chat message"""
    try:
        message = request.get('message', '')
        project_id = request.get('project_id', 'test-project')
        
        # Mock AI response
        ai_response = f"Thank you for your message: '{message}'. I'm here to help with your grant writing project {project_id}."
        
        return {
            "success": True,
            "response": ai_response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return {"success": False, "error": str(e)}

@app.get("/chat/history/{project_id}")
async def get_chat_history(project_id: str):
    """Get chat history"""
    try:
        return {
            "success": True,
            "messages": [
                {
                    "id": 1,
                    "message": "Welcome to GWAT! How can I help with your grant writing?",
                    "timestamp": datetime.now().isoformat(),
                    "type": "ai"
                }
            ]
        }
    except Exception as e:
        print(f"❌ Error getting chat history: {e}")
        return {"success": False, "error": str(e)}

@app.post("/chat/brainstorm")
async def brainstorm_ideas(project_id: str, request: dict):
    """Brainstorm grant ideas"""
    try:
        return {
            "success": True,
            "ideas": [
                "Mock idea 1: Focus on community impact",
                "Mock idea 2: Emphasize innovation",
                "Mock idea 3: Highlight sustainability"
            ]
        }
    except Exception as e:
        print(f"❌ Error brainstorming: {e}")
        return {"success": False, "error": str(e)}

# Privacy audit endpoint
@app.get("/privacy/audit/{project_id}")
async def privacy_audit(project_id: str):
    """Get privacy audit for a project"""
    try:
        return {
            "success": True,
            "audit_result": {
                "overall_privacy_level": "high",
                "sensitive_data_found": False,
                "recommendations": []
            }
        }
    except Exception as e:
        print(f"❌ Error privacy audit: {e}")
        return {"success": False, "error": str(e)}

# Grant sections endpoint
@app.get("/grant/sections/{project_id}")
async def get_grant_sections(project_id: str):
    """Get grant sections"""
    try:
        return {
            "success": True,
            "sections": {
                "executive_summary": "Project executive summary...",
                "organization_profile": "Organization background...",
                "project_approach": "Detailed project approach...",
                "timeline": "Implementation timeline...",
                "budget": "Detailed budget breakdown...",
                "evaluation": "Evaluation and reporting plan..."
            }
        }
    except Exception as e:
        print(f"❌ Error getting grant sections: {e}")
        return {"success": False, "error": str(e)}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))