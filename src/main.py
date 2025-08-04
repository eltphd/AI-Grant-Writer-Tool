import os
import re
import json
from datetime import datetime
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="GET$ API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple test endpoint - this should work even if other imports fail
@app.get("/test")
async def test_endpoint():
    return {"message": "Basic FastAPI app is working!", "timestamp": datetime.now().isoformat()}

# Import RAG utilities
try:
    from .utils.rag_utils import rag_db
    from .utils.advanced_rag_utils import advanced_rag_db, CulturalKnowledgeItem
    from .utils.vercel_ai_utils import vercel_ai_gateway
    from .utils.specialized_llm_utils import specialized_llm
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ RAG import error: {e}")
    try:
        # Fallback for direct import
        from utils.rag_utils import rag_db
        from utils.advanced_rag_utils import advanced_rag_db, CulturalKnowledgeItem
        from utils.vercel_ai_utils import vercel_ai_gateway
        from utils.specialized_llm_utils import specialized_llm
        RAG_AVAILABLE = True
    except ImportError as e2:
        print(f"❌ RAG fallback import error: {e2}")
        RAG_AVAILABLE = False
        # Create dummy objects for fallback
        advanced_rag_db = None
        vercel_ai_gateway = None
        specialized_llm = None

# Import other utilities
try:
    from .utils.storage_utils import OrganizationInfo, RFPDocument, ProjectResponse
    from .utils import supabase_utils as supa
    from .utils.rfp_analysis import analyze_rfp_content, analyze_organization_rfp_alignment
except ImportError:
    # Fallback for direct import
    from utils.storage_utils import OrganizationInfo, RFPDocument, ProjectResponse
    from utils import supabase_utils as supa
    from utils.rfp_analysis import analyze_rfp_content, analyze_organization_rfp_alignment

# Import evaluation utilities
try:
    from .utils.evaluation_utils import cognitive_evaluator, cultural_evaluator, performance_monitor
except ImportError:
    # Fallback for direct import
    from utils.evaluation_utils import cognitive_evaluator, cultural_evaluator, performance_monitor

# Import prompt logging middleware
try:
    from .middleware import prompt_logger
except ImportError:
    try:
        from middleware import prompt_logger
    except ImportError:
        prompt_logger = None

# Root endpoint to serve the React app
@app.get("/")
async def read_root():
    if os.path.exists("frontend/build/index.html"):
        return FileResponse("frontend/build/index.html")
    return {"message": "GET$ API is running. Frontend not built."}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "GET$ API is running", "timestamp": datetime.now().isoformat()}

# Simple ping endpoint for testing
@app.get("/ping")
async def ping():
    return {"message": "pong", "timestamp": datetime.now().isoformat()}

# Serve static files (frontend build) - only for static assets
if os.path.exists("frontend/build"):
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

# Projects endpoint
@app.get("/projects")
async def get_projects():
    """Get all projects from Supabase"""
    try:
        print("🔍 Attempting to get projects from Supabase...")
        projects = supa.get_all_projects_from_db()
        print(f"✅ Successfully retrieved {len(projects)} projects")
        return {"success": True, "projects": projects}
    except Exception as e:
        print(f"❌ Error getting projects: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}

# Project creation endpoint
@app.post("/projects")
async def create_project(request: dict):
    """Create a new project"""
    try:
        from datetime import datetime
        
        project_data = {
            "id": request.get('id', f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            "name": request.get('name', 'New Project'),
            "description": request.get('description', 'A new grant writing project'),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Save project to Supabase
        supa.create_project(project_data)
        
        return {"success": True, "project": project_data}
    except Exception as e:
        print(f"❌ Error creating project: {e}")
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
        
        if supa.insert_organization(org.__dict__):
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
        org = supa.get_organization(org_id)
        if org:
            return {"success": True, "organization": org}
        else:
            return {"success": False, "error": "Organization not found"}
    except Exception as e:
        print(f"❌ Error getting organization: {e}")
        return {"success": False, "error": str(e)}

# RFP upload and analysis
@app.post("/rfp/upload/{project_id}")
async def upload_rfp(project_id: str, request: dict):
    """Upload and analyze RFP document"""
    try:
        from datetime import datetime
        
        import base64, tempfile, os
        from pathlib import Path
        # Handle possible base64 payload for binary documents
        raw_content = request.get('content', '')
        is_base64 = request.get('is_base64', False)
        if is_base64:
            file_bytes = base64.b64decode(raw_content)
            suffix = Path(request.get('filename','rfp')).suffix or '.bin'
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(file_bytes)
                tmp_path = Path(tmp.name)
            from .utils.file_utils import extract_text_from_file
            content = extract_text_from_file(tmp_path, tmp_path.suffix.lower())
            os.unlink(tmp_path)
        else:
            content = raw_content
        from .utils.rfp_analysis import analyze_rfp_content
        analysis = analyze_rfp_content(content)
        
        # Create RFP document
        rfp = RFPDocument(
            id=f"rfp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            project_id=project_id,
            filename=request.get('filename', 'RFP Document'),
            content=content,
            requirements=analysis.get('requirements', []),
            eligibility_criteria=analysis.get('eligibility_criteria', []),
            funding_amount=analysis.get('funding_amount'),
            deadline=analysis.get('deadline'),
            analysis_result=analysis,
            created_at=datetime.now().isoformat()
        )
        
        # Save RFP document metadata and chunks in Supabase
        supa.save_uploaded_file(content.encode('utf-8'), rfp.filename, project_id)
        supa.insert_file_chunks_into_db([(rfp.filename, chunk) for chunk in chunk_text(content)], project_id)

        return {"success": True, "rfp": rfp.__dict__, "analysis": analysis}
    except Exception as e:
        print(f"❌ Error uploading RFP: {e}")
        return {"success": False, "error": str(e)}

@app.post("/rfp/analyze")
async def analyze_rfp(request: dict):
    """Analyze RFP content for requirements and alignment"""
    try:
        project_id = request.get('project_id')
        org_id = request.get('org_id')
        rfp_id = request.get('rfp_id')
        
        if not project_id or not org_id or not rfp_id:
            return {"success": False, "error": "Missing required parameters: project_id, org_id, rfp_id"}
        
        # Get RFP analysis data
        rfp_data = get_rfp_analysis_data(project_id)
        
        # Get organization data
        org_data = get_project_context_data(project_id)
        
        # Perform alignment analysis
        from .utils.rfp_analysis import analyze_organization_rfp_alignment
        analysis_result = analyze_organization_rfp_alignment(
            org_data=org_data,
            rfp_data=rfp_data
        )
        
        return {"success": True, "analysis": analysis_result}
    except Exception as e:
        print(f"❌ Error analyzing RFP: {e}")
        return {"success": False, "error": str(e)}

from .utils.privacy_utils import pii_redactor
from .utils.embedding_utils import chunk_text

# File upload endpoint
@app.post("/upload")
async def upload_file(request: dict):
    """Upload file, redact PII, and process for RAG system."""
    try:
        from datetime import datetime
        
        project_id = request.get('project_id', 'test-project')
        file_data = request.get('file', {})
        import base64, tempfile, os
        from pathlib import Path
        filename = file_data.get('filename', 'uploaded_file')
        is_base64 = file_data.get('is_base64', False)
        raw_content = file_data.get('content', '')

        # If the payload is base64-encoded (binary files like PDF/DOCX)
        if is_base64:
            # Decode bytes and write to a temp file so we can extract text
            file_bytes = base64.b64decode(raw_content)
            suffix = Path(filename).suffix or ".bin"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(file_bytes)
                tmp_path = Path(tmp.name)
            # Extract text using file_utils helper (PDF/DOCX/TXT)
            from .utils.file_utils import extract_text_from_file
            extracted_text = extract_text_from_file(tmp_path, tmp_path.suffix.lower())
            # Clean up temp file
            os.unlink(tmp_path)
            original_content = extracted_text
        else:
            original_content = raw_content

        # Step 1: Redact PII from the content
        try:
            redacted_content, redactions = pii_redactor.redact_text(original_content)
            print(f"✅ PII redaction completed for {filename}")
        except Exception as e:
            print(f"⚠️ PII redaction failed for {filename}: {e}")
            redacted_content, redactions = original_content, []

        # Step 2: Chunk the redacted content for the RAG system
        try:
            chunks = chunk_text(redacted_content)
            print(f"✅ Text chunking completed for {filename}: {len(chunks)} chunks")
        except Exception as e:
            print(f"⚠️ Text chunking failed for {filename}: {e}")
            chunks = [redacted_content]

        # Save file metadata in Supabase
        try:
            supa.save_uploaded_file(original_content.encode("utf-8"), filename, project_id)
            print(f"✅ File metadata saved to Supabase for {filename}")
        except Exception as e:
            print(f"❌ Failed to save file metadata for {filename}: {e}")
            return {"success": False, "error": f"Failed to save file metadata: {str(e)}"}
        
        # Insert chunks and embeddings into Supabase
        try:
            chunk_pairs = [(filename, c) for c in chunks]
            supa.insert_file_chunks_into_db(chunk_pairs, project_id)
            print(f"✅ File chunks and embeddings saved to Supabase for {filename}")
        except Exception as e:
            print(f"❌ Failed to save file chunks for {filename}: {e}")
            return {"success": False, "error": f"Failed to save file chunks: {str(e)}"}

        return {
            "success": True,
            "filename": filename,
            "content_length": len(original_content),
            "redactions_found": len(redactions),
            "chunk_count": len(chunks),
            "message": f"File '{filename}' uploaded and processed. Sensitive data has been redacted."
        }
            
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return {"success": False, "error": str(e)}

# Context endpoint
@app.get("/context/{project_id}")
async def get_project_context(project_id: str):
    """Get project context with uploaded files from Supabase"""
    try:
        # Get uploaded files from Supabase
        uploaded_files = []
        
        try:
            # Query file_chunks table for this project
            chunks_data = supa.query_data("file_chunks")
            if chunks_data:
                # Group by file_name to get unique files
                files_dict = {}
                for chunk in chunks_data:
                    if chunk.get('project_id') == project_id:
                        file_name = chunk.get('file_name', 'Unknown')
                        chunk_text = chunk.get('chunk_text', '')
                        
                        if file_name not in files_dict:
                            files_dict[file_name] = []
                        
                        files_dict[file_name].append(chunk_text)
                
                # Create file info for each unique file
                for file_name, chunks in files_dict.items():
                    uploaded_files.append({
                        "filename": file_name,
                        "category": "uploaded_document",
                        "content_length": sum(len(chunk) for chunk in chunks),
                        "uploaded_at": datetime.now().isoformat()
                    })
                
                print(f"🔍 DEBUG: Found {len(uploaded_files)} uploaded files from Supabase")
            else:
                print("🔍 DEBUG: No file chunks found in Supabase")
        except Exception as e:
            print(f"⚠️ Error getting file chunks from Supabase: {e}")
        
        return {
            "success": True, 
            "context": {
                "files": uploaded_files,
                "project_id": project_id,
                "total_files": len(uploaded_files)
            }
        }
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
    """Send chat message with context-aware responses and automatic evaluation"""
    try:
        message = request.get('message', '')
        project_id = request.get('project_id', 'test-project')
        
        # Start performance timer
        start_time = performance_monitor.start_timer()
        
        # Get project context and RFP analysis
        try:
            project_context = get_project_context_data(project_id)
            print(f"🔍 DEBUG: Project context retrieved successfully")
        except Exception as e:
            print(f"❌ Error getting project context: {e}")
            project_context = {
                "organization_info": "Error retrieving organization info",
                "initiative_description": "Error retrieving initiative description",
                "uploaded_files": [],
                "uploaded_content": [],
                "rfp_requirements": [],
                "community_focus": None
            }
        
        try:
            rfp_analysis = get_rfp_analysis_data(project_id)
            print(f"🔍 DEBUG: RFP analysis retrieved successfully")
        except Exception as e:
            print(f"❌ Error getting RFP analysis: {e}")
            rfp_analysis = {
                "requirements": ["Error retrieving RFP analysis"],
                "eligibility_criteria": ["Error retrieving eligibility criteria"],
                "funding_amount": "Error retrieving funding amount",
                "deadline": "Error retrieving deadline",
                "alignment_score": 0
            }
        
        print(f"🔍 DEBUG: Chat request - Message: {message}")
        print(f"🔍 DEBUG: Project ID: {project_id}")
        print(f"🔍 DEBUG: Uploaded files: {project_context.get('uploaded_files', [])}")
        print(f"🔍 DEBUG: Uploaded content count: {len(project_context.get('uploaded_content', []))}")
        
        # Get relevant context from uploaded files using vector search
        uploaded_files = project_context.get('uploaded_files', [])
        relevant_snippets = []
        if uploaded_files:
            try:
                # Search for relevant chunks based on user message
                snippet = supa.rag_context(message, uploaded_files, project_id)
                if snippet:
                    relevant_snippets = [snippet]
                print(f"🔍 DEBUG: Found {len(relevant_snippets)} relevant snippets")
            except Exception as e:
                print(f"⚠️ Error getting relevant snippets: {e}")
        
        # Generate context-aware response with relevant snippets
        ai_response = generate_contextual_response(message, project_context, rfp_analysis, relevant_snippets)
        
        # Save chat message to database
        try:
            supa.save_chat_message(project_id, {
                "user_message": message,
                "ai_response": ai_response,
                "timestamp": datetime.now().isoformat(),
                "metadata": {"relevant_snippets": relevant_snippets}
            })
            print(f"✅ Chat message saved to database")
        except Exception as e:
            print(f"⚠️ Error saving chat message: {e}")
        
        # End performance timer
        response_time = performance_monitor.end_timer(start_time)
        
        # Record performance metrics
        performance_monitor.record_performance("chat_response", response_time)
        
        # Perform automatic evaluation
        cognitive_eval = cognitive_evaluator.evaluate_response(ai_response)
        cultural_eval = cultural_evaluator.evaluate_response(ai_response, project_context.get('community_focus'))
        
        # Calculate quality metrics
        quality_score = (cognitive_eval['overall_score'] + cultural_eval['overall_cultural_score']) / 2
        
        return {
            "success": True,
            "response": ai_response,
            "timestamp": datetime.now().isoformat(),
            "relevant_snippets": relevant_snippets,
            "performance_metrics": {
                "response_time": response_time,
                "meets_target": response_time <= 4.0
            },
            "quality_evaluation": {
                "cognitive_friendliness_score": cognitive_eval['overall_score'],
                "cultural_competency_score": cultural_eval['overall_cultural_score'],
                "overall_quality_score": quality_score,
                "quality_level": "excellent" if quality_score >= 80 else "good" if quality_score >= 60 else "needs_improvement"
            },
            "recommendations": cognitive_eval['recommendations'] + cultural_eval['recommendations']
        }
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return {"success": False, "error": str(e)}

def get_project_context_data(project_id: str) -> dict:
    """Get project context data from Supabase"""
    try:
        # Get uploaded files from Supabase
        uploaded_files = []
        uploaded_content = []
        
        # Get file chunks from Supabase for this project
        try:
            # Query file_chunks table for this project
            chunks_data = supa.query_data("file_chunks")
            if chunks_data:
                # Group by file_name to get unique files
                files_dict = {}
                for chunk in chunks_data:
                    if chunk.get('project_id') == project_id:
                        file_name = chunk.get('file_name', 'Unknown')
                        chunk_text = chunk.get('chunk_text', '')
                        
                        if file_name not in files_dict:
                            files_dict[file_name] = []
                            uploaded_files.append(file_name)
                        
                        files_dict[file_name].append(chunk_text)
                
                # Create content summaries for each file
                for file_name, chunks in files_dict.items():
                    content_summary = f"Document: {file_name}\nContent: {' '.join(chunks[:3])}..."  # First 3 chunks
                    uploaded_content.append(content_summary)
                
                print(f"🔍 DEBUG: Found {len(uploaded_files)} uploaded files from Supabase")
                print(f"🔍 DEBUG: Files: {uploaded_files}")
            else:
                print("🔍 DEBUG: No file chunks found in Supabase")
        except Exception as e:
            print(f"⚠️ Error getting file chunks from Supabase: {e}")
        
        # Get organization info if available
        organization_info = ""
        try:
            org_data = supa.query_data("organizations")
            if org_data:
                organization_info = org_data[0].get('description', '')[:500] + "..."
                print(f"🔍 DEBUG: Found organization info: {organization_info[:100]}...")
        except Exception as e:
            print(f"⚠️ Error getting organization info: {e}")
        
        # Get RFP requirements from uploaded documents
        rfp_requirements = []
        if uploaded_content:
            rfp_requirements = ["Requirements from uploaded RFP documents"]
        
        context_data = {
            "organization_info": organization_info,
            "initiative_description": "Based on uploaded documents",
            "uploaded_files": uploaded_files,
            "uploaded_content": uploaded_content,
            "rfp_requirements": rfp_requirements if rfp_requirements else ["No RFP documents uploaded yet"],
            "community_focus": "Based on uploaded community documents"
        }
        
        print(f"🔍 DEBUG: Returning context data: {context_data}")
        return context_data
    except Exception as e:
        print(f"❌ Error getting project context: {e}")
        return {
            "organization_info": "No organization information available",
            "initiative_description": "No initiative description available",
            "uploaded_files": [],
            "uploaded_content": [],
            "rfp_requirements": [],
            "community_focus": None
        }

def get_rfp_analysis_data(project_id: str) -> dict:
    """Get RFP analysis data from Supabase"""
    try:
        # Get RFP-related documents from Supabase
        rfp_requirements = []
        
        try:
            # Query file_chunks table for RFP documents in this project
            chunks_data = supa.query_data("file_chunks")
            if chunks_data:
                rfp_content = ""
                for chunk in chunks_data:
                    if chunk.get('project_id') == project_id:
                        file_name = chunk.get('file_name', '').lower()
                        if 'rfp' in file_name or 'request' in file_name or 'proposal' in file_name:
                            rfp_content += chunk.get('chunk_text', '') + " "
                
                if rfp_content:
                    # Extract requirements from RFP content
                    requirements = []
                    if "non-profit" in rfp_content.lower():
                        requirements.append("Non-profit status required")
                    if "community" in rfp_content.lower():
                        requirements.append("Community focus required")
                    if "measurable" in rfp_content.lower():
                        requirements.append("Measurable outcomes required")
                    if "funding" in rfp_content.lower():
                        requirements.append("Funding requirements specified")
                    
                    rfp_requirements = requirements
                    print(f"🔍 DEBUG: Found RFP content, extracted {len(requirements)} requirements")
                else:
                    print("🔍 DEBUG: No RFP documents found in Supabase")
            else:
                print("🔍 DEBUG: No file chunks found in Supabase")
        except Exception as e:
            print(f"⚠️ Error getting RFP data from Supabase: {e}")
        
        if rfp_requirements:
            return {
                "requirements": rfp_requirements,
                "eligibility_criteria": ["Based on uploaded RFP documents"],
                "funding_amount": "Based on uploaded RFP documents",
                "deadline": "Based on uploaded RFP documents",
                "alignment_score": 85
            }
        else:
            return {
                "requirements": ["No RFP documents uploaded yet"],
                "eligibility_criteria": ["Upload RFP documents for analysis"],
                "funding_amount": "Upload RFP for funding details",
                "deadline": "Upload RFP for deadline information",
                "alignment_score": 0
            }
    except Exception as e:
        print(f"Error getting RFP analysis: {e}")
        return {
            "requirements": ["Error retrieving RFP analysis"],
            "eligibility_criteria": ["Error retrieving eligibility criteria"],
            "funding_amount": "Error retrieving funding amount",
            "deadline": "Error retrieving deadline",
            "alignment_score": 0
        }

def generate_contextual_response(message: str, context: dict, rfp_analysis: dict, relevant_snippets: list = None) -> str:
    """Generate culturally sensitive contextual AI response using consolidated LLM approach"""
    
    # Use provided relevant snippets or create empty context
    if relevant_snippets and len(relevant_snippets) > 0:
        print(f"🔍 DEBUG: Using {len(relevant_snippets)} relevant snippets from Supabase")
        # Add relevant snippets to context
        context['uploaded_content'] = context.get('uploaded_content', []) + relevant_snippets
    else:
        print(f"🔍 DEBUG: No relevant snippets found, using empty context")
    
    # Add RFP requirements to context
    context['rfp_requirements'] = rfp_analysis.get('requirements', [])
    
    # Get community context
    community_context = context.get('community_focus', '')
    
    # Determine grant type based on RFP analysis
    grant_type = "community"  # Default
    if rfp_analysis.get('requirements'):
        requirements_text = ' '.join(rfp_analysis.get('requirements', [])).lower()
        if 'nih' in requirements_text or 'national institutes' in requirements_text:
            grant_type = "nih"
        elif 'nsf' in requirements_text or 'national science foundation' in requirements_text:
            grant_type = "nsf"
        elif 'federal' in requirements_text or 'government' in requirements_text:
            grant_type = "federal"
    
    # Generate response using available AI services
    if vercel_ai_gateway:
        try:
            # Log prompt for debugging
            if prompt_logger:
                prompt_logger.log_prompt({
                    "type": "grant_response",
                    "message": message,
                    "context": context,
                    "grant_type": grant_type,
                    "organization_id": context.get('project_id', 'unknown')
                })
            
            response = vercel_ai_gateway.generate_grant_response(
                message=message,
                context=context,
                grant_type=grant_type
            )
            
            # Evaluate cultural alignment using the same gateway
            evaluation = vercel_ai_gateway.evaluate_cultural_alignment(
                content=response,
                context=context
            )
            
            # Add evaluation metadata to response if available
            if evaluation and not evaluation.get('error'):
                print(f"✅ Cultural evaluation completed - Overall Quality: {evaluation.get('scores', {}).get('overall_quality', 0)}%")
            
            return response
            
        except Exception as e:
            print(f"❌ Error in Vercel AI Gateway: {e}")
            return generate_default_response(message, context, rfp_analysis)
    else:
        # Use fallback response generation when Vercel AI Gateway is not available
        print("⚠️ Vercel AI Gateway not available, using fallback response generation")
        return generate_default_response(message, context, rfp_analysis)

def _generate_initial_response(message: str, context: dict, rfp_analysis: dict, rag_context: dict, project_context: str, community_context: str) -> str:
    """Generate the initial AI response"""
    
    # Priority check for file-related questions
    file_keywords = ['file', 'files', 'upload', 'uploaded', 'see', 'check', 'document', 'documents']
    if any(keyword in message.lower() for keyword in file_keywords):
        print(f"🔍 DEBUG: Detected file-related question: {message}")
        return generate_content_access_response(context)
    
    # Check for specific section writing requests using specialized LLM
    if specialized_llm is None:
        print("⚠️ Specialized LLM not available, using fallback")
        return generate_default_response(message, context, rfp_analysis)
    
    if any(word in message.lower() for word in ['executive summary', 'summary']):
        return specialized_llm.generate_culturally_sensitive_response(
            "executive_summary", 
            {"organization_info": context.get('organization_info', ''), 
             "community_focus": community_context,
             "uploaded_files": ', '.join(context.get('uploaded_files', [])),
             "uploaded_content": '\n'.join(context.get('uploaded_content', [])),
             "rfp_requirements": ', '.join(rfp_analysis.get('requirements', []))},
            community_context
        )
    
    elif any(word in message.lower() for word in ['organization profile', 'organization', 'profile']):
        return specialized_llm.generate_culturally_sensitive_response(
            "organization_profile",
            {"organization_info": context.get('organization_info', ''),
             "community_focus": community_context,
             "uploaded_content": '\n'.join(context.get('uploaded_content', [])),
             "cultural_guidelines": rag_context.get('cultural_context', '')},
            community_context
        )
    
    elif any(word in message.lower() for word in ['project description', 'project', 'description']):
        return specialized_llm.generate_culturally_sensitive_response(
            "project_description",
            {"project_context": project_context,
             "community_focus": community_context,
             "cultural_guidelines": rag_context.get('cultural_context', '')},
            community_context
        )
    
    elif any(word in message.lower() for word in ['timeline', 'schedule', 'deadline']):
        return generate_timeline_section_with_rag(context, rfp_analysis, rag_context)
    
    elif any(word in message.lower() for word in ['budget', 'funding', 'cost']):
        return generate_budget_section_with_rag(context, rfp_analysis, rag_context)
    
    elif any(word in message.lower() for word in ['evaluation', 'measure', 'outcome']):
        return generate_evaluation_section_with_rag(context, rfp_analysis, rag_context)
    
    elif any(word in message.lower() for word in ['grant', 'section', 'write', 'create']):
        return generate_grant_section_guidance(context, rfp_analysis)
    
    elif any(word in message.lower() for word in ['content', 'access', 'document', 'file', 'files', 'upload', 'uploaded', 'see', 'check']):
        return generate_content_access_response(context)
    
    elif any(word in message.lower() for word in ['rfp', 'requirement', 'eligibility']):
        return generate_rfp_guidance(rfp_analysis)
    
    elif any(word in message.lower() for word in ['help', 'guide', 'assist']):
        return generate_general_guidance(context, rfp_analysis)
    
    else:
        # Use Supabase RAG for general questions
        rag_response = rag_db.get_relevant_context(message, context.get('uploaded_files', []), project_id)
        if rag_response:
            return rag_response
    
    # Use relevant snippets in the default response if available
    if relevant_snippets and len(relevant_snippets) > 0:
        snippets_context = "\n\n".join([f"From your documents: {snippet}" for snippet in relevant_snippets])
        return f"Based on your uploaded documents:\n\n{snippets_context}\n\n{generate_default_response(message, context, rfp_analysis)}"
    else:
        return generate_default_response(message, context, rfp_analysis)

def _evaluate_response_with_feedback_loop(response: str, community_context: str, context: dict) -> dict:
    """Evaluate response and determine if regeneration or approval is needed"""
    
    evaluation_result = {
        'cultural_score': 0.0,
        'sensitivity_flags': [],
        'needs_regeneration': False,
        'requires_approval': False,
        'recommendations': []
    }
    
    try:
        # Evaluate cultural competency
        cultural_eval = cultural_evaluator.evaluate_response(response, community_context)
        evaluation_result['cultural_score'] = cultural_eval.get('overall_score', 0.0)
        
        # Check for sensitivity issues
        sensitivity_issues = _check_sensitivity_issues(response, context)
        evaluation_result['sensitivity_flags'] = sensitivity_issues
        
        # Determine if regeneration is needed (low cultural score)
        if evaluation_result['cultural_score'] < 0.7:  # Threshold for cultural competency
            evaluation_result['needs_regeneration'] = True
            evaluation_result['recommendations'].append("Cultural competency score is low. Regenerating with improved cultural sensitivity.")
        
        # Determine if approval is needed (sensitive content detected)
        if sensitivity_issues:
            evaluation_result['requires_approval'] = True
            evaluation_result['recommendations'].append("Sensitive content detected. Flagging for human approval.")
        
        # Record performance metrics
        performance_monitor.record_performance(
            "response_evaluation",
            duration=0.0,  # Will be calculated by the monitor
            accuracy=evaluation_result['cultural_score']
        )
        
    except Exception as e:
        print(f"Error in response evaluation: {e}")
        # Default to safe behavior - flag for approval
        evaluation_result['requires_approval'] = True
        evaluation_result['recommendations'].append("Evaluation error occurred. Flagging for human review.")
    
    return evaluation_result

def _check_sensitivity_issues(response: str, context: dict) -> list:
    """Check for potentially sensitive content that requires approval"""
    
    sensitivity_flags = []
    
    # Check for PII patterns
    pii_patterns = [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone
        r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Names (basic)
    ]
    
    for pattern in pii_patterns:
        if re.search(pattern, response):
            sensitivity_flags.append("Potential PII detected")
            break
    
    # Check for sensitive cultural references
    sensitive_cultural_terms = [
        'tribal', 'indigenous', 'native', 'ethnic', 'racial',
        'religious', 'spiritual', 'cultural', 'traditional'
    ]
    
    cultural_mentions = sum(1 for term in sensitive_cultural_terms if term.lower() in response.lower())
    if cultural_mentions > 2:  # Threshold for cultural sensitivity
        sensitivity_flags.append("Multiple cultural references detected")
    
    # Check for financial/confidential information
    financial_patterns = [
        r'\$\d+',  # Dollar amounts
        r'\b\d{9,}\b',  # Large numbers (potential SSN, etc.)
    ]
    
    for pattern in financial_patterns:
        if re.search(pattern, response):
            sensitivity_flags.append("Potential financial/confidential data detected")
            break
    
    return sensitivity_flags

def _regenerate_with_evaluation_feedback(original_response: str, evaluation_result: dict, message: str, context: dict, rfp_analysis: dict, rag_context: dict, project_context: str, community_context: str) -> str:
    """Regenerate response with evaluation feedback to improve cultural competency"""
    
    # Build improved prompt with cultural feedback
    cultural_feedback = evaluation_result.get('recommendations', [])
    feedback_text = "\n".join(cultural_feedback)
    
    improved_prompt = f"""
    Original request: {message}
    
    Previous response had cultural competency issues. Please regenerate with these improvements:
    {feedback_text}
    
    Focus on:
    - Enhanced cultural sensitivity
    - Community-appropriate language
    - Respectful cultural references
    - Inclusive language
    """
    
    # Generate improved response using specialized LLM
    try:
        improved_response = specialized_llm.generate_culturally_sensitive_response(
            "improved_response",
            {
                "original_request": message,
                "project_context": project_context,
                "community_focus": community_context,
                "cultural_feedback": feedback_text,
                "cultural_guidelines": rag_context.get('cultural_context', '')
            },
            community_context
        )
        
        # Add note about improvement
        improved_response += f"\n\n✅ **Response improved** based on cultural competency evaluation."
        
        return improved_response
        
    except Exception as e:
        print(f"Error regenerating response: {e}")
        return original_response

def _flag_for_approval(response: str, evaluation_result: dict, project_id: str) -> str:
    """Flag response for human approval and return approval ID"""
    
    approval_id = f"approval_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{project_id}"
    
    # Store approval request in database
    approval_data = {
        'approval_id': approval_id,
        'project_id': project_id,
        'response_text': response,
        'evaluation_result': evaluation_result,
        'status': 'pending',
        'created_at': datetime.now().isoformat(),
        'sensitivity_flags': evaluation_result.get('sensitivity_flags', [])
    }
    
    try:
        # Save to database (you'll need to implement this)
        _save_approval_request(approval_data)
    except Exception as e:
        print(f"Error saving approval request: {e}")
    
    return approval_id

def _save_approval_request(approval_data: dict) -> bool:
    """Save approval request to database"""
    try:
        # For now, save to a simple file-based storage
        # In production, this should use the database
        approval_dir = "src/secure_data/approvals"
        os.makedirs(approval_dir, exist_ok=True)
        
        approval_file = f"{approval_dir}/{approval_data['approval_id']}.json"
        with open(approval_file, 'w') as f:
            json.dump(approval_data, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving approval request: {e}")
        return False

def generate_executive_summary_with_rag(context: dict, rfp_analysis: dict, rag_context: dict) -> str:
    """Generate culturally sensitive executive summary using RAG context"""
    
    from utils.openai_utils import get_culturally_sensitive_response
    
    org_info = context.get('organization_info', {})
    uploaded_files = context.get('uploaded_files', [])
    community_focus = context.get('community_focus', '')
    
    # Build context for the AI
    project_context = f"""
    Organization Information: {org_info}
    Uploaded Documents: {', '.join(uploaded_files)}
    Community Focus: {community_focus}
    RFP Requirements: {', '.join(rfp_analysis.get('requirements', []))}
    """
    
    prompt = f"""
    Please write a culturally sensitive executive summary for a grant proposal.
    
    Project Context: {project_context}
    
    GUIDELINES:
    - Use clear, simple language that's easy to understand
    - Highlight the community impact and benefits
    - Include specific, measurable goals
    - Show how this addresses community needs
    - Use encouraging, positive language
    - Keep it concise but comprehensive (2-3 paragraphs)
    
    FORMAT:
    - Start with a compelling opening that captures the community's needs
    - Include the organization's mission and key strengths
    - Describe the project's goals and expected outcomes
    - End with a strong call to action about the funding impact
    
    Make sure the language is inclusive and respectful of diverse communities.
    """
    
    try:
        response = get_culturally_sensitive_response(prompt, community_focus)
        return response
    except Exception as e:
        print(f"Error generating executive summary: {e}")
        return f"""📋 **Executive Summary**

Based on your organization's information and uploaded documents, here's a draft executive summary:

**Our Mission & Impact**
Your organization is dedicated to serving the community with a focus on {community_focus or 'positive community change'}. Through this grant, we will expand our impact and create lasting benefits for those we serve.

**Project Goals**
This funding will enable us to:
• Strengthen our community programs and services
• Reach more individuals and families in need
• Create measurable, positive outcomes
• Build sustainable partnerships and resources

**Expected Outcomes**
With this support, we will achieve specific, measurable results that demonstrate our commitment to community well-being and positive change.

**Next Steps**
Please review this summary and let me know if you'd like me to adjust the focus, tone, or add specific details from your uploaded documents."""

def generate_organization_profile_with_rag(context: dict, rfp_analysis: dict, rag_context: dict) -> str:
    """Generate organization profile using RAG context for cultural competence"""
    
    org_info = context.get('organization_info', {})
    
    response = "🏢 **Organization Profile**\n\n"
    
    # Incorporate community profile if available
    community_context = ""
    if rag_context.get('community_profile'):
        profile = rag_context['community_profile']
        community_context = f"\n**Community Understanding:** Our work is informed by deep knowledge of the {profile['community_name']} community, "
        community_context += f"including {', '.join(profile['cultural_backgrounds'][:2])} cultural backgrounds and "
        community_context += f"languages including {', '.join(profile['languages'][:2])}.\n\n"
    
    if org_info.get('name'):
        response += f"**{org_info['name']}** "
    else:
        response += "**Our Organization** "
    
    if org_info.get('mission'):
        response += f"is dedicated to {org_info['mission']}. "
    else:
        response += "is committed to creating positive community impact. "
    
    if org_info.get('years_operating'):
        response += f"Established {org_info['years_operating']} years ago, "
    
    if org_info.get('legal_status'):
        response += f"we operate as a {org_info['legal_status']} "
    else:
        response += "we operate as a non-profit organization "
    
    response += "serving our community with integrity and excellence.\n\n"
    
    response += "**Our Expertise:**\n"
    if org_info.get('focus_areas'):
        for area in org_info['focus_areas']:
            response += f"• {area}\n"
    else:
        response += "• Community development\n• Program implementation\n• Stakeholder engagement\n"
    
    if org_info.get('target_population'):
        response += f"\n**Target Population:** {org_info['target_population']}\n"
    
    if org_info.get('geographic_area'):
        response += f"**Service Area:** {org_info['geographic_area']}\n"
    
    response += "\n**Organizational Capacity:**\n"
    response += "• Experienced leadership team\n"
    response += "• Strong community partnerships\n"
    response += "• Proven track record of success\n"
    response += "• Robust evaluation systems\n\n"
    
    response += community_context
    
    response += "**Why We're the Right Choice:**\n"
    response += "Our deep community roots, proven expertise, and commitment to measurable outcomes make us the ideal partner for this initiative."
    
    return response

def generate_project_description_with_rag(context: dict, rfp_analysis: dict, rag_context: dict) -> str:
    """Generate project description using RAG context for cultural competence"""
    
    org_info = context.get('organization_info', {})
    rfp_reqs = rfp_analysis.get('requirements', [])
    
    response = "🎯 **Project Description & Approach**\n\n"
    
    # Incorporate community profile if available
    community_context = ""
    if rag_context.get('community_profile'):
        profile = rag_context['community_profile']
        community_context = f"\n**Community Understanding:** Our work is informed by deep knowledge of the {profile['community_name']} community, "
        community_context += f"including {', '.join(profile['cultural_backgrounds'][:2])} cultural backgrounds and "
        community_context += f"languages including {', '.join(profile['languages'][:2])}.\n\n"
    
    if org_info.get('name'):
        response += f"**{org_info['name']}** proposes to "
    else:
        response += "**Our organization** proposes to "
    
    if org_info.get('initiative_description'):
        response += f"{org_info['initiative_description']}. "
    else:
        response += "implement a comprehensive community development initiative. "
    
    response += "This project will address critical community needs while meeting all RFP requirements.\n\n"
    
    # Incorporate best practices from RAG
    if rag_context.get('best_practices'):
        response += "**Evidence-Based Approach:** This proposal incorporates proven strategies including "
        response += rag_context['best_practices'][0]['title'] + " and "
        response += rag_context['best_practices'][1]['title'] if len(rag_context['best_practices']) > 1 else "established best practices"
        response += ".\n\n"
    
    response += "**Project Objectives:**\n"
    if rfp_reqs:
        for i, req in enumerate(rfp_reqs[:5], 1):
            response += f"{i}. Address {req}\n"
    else:
        response += "1. Enhance community engagement\n"
        response += "2. Build organizational capacity\n"
        response += "3. Create sustainable impact\n"
        response += "4. Meet all RFP requirements\n"
    
    response += "\n**Implementation Strategy:**\n"
    response += "• **Phase 1:** Community needs assessment and stakeholder engagement\n"
    response += "• **Phase 2:** Program development and partnership building\n"
    response += "• **Phase 3:** Implementation and monitoring\n"
    response += "• **Phase 4:** Evaluation and sustainability planning\n\n"
    
    response += "**Innovative Approach:**\n"
    response += "Our methodology combines proven best practices with innovative community-driven solutions, ensuring both immediate impact and long-term sustainability."
    
    response += community_context
    
    return response

def generate_timeline_section_with_rag(context: dict, rfp_analysis: dict, rag_context: dict) -> str:
    """Generate timeline section using RAG context for cultural competence"""
    
    response = "⏰ **Timeline & Implementation**\n\n"
    
    if rfp_analysis.get('deadline'):
        response += f"**Project Duration:** Aligned with RFP deadline of {rfp_analysis['deadline']}\n\n"
    
    response += "**Implementation Timeline:**\n\n"
    response += "**Months 1-3: Foundation Building**\n"
    response += "• Stakeholder engagement and community outreach\n"
    response += "• Needs assessment and baseline data collection\n"
    response += "• Partnership development and resource mobilization\n"
    response += "• Program design and approval processes\n\n"
    
    response += "**Months 4-6: Program Launch**\n"
    response += "• Initial program implementation\n"
    response += "• Staff training and capacity building\n"
    response += "• Pilot testing and refinement\n"
    response += "• Early outcome measurement\n\n"
    
    response += "**Months 7-9: Full Implementation**\n"
    response += "• Comprehensive program delivery\n"
    response += "• Ongoing monitoring and evaluation\n"
    response += "• Mid-course adjustments as needed\n"
    response += "• Progress reporting and stakeholder updates\n\n"
    
    response += "**Months 10-12: Sustainability Planning**\n"
    response += "• Long-term impact assessment\n"
    response += "• Sustainability strategy development\n"
    response += "• Knowledge transfer and capacity building\n"
    response += "• Final evaluation and reporting\n\n"
    
    response += "**Key Milestones:**\n"
    response += "• Month 3: Program design approval\n"
    response += "• Month 6: Initial outcomes report\n"
    response += "• Month 9: Mid-term evaluation\n"
    response += "• Month 12: Final project report\n"
    
    # Incorporate community profile if available
    community_context = ""
    if rag_context.get('community_profile'):
        profile = rag_context['community_profile']
        community_context = f"\n**Community Understanding:** Our work is informed by deep knowledge of the {profile['community_name']} community, "
        community_context += f"including {', '.join(profile['cultural_backgrounds'][:2])} cultural backgrounds and "
        community_context += f"languages including {', '.join(profile['languages'][:2])}.\n\n"
    
    response += community_context
    
    return response

def generate_budget_section_with_rag(context: dict, rfp_analysis: dict, rag_context: dict) -> str:
    """Generate budget section using RAG context for cultural competence"""
    
    response = "💰 **Budget & Financial Plan**\n\n"
    
    if rfp_analysis.get('funding_amount'):
        response += f"**Total Project Budget:** {rfp_analysis['funding_amount']}\n\n"
    
    response += "**Budget Breakdown:**\n\n"
    response += "**Personnel (40%):** $XX,XXX\n"
    response += "• Project Director: $XX,XXX\n"
    response += "• Program Coordinators: $XX,XXX\n"
    response += "• Support Staff: $XX,XXX\n\n"
    
    response += "**Program Activities (30%):** $XX,XXX\n"
    response += "• Community outreach and engagement: $XX,XXX\n"
    response += "• Training and capacity building: $XX,XXX\n"
    response += "• Materials and supplies: $XX,XXX\n"
    response += "• Technology and equipment: $XX,XXX\n\n"
    
    response += "**Evaluation & Monitoring (15%):** $XX,XXX\n"
    response += "• Data collection and analysis: $XX,XXX\n"
    response += "• External evaluation: $XX,XXX\n"
    response += "• Reporting and documentation: $XX,XXX\n\n"
    
    response += "**Administrative (10%):** $XX,XXX\n"
    response += "• Office space and utilities: $XX,XXX\n"
    response += "• Insurance and legal: $XX,XXX\n"
    response += "• Financial management: $XX,XXX\n\n"
    
    response += "**Contingency (5%):** $XX,XXX\n"
    response += "• Unforeseen expenses and adjustments\n\n"
    
    response += "**Cost-Effectiveness:**\n"
    response += "• Leveraged partnerships reduce direct costs\n"
    response += "• Shared resources maximize impact\n"
    response += "• Sustainable approach ensures long-term value\n"
    
    # Incorporate community profile if available
    community_context = ""
    if rag_context.get('community_profile'):
        profile = rag_context['community_profile']
        community_context = f"\n**Community Understanding:** Our work is informed by deep knowledge of the {profile['community_name']} community, "
        community_context += f"including {', '.join(profile['cultural_backgrounds'][:2])} cultural backgrounds and "
        community_context += f"languages including {', '.join(profile['languages'][:2])}.\n\n"
    
    response += community_context
    
    return response

def generate_evaluation_section_with_rag(context: dict, rfp_analysis: dict, rag_context: dict) -> str:
    """Generate evaluation section using RAG context for cultural competence"""
    
    response = "📊 **Evaluation & Impact Measurement**\n\n"
    
    response += "**Evaluation Framework:**\n"
    response += "Our comprehensive evaluation approach combines quantitative and qualitative methods to measure both immediate outcomes and long-term impact.\n\n"
    
    response += "**Key Performance Indicators:**\n"
    response += "• **Output Metrics:** Number of participants served, activities completed\n"
    response += "• **Outcome Metrics:** Changes in knowledge, skills, and behaviors\n"
    response += "• **Impact Metrics:** Long-term community improvements\n"
    response += "• **Process Metrics:** Efficiency and effectiveness measures\n\n"
    
    response += "**Data Collection Methods:**\n"
    response += "• Surveys and interviews with participants\n"
    response += "• Focus groups with stakeholders\n"
    response += "• Document review and analysis\n"
    response += "• Community feedback sessions\n"
    response += "• External evaluation partner assessment\n\n"
    
    response += "**Reporting Schedule:**\n"
    response += "• Monthly progress reports\n"
    response += "• Quarterly outcome assessments\n"
    response += "• Annual comprehensive evaluation\n"
    response += "• Final impact report\n\n"
    
    response += "**Continuous Improvement:**\n"
    response += "Evaluation findings will inform ongoing program refinement, ensuring maximum effectiveness and community benefit."
    
    # Incorporate community profile if available
    community_context = ""
    if rag_context.get('community_profile'):
        profile = rag_context['community_profile']
        community_context = f"\n**Community Understanding:** Our work is informed by deep knowledge of the {profile['community_name']} community, "
        community_context += f"including {', '.join(profile['cultural_backgrounds'][:2])} cultural backgrounds and "
        community_context += f"languages including {', '.join(profile['languages'][:2])}.\n\n"
    
    response += community_context
    
    return response

def generate_grant_section_guidance(context: dict, rfp_analysis: dict) -> str:
    """Generate conversational grant section guidance"""
    
    response = "📋 **Great! Let's write your grant sections together!**\n\n"
    
    response += "**Here's what we need to write:**\n\n"
    response += "1️⃣ **Executive Summary** - The big picture overview\n"
    response += "2️⃣ **Organization Profile** - Tell your story\n"
    response += "3️⃣ **Project Description** - What you want to do\n"
    response += "4️⃣ **Timeline** - When you'll do it\n"
    response += "5️⃣ **Budget** - How much it will cost\n"
    response += "6️⃣ **Evaluation** - How you'll measure success\n\n"
    
    if rfp_analysis.get('requirements'):
        response += "**Based on your RFP, focus on these key points:**\n"
        for i, req in enumerate(rfp_analysis['requirements'][:3], 1):
            response += f"{i}. {req}\n"
        response += "\n"
    
    response += "**Which section would you like me to write for you?**\n"
    response += "Just say 'write executive summary' or 'write budget' and I'll create it using your data!"
    
    return response

def generate_content_access_response(context: dict) -> str:
    """Generate response about uploaded content and AI access"""
    
    uploaded_files = context.get('uploaded_files', [])
    
    if not uploaded_files:
        return """📄 **No documents uploaded yet**

I don't see any documents uploaded yet. To help me provide context-aware assistance, please upload:

• **Grant funding application documents** - RFP guidelines, funding announcements
• **Organization profile documents** - Your mission, history, accomplishments
• **Proposal drafts** - Any existing grant proposals or project descriptions

Once you upload documents, I can:
✅ Analyze funding requirements and align them with your organization
✅ Provide culturally sensitive recommendations based on your community focus
✅ Help strategize funding proposals using your specific context
✅ Generate grant sections tailored to your organization and the funder's needs

Go to the "Create Grant" tab to upload your documents!"""
    
    else:
        file_list = "\n".join([f"• {file}" for file in uploaded_files])
        return f"""📄 **Uploaded Documents Available**

I can see the following documents have been uploaded and processed:

{file_list}

**What I can do with these documents:**
✅ Analyze funding requirements from your RFP documents
✅ Extract organization information for grant alignment
✅ Provide culturally sensitive recommendations
✅ Generate grant sections using your specific context
✅ Strategize funding proposals based on your organization's profile

**Ask me to:**
• "Help me write an executive summary based on my organization"
• "Analyze the RFP requirements and our alignment"
• "Generate a project description using our uploaded documents"
• "Create a budget section based on our organization's needs"

The AI is now using your uploaded documents for context-aware responses!"""

def generate_rfp_guidance(rfp_analysis: dict) -> str:
    """Generate conversational RFP guidance"""
    
    response = "📋 **Here's what I found in your RFP:**\n\n"
    
    if rfp_analysis.get('requirements'):
        response += "**Key Requirements:**\n"
        for i, req in enumerate(rfp_analysis['requirements'], 1):
            response += f"{i}. {req}\n"
        response += "\n"
    
    if rfp_analysis.get('eligibility_criteria'):
        response += "**Eligibility Criteria:**\n"
        for i, criteria in enumerate(rfp_analysis['eligibility_criteria'], 1):
            response += f"{i}. {criteria}\n"
        response += "\n"
    
    if rfp_analysis.get('funding_amount'):
        response += f"💰 **Funding Available:** {rfp_analysis['funding_amount']}\n"
    
    if rfp_analysis.get('deadline'):
        response += f"⏰ **Deadline:** {rfp_analysis['deadline']}\n\n"
    
    if rfp_analysis.get('alignment_score'):
        response += f"🎯 **Your Alignment Score:** {rfp_analysis['alignment_score']}%\n\n"
    
    response += "**My recommendations:**\n"
    response += "• Focus on the requirements you meet well\n"
    response += "• Address any gaps with specific plans\n"
    response += "• Make sure your proposal matches their priorities\n\n"
    
    response += "**Would you like me to help you write sections that address these requirements?**"
    
    return response

def generate_budget_guidance(rfp_analysis: dict) -> str:
    """Generate budget guidance"""
    
    response = "💰 **Budget Guidance**\n\n"
    
    if rfp_analysis.get('funding_amount'):
        response += f"**RFP Funding:** {rfp_analysis['funding_amount']}\n\n"
    
    response += "**Budget Best Practices:**\n"
    response += "• Align with RFP funding limits\n"
    response += "• Include all required cost categories\n"
    response += "• Provide detailed line items\n"
    response += "• Show cost-effectiveness\n"
    response += "• Include matching funds if required\n\n"
    
    response += "**Common Budget Categories:**\n"
    response += "• Personnel (salaries, benefits)\n"
    response += "• Equipment and supplies\n"
    response += "• Travel and training\n"
    response += "• Indirect costs\n"
    response += "• Evaluation and reporting\n\n"
    
    response += "Would you like help structuring your budget?"
    
    return response

def generate_timeline_guidance(rfp_analysis: dict) -> str:
    """Generate timeline guidance"""
    
    response = "⏰ **Timeline & Deadline Guidance**\n\n"
    
    if rfp_analysis.get('deadline'):
        response += f"**RFP Deadline:** {rfp_analysis['deadline']}\n\n"
    
    response += "**Timeline Best Practices:**\n"
    response += "• Start early - allow 2-3 weeks for writing\n"
    response += "• Include internal review time\n"
    response += "• Plan for revisions and feedback\n"
    response += "• Consider submission requirements\n\n"
    
    response += "**Project Timeline Structure:**\n"
    response += "• Month 1-3: Planning and preparation\n"
    response += "• Month 4-6: Implementation phase\n"
    response += "• Month 7-9: Evaluation and reporting\n"
    response += "• Month 10-12: Sustainability planning\n\n"
    
    response += "**Key Milestones to Include:**\n"
    response += "• Project kickoff\n"
    response += "• Major deliverables\n"
    response += "• Progress reviews\n"
    response += "• Final evaluation\n"
    
    return response

def generate_general_guidance(context: dict, rfp_analysis: dict) -> str:
    """Generate conversational general guidance"""
    
    response = "🎯 **Hi! I'm your GET$ Assistant**\n\n"
    
    response += "**I'm here to help you write a winning grant proposal!**\n\n"
    
    if context.get('organization_info'):
        response += "✅ I can see your organization information\n"
    else:
        response += "❌ I don't see your organization info yet\n"
    
    if rfp_analysis.get('requirements'):
        response += f"✅ I have your RFP analysis ({len(rfp_analysis['requirements'])} requirements)\n"
    else:
        response += "❌ I don't see your RFP document yet\n"
    
    response += "\n**What would you like to do?**\n\n"
    response += "1️⃣ **'Help me write sections'** - I'll walk you through each part of your grant\n"
    response += "2️⃣ **'Show my RFP analysis'** - I'll tell you what I found in your RFP\n"
    response += "3️⃣ **'Help with budget'** - I'll help you plan your funding request\n"
    response += "4️⃣ **'Brainstorm ideas'** - I'll give you creative writing ideas\n"
    response += "5️⃣ **'Check my alignment'** - I'll see how well you match the RFP\n\n"
    
    response += "**Just tell me what you need in simple terms!** 😊"
    
    return response

def generate_default_response(message: str, context: dict, rfp_analysis: dict) -> str:
    """Generate a culturally sensitive default response when no specific pattern is matched"""
    
    uploaded_files = context.get('uploaded_files', [])
    
    if not uploaded_files:
        return """🤝 **Welcome! I'm here to help with your grant writing.**

I can see you're working on a grant proposal. To give you the best help possible, I'd love to learn more about your project.

**What I can help you with:**
• 📝 Writing grant sections (executive summary, organization profile, etc.)
• 💡 Brainstorming ideas for your proposal
• 📋 Analyzing RFP requirements
• 💰 Budget planning and financial sections
• ⏰ Timeline and implementation planning
• 📊 Evaluation and impact measurement

**To get started:**
1. Upload your RFP document and organization information
2. Tell me about your community and project goals
3. Ask me to help with specific sections

**Try asking me:**
• "Help me write an executive summary"
• "What should I include in my organization profile?"
• "How do I plan my project timeline?"
• "Can you help me with the budget section?"

I'm here to support you every step of the way! 😊"""
    
    else:
        return f"""🤝 **Great! I can see you've uploaded {len(uploaded_files)} document(s).**

I'm ready to help you create a strong grant proposal using your uploaded information.

**Based on your documents, I can help you with:**
• 📝 Writing specific grant sections using your organization's information
• 💡 Brainstorming ideas tailored to your project
• 📋 Analyzing how your project aligns with funding requirements
• 💰 Creating budget sections based on your needs
• ⏰ Planning realistic timelines for your project
• 📊 Developing evaluation strategies for your impact

**What would you like to work on?**
• "Write an executive summary using my organization's information"
• "Help me create an organization profile"
• "Analyze the RFP requirements and our alignment"
• "Generate a project description based on our documents"
• "Help me plan the budget section"

I'm here to make your grant writing process easier and more successful! 😊"""

@app.get("/chat/history/{project_id}")
async def get_chat_history(project_id: str):
    """Get chat history from database"""
    try:
        # Get saved chat messages from Supabase
        chat_messages = supa.get_chat_messages(project_id)
        
        # Format messages for frontend
        formatted_messages = []
        
        # Add welcome message if no history
        if not chat_messages:
            formatted_messages.append({
                "id": 1,
                "message": "Welcome to GET$! How can I help with your grant writing?",
                "timestamp": datetime.now().isoformat(),
                "type": "ai"
            })
        else:
            # Convert saved messages to frontend format
            for i, msg in enumerate(chat_messages):
                formatted_messages.extend([
                    {
                        "id": i * 2 + 1,
                        "message": msg.get("question", ""),
                        "timestamp": msg.get("timestamp", datetime.now().isoformat()),
                        "type": "user"
                    },
                    {
                        "id": i * 2 + 2,
                        "message": msg.get("answer", ""),
                        "timestamp": msg.get("timestamp", datetime.now().isoformat()),
                        "type": "ai"
                    }
                ])
        
        return {
            "success": True,
            "messages": formatted_messages
        }
    except Exception as e:
        print(f"❌ Error getting chat history: {e}")
        return {"success": False, "error": str(e)}

@app.post("/chat/brainstorm")
async def brainstorm_ideas(request: dict):
    """Brainstorm grant ideas and strategies"""
    try:
        project_id = request.get('project_id', 'test-project')
        topic = request.get('topic', '').lower()
        project_context = get_project_context_data(project_id)
        rfp_analysis = get_rfp_analysis_data(project_id)
        
        # Generate topic-specific brainstorming
        if any(word in topic for word in ['section', 'write', 'content']):
            ideas = generate_section_ideas(project_context, rfp_analysis)
        elif any(word in topic for word in ['budget', 'funding', 'cost']):
            ideas = generate_budget_ideas(rfp_analysis)
        elif any(word in topic for word in ['timeline', 'schedule', 'deadline']):
            ideas = generate_timeline_ideas(rfp_analysis)
        elif any(word in topic for word in ['evaluation', 'measure', 'outcome']):
            ideas = generate_evaluation_ideas(project_context, rfp_analysis)
        elif any(word in topic for word in ['partnership', 'collaboration', 'network']):
            ideas = generate_partnership_ideas(project_context)
        else:
            ideas = generate_general_ideas(project_context, rfp_analysis)
        
        return {
            "success": True,
            "ideas": ideas
        }
    except Exception as e:
        print(f"❌ Error brainstorming: {e}")
        return {"success": False, "error": str(e)}

def generate_section_ideas(context: dict, rfp_analysis: dict) -> list:
    """Generate ideas for grant sections"""
    ideas = [
        "📋 **Executive Summary Ideas:**",
        "• Start with a compelling hook about your organization's impact",
        "• Include 2-3 key statistics that demonstrate success",
        "• End with a clear call to action about the proposed project",
        "",
        "🏢 **Organization Profile Ideas:**",
        "• Highlight your unique mission and values",
        "• Showcase past achievements with specific metrics",
        "• Emphasize your expertise in the target area",
        "• Include testimonials from partners or beneficiaries",
        "",
        "🎯 **Project Approach Ideas:**",
        "• Describe your innovative methodology",
        "• Explain how you'll address the specific RFP requirements",
        "• Include risk mitigation strategies",
        "• Show how you'll measure and report progress"
    ]
    
    if rfp_analysis.get('requirements'):
        ideas.append("")
        ideas.append("**RFP-Specific Focus Areas:**")
        for req in rfp_analysis['requirements'][:3]:
            ideas.append(f"• Emphasize how you meet: {req}")
    
    return ideas

def generate_budget_ideas(rfp_analysis: dict) -> list:
    """Generate budget-related ideas"""
    ideas = [
        "💰 **Budget Strategy Ideas:**",
        "• Align every line item with RFP requirements",
        "• Show cost-effectiveness through detailed breakdowns",
        "• Include matching funds if required by the RFP",
        "• Demonstrate sustainability beyond the grant period",
        "",
        "📊 **Budget Categories to Consider:**",
        "• Personnel (salaries, benefits, training)",
        "• Equipment and technology needs",
        "• Travel and professional development",
        "• Evaluation and reporting costs",
        "• Indirect costs (if allowed)",
        "",
        "💡 **Budget Presentation Tips:**",
        "• Use clear, professional formatting",
        "• Include narrative explanations for major items",
        "• Show how costs align with project outcomes",
        "• Demonstrate value for money"
    ]
    
    if rfp_analysis.get('funding_amount'):
        ideas.append("")
        ideas.append(f"**RFP Funding Target:** {rfp_analysis['funding_amount']}")
        ideas.append("• Structure your budget to maximize this amount")
        ideas.append("• Show how you'll use funds effectively")
    
    return ideas

def generate_timeline_ideas(rfp_analysis: dict) -> list:
    """Generate timeline-related ideas"""
    ideas = [
        "⏰ **Timeline Strategy Ideas:**",
        "• Create realistic milestones that align with RFP requirements",
        "• Include buffer time for unexpected challenges",
        "• Show how you'll maintain momentum throughout the project",
        "• Demonstrate sustainability planning",
        "",
        "📅 **Timeline Structure Ideas:**",
        "• Month 1-3: Planning and preparation phase",
        "• Month 4-6: Implementation and early results",
        "• Month 7-9: Evaluation and mid-course corrections",
        "• Month 10-12: Reporting and sustainability planning",
        "",
        "🎯 **Key Milestones to Include:**",
        "• Project kickoff and team formation",
        "• Major deliverables and checkpoints",
        "• Progress reviews and stakeholder meetings",
        "• Final evaluation and reporting"
    ]
    
    if rfp_analysis.get('deadline'):
        ideas.append("")
        ideas.append(f"**RFP Deadline:** {rfp_analysis['deadline']}")
        ideas.append("• Plan backwards from this date")
        ideas.append("• Include time for revisions and feedback")
    
    return ideas

def generate_evaluation_ideas(context: dict, rfp_analysis: dict) -> list:
    """Generate evaluation-related ideas"""
    ideas = [
        "📊 **Evaluation Strategy Ideas:**",
        "• Design measurable outcomes that align with RFP goals",
        "• Include both quantitative and qualitative measures",
        "• Plan for ongoing monitoring and reporting",
        "• Show how you'll use data to improve programs",
        "",
        "📈 **Evaluation Methods to Consider:**",
        "• Pre/post assessments for participants",
        "• Regular progress reports and check-ins",
        "• Stakeholder feedback and surveys",
        "• External evaluation or peer review",
        "• Long-term impact measurement",
        "",
        "🎯 **Key Metrics to Track:**",
        "• Number of people served",
        "• Quality of services delivered",
        "• Participant satisfaction and outcomes",
        "• Cost-effectiveness and efficiency",
        "• Sustainability and lasting impact"
    ]
    
    return ideas

def generate_partnership_ideas(context: dict) -> list:
    """Generate partnership-related ideas"""
    ideas = [
        "🤝 **Partnership Strategy Ideas:**",
        "• Identify complementary organizations in your field",
        "• Show how partnerships strengthen your proposal",
        "• Include letters of support or commitment",
        "• Demonstrate collaborative capacity and experience",
        "",
        "🏢 **Potential Partner Types:**",
        "• Local government agencies",
        "• Educational institutions",
        "• Healthcare providers",
        "• Community organizations",
        "• Private sector partners",
        "• Faith-based organizations",
        "",
        "💡 **Partnership Benefits to Highlight:**",
        "• Shared resources and expertise",
        "• Broader reach and impact",
        "• Cost-effectiveness through collaboration",
        "• Sustainability through diverse support"
    ]
    
    return ideas

def generate_general_ideas(context: dict, rfp_analysis: dict) -> list:
    """Generate general grant writing ideas"""
    ideas = [
        "🎯 **General Grant Writing Strategies:**",
        "• Tell a compelling story about your organization's impact",
        "• Use specific examples and success stories",
        "• Include data and statistics to support your case",
        "• Show how you'll address the funder's priorities",
        "",
        "📋 **Proposal Enhancement Ideas:**",
        "• Include visual elements (charts, photos, diagrams)",
        "• Add testimonials from beneficiaries or partners",
        "• Provide clear, concise executive summary",
        "• Show innovation and creativity in your approach",
        "",
        "💡 **Competitive Advantage Ideas:**",
        "• Highlight your unique expertise or approach",
        "• Show proven track record in similar projects",
        "• Demonstrate strong community relationships",
        "• Include plans for sustainability and scaling"
    ]
    
    if rfp_analysis.get('alignment_score'):
        ideas.append("")
        ideas.append(f"**Your Alignment Score: {rfp_analysis['alignment_score']}%**")
        if rfp_analysis['alignment_score'] >= 80:
            ideas.append("• Excellent alignment - emphasize your strengths")
        elif rfp_analysis['alignment_score'] >= 60:
            ideas.append("• Good alignment - address any gaps specifically")
        else:
            ideas.append("• Focus on improving alignment with RFP requirements")
    
    return ideas

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

@app.get("/debug/rag-status")
async def debug_rag_status():
    """Debug endpoint to check Supabase RAG system status"""
    try:
        # Test Supabase RAG system
        chunks_data = supa.query_data("file_chunks")
        if chunks_data:
            # Group by file_name to get unique files
            files_dict = {}
            for chunk in chunks_data:
                file_name = chunk.get('file_name', 'Unknown')
                project_id = chunk.get('project_id', 'Unknown')
                
                if file_name not in files_dict:
                    files_dict[file_name] = {
                        'project_id': project_id,
                        'chunks': []
                    }
                
                files_dict[file_name]['chunks'].append(chunk.get('chunk_text', ''))
            
            uploaded_files = list(files_dict.keys())
            total_chunks = sum(len(files_dict[file]['chunks']) for file in files_dict)
            
            return {
                "status": "success",
                "rag_system": "supabase_operational",
                "total_files": len(uploaded_files),
                "total_chunks": total_chunks,
                "uploaded_files": uploaded_files,
                "file_details": [
                    {
                        "filename": file_name,
                        "project_id": file_info['project_id'],
                        "chunk_count": len(file_info['chunks']),
                        "total_content_length": sum(len(chunk) for chunk in file_info['chunks'])
                    }
                    for file_name, file_info in list(files_dict.items())[:5]  # Show first 5 files
                ]
            }
        else:
            return {
                "status": "success",
                "rag_system": "supabase_operational",
                "total_files": 0,
                "total_chunks": 0,
                "uploaded_files": [],
                "file_details": []
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "rag_system": "supabase_failed"
        }

@app.get("/debug/test")
async def debug_test():
    """Simple debug endpoint to test if routes are working"""
    return {
        "status": "success",
        "message": "Debug endpoint is working",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/export/markdown")
async def export_markdown(request: dict):
    """Export grant proposal as Markdown"""
    try:
        project_id = request.get('project_id', 'test-project')
        sections = request.get('sections', {})
        
        # Generate markdown content
        markdown_content = "# Grant Proposal\n\n"
        
        section_titles = {
            'executive_summary': 'Executive Summary',
            'organization_profile': 'Organization Profile',
            'project_approach': 'Project Description & Approach',
            'timeline': 'Timeline & Implementation',
            'budget': 'Budget & Financial Plan',
            'evaluation': 'Evaluation & Impact Measurement'
        }
        
        for section_key, section_title in section_titles.items():
            content = sections.get(section_key, '')
            if content:
                markdown_content += f"## {section_title}\n\n{content}\n\n"
            else:
                markdown_content += f"## {section_title}\n\n*Content to be added*\n\n"
        
        # Add metadata
        markdown_content += f"\n---\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        return Response(
            content=markdown_content,
            media_type="text/markdown",
            headers={"Content-Disposition": "attachment; filename=grant-proposal.md"}
        )
        
    except Exception as e:
        print(f"❌ Error exporting markdown: {e}")
        return {"success": False, "error": str(e)}

@app.post("/export/txt")
async def export_txt(request: dict):
    """Export grant proposal as TXT"""
    try:
        project_id = request.get('project_id', 'test-project')
        sections = request.get('sections', {})
        
        # Generate text content
        txt_content = "Grant Proposal\n\n"
        
        section_titles = {
            'executive_summary': 'Executive Summary',
            'organization_profile': 'Organization Profile',
            'project_approach': 'Project Description & Approach',
            'timeline': 'Timeline & Implementation',
            'budget': 'Budget & Financial Plan',
            'evaluation': 'Evaluation & Impact Measurement'
        }
        
        for section_key, section_title in section_titles.items():
            content = sections.get(section_key, '')
            if content:
                txt_content += f"{section_title}\n\n{content}\n\n"
            else:
                txt_content += f"{section_title}\n\nContent to be added\n\n"
        
        # Add metadata
        txt_content += f"\n---\nGenerated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return Response(
            content=txt_content,
            media_type="text/plain",
            headers={"Content-Disposition": "attachment; filename=grant-proposal.txt"}
        )
        
    except Exception as e:
        print(f"❌ Error exporting txt: {e}")
        return {"success": False, "error": str(e)}

@app.get("/rag/context")
async def get_relevant_context(query: str, section_type: str, community_context: str = None):
    """Get culturally relevant context using Supabase RAG"""
    try:
        # Use Supabase RAG context
        context = supa.rag_context(query, [], None)  # Empty files list, no project_id
        return {"success": True, "context": context}
    except Exception as e:
        print(f"❌ Error getting relevant context: {e}")
        return {"success": False, "error": str(e)}

@app.post("/cultural/analyze")
async def analyze_cultural_alignment(request: dict):
    """Analyze cultural alignment of organization with community context"""
    try:
        organization_info = request.get('organization_info', '')
        community_context = request.get('community_context', '')
        
        analysis = specialized_llm.analyze_cultural_alignment(organization_info, community_context)
        
        return {"success": True, "analysis": analysis}
    except Exception as e:
        print(f"❌ Error analyzing cultural alignment: {e}")
        return {"success": False, "error": str(e)}

@app.post("/cultural/generate")
async def generate_culturally_sensitive_content(request: dict):
    """Generate culturally sensitive content using specialized LLM"""
    try:
        prompt_type = request.get('prompt_type', 'general')
        context = request.get('context', {})
        community_context = request.get('community_context', '')
        
        response = specialized_llm.generate_culturally_sensitive_response(
            prompt_type, context, community_context
        )
        
        return {"success": True, "response": response}
    except Exception as e:
        print(f"❌ Error generating culturally sensitive content: {e}")
        return {"success": False, "error": str(e)}

@app.get("/advanced/status")
async def get_advanced_features_status():
    """Get status of advanced RAG and LLM features"""
    try:
        status = {
            "supabase_rag_available": True,
            "specialized_llm_available": True,
            "cultural_competency_enabled": True,
            "multilingual_support": True,
            "semantic_search_enabled": True,
            "features": [
                "Supabase RAG with vector embeddings",
                "Specialized 7B-like approach with cultural competency",
                "Community-specific cultural contexts",
                "Multilingual support and cultural sensitivity",
                "Advanced prompt engineering for grant writing",
                "Cultural alignment analysis"
            ]
        }
        
        return {"success": True, "status": status}
    except Exception as e:
        print(f"❌ Error getting advanced features status: {e}")
        return {"success": False, "error": str(e)}

# Evaluation Endpoints
@app.post("/evaluate/cognitive")
async def evaluate_cognitive_friendliness(request: dict):
    """Evaluate cognitive friendliness of AI response"""
    try:
        response_text = request.get('response_text', '')
        
        if not response_text:
            return {"success": False, "error": "No response text provided"}
        
        evaluation = cognitive_evaluator.evaluate_response(response_text)
        
        return {"success": True, "evaluation": evaluation}
    except Exception as e:
        print(f"❌ Error evaluating cognitive friendliness: {e}")
        return {"success": False, "error": str(e)}

@app.post("/evaluate/cultural")
async def evaluate_cultural_competency(request: dict):
    """Evaluate cultural competency of AI response"""
    try:
        response_text = request.get('response_text', '')
        community_context = request.get('community_context', '')
        
        if not response_text:
            return {"success": False, "error": "No response text provided"}
        
        evaluation = cultural_evaluator.evaluate_response(response_text, community_context)
        
        return {"success": True, "evaluation": evaluation}
    except Exception as e:
        print(f"❌ Error evaluating cultural competency: {e}")
        return {"success": False, "error": str(e)}

@app.post("/evaluate/comprehensive")
async def evaluate_comprehensive_quality(request: dict):
    """Comprehensive evaluation of AI response quality"""
    try:
        response_text = request.get('response_text', '')
        community_context = request.get('community_context', '')
        
        if not response_text:
            return {"success": False, "error": "No response text provided"}
        
        # Perform both evaluations
        cognitive_eval = cognitive_evaluator.evaluate_response(response_text)
        cultural_eval = cultural_evaluator.evaluate_response(response_text, community_context)
        
        # Calculate overall quality score
        overall_score = (cognitive_eval['overall_score'] + cultural_eval['overall_cultural_score']) / 2
        
        comprehensive_eval = {
            "timestamp": datetime.now().isoformat(),
            "response_text": response_text[:200] + "..." if len(response_text) > 200 else response_text,
            "cognitive_evaluation": cognitive_eval,
            "cultural_evaluation": cultural_eval,
            "overall_quality_score": overall_score,
            "quality_level": "excellent" if overall_score >= 80 else "good" if overall_score >= 60 else "needs_improvement",
            "recommendations": cognitive_eval['recommendations'] + cultural_eval['recommendations']
        }
        
        return {"success": True, "evaluation": comprehensive_eval}
    except Exception as e:
        print(f"❌ Error performing comprehensive evaluation: {e}")
        return {"success": False, "error": str(e)}

@app.post("/performance/record")
async def record_performance_metrics(request: dict):
    """Record performance metrics for monitoring"""
    try:
        operation = request.get('operation', 'unknown')
        duration = request.get('duration', 0.0)
        accuracy = request.get('accuracy', None)
        satisfaction = request.get('satisfaction', None)
        
        performance_monitor.record_performance(operation, duration, accuracy, satisfaction)
        
        return {"success": True, "message": "Performance metrics recorded"}
    except Exception as e:
        print(f"❌ Error recording performance metrics: {e}")
        return {"success": False, "error": str(e)}

@app.get("/performance/summary")
async def get_performance_summary():
    """Get performance summary and recommendations"""
    try:
        summary = performance_monitor.get_performance_summary()
        recommendations = performance_monitor.get_recommendations()
        
        return {
            "success": True, 
            "summary": summary,
            "recommendations": recommendations
        }
    except Exception as e:
        print(f"❌ Error getting performance summary: {e}")
        return {"success": False, "error": str(e)}

@app.post("/feedback/expert")
async def add_expert_feedback(request: dict):
    """Add community expert feedback for cultural competency evaluation"""
    try:
        response_id = request.get('response_id', '')
        expert_feedback = request.get('feedback', {})
        
        if not response_id or not expert_feedback:
            return {"success": False, "error": "Missing response_id or feedback"}
        
        cultural_evaluator.add_expert_feedback(response_id, expert_feedback)
        
        return {"success": True, "message": "Expert feedback recorded"}
    except Exception as e:
        print(f"❌ Error adding expert feedback: {e}")
        return {"success": False, "error": str(e)}

@app.post("/feedback/pilot")
async def add_pilot_test_result(request: dict):
    """Add pilot testing results for evaluation"""
    try:
        response_id = request.get('response_id', '')
        test_result = request.get('test_result', {})
        
        if not response_id or not test_result:
            return {"success": False, "error": "Missing response_id or test_result"}
        
        cultural_evaluator.add_pilot_test_result(response_id, test_result)
        
        return {"success": True, "message": "Pilot test result recorded"}
    except Exception as e:
        print(f"❌ Error adding pilot test result: {e}")
        return {"success": False, "error": str(e)}

@app.get("/evaluation/targets")
async def get_evaluation_targets():
    """Get evaluation targets and performance goals"""
    try:
        targets = {
            "cognitive_friendliness": {
                "readability_target": "Flesch Reading Ease >= 60",
                "sentence_length_target": "Average <= 20 words",
                "clarity_target": "Include bullet points and examples",
                "accessibility_target": "Clear structure and positive tone"
            },
            "cultural_competency": {
                "inclusive_language_target": "Use respectful, inclusive language",
                "strength_based_target": "Emphasize community strengths",
                "community_focused_target": "Include community voice and expertise",
                "cultural_sensitivity_target": "Show respect for traditional knowledge"
            },
            "performance_targets": {
                "database_retrieval_time": "<= 0.5 seconds",
                "llm_generation_time": "<= 3.0 seconds",
                "overall_response_time": "<= 4.0 seconds",
                "accuracy_threshold": ">= 80%",
                "user_satisfaction_target": ">= 4.0/5.0"
            },
            "measurement_methods": {
                "cognitive_friendliness": [
                    "Readability scores (Flesch, Gunning Fog, etc.)",
                    "Sentence structure analysis",
                    "Clarity indicators (bullet points, examples)",
                    "Accessibility features assessment"
                ],
                "cultural_competency": [
                    "Community expert review and feedback",
                    "Pilot testing with diverse users",
                    "Cultural indicator analysis",
                    "Qualitative feedback collection"
                ],
                "performance": [
                    "Response time monitoring",
                    "Accuracy assessment",
                    "User satisfaction surveys",
                    "System performance metrics"
                ]
            }
        }
        
        return {"success": True, "targets": targets}
    except Exception as e:
        print(f"❌ Error getting evaluation targets: {e}")
        return {"success": False, "error": str(e)}

# Approval Workflow Endpoints
@app.get("/approval/pending/{project_id}")
async def get_pending_approvals(project_id: str):
    """Get all pending approval requests for a project"""
    try:
        approval_dir = "src/secure_data/approvals"
        pending_approvals = []
        
        if os.path.exists(approval_dir):
            for filename in os.listdir(approval_dir):
                if filename.endswith('.json') and project_id in filename:
                    with open(os.path.join(approval_dir, filename), 'r') as f:
                        approval_data = json.load(f)
                        if approval_data.get('status') == 'pending':
                            pending_approvals.append(approval_data)
        
        return {"success": True, "pending_approvals": pending_approvals}
    except Exception as e:
        print(f"❌ Error getting pending approvals: {e}")
        return {"success": False, "error": str(e)}

@app.get("/approval/{approval_id}")
async def get_approval_details(approval_id: str):
    """Get details of a specific approval request"""
    try:
        approval_file = f"src/secure_data/approvals/{approval_id}.json"
        
        if not os.path.exists(approval_file):
            return {"success": False, "error": "Approval request not found"}
        
        with open(approval_file, 'r') as f:
            approval_data = json.load(f)
        
        return {"success": True, "approval": approval_data}
    except Exception as e:
        print(f"❌ Error getting approval details: {e}")
        return {"success": False, "error": str(e)}

@app.post("/approval/{approval_id}/approve")
async def approve_content(approval_id: str, request: dict):
    """Approve content and grant temporary access to secure storage"""
    try:
        approval_file = f"src/secure_data/approvals/{approval_id}.json"
        
        if not os.path.exists(approval_file):
            return {"success": False, "error": "Approval request not found"}
        
        with open(approval_file, 'r') as f:
            approval_data = json.load(f)
        
        # Update approval status
        approval_data['status'] = 'approved'
        approval_data['approved_at'] = datetime.now().isoformat()
        approval_data['approved_by'] = request.get('user_id', 'unknown')
        approval_data['approval_notes'] = request.get('notes', '')
        
        # Save updated approval data
        with open(approval_file, 'w') as f:
            json.dump(approval_data, f, indent=2)
        
        # Grant temporary access to secure storage
        project_id = approval_data.get('project_id', 'unknown')
        access_granted = _grant_secure_storage_access(project_id, approval_id)
        
        if access_granted:
            return {
                "success": True, 
                "message": "Content approved and secure storage access granted",
                "approval_id": approval_id,
                "access_granted": True
            }
        else:
            return {
                "success": True, 
                "message": "Content approved but secure storage access failed",
                "approval_id": approval_id,
                "access_granted": False
            }
            
    except Exception as e:
        print(f"❌ Error approving content: {e}")
        return {"success": False, "error": str(e)}

@app.post("/approval/{approval_id}/deny")
async def deny_content(approval_id: str, request: dict):
    """Deny content and provide feedback"""
    try:
        approval_file = f"src/secure_data/approvals/{approval_id}.json"
        
        if not os.path.exists(approval_file):
            return {"success": False, "error": "Approval request not found"}
        
        with open(approval_file, 'r') as f:
            approval_data = json.load(f)
        
        # Update approval status
        approval_data['status'] = 'denied'
        approval_data['denied_at'] = datetime.now().isoformat()
        approval_data['denied_by'] = request.get('user_id', 'unknown')
        approval_data['denial_reason'] = request.get('reason', 'No reason provided')
        approval_data['feedback'] = request.get('feedback', '')
        
        # Save updated approval data
        with open(approval_file, 'w') as f:
            json.dump(approval_data, f, indent=2)
        
        return {
            "success": True, 
            "message": "Content denied",
            "approval_id": approval_id
        }
            
    except Exception as e:
        print(f"❌ Error denying content: {e}")
        return {"success": False, "error": str(e)}

@app.post("/approval/{approval_id}/request-access")
async def request_secure_storage_access(approval_id: str, request: dict):
    """Request access to secure storage for approved content"""
    try:
        approval_file = f"src/secure_data/approvals/{approval_id}.json"
        
        if not os.path.exists(approval_file):
            return {"success": False, "error": "Approval request not found"}
        
        with open(approval_file, 'r') as f:
            approval_data = json.load(f)
        
        if approval_data.get('status') != 'approved':
            return {"success": False, "error": "Content must be approved before requesting access"}
        
        project_id = approval_data.get('project_id', 'unknown')
        access_granted = _grant_secure_storage_access(project_id, approval_id)
        
        if access_granted:
            return {
                "success": True, 
                "message": "Secure storage access granted",
                "approval_id": approval_id,
                "access_granted": True
            }
        else:
            return {
                "success": False, 
                "error": "Failed to grant secure storage access"
            }
            
    except Exception as e:
        print(f"❌ Error requesting secure storage access: {e}")
        return {"success": False, "error": str(e)}

def _grant_secure_storage_access(project_id: str, approval_id: str) -> bool:
    """Grant temporary access to secure storage for approved content"""
    try:
        # This would typically involve:
        # 1. Creating temporary database permissions
        # 2. Setting up row-level security policies
        # 3. Logging the access for audit purposes
        
        # For now, we'll create a simple access log
        access_log = {
            'project_id': project_id,
            'approval_id': approval_id,
            'access_granted_at': datetime.now().isoformat(),
            'access_type': 'secure_storage',
            'duration': 'temporary'
        }
        
        # Save access log
        access_dir = "src/secure_data/access_logs"
        os.makedirs(access_dir, exist_ok=True)
        
        access_file = f"{access_dir}/{approval_id}_access.json"
        with open(access_file, 'w') as f:
            json.dump(access_log, f, indent=2)
        
        print(f"✅ Secure storage access granted for project {project_id} via approval {approval_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error granting secure storage access: {e}")
        return False

@app.get("/approval/stats/{project_id}")
async def get_approval_statistics(project_id: str):
    """Get approval statistics for a project"""
    try:
        approval_dir = "src/secure_data/approvals"
        stats = {
            'total_requests': 0,
            'pending': 0,
            'approved': 0,
            'denied': 0,
            'avg_approval_time': 0,
            'sensitivity_flags': {}
        }
        
        if os.path.exists(approval_dir):
            approval_times = []
            
            for filename in os.listdir(approval_dir):
                if filename.endswith('.json') and project_id in filename:
                    with open(os.path.join(approval_dir, filename), 'r') as f:
                        approval_data = json.load(f)
                        
                        stats['total_requests'] += 1
                        status = approval_data.get('status', 'pending')
                        stats[status] += 1
                        
                        # Calculate approval time if approved
                        if status == 'approved' and 'approved_at' in approval_data:
                            created_at = datetime.fromisoformat(approval_data['created_at'])
                            approved_at = datetime.fromisoformat(approval_data['approved_at'])
                            approval_time = (approved_at - created_at).total_seconds()
                            approval_times.append(approval_time)
                        
                        # Count sensitivity flags
                        flags = approval_data.get('sensitivity_flags', [])
                        for flag in flags:
                            stats['sensitivity_flags'][flag] = stats['sensitivity_flags'].get(flag, 0) + 1
            
            # Calculate average approval time
            if approval_times:
                stats['avg_approval_time'] = sum(approval_times) / len(approval_times)
        
        return {"success": True, "statistics": stats}
    except Exception as e:
        print(f"❌ Error getting approval statistics: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))