"""Utilities for communicating with the FastAPI back‑end.

This module wraps the HTTP calls made from the Streamlit front‑end to the
FastAPI service.  It provides helper functions for CRUD operations on
projects, files and questions.  See also client_api_utils.py for
client‑specific operations.
"""

import requests
import streamlit as st  # noqa: F401 - imported for side effects of session state
from typing import Any

try:
    import utils.config as config  # type: ignore
except Exception:
    from . import config  # type: ignore


def _parse_result_helper(response: requests.Response, default: Any = {}):
    """Parse JSON from a requests.Response, handling non‑200 codes."""
    if response.status_code == 200:
        try:
            return response.json()
        except Exception:
            return default
    else:
        st.error(f"Status code {response.status_code}", icon="🚨")
        return default


def get_all_records(table_name: str) -> Any:
    """Return all records from a given table by name."""
    try:
        data = {"text": table_name}
        response = requests.post(f"{config.FASTAPI_URL}get_data", json=data)
        return _parse_result_helper(response)
    except Exception as e:
        print(f"ERROR get_all_records: {e}")
        return {}


def get_questions(selected_project: dict) -> Any:
    """Return questions for a given project ID."""
    try:
        params = {"project_id": str(selected_project.get("id"))}
        response = requests.get(f"{config.FASTAPI_URL}get_questions", params=params)
        return _parse_result_helper(response)
    except Exception as e:
        print(f"ERROR get_questions: {e}")
        return {}


def insert_file(filename: str, file: Any) -> int:
    """Upload a file without chunking."""
    try:
        files = {"file": file.getvalue()}
        data = {"file_name": filename}
        response = requests.post(f"{config.FASTAPI_URL}file_upload", files=files, data=data)
        return response.status_code
    except Exception as e:
        print(f"ERROR insert_file: {e}")
        return 500


def insert_file_v2(filename: str, file: Any) -> int:
    """Upload a file and split into chunks on the server side."""
    try:
        files = {"file": file.getvalue()}
        data = {"file_name": filename}
        response = requests.post(f"{config.FASTAPI_URL}file_upload_chunks", files=files, data=data)
        return response.status_code
    except Exception as e:
        print(f"ERROR insert_file_v2: {e}")
        return 500


def insert_text_snippet(text: str) -> int:
    """Upload a snippet of text as a manual file (.manual)."""
    try:
        files = {"file": bytes(text, "utf-8")}
        data = {"file_name": f"{_format_file_name(text)}.manual"}
        response = requests.post(f"{config.FASTAPI_URL}file_upload_chunks", files=files, data=data)
        return response.status_code
    except Exception as e:
        print(f"ERROR insert_text_snippet: {e}")
        return 500


def _format_file_name(file_name: str) -> str:
    file_name = file_name.lower().split(".")[0]
    return "_".join(file_name.split(" ")[:5])


def insert_project(project_name: str, project_description: str, client_id: str | None = None) -> Any:
    """Create a new project via the API.

    A client_id may be supplied to associate this project with an existing client.
    """
    try:
        params = {
            "project_name": project_name,
            "project_description": project_description,
        }
        if client_id:
            params["client_id"] = client_id
        response = requests.post(f"{config.FASTAPI_URL}create_project", params=params)
        return _parse_result_helper(response)
    except Exception as e:
        print(f"ERROR insert_project: {e}")
        return {}


def save_questions(questions: list[dict], selected_project: dict) -> Any:
    """Save a list of questions for a given project ID."""
    try:
        project_id = selected_project.get("id")
        data = {"questions": questions}
        params = {"project_id": project_id}
        response = requests.post(f"{config.FASTAPI_URL}save_questions", json=data, params=params)
        return _parse_result_helper(response)
    except Exception as e:
        print(f"ERROR save_questions: {e}")
        return {}


def check_open_ai_credentials() -> Any:
    """Check that the API has valid OpenAI credentials configured."""
    try:
        response = requests.get(f"{config.FASTAPI_URL}check_credentials")
        return _parse_result_helper(response)
    except Exception as e:
        print(f"ERROR check_open_ai_credentials: {e}")
        return {}


def get_openai_embeddings(text: str) -> Any:
    """Retrieve OpenAI embeddings for a given text via the API."""
    try:
        data = {"text": text}
        response = requests.post(f"{config.FASTAPI_URL}get_embeddings", json=data)
        return _parse_result_helper(response)
    except Exception as e:
        print(f"ERROR get_openai_embeddings: {e}")
        return {}


def ask_rag_question(question: list) -> Any:
    """Ask a question via RAG and return the raw response."""
    try:
        data = {"question": question[1]}
        response = requests.post(f"{config.FASTAPI_URL}ask_auto_gen_question", data=data)
        return _parse_result_helper(response)
    except Exception as e:
        print(f"ERROR ask_rag_question: {e}")
        return {}


def ask_group_chat(qa_problem: str, context: str) -> Any:
    """Ask a question with context via a multi‑agent RAG chat."""
    try:
        data = {"qa_problem": qa_problem, "context": context}
        response = requests.post(f"{config.FASTAPI_URL}construct_agent_group_chat", data=data)
        return _parse_result_helper(response)
    except Exception as e:
        print(f"ERROR ask_group_chat: {e}")
        return {}


def construct_agent() -> Any:
    """Initialize a RAG proxy agent using selected files and project name."""
    try:
        file_paths = st.session_state.get("selected_files")
        project_name = st.session_state.get("selected_project")
        if file_paths and project_name:
            data = {"file_paths": file_paths, "project_name": project_name}
            response = requests.post(f"{config.FASTAPI_URL}construct_agent", data=data)
            return _parse_result_helper(response)
    except Exception as e:
        print(f"ERROR construct_agent: {e}")
    return {}


def get_rag_context(question: list, files: list) -> Any:
    """Retrieve RAG context for a question and list of files."""
    try:
        data = {"question": str(question[4]), "files": files}
        response = requests.post(f"{config.FASTAPI_URL}get_rag_context", data=data)
        return _parse_result_helper(response, default="")
    except Exception as e:
        print(f"ERROR get_rag_context: {e}")
        return ""