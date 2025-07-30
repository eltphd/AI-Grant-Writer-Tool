from fastapi import FastAPI
import os

# Optional: Load .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Skipping .env loading.")

# Optional: import your utility module safely
try:
    from utils import file_utils  # adjust to actual utils file if needed
except ImportError as e:
    print(f"[Startup Warning] Could not import file_utils: {e}")

# Initialize the app
app = FastAPI()

# Health check route
@app.get("/ping")
def ping():
    return {"message": "pong"}

# Root route to prevent 404 on /
@app.get("/")
def root():
    return {"message": "Hello from FastAPI backend!"}

# Optional: more routes here later (e.g., /generate)