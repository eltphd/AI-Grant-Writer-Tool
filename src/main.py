import os
import sys
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import jwt
from passlib.context import CryptContext

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.utils import file_utils, openai_utils, storage_utils, postgres_storage, supabase_utils, privacy_utils, embedding_utils, grant_sections

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Pydantic models for authentication
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Authentication utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(email=email)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = get_user_by_email(token_data.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user from database by email"""
    if config.USE_SUPABASE:
        return supabase_utils.get_user_by_email(email)
    else:
        return postgres_storage.get_user_by_email(email)

def create_user_in_db(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create user in database"""
    if config.USE_SUPABASE:
        return supabase_utils.create_user(user_data)
    else:
        return postgres_storage.create_user(user_data)

# Initialize FastAPI app
app = FastAPI(title="GWAT API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication endpoints
@app.post("/auth/register", response_model=Token)
async def register(user: UserCreate):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user data
        user_data = {
            "id": str(uuid.uuid4()),
            "email": user.email,
            "name": user.name,
            "hashed_password": get_password_hash(user.password),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Save to database
        created_user = create_user_in_db(user_data)
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except Exception as e:
        print(f"❌ Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )

@app.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Login user"""
    try:
        # Get user from database
        user = get_user_by_email(user_credentials.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(user_credentials.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_credentials.email}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except Exception as e:
        print(f"❌ Error logging in user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during login"
        )

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user(current_user: Dict[str, Any] = Depends(verify_token)):
    """Get current user information"""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "name": current_user["name"],
        "created_at": current_user["created_at"]
    }

@app.post("/auth/refresh")
async def refresh_token(current_user: Dict[str, Any] = Depends(verify_token)):
    """Refresh access token"""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# User-specific project endpoints
@app.get("/projects")
async def get_user_projects(current_user: Dict[str, Any] = Depends(verify_token)):
    """Get all projects for the current user"""
    try:
        user_id = current_user["id"]
        if config.USE_SUPABASE:
            projects = supabase_utils.get_user_projects(user_id)
        else:
            projects = postgres_storage.get_user_projects(user_id)
        
        return {"success": True, "projects": projects}
    except Exception as e:
        print(f"❌ Error getting user projects: {e}")
        return {"success": False, "error": str(e)}

@app.post("/projects")
async def create_user_project(
    project_data: dict,
    current_user: Dict[str, Any] = Depends(verify_token)
):
    """Create a new project for the current user"""
    try:
        user_id = current_user["id"]
        project_data["user_id"] = user_id
        project_data["created_at"] = datetime.utcnow()
        project_data["updated_at"] = datetime.utcnow()
        
        if config.USE_SUPABASE:
            project = supabase_utils.create_user_project(project_data)
        else:
            project = postgres_storage.create_user_project(project_data)
        
        return {"success": True, "project": project}
    except Exception as e:
        print(f"❌ Error creating user project: {e}")
        return {"success": False, "error": str(e)}

@app.get("/projects/{project_id}")
async def get_user_project(
    project_id: str,
    current_user: Dict[str, Any] = Depends(verify_token)
):
    """Get a specific project for the current user"""
    try:
        user_id = current_user["id"]
        if config.USE_SUPABASE:
            project = supabase_utils.get_user_project(project_id, user_id)
        else:
            project = postgres_storage.get_user_project(project_id, user_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        return {"success": True, "project": project}
    except Exception as e:
        print(f"❌ Error getting user project: {e}")
        return {"success": False, "error": str(e)}

@app.delete("/projects/{project_id}")
async def delete_user_project(
    project_id: str,
    current_user: Dict[str, Any] = Depends(verify_token)
):
    """Delete a project for the current user"""
    try:
        user_id = current_user["id"]
        if config.USE_SUPABASE:
            success = supabase_utils.delete_user_project(project_id, user_id)
        else:
            success = postgres_storage.delete_user_project(project_id, user_id)
        
        return {"success": success}
    except Exception as e:
        print(f"❌ Error deleting user project: {e}")
        return {"success": False, "error": str(e)}

# Update existing endpoints to be user-specific
@app.post("/upload")
async def upload_file(
    project_id: str,
    file: UploadFile,
    current_user: Dict[str, Any] = Depends(verify_token)
):
    """Upload a file for a specific user's project"""
    try:
        user_id = current_user["id"]
        
        # Verify project belongs to user
        if config.USE_SUPABASE:
            project = supabase_utils.get_user_project(project_id, user_id)
        else:
            project = postgres_storage.get_user_project(project_id, user_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Process file upload
        file_content = await file.read()
        file_info = {
            "filename": file.filename,
            "file_size": len(file_content),
            "content_type": file.content_type,
            "user_id": user_id,
            "project_id": project_id
        }
        
        # Save file and process
        if config.USE_SUPABASE:
            result = supabase_utils.save_file(file_info, file_content)
        else:
            result = file_utils.save_file(file_info, file_content)
        
        # Process for privacy and embeddings
        if result["success"]:
            # Privacy processing
            privacy_result = privacy_utils.privacy_manager.process_text_for_storage(
                result["text_content"], project_id, user_id
            )
            
            # Embedding processing
            embedding_result = embedding_utils.embedding_manager.create_embeddings_for_text(
                privacy_result["redacted_text"], project_id, user_id
            )
        
        return result
        
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return {"success": False, "error": str(e)}

@app.post("/chat/send_message")
async def send_message(
    project_id: str,
    message: dict,
    current_user: Dict[str, Any] = Depends(verify_token)
):
    """Send a chat message for a specific user's project"""
    try:
        user_id = current_user["id"]
        
        # Verify project belongs to user
        if config.USE_SUPABASE:
            project = supabase_utils.get_user_project(project_id, user_id)
        else:
            project = postgres_storage.get_user_project(project_id, user_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Save message with user context
        message_data = {
            "project_id": project_id,
            "user_id": user_id,
            "message": message.get("message", ""),
            "timestamp": datetime.utcnow(),
            "message_type": "user"
        }
        
        if config.USE_SUPABASE:
            supabase_utils.save_chat_message(message_data)
        else:
            postgres_storage.save_chat_message(message_data)
        
        # Get context for AI response
        project_context = ""
        if config.USE_SUPABASE:
            context_data = supabase_utils.get_project_context(project_id, user_id)
        else:
            context_data = postgres_storage.get_project_context(project_id, user_id)
        
        if context_data:
            if "organization_info" in context_data:
                project_context += f"Organization: {context_data['organization_info']}\n"
            if "initiative_description" in context_data:
                project_context += f"Initiative: {context_data['initiative_description']}"
        
        # Get chat history and semantic context
        if config.USE_SUPABASE:
            chat_history = supabase_utils.get_chat_history(project_id, user_id)
            semantic_context = embedding_utils.embedding_manager.create_context_for_ai(
                project_id, user_id, message.get("message", "")
            )
        else:
            chat_history = postgres_storage.get_chat_history(project_id, user_id)
            semantic_context = embedding_utils.embedding_manager.create_context_for_ai(
                project_id, user_id, message.get("message", "")
            )
        
        # Combine context for AI
        full_context = f"{project_context}\n\nChat History: {chat_history}\n\nSemantic Context: {semantic_context}"
        
        # Get AI response
        ai_response = openai_utils.chat_grant_assistant(
            message.get("message", ""), 
            project_id, 
            full_context
        )
        
        # Save AI response
        ai_message_data = {
            "project_id": project_id,
            "user_id": user_id,
            "message": ai_response,
            "timestamp": datetime.utcnow(),
            "message_type": "ai"
        }
        
        if config.USE_SUPABASE:
            supabase_utils.save_chat_message(ai_message_data)
        else:
            postgres_storage.save_chat_message(ai_message_data)
        
        return {
            "success": True,
            "response": ai_response,
            "project_id": project_id
        }
        
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return {"success": False, "error": str(e)}

@app.get("/chat/history/{project_id}")
async def get_chat_history(
    project_id: str,
    current_user: Dict[str, Any] = Depends(verify_token)
):
    """Get chat history for a specific user's project"""
    try:
        user_id = current_user["id"]
        
        # Verify project belongs to user
        if config.USE_SUPABASE:
            project = supabase_utils.get_user_project(project_id, user_id)
        else:
            project = postgres_storage.get_user_project(project_id, user_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if config.USE_SUPABASE:
            messages = supabase_utils.get_chat_messages(project_id, user_id)
        else:
            messages = postgres_storage.get_chat_messages(project_id, user_id)
        
        return {"success": True, "messages": messages}
        
    except Exception as e:
        print(f"❌ Error getting chat history: {e}")
        return {"success": False, "error": str(e)}

# Update context endpoint to be user-specific
@app.post("/context/{project_id}")
async def update_project_context(
    project_id: str,
    context_data: dict,
    current_user: Dict[str, Any] = Depends(verify_token)
):
    """Update project context for a specific user"""
    try:
        user_id = current_user["id"]
        
        # Verify project belongs to user
        if config.USE_SUPABASE:
            project = supabase_utils.get_user_project(project_id, user_id)
        else:
            project = postgres_storage.get_user_project(project_id, user_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        context_data["user_id"] = user_id
        context_data["updated_at"] = datetime.utcnow()
        
        if config.USE_SUPABASE:
            result = supabase_utils.update_project_context(project_id, context_data)
        else:
            result = postgres_storage.update_project_context(project_id, context_data)
        
        return result
        
    except Exception as e:
        print(f"❌ Error updating project context: {e}")
        return {"success": False, "error": str(e)}

# Update grant sections endpoints to be user-specific
@app.get("/grant/sections/{project_id}")
async def get_grant_sections(
    project_id: str,
    current_user: Dict[str, Any] = Depends(verify_token)
):
    """Get grant sections for a specific user's project"""
    try:
        user_id = current_user["id"]
        
        # Verify project belongs to user
        if config.USE_SUPABASE:
            project = supabase_utils.get_user_project(project_id, user_id)
        else:
            project = postgres_storage.get_user_project(project_id, user_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Get or create grant document
        document = grant_sections.grant_section_manager.get_grant_document(project_id, user_id)
        if not document:
            document = grant_sections.grant_section_manager.create_grant_document(project_id, user_id)
        
        # Get chat messages for auto-population
        if config.USE_SUPABASE:
            chat_messages = supabase_utils.get_chat_messages(project_id, user_id)
        else:
            chat_messages = postgres_storage.get_chat_messages(project_id, user_id)
        
        # Auto-populate sections from chat if document is empty
        if document.total_words == 0 and chat_messages:
            grant_sections.grant_section_manager.auto_populate_from_chat(project_id, user_id, chat_messages)
            document = grant_sections.grant_section_manager.get_grant_document(project_id, user_id)
        
        # Prepare response
        sections = {}
        for section_id, section in document.sections.items():
            sections[section_id] = {
                "id": section.id,
                "title": section.title,
                "content": section.content,
                "target_length": section.target_length,
                "description": section.description,
                "word_count": section.word_count,
                "status": section.status,
                "last_updated": section.last_updated
            }
        
        stats = grant_sections.grant_section_manager.get_document_stats(project_id, user_id)
        
        return {
            "success": True,
            "sections": sections,
            "stats": stats,
            "chat_summary": document.chat_summary,
            "last_updated": document.last_updated
        }
        
    except Exception as e:
        print(f"❌ Error getting grant sections: {e}")
        return {"success": False, "error": str(e)}

@app.post("/grant/sections/{project_id}/auto-populate")
async def auto_populate_sections(
    project_id: str,
    current_user: Dict[str, Any] = Depends(verify_token)
):
    """Auto-populate grant sections from chat conversation"""
    try:
        user_id = current_user["id"]
        
        # Verify project belongs to user
        if config.USE_SUPABASE:
            project = supabase_utils.get_user_project(project_id, user_id)
        else:
            project = postgres_storage.get_user_project(project_id, user_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Get chat messages
        if config.USE_SUPABASE:
            chat_messages = supabase_utils.get_chat_messages(project_id, user_id)
        else:
            chat_messages = postgres_storage.get_chat_messages(project_id, user_id)
        
        # Auto-populate sections
        result = grant_sections.grant_section_manager.auto_populate_from_chat(project_id, user_id, chat_messages)
        
        return {
            "success": True,
            "populated_sections": result["populated_sections"],
            "total_sections": result["total_sections"]
        }
        
    except Exception as e:
        print(f"❌ Error auto-populating sections: {e}")
        return {"success": False, "error": str(e)}

@app.get("/grant/sections/{project_id}/export/markdown")
async def export_grant_markdown(
    project_id: str,
    current_user: Dict[str, Any] = Depends(verify_token)
):
    """Export grant document as markdown"""
    try:
        user_id = current_user["id"]
        
        # Verify project belongs to user
        if config.USE_SUPABASE:
            project = supabase_utils.get_user_project(project_id, user_id)
        else:
            project = postgres_storage.get_user_project(project_id, user_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        markdown_content = grant_sections.grant_section_manager.export_to_markdown(project_id, user_id)
        
        from fastapi.responses import Response
        return Response(
            content=markdown_content,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=grant-application-{project_id}.md"}
        )
        
    except Exception as e:
        print(f"❌ Error exporting markdown: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error exporting document"
        )

@app.get("/grant/sections/{project_id}/export/docx")
async def export_grant_docx(
    project_id: str,
    current_user: Dict[str, Any] = Depends(verify_token)
):
    """Export grant document as DOCX"""
    try:
        user_id = current_user["id"]
        
        # Verify project belongs to user
        if config.USE_SUPABASE:
            project = supabase_utils.get_user_project(project_id, user_id)
        else:
            project = postgres_storage.get_user_project(project_id, user_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        docx_content = grant_sections.grant_section_manager.export_to_docx(project_id, user_id)
        
        from fastapi.responses import Response
        return Response(
            content=docx_content,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename=grant-application-{project_id}.docx"}
        )
        
    except Exception as e:
        print(f"❌ Error exporting DOCX: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error exporting document"
        )

# Keep existing endpoints for backward compatibility but add user context
@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "message": "GWAT API is running!",
        "timestamp": datetime.utcnow(),
        "api_key_status": "configured" if os.getenv("OPENAI_API_KEY") else "not configured",
        "environment_vars": {
            "OPENAI_API_KEY": "set" if os.getenv("OPENAI_API_KEY") else "not set",
            "USE_SUPABASE": os.getenv("USE_SUPABASE", "false"),
            "SUPABASE_URL": "set" if os.getenv("SUPABASE_URL") else "not set",
            "DB_HOSTNAME": "set" if os.getenv("DB_HOSTNAME") else "not set",
            "PORT": os.getenv("PORT", "8080")
        }
    }

@app.get("/simple")
async def simple_test():
    """Simple test endpoint"""
    return {"status": "ok", "message": "Simple endpoint working"}

@app.post("/generate")
async def generate_response(request: dict):
    """Generate AI response (legacy endpoint)"""
    try:
        question = request.get("question", "")
        project_id = request.get("project_id", "default")
        
        # Get AI response
        response = openai_utils.chat_grant_assistant(question, project_id)
        
        return {"response": response}
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        return {"error": str(e)}

@app.post("/analyze")
async def analyze_content(request: dict):
    """Analyze content (legacy endpoint)"""
    try:
        content = request.get("content", "")
        analysis_type = request.get("type", "general")
        
        # Get AI analysis
        response = openai_utils.analyze_content(content, analysis_type)
        
        return {"analysis": response}
    except Exception as e:
        print(f"❌ Error analyzing content: {e}")
        return {"error": str(e)}

# Startup event
@app.on_event("startup")
async def startup_event():
    print("🚀 FastAPI startup event triggered")
    print(f"🔧 Startup - OPENAI_API_KEY: {'set' if os.getenv('OPENAI_API_KEY') else 'not set'}")
    print(f"🔧 Startup - PORT: {os.getenv('PORT', '8080')}")
    print(f"🔧 Startup - RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'development')}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))