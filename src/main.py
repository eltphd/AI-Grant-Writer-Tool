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
except ImportError as e:
    print(f"[Startup Warning] Could not import utils.file_utils: {e}")

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
        print(f"✅ /generate called with data: {data}")
        return {"result": f"Echoing: {data.get('question')}"}
    except Exception as e:
        print(f"❌ Error in /generate: {e}")
        return {"error": str(e)}

# Chat message route
@app.post("/chat/send_message")
async def send_message(request: Request):
    try:
        data = await request.json()
        print(f"✅ /chat/send_message called with data: {data}")
        return {"ai_response": f"Simulated reply: {data.get('message')}"}
    except Exception as e:
        print(f"❌ Error in /chat/send_message: {e}")
        return {"error": str(e)}

# Brainstorming route
@app.post("/chat/brainstorm")
async def brainstorm(request: Request):
    try:
        data = await request.json()
        print(f"✅ /chat/brainstorm called with data: {data}")
        return {
            "ideas": [
                {
                    "area": "Strategy",
                    "suggestions": ["Plan your timeline", "Define outcomes"],
                    "examples": ["Launch pilot in Q2"],
                }
            ]
        }
    except Exception as e:
        print(f"❌ Error in /chat/brainstorm: {e}")
        return {"error": str(e)}