from fastapi import FastAPI, Request
import os
from datetime import datetime

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
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["https://ai-grant-writer-tool.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check route
@app.get("/ping")
def ping():
    return {"message": "pong"}

# Root route to prevent 404 on /
@app.get("/")
def root():
    return {"message": "Hello from FastAPI backend!"}

# Generate route for basic Q&A
@app.post("/generate")
async def generate(request: Request):
    data = await request.json()
    return {"result": f"Echoing: {data.get('question')}"}

# Chat message route
@app.post("/chat/send_message")
async def send_message(request: Request):
    data = await request.json()
    return {"ai_response": f"Simulated reply: {data.get('message')}"}

# Brainstorming route
@app.post("/chat/brainstorm")
async def brainstorm(request: Request):
    data = await request.json()
    return {
        "ideas": [
            {
                "area": "Strategy",
                "suggestions": ["Plan your timeline", "Define outcomes"],
                "examples": ["Launch pilot in Q2"],
            }
        ]
    }