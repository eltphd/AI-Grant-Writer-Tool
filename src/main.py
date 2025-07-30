from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import json

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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-grant-writer-tool-8of3dhqh8-ericas-projects-637268fc.vercel.app",
        "https://ai-grant-writer-tool-9fymds8sk-ericas-projects-637268fc.vercel.app",
        "https://ai-grant-writer-tool-ericas-projects-637268fc.vercel.app",
        "https://ai-grant-writer-tool-git-main-ericas-projects-637268fc.vercel.app",
        "https://ai-grant-writer-tool.vercel.app",
        "http://localhost:3000",  # for local development
        "*"  # fallback for any other domains
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add error handler for CORS preflight
@app.options("/{path:path}")
async def options_handler(request: Request):
    return JSONResponse(content={}, status_code=200)

# Health check route
@app.get("/ping")
def ping():
    return {"message": "pong"}

# Root route to prevent 404 on /
@app.get("/")
def root():
    return {"message": "Hello from FastAPI backend!"}

# Test endpoint for connectivity
@app.get("/test")
def test():
    return {"status": "ok", "message": "Backend is working!"}

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