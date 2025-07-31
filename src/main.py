from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import sys
import traceback

print("🚀 Starting FastAPI application...")

# Optional: Load .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded .env file")
except ImportError:
    print("python-dotenv not installed. Skipping .env loading.")
except Exception as e:
    print(f"⚠️ Error loading .env: {e}")

# Debug environment variables at startup
import os
print("🔧 Environment variables at startup:")
print(f"🔧 OPENAI_API_KEY: {'set' if os.getenv('OPENAI_API_KEY') else 'not set'}")
print(f"🔧 USE_SUPABASE: {os.getenv('USE_SUPABASE', 'not set')}")
print(f"🔧 SUPABASE_URL: {'set' if os.getenv('SUPABASE_URL') else 'not set'}")
print(f"🔧 DB_HOSTNAME: {os.getenv('DB_HOSTNAME', 'not set')}")
print(f"🔧 PORT: {os.getenv('PORT', 'not set')}")

# Import utility modules
try:
    print("🔧 Attempting to import utils modules...")
    # Add src directory to Python path
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
        print(f"🔧 Added {parent_dir} to Python path")
    
    from src.utils import file_utils
    from src.utils import openai_utils
    from src.utils import storage_utils
    from src.utils import postgres_storage
    from src.utils import config
    from src.utils import privacy_utils
    from src.utils import embedding_utils
    from src.utils import grant_sections
    
    print("✅ Successfully imported utils modules")
    print("✅ file_utils type:", type(file_utils))
    print("✅ openai_utils type:", type(openai_utils))
    print("✅ storage_utils type:", type(storage_utils))
    print("✅ postgres_storage type:", type(postgres_storage))
    print("✅ grant_sections type:", type(grant_sections))
    
except ImportError as e:
    print(f"❌ Error importing utils modules: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("🔧 Initializing FastAPI app...")

# Initialize the app
app = FastAPI()

print("✅ FastAPI app initialized")

@app.on_event("startup")
async def startup_event():
    print("🚀 FastAPI startup event triggered")
    import os
    print(f"🔧 Startup - OPENAI_API_KEY: {'set' if os.getenv('OPENAI_API_KEY') else 'not set'}")
    print(f"🔧 Startup - PORT: {os.getenv('PORT', 'not set')}")
    print(f"🔧 Startup - RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'not set')}")

# Custom CORS middleware to ensure headers are always present
class CustomCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Handle preflight requests
        if request.method == "OPTIONS":
            return Response(
                content="",
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": "https://ai-grant-writer-tool.vercel.app",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Max-Age": "86400",
                }
            )
        
        response = await call_next(request)
        
        # Add CORS headers to all responses
        response.headers["Access-Control-Allow-Origin"] = "https://ai-grant-writer-tool.vercel.app"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response

# Add CORS middleware
app.add_middleware(CustomCORSMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ai-grant-writer-tool.vercel.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add error handler for CORS preflight
@app.options("/{path:path}")
async def options_handler(request: Request):
    return JSONResponse(
        content={}, 
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "https://ai-grant-writer-tool.vercel.app",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )

# Health check route
@app.get("/ping")
def ping():
    print("✅ /ping endpoint called")
    return JSONResponse(
        content={"message": "pong", "timestamp": datetime.now().isoformat()},
        headers={
            "Access-Control-Allow-Origin": "https://ai-grant-writer-tool.vercel.app",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )

# Simple health check that doesn't depend on imports
@app.get("/health")
def health():
    print("✅ /health endpoint called")
    import os
    return JSONResponse(
        content={
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "environment_vars": {
                "OPENAI_API_KEY_set": bool(os.getenv("OPENAI_API_KEY")),
                "PORT": os.getenv("PORT", "not set"),
                "RAILWAY_ENVIRONMENT": os.getenv("RAILWAY_ENVIRONMENT", "not set")
            }
        },
        headers={
            "Access-Control-Allow-Origin": "https://ai-grant-writer-tool.vercel.app",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )

# Super simple test endpoint
@app.get("/simple")
def simple():
    print("✅ /simple endpoint called")
    return JSONResponse(
        content={
            "message": "Simple endpoint working!",
            "timestamp": datetime.now().isoformat()
        },
        headers={
            "Access-Control-Allow-Origin": "https://ai-grant-writer-tool.vercel.app",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )

# Root route to prevent 404 on /
@app.get("/")
def root():
    print("✅ / endpoint called")
    return JSONResponse(
        content={"message": "Hello from FastAPI backend!", "timestamp": datetime.now().isoformat()},
        headers={
            "Access-Control-Allow-Origin": "https://ai-grant-writer-tool.vercel.app",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )

# Test endpoint for connectivity
@app.get("/test")
def test():
    print("✅ /test endpoint called")
    
    # Test OpenAI connection
    openai_status = "unknown"
    api_key_status = "not found"
    
    # Check environment variable directly
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        api_key_status = f"found (length: {len(api_key)}, starts with: {api_key[:7]}...)"
    else:
        api_key_status = "not found in environment"
    
    try:
        response = openai_utils.get_openai_response("Hello", "You are a helpful assistant.", max_tokens=10)
        if response and not response.startswith("⚠️"):
            openai_status = "working"
        else:
            openai_status = f"not working: {response}"
    except Exception as e:
        openai_status = f"error: {str(e)}"
    
    return JSONResponse(
        content={
            "status": "ok", 
            "message": "Backend is working!", 
            "timestamp": datetime.now().isoformat(),
            "openai_status": openai_status,
            "api_key_status": api_key_status,
            "environment_vars": {
                "OPENAI_API_KEY_set": bool(api_key),
                "USE_SUPABASE": os.getenv("USE_SUPABASE", "not set"),
                "SUPABASE_URL_set": bool(os.getenv("SUPABASE_URL")),
                "DB_HOSTNAME": os.getenv("DB_HOSTNAME", "not set")
            }
        },
        headers={
            "Access-Control-Allow-Origin": "https://ai-grant-writer-tool.vercel.app",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )

# Generate route for basic Q&A
@app.post("/generate")
async def generate(request: Request):
    try:
        data = await request.json()
        question = data.get('question', '')
        project_id = data.get('projectId')
        
        print(f"✅ /generate called with question: {question}")
        
        # Get project context if available
        project_context = ""
        if project_id:
            if storage_utils_available:
                project_context = storage_utils.get_context_summary(project_id)
            elif postgres_storage_available:
                project_context = postgres_storage.get_context_summary(project_id)
            else:
                project_context = file_utils.get_context_summary(project_id)
        
        # Generate AI response using OpenAI
        try:
            ai_response = openai_utils.generate_grant_response(question, project_context)
        except Exception as e:
            print(f"❌ OpenAI error: {e}")
            ai_response = f"I'm sorry, I'm having trouble connecting to the AI service right now. Please try again later. Error: {str(e)}"
        
        return {"result": ai_response}
    except Exception as e:
        print(f"❌ Error in /generate: {e}")
        return {"error": str(e)}

# Chat message route
@app.post("/chat/send_message")
async def send_message(request: Request):
    try:
        data = await request.json()
        message = data.get('message', '')
        project_id = data.get('project_id')
        message_type = data.get('message_type', 'user')
        
        print(f"✅ /chat/send_message called with message: {message}")
        
        # Get project context if available
        project_context = ""
        if project_id:
            if storage_utils_available:
                project_context = storage_utils.get_context_summary(project_id)
            elif postgres_storage_available:
                project_context = postgres_storage.get_context_summary(project_id)
            else:
                project_context = file_utils.get_context_summary(project_id)
        
        # Get chat history for RAG context
        chat_history = ""
        if project_id:
            try:
                if storage_utils_available:
                    chat_history = storage_utils.get_chat_history(project_id)
                elif postgres_storage_available:
                    chat_history = postgres_storage.get_chat_history(project_id)
                else:
                    chat_history = file_utils.get_chat_history(project_id)
            except Exception as e:
                print(f"⚠️ Could not retrieve chat history: {e}")
        
        # Get semantic search context for better AI responses
        semantic_context = ""
        if project_id:
            try:
                semantic_context = embedding_utils.embedding_manager.create_context_for_ai(
                    message, project_id, max_context_length=2000
                )
            except Exception as e:
                print(f"⚠️ Could not retrieve semantic context: {e}")
        
        # Combine context for RAG (prioritize semantic search, then chat history, then project context)
        context_parts = []
        if semantic_context:
            context_parts.append(f"Relevant Context: {semantic_context}")
        if chat_history:
            context_parts.append(f"Chat History: {chat_history}")
        if project_context:
            context_parts.append(f"Project Context: {project_context}")
        
        full_context = "\n\n".join(context_parts)
        
        # Generate AI response using OpenAI
        try:
            ai_response = openai_utils.chat_grant_assistant(message, full_context)
            
            # Store the conversation for future RAG
            if project_id:
                conversation_data = {
                    "user_message": message,
                    "ai_response": ai_response,
                    "timestamp": datetime.now().isoformat()
                }
                
                try:
                    if storage_utils_available:
                        storage_utils.save_chat_message(project_id, conversation_data)
                    elif postgres_storage_available:
                        postgres_storage.save_chat_message(project_id, conversation_data)
                    else:
                        file_utils.save_chat_message(project_id, conversation_data)
                except Exception as e:
                    print(f"⚠️ Could not save chat message: {e}")
                    
        except Exception as e:
            print(f"❌ OpenAI chat error: {e}")
            ai_response = f"I'm sorry, I'm having trouble connecting to the AI service right now. Please try again later. Error: {str(e)}"
        
        return {"ai_response": ai_response}
    except Exception as e:
        print(f"❌ Error in /chat/send_message: {e}")
        return {"error": str(e)}

# Brainstorming route
@app.post("/chat/brainstorm")
async def brainstorm(request: Request):
    try:
        data = await request.json()
        topic = data.get('topic', '')
        project_id = data.get('project_id')
        
        print(f"✅ /chat/brainstorm called with topic: {topic}")
        
        # Get project context if available
        project_context = ""
        if project_id:
            if storage_utils_available:
                project_context = storage_utils.get_context_summary(project_id)
            elif postgres_storage_available:
                project_context = postgres_storage.get_context_summary(project_id)
            else:
                project_context = file_utils.get_context_summary(project_id)
        
        # Generate brainstorming ideas using OpenAI
        try:
            ideas = openai_utils.brainstorm_grant_ideas(topic, project_context)
        except Exception as e:
            print(f"❌ OpenAI brainstorm error: {e}")
            ideas = {
                "topic": topic,
                "suggestions": f"I'm sorry, I'm having trouble connecting to the AI service right now. Please try again later. Error: {str(e)}",
                "error": str(e)
            }
        
        return ideas
    except Exception as e:
        print(f"❌ Error in /chat/brainstorm: {e}")
        return {"error": str(e)}

# File upload endpoint
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    project_id: str = Form(...)
):
    try:
        print(f"✅ /upload called for project {project_id}, file: {file.filename}")
        
        # Validate file size (max 10MB)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB
            return {
                "success": False,
                "error": "File size too large. Maximum size is 10MB."
            }
        
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.doc', '.txt', '.md']
        file_extension = '.' + file.filename.split('.')[-1].lower()
        if file_extension not in allowed_extensions:
            return {
                "success": False,
                "error": f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
            }
        
        # Save file and extract context
        if storage_utils_available:
            result = storage_utils.save_uploaded_file(file_content, file.filename, project_id)
        elif postgres_storage_available:
            result = postgres_storage.save_uploaded_file(file_content, file.filename, project_id)
        else:
            result = file_utils.save_uploaded_file(file_content, file.filename, project_id)
        
        if result.get("success"):
            # Process for privacy compliance and create embeddings
            try:
                extracted_text = result.get("extracted_text", "")
                if extracted_text:
                    # Process text for privacy compliance
                    privacy_record = privacy_utils.privacy_manager.process_text_for_storage(
                        extracted_text, project_id, "file_upload"
                    )
                    
                    # Create embeddings for semantic search
                    embeddings = embedding_utils.embedding_manager.create_embeddings_for_text(
                        extracted_text, project_id, "file_upload"
                    )
                    
                    # Add privacy and embedding info to result
                    result["privacy_info"] = {
                        "entities_detected": len(privacy_record["entities"]),
                        "privacy_level": privacy_record["privacy_level"],
                        "redacted_text_length": len(privacy_record["redacted_text"])
                    }
                    result["embedding_info"] = {
                        "embeddings_created": len(embeddings),
                        "chunks_processed": len(embeddings)
                    }
                    
                    print(f"✅ Privacy processing: {len(privacy_record['entities'])} entities detected")
                    print(f"✅ Embeddings created: {len(embeddings)} chunks")
                    
            except Exception as e:
                print(f"⚠️ Privacy/embedding processing error: {e}")
                # Continue with upload even if privacy processing fails
            
            return {
                "success": True,
                "message": f"File {file.filename} uploaded successfully",
                "file_info": result
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown error")
            }
            
    except Exception as e:
        print(f"❌ Error in /upload: {e}")
        return {"success": False, "error": str(e)}

# Get project context
@app.get("/context/{project_id}")
async def get_context(project_id: str):
    try:
        print(f"✅ /context/{project_id} called")
        
        if storage_utils_available:
            context = storage_utils.get_project_context(project_id)
        elif postgres_storage_available:
            context = postgres_storage.get_project_context(project_id)
        else:
            context = file_utils.get_project_context(project_id)
        return context
        
    except Exception as e:
        print(f"❌ Error in /context/{project_id}: {e}")
        return {
            "project_id": project_id,
            "files": [],
            "organization_info": "",
            "initiative_description": "",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "error": str(e)
        }

# Update project information
@app.post("/context/{project_id}")
async def update_context(project_id: str, request: Request):
    try:
        data = await request.json()
        organization_info = data.get('organization_info', '')
        initiative_description = data.get('initiative_description', '')
        
        print(f"✅ /context/{project_id} update called")
        
        if storage_utils_available:
            success = storage_utils.update_project_info(project_id, organization_info, initiative_description)
        elif postgres_storage_available:
            success = postgres_storage.update_project_info(project_id, organization_info, initiative_description)
        else:
            success = file_utils.update_project_info(project_id, organization_info, initiative_description)
        
        if success:
            return {"success": True, "message": "Project information updated successfully"}
        else:
            return {"success": False, "error": "Failed to update project information"}
            
    except Exception as e:
        print(f"❌ Error in /context/{project_id} update: {e}")
        return {"success": False, "error": str(e)}

# Delete project context
@app.delete("/context/{project_id}")
async def delete_context(project_id: str):
    try:
        print(f"✅ /context/{project_id} delete called")
        
        if storage_utils_available:
            success = storage_utils.delete_project_context(project_id)
        elif postgres_storage_available:
            success = postgres_storage.delete_project_context(project_id)
        else:
            success = file_utils.delete_project_context(project_id)
        
        if success:
            return {"success": True, "message": "Project context deleted successfully"}
        else:
            return {"success": False, "error": "Failed to delete project context"}
            
    except Exception as e:
        print(f"❌ Error in /context/{project_id} delete: {e}")
        return {"success": False, "error": str(e)}

# Get chat history for a project
@app.get("/chat/history/{project_id}")
async def get_chat_history(project_id: str):
    try:
        print(f"✅ /chat/history/{project_id} called")
        
        if storage_utils_available:
            messages = storage_utils.get_chat_messages(project_id)
        elif postgres_storage_available:
            messages = postgres_storage.get_chat_messages(project_id)
        else:
            messages = file_utils.get_chat_messages(project_id)
        
        return {
            "project_id": project_id,
            "messages": messages,
            "message_count": len(messages)
        }
        
    except Exception as e:
        print(f"❌ Error in /chat/history/{project_id}: {e}")
        return {
            "project_id": project_id,
            "messages": [],
            "message_count": 0,
            "error": str(e)
        }

# Privacy audit endpoint
@app.get("/privacy/audit/{project_id}")
async def privacy_audit(project_id: str):
    try:
        print(f"✅ /privacy/audit/{project_id} called")
        
        # Get project context for audit
        project_context = ""
        if storage_utils_available:
            project_context = storage_utils.get_context_summary(project_id)
        elif postgres_storage_available:
            project_context = postgres_storage.get_context_summary(project_id)
        else:
            project_context = file_utils.get_context_summary(project_id)
        
        # Get chat messages for audit
        chat_messages = []
        if storage_utils_available:
            chat_messages = storage_utils.get_chat_messages(project_id)
        elif postgres_storage_available:
            chat_messages = postgres_storage.get_chat_messages(project_id)
        else:
            chat_messages = file_utils.get_chat_messages(project_id)
        
        # Create audit records for analysis
        audit_records = []
        
        # Audit project context
        if project_context and project_context != "No context available.":
            audit_records.append({
                "content_type": "project_context",
                "content": project_context,
                "privacy_level": "high" if any(keyword in project_context.lower() for keyword in ['ssn', 'phone', 'email', 'address']) else "low"
            })
        
        # Audit chat messages
        for msg in chat_messages:
            audit_records.append({
                "content_type": "chat_message",
                "content": f"{msg.get('user_message', '')} {msg.get('ai_response', '')}",
                "timestamp": msg.get('timestamp'),
                "privacy_level": "high" if any(keyword in str(msg).lower() for keyword in ['ssn', 'phone', 'email', 'address']) else "low"
            })
        
        # Perform privacy audit
        audit_result = privacy_utils.privacy_manager.audit_privacy_compliance(project_id, audit_records)
        
        return {
            "project_id": project_id,
            "audit_result": audit_result,
            "total_records_audited": len(audit_records),
            "audit_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error in /privacy/audit/{project_id}: {e}")
        return {
            "project_id": project_id,
            "error": str(e),
            "audit_timestamp": datetime.now().isoformat()
        }

# Analyze organization and initiative for grant writing guidance
@app.post("/analyze")
async def analyze_organization(request: Request):
    try:
        data = await request.json()
        organization_info = data.get('organization_info', '')
        initiative_description = data.get('initiative_description', '')
        
        print(f"✅ /analyze called with organization info and initiative description")
        
        # Generate analysis using OpenAI
        analysis = openai_utils.analyze_grant_requirements(organization_info, initiative_description)
        
        return analysis
    except Exception as e:
        print(f"❌ Error in /analyze: {e}")
        return {"error": str(e)}

@app.get("/grant/sections/{project_id}")
async def get_grant_sections(project_id: str):
    """Get grant sections for a project."""
    try:
        # Get or create grant document
        document = grant_sections.grant_section_manager.get_grant_document(project_id)
        if not document:
            document = grant_sections.grant_section_manager.create_grant_document(project_id)
        
        # Return document state
        doc_state = {section_id: section.content for section_id, section in document.sections.items()}
        
        return {
            "success": True,
            "project_id": project_id,
            "doc_state": doc_state,
            "stats": grant_sections.grant_section_manager.get_document_stats(project_id)
        }
    except Exception as e:
        print(f"❌ Error getting grant sections: {e}")
        return {"success": False, "error": str(e)}

@app.post("/grant/sections/{project_id}/{section_id}")
async def update_grant_section(project_id: str, section_id: str, request: dict):
    """Update a specific grant section."""
    try:
        content = request.get("content", "")
        
        # Update section
        result = grant_sections.grant_section_manager.update_section(project_id, section_id, content)
        
        return {
            "success": True,
            "project_id": project_id,
            "section_id": section_id,
            **result
        }
    except Exception as e:
        print(f"❌ Error updating grant section: {e}")
        return {"success": False, "error": str(e)}

@app.post("/grant/sections/{project_id}/{section_id}/regenerate")
async def regenerate_grant_section(project_id: str, section_id: str, request: dict):
    """Regenerate a grant section using AI."""
    try:
        context = request.get("context", "")
        
        # Get project context for AI generation
        project_context = ""
        if config.USE_SUPABASE:
            context_data = storage_utils.get_project_context(project_id)
            if context_data and "organization_info" in context_data:
                project_context = f"Organization: {context_data['organization_info']}\n"
                if "initiative_description" in context_data:
                    project_context += f"Initiative: {context_data['initiative_description']}"
        else:
            context_data = postgres_storage.get_project_context(project_id)
            if context_data and "organization_info" in context_data:
                project_context = f"Organization: {context_data['organization_info']}\n"
                if "initiative_description" in context_data:
                    project_context += f"Initiative: {context_data['initiative_description']}"
        
        # Generate new content using AI
        section_info = grant_sections.grant_section_manager.CORE_SECTIONS.get(section_id, {})
        prompt = f"""
        Generate content for the '{section_info.get('title', 'Grant Section')}' section.
        
        Section Description: {section_info.get('description', '')}
        Target Length: {section_info.get('target_length', '')}
        
        Project Context:
        {project_context}
        
        Additional Context:
        {context}
        
        Please generate comprehensive, professional content for this grant section.
        """
        
        # Get AI response
        ai_response = openai_utils.chat_grant_assistant(prompt, project_id)
        
        # Update section with AI-generated content
        result = grant_sections.grant_section_manager.update_section(project_id, section_id, ai_response)
        
        return {
            "success": True,
            "project_id": project_id,
            "section_id": section_id,
            "ai_generated": True,
            **result
        }
    except Exception as e:
        print(f"❌ Error regenerating grant section: {e}")
        return {"success": False, "error": str(e)}

@app.get("/grant/sections/{project_id}/export/markdown")
async def export_grant_markdown(project_id: str):
    """Export grant document as markdown."""
    try:
        markdown_content = grant_sections.grant_section_manager.export_to_markdown(project_id)
        
        return {
            "success": True,
            "project_id": project_id,
            "content": markdown_content,
            "format": "markdown"
        }
    except Exception as e:
        print(f"❌ Error exporting grant markdown: {e}")
        return {"success": False, "error": str(e)}

@app.get("/grant/sections/{project_id}/export/docx")
async def export_grant_docx(project_id: str):
    """Export grant document as DOCX."""
    try:
        docx_content = grant_sections.grant_section_manager.export_to_docx(project_id)
        
        return {
            "success": True,
            "project_id": project_id,
            "content": docx_content.decode('utf-8'),
            "format": "docx"
        }
    except Exception as e:
        print(f"❌ Error exporting grant DOCX: {e}")
        return {"success": False, "error": str(e)}

@app.get("/grant/sections/{project_id}/stats")
async def get_grant_stats(project_id: str):
    """Get grant document statistics."""
    try:
        stats = grant_sections.grant_section_manager.get_document_stats(project_id)
        
        return {
            "success": True,
            "project_id": project_id,
            **stats
        }
    except Exception as e:
        print(f"❌ Error getting grant stats: {e}")
        return {"success": False, "error": str(e)}

@app.get("/grant/templates")
async def get_grant_templates():
    """Get grant section templates."""
    try:
        templates = grant_sections.grant_section_manager.get_section_templates()
        
        return {
            "success": True,
            **templates
        }
    except Exception as e:
        print(f"❌ Error getting grant templates: {e}")
        return {"success": False, "error": str(e)}