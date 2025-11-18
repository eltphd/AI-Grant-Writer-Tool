# How to Launch AI Grant Writer Tool

## Option 1: Direct Python Launch (Recommended for Development)

```bash
cd /Users/tarttphd/Documents/GitHub/AI-Grant-Writer-Tool

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Set environment variables (or use .env file)
export OPENAI_API_KEY=your_key
export SUPABASE_URL=your_url
export SUPABASE_KEY=your_key
export AI_GATEWAY_API_KEY=your_key

# Launch the FastAPI server
python -m uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

Or using the built-in main:

```bash
cd /Users/tarttphd/Documents/GitHub/AI-Grant-Writer-Tool
python src/main.py
```

## Option 2: Using Docker Compose

```bash
cd /Users/tarttphd/Documents/GitHub/AI-Grant-Writer-Tool
docker-compose up --build
```

## Option 3: Python Module Launch

```python
# From the repository root directory
import os
import sys
sys.path.insert(0, 'src')

from main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8080))
    )
```

## Quick Launch Script

Save this as `launch.py` in the repository root:

```python
#!/usr/bin/env python3
"""Launch script for AI Grant Writer Tool"""
import os
import sys
from pathlib import Path

# Add src to path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root / "src"))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Launch app
if __name__ == "__main__":
    import uvicorn
    from main import app
    
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting AI Grant Writer Tool on http://{host}:{port}")
    print(f"📚 API docs available at http://{host}:{port}/docs")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=True  # Auto-reload on code changes
    )
```

Then run:
```bash
python launch.py
```

## Environment Variables Required

Create a `.env` file in the repository root:

```bash
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_role_key
AI_GATEWAY_API_KEY=your_vercel_ai_gateway_key
PORT=8080
HOST=0.0.0.0
```

## Access the Application

Once launched:
- **API**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs
- **Test Endpoint**: http://localhost:8080/test

