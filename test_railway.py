#!/usr/bin/env python3
"""
Minimal FastAPI test for Railway deployment
"""

from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="Test API", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Hello World", "timestamp": datetime.now().isoformat()}

@app.get("/test")
async def test():
    return {"message": "Test endpoint working", "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 