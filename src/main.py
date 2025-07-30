import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
"""Main FastAPI app for the AI Grant Writer.

This module defines all HTTP endpoints exposed by the service.  It acts as
the bridge between incoming requests and the database/LLM utilities.
"""

from fastapi import FastAPI, UploadFile, Form, HTTPException, status
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import List, Annotated, Optional, Any, Dict
import uvicorn
import os
from fastapi.staticfiles import StaticFiles
import os
import io
import json
import zipfile
from datetime import datetime

# Read OpenAI API key from environment.  Replace this with your own key or
# integrate with a different provider as needed.
open_api_key = os.environ.get("OPENAI_API_KEY", "PLACE_YOUR_KEY_HERE")

# Local imports.  When running as a package (e.g. via docker), the src
# prefix will be available.  When running locally, fallback to relative
# imports to keep things working during development.
try:
    import src.utils.config as config  # type: ignore
    # Conditionally import either the Supabase or pgvector utility module
    if config.USE_SUPABASE:
        import src.utils.supabase_utils as db_utils  # type: ignore
    else:
        import src.utils.pgvector_utils as db_utils  # type: ignore
    import src.utils.langchain_utils as langchain_utils  # type: ignore
    import src.utils.auto_gen_utils as auto_gen_utils  # type: ignore
    import src.utils.utils as utils  # type: ignore
except Exception:
    import utils.config as config  # type: ignore
    if config.USE_SUPABASE:
        import utils.supabase_utils as db_utils  # type: ignore
    else:
        import utils.pgvector_utils as db_utils  # type: ignore
    import utils.langchain_utils as langchain_utils  # type: ignore
    import utils.auto_gen_utils as auto_gen_utils  # type: ignore
    import utils.utils as utils  # type: ignore

app = FastAPI()


class Text(BaseModel):
    text: str


class Question(BaseModel):
    question: str
    answer: str
    project_id: int
    embedding: str
    chat_history: str


class Questions(BaseModel):
    questions: List[Question]


# New Pydantic models for client management
class Client(BaseModel):
    name: str
    organization: str
    contact_info: str
    demographics: str
    goals: str


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    organization: Optional[str] = None
    contact_info: Optional[str] = None
    demographics: Optional[str] = None
    goals: Optional[str] = None


class ChatMessage(BaseModel):
    message: str
    project_id: Optional[int] = None
    message_type: str = "user"  # "user" or "assistant"
    context: Optional[str] = None


class ChatSession(BaseModel):
    project_id: int
    session_name: str
    messages: List[ChatMessage] = []


class BrainstormingRequest(BaseModel):
    topic: str
    project_id: Optional[int] = None
    context: Optional[str] = None
    focus_areas: Optional[List[str]] = None


@app.get("/healthcheck")
async def healthcheck() -> str:
    """Simple health check endpoint."""
    return "OK"


@app.get("/check_credentials")
async def check_credentials() -> str | None:
    """Check that an OpenAI API key has been configured."""
    if open_api_key != "PLACE_YOUR_KEY_HERE":
        return "OK"
    return None


# -----------------------------------------------------------------------------
# Client management endpoints
# -----------------------------------------------------------------------------

@app.post("/create_client")
async def create_client(client: Client):
    """Create a new client in the database."""
    if db_utils.insert_client(client):
        return {"clientName": client.name}
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=config.ERROR_MESSAGE,
    )


@app.get("/get_clients")
def get_clients():
    """Return all clients in the database."""
    result = db_utils.query_data("clients")
    if result is not False:
        return result
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=config.ERROR_MESSAGE,
    )


@app.put("/update_client/{client_id}")
async def update_client(client_id: int, client: ClientUpdate):
    """Update an existing client's details."""
    if db_utils.update_client(client_id, client):
        return {"clientId": client_id}
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=config.ERROR_MESSAGE,
    )


# -----------------------------------------------------------------------------
# Chat and Brainstorming endpoints
# -----------------------------------------------------------------------------

@app.post("/chat/send_message")
async def send_chat_message(chat_message: ChatMessage):
    """Send a chat message and get AI response."""
    try:
        # Get context from project files if project_id is provided
        context = ""
        if chat_message.project_id:
            # Get project files and their content for context
            project_files = db_utils.query_data("files")  # You might need to filter by project_id
            if project_files:
                context = "Project context available for reference."
        
        # Generate AI response based on message and context
        ai_response = generate_chat_response(chat_message.message, context, chat_message.context)
        
        # Save the conversation to database
        if chat_message.project_id:
            db_utils.save_chat_message(chat_message.project_id, chat_message.message, ai_response)
        
        return {
            "user_message": chat_message.message,
            "ai_response": ai_response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}"
        )


@app.post("/chat/brainstorm")
async def brainstorm_ideas(brainstorm_request: BrainstormingRequest):
    """Generate brainstorming ideas for mission, vision, or other topics."""
    try:
        ideas = generate_brainstorming_ideas(
            brainstorm_request.topic,
            brainstorm_request.context,
            brainstorm_request.focus_areas
        )
        
        return {
            "topic": brainstorm_request.topic,
            "ideas": ideas,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating brainstorming ideas: {str(e)}"
        )


@app.get("/chat/sessions/{project_id}")
async def get_chat_sessions(project_id: int):
    """Get all chat sessions for a project."""
    try:
        sessions = db_utils.get_chat_sessions(project_id)
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving chat sessions: {str(e)}"
        )


@app.get("/chat/messages/{session_id}")
async def get_chat_messages(session_id: int):
    """Get all messages for a specific chat session."""
    try:
        messages = db_utils.get_chat_messages(session_id)
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving chat messages: {str(e)}"
        )


def generate_chat_response(user_message: str, project_context: str = "", additional_context: str = "") -> str:
    """Generate AI response for chat messages."""
    # This is a simplified response generator
    # In a real implementation, you would use your LLM utilities
    
    context_parts = []
    if project_context:
        context_parts.append(f"Project Context: {project_context}")
    if additional_context:
        context_parts.append(f"Additional Context: {additional_context}")
    
    context_text = " ".join(context_parts)
    
    # Use the existing langchain utilities to generate response
    if hasattr(langchain_utils, 'generate_response'):
        return langchain_utils.generate_response(user_message, context_text)
    else:
        # Fallback response generation
        return f"""Thank you for your question about "{user_message}". 

Based on grant writing best practices, here are some key considerations:

1. **Clarity and Specificity**: Ensure your writing is clear and specific
2. **Evidence-Based**: Support your claims with concrete evidence
3. **Alignment**: Make sure your proposal aligns with the funding agency's mission
4. **Measurable Outcomes**: Include specific, measurable outcomes

{context_text}

Would you like me to elaborate on any of these points or help you with a specific aspect of your grant proposal?"""


def generate_brainstorming_ideas(topic: str, context: str = "", focus_areas: List[str] = None) -> List[dict]:
    """Generate brainstorming ideas for various topics."""
    
    if focus_areas is None:
        focus_areas = ["mission", "vision", "objectives", "strategies"]
    
    ideas = []
    
    for area in focus_areas:
        if area == "mission":
            ideas.append({
                "area": "Mission Statement",
                "suggestions": [
                    "Focus on the core problem your organization solves",
                    "Emphasize the impact on your target population",
                    "Use clear, inspiring language",
                    "Keep it concise but comprehensive"
                ],
                "examples": [
                    "To empower underserved communities through innovative educational programs",
                    "To advance scientific discovery that improves human health and well-being"
                ]
            })
        elif area == "vision":
            ideas.append({
                "area": "Vision Statement",
                "suggestions": [
                    "Describe your ideal future state",
                    "Be aspirational but realistic",
                    "Connect to broader societal impact",
                    "Use forward-looking language"
                ],
                "examples": [
                    "A world where every individual has access to quality education and opportunity",
                    "Leading breakthrough discoveries that transform healthcare delivery"
                ]
            })
        elif area == "objectives":
            ideas.append({
                "area": "Strategic Objectives",
                "suggestions": [
                    "Make objectives SMART (Specific, Measurable, Achievable, Relevant, Time-bound)",
                    "Align with funding agency priorities",
                    "Include both short-term and long-term goals",
                    "Demonstrate clear impact pathways"
                ],
                "examples": [
                    "Increase program participation by 25% within 18 months",
                    "Develop three new partnerships with community organizations by year end"
                ]
            })
        elif area == "strategies":
            ideas.append({
                "area": "Implementation Strategies",
                "suggestions": [
                    "Detail your approach to achieving objectives",
                    "Include stakeholder engagement plans",
                    "Address potential challenges and mitigation strategies",
                    "Show evidence-based methodology"
                ],
                "examples": [
                    "Implement community-based participatory research methods",
                    "Establish partnerships with local healthcare providers"
                ]
            })
    
    return ideas


# -----------------------------------------------------------------------------
# Existing endpoints for projects, files and questions
# -----------------------------------------------------------------------------

@app.post("/create_project")
async def create_project(
    project_name: str,
    project_description: str,
    client_id: Optional[int] = None,
):
    """Create a new project.  Optionally link it to a client via client_id."""
    if db_utils.insert_project(project_name, project_description, client_id):
        return {"projectName": project_name}
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=config.ERROR_MESSAGE,
    )


@app.post("/file_upload")
async def file_upload(
    file_name: Annotated[str, Form(...)],
    file: List[UploadFile],
):
    """Upload a file to the DB."""
    file_bytes = file[0].file.read()
    if file_path := utils.save_file_locally(file_name, file_bytes):
        if db_utils.insert_file(file_name):
            return {"filename": file_name}
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=config.ERROR_MESSAGE,
    )


@app.post("/file_upload_chunks")
async def file_upload_chunks(
    file_name: Annotated[str, Form(...)],
    file: List[UploadFile],
):
    """Upload a file and split it into chunks before inserting."""
    file_obj = file[0].file
    if file_name := utils.save_file_chunks(file_name, file_obj, open_api_key):
        if db_utils.insert_file(file_name):
            return {"filename": file_name}
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=config.ERROR_MESSAGE,
    )


@app.post("/get_data")
def get_data_from_db(text: Text):
    """Return all records from a given table name."""
    result = db_utils.query_data(text.text)
    if result is not False:
        return result
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=config.ERROR_MESSAGE,
    )


@app.get("/get_questions")
def get_questions_from_db(project_id: str):
    """Return all questions for a given project ID."""
    result = db_utils.query_questions(project_id)
    if result is not False:
        return result
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=config.ERROR_MESSAGE,
    )


@app.post("/save_questions")
def save_questions_to_db(project_id: str, questions: Questions):
    """Insert or replace questions into the DB."""
    if db_utils.save_questions(int(project_id), questions):
        return {"result": True}
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=config.ERROR_MESSAGE,
    )


@app.post("/get_embeddings")
def open_ai_embeddings(text: Text):
    """Return embeddings from text via LangChain utilities."""
    result = langchain_utils.get_open_ai_embeddings(text.text)
    if result:
        return result
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=config.ERROR_MESSAGE,
    )


@app.post("/ask_auto_gen_question")
def ask_rag_question(question: Annotated[str, Form(...)]):
    """Ask a question via the RAG agent and return the answer and context."""
    res, context = auto_gen_utils.ask_rag_question_pgvector(question)
    if res and context:
        return res, context
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=config.ERROR_MESSAGE,
    )


@app.post("/construct_agent")
def construct_agent(
    file_paths: Annotated[List[str], Form(...)],
    project_name: Annotated[str, Form(...)],
):
    """Initialize a RAG proxy agent given selected files and a project name."""
    if auto_gen_utils.construct_rag_proxy_agent_pgvector(file_paths, project_name):
        return {}
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=config.ERROR_MESSAGE,
    )


@app.post("/construct_agent_group_chat")
def construct_agent_group_chat(
    qa_problem: Annotated[str, Form(...)],
    context: Annotated[str, Form(...)],
):
    """Construct a multi‑agent AutoGen chat response for a question and context."""
    summary, chat_history = auto_gen_utils.ask_rag_question_maximum_feedback(qa_problem, context)
    if summary and chat_history:
        return {"summary": summary, "chat_history": chat_history}
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=config.ERROR_MESSAGE,
    )


@app.post("/get_rag_context")
def get_rag_context_endpoint(
    question: Annotated[str, Form(...)],
    files: Annotated[List[str], Form(...)],
):
    """Retrieve RAG context for a question given selected files."""
    result = db_utils.rag_context(question, files)
    if result:
        return result
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=config.ERROR_MESSAGE,
    )


# -----------------------------------------------------------------------------
# Data export endpoint
# -----------------------------------------------------------------------------

@app.get("/export_data")
def export_all_data() -> StreamingResponse:
    """Export all data tables as a zipped set of JSON files.

    This endpoint returns a ZIP archive containing JSON representations of the
    clients, projects, files, file_chunks and questions tables.  Each table is
    written to its own file (e.g. ``clients.json``).  If running in Supabase
    mode, the JSON returned by the Supabase API is used directly.  If using
    PostgreSQL, the rows are mapped to dictionaries using known column names.
    """
    try:
        # Fetch raw data from the database via the utility layer
        clients_raw = db_utils.query_data("clients") or []
        projects_raw = db_utils.query_data("projects") or []
        files_raw = db_utils.query_data("files") or []
        chunks_raw = db_utils.query_data("file_chunks") or []
        questions_raw = db_utils.query_data("questions") or []

        def map_rows(rows: List[Any], columns: List[str]) -> List[Dict[str, Any]]:
            """Map a list of row tuples to dictionaries using the provided columns."""
            mapped: List[Dict[str, Any]] = []
            for row in rows:
                # If Supabase returns dicts already, keep them
                if isinstance(row, dict):
                    mapped.append(row)
                else:
                    # Build dict from tuple/list and provided column names
                    try:
                        mapped.append({col: row[idx] for idx, col in enumerate(columns)})
                    except Exception:
                        mapped.append({"data": row})
            return mapped

        # Map rows to dictionaries for PostgreSQL.  If using Supabase these
        # functions will just return the dicts unchanged.
        clients = map_rows(
            clients_raw,
            ["id", "name", "organization", "contact_info", "demographics", "goals", "created_at"],
        )
        projects = map_rows(
            projects_raw,
            ["id", "name", "description", "client_id", "created_at"],
        )
        files = map_rows(
            files_raw,
            ["id", "file_name", "created_at"],
        )
        chunks = map_rows(
            chunks_raw,
            ["id", "file_name", "chunk_text", "embedding", "created_at"],
        )
        questions = map_rows(
            questions_raw,
            ["id", "question", "answer", "project_id", "embedding", "chat_history", "created_at"],
        )

        # Build ZIP archive in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("clients.json", json.dumps(clients, ensure_ascii=False, default=str, indent=2))
            zf.writestr("projects.json", json.dumps(projects, ensure_ascii=False, default=str, indent=2))
            zf.writestr("files.json", json.dumps(files, ensure_ascii=False, default=str, indent=2))
            zf.writestr("file_chunks.json", json.dumps(chunks, ensure_ascii=False, default=str, indent=2))
            zf.writestr("questions.json", json.dumps(questions, ensure_ascii=False, default=str, indent=2))
        zip_buffer.seek(0)
        headers = {"Content-Disposition": "attachment; filename=export_data.zip"}
        return StreamingResponse(zip_buffer, media_type="application/zip", headers=headers)
    except Exception as e:
        # Log the error and raise an HTTP exception
        print("Error exporting data:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=config.ERROR_MESSAGE,
        )

# ----------------------------------------------------------------------------
# React front‑end static file serving
# ----------------------------------------------------------------------------

# Mount the static assets generated by the React build.  When the app is
# containerised, the ``frontend/build`` directory is copied into the image at
# ``/app/frontend/build``.  Serving these files from "/static" allows the
# React app to load its JavaScript, CSS and other assets.
static_dir = os.path.join(os.getcwd(), "frontend", "build")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=os.path.join(static_dir, "static")), name="static")

    @app.get("/{full_path:path}", response_class=HTMLResponse)
    async def serve_react_app(full_path: str) -> HTMLResponse:
        """Serve the React application's index.html for any unknown path.

        This catch‑all route allows React Router to handle client‑side routing.
        It should be defined after all API endpoints so that more specific
        routes (like ``/create_project``) continue to function normally.
        """
        index_file = os.path.join(static_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Frontend not built")


if __name__ == "__main__":
    # Run the app.  When deploying via Docker, the command line will be
    # overridden, so this is mostly for local development.
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)