#!/usr/bin/env python3
"""Launch script for AI Grant Writer Tool"""
import os
import sys
from pathlib import Path

# Add src to path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root / "src"))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    print("   Or set environment variables manually")

# Launch app
if __name__ == "__main__":
    import uvicorn
    
    try:
        from main import app
    except ImportError as e:
        print(f"❌ Error importing app: {e}")
        print("   Make sure you're in the repository root directory")
        sys.exit(1)
    
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting AI Grant Writer Tool")
    print(f"📍 Server: http://{host}:{port}")
    print(f"📚 API docs: http://{host}:{port}/docs")
    print(f"🧪 Test endpoint: http://{host}:{port}/test")
    print("")
    print("Press Ctrl+C to stop the server")
    print("")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=True  # Auto-reload on code changes
    )

