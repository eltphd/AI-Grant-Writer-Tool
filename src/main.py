from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Optional: Load .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Skipping .env loading.")

# Import utility modules
try:
    from utils import file_utils  # from src/utils/file_utils.py
    from utils import openai_utils  # from src/utils/openai_utils.py
    print("✅ Successfully imported utils modules")
    print(f"✅ file_utils type: {type(file_utils)}")
    print(f"✅ openai_utils type: {type(openai_utils)}")
except ImportError as e:
    print(f"❌ Error importing utils modules: {e}")
    import traceback
    traceback.print_exc()
    # Create dummy modules to prevent crashes
    class DummyFileUtils:
        def save_uploaded_file(self, *args, **kwargs):
            return {"success": False, "error": "File utils not available"}
        def get_project_context(self, *args, **kwargs):
            return {"error": "File utils not available"}
        def update_project_info(self, *args, **kwargs):
            return False
        def delete_project_context(self, *args, **kwargs):
            return False
        def get_context_summary(self, *args, **kwargs):
            return "Context not available"
    
    class DummyOpenAIUtils:
        def get_openai_response(self, *args, **kwargs):
            return "⚠️ OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable to enable AI responses."
        def generate_grant_response(self, *args, **kwargs):
            return "⚠️ OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable to enable AI responses."
        def chat_grant_assistant(self, *args, **kwargs):
            return "⚠️ OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable to enable AI responses."
        def brainstorm_grant_ideas(self, *args, **kwargs):
            return {
                "topic": args[0] if args else "unknown",
                "suggestions": "⚠️ OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable to enable AI responses.",
                "error": "OpenAI utils not available"
            }
        def analyze_grant_requirements(self, *args, **kwargs):
            return {
                "analysis": "⚠️ OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable to enable AI responses.",
                "error": "OpenAI utils not available"
            }
    
    file_utils = DummyFileUtils()
    openai_utils = DummyOpenAIUtils()

# Initialize the app
app = FastAPI()

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
    try:
        if openai_utils.get_openai_response("Hello", "You are a helpful assistant.", max_tokens=10):
            openai_status = "working"
        else:
            openai_status = "not configured"
    except Exception as e:
        openai_status = f"error: {str(e)}"
    
    return JSONResponse(
        content={
            "status": "ok", 
            "message": "Backend is working!", 
            "timestamp": datetime.now().isoformat(),
            "openai_status": openai_status
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
            project_context = file_utils.get_context_summary(project_id)
        
        # Generate AI response using OpenAI
        try:
            ai_response = openai_utils.chat_grant_assistant(message, project_context)
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
        result = file_utils.save_uploaded_file(file_content, file.filename, project_id)
        
        if result.get("success"):
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
        
        success = file_utils.delete_project_context(project_id)
        
        if success:
            return {"success": True, "message": "Project context deleted successfully"}
        else:
            return {"success": False, "error": "Failed to delete project context"}
            
    except Exception as e:
        print(f"❌ Error in /context/{project_id} delete: {e}")
        return {"success": False, "error": str(e)}

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