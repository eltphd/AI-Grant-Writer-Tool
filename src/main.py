from fastapi import FastAPI, Request
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

# Optional: import your utility module safely
try:
    from utils import file_utils  # from src/utils/file_utils.py
    from utils import openai_utils  # from src/utils/openai_utils.py
except ImportError as e:
    print(f"[Startup Warning] Could not import utils modules: {e}")

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
    return JSONResponse(
        content={"status": "ok", "message": "Backend is working!", "timestamp": datetime.now().isoformat()},
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
            # TODO: Implement project context retrieval from database
            project_context = f"Project ID: {project_id}"
        
        # Generate AI response using OpenAI
        ai_response = openai_utils.generate_grant_response(question, project_context)
        
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
            # TODO: Implement project context retrieval from database
            project_context = f"Project ID: {project_id}"
        
        # Generate AI response using OpenAI
        ai_response = openai_utils.chat_grant_assistant(message, project_context)
        
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
            # TODO: Implement project context retrieval from database
            project_context = f"Project ID: {project_id}"
        
        # Generate brainstorming ideas using OpenAI
        ideas = openai_utils.brainstorm_grant_ideas(topic, project_context)
        
        return ideas
    except Exception as e:
        print(f"❌ Error in /chat/brainstorm: {e}")
        return {"error": str(e)}

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