#!/usr/bin/env python3
"""
Railway deployment debug script
"""

import os
import sys

def check_environment():
    """Check if required environment variables are set"""
    print("🔍 Checking environment variables...")
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_SERVICE_KEY', 
        'OPENAI_API_KEY',
        'AI_GATEWAY_API_KEY'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * len(value)}")
        else:
            print(f"❌ {var}: NOT SET")
    
    print(f"✅ PORT: {os.getenv('PORT', 'NOT SET')}")

def check_imports():
    """Check if all required modules can be imported"""
    print("\n🔍 Checking imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
    
    try:
        import uvicorn
        print("✅ Uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
    
    try:
        from utils import supabase_utils
        print("✅ Supabase utils imported successfully")
    except ImportError as e:
        print(f"❌ Supabase utils import failed: {e}")

if __name__ == "__main__":
    print("🚀 Railway Debug Script")
    print("=" * 30)
    
    check_environment()
    check_imports()
    
    print("\n✅ Debug script completed") 