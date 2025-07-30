"""Utility functions for interacting with a Supabase backend via its REST API.

This module provides a drop‑in replacement for pgvector_utils when the
application is configured to talk to Supabase instead of a local
PostgreSQL database.  It uses the Supabase HTTP endpoints exposed via
PostgREST to perform basic CRUD operations.  Vector search (used for
Retrieval‑Augmented Generation) is not implemented here because the
Supabase REST API does not currently expose pgvector operators via HTTP.

Operations implemented include inserting and updating clients, projects,
files, file chunks, and questions.  Each function returns simple Python
objects (or True/False) similar to pgvector_utils for compatibility with
the rest of the application.  Errors are logged and result in a False
return value or None depending on the context.
"""

from __future__ import annotations

import json
import os
from typing import Any, Iterable, Optional

import requests

# Load Supabase configuration from config.py.  We import lazily to avoid
# circular dependencies when the FastAPI app determines which util module
# to use.  Relative import is attempted first for local execution and
# falls back to absolute import when running under the src package.
try:
    from src.utils import config  # type: ignore
except Exception:
    import config  # type: ignore


def _build_headers() -> dict[str, str]:
    """Construct the headers required for Supabase REST requests."""
    return {
        "apikey": config.SUPABASE_KEY,
        "Authorization": f"Bearer {config.SUPABASE_KEY}",
        "Content-Type": "application/json",
    }


def _request(method: str, path: str, **kwargs: Any) -> Optional[Any]:
    """Helper to make an HTTP request to the Supabase REST API.

    Args:
        method: The HTTP method (GET, POST, PATCH, DELETE).
        path: The path to append to the base Supabase URL (should start
            with "/rest/v1/").
        kwargs: Additional arguments passed through to requests.request().

    Returns:
        The parsed JSON response if successful, or None on error.
    """
    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        print("Supabase configuration missing; cannot perform request")
        return None
    url = config.SUPABASE_URL.rstrip("/") + path
    headers = _build_headers()
    # Merge custom headers but allow caller to override defaults
    custom_headers = kwargs.pop("headers", {})
    headers.update(custom_headers)
    try:
        response = requests.request(method, url, headers=headers, **kwargs)
        # 2xx responses indicate success
        if response.ok:
            # Return JSON if present; some operations (insert) may return
            # an empty body when Prefer=return=minimal is used.
            if response.text:
                try:
                    return response.json()
                except Exception:
                    return response.text
            return True
        else:
            # Print the error for debugging
            print(f"Supabase request failed: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"Supabase request exception: {e}")
        return None


# ---------------------------------------------------------------------------
# CRUD Functions
# ---------------------------------------------------------------------------

def query_data(table_name: str) -> Optional[Any]:
    """Return all rows from the specified table via Supabase REST API.

    Args:
        table_name: The name of the table to query.

    Returns:
        A list of rows (dictionaries) or None if an error occurred.
    """
    return _request("GET", f"/rest/v1/{table_name}?select=*")


def query_questions(project_id: str) -> Optional[Any]:
    """Return all question records for a given project ID via Supabase."""
    return _request(
        "GET",
        f"/rest/v1/questions?project_id=eq.{project_id}&select=*",
    )


def insert_file(filename: str) -> bool:
    """Insert a file record into the files table."""
    data = {"file_name": filename}
    # Prefer return=representation so we get the inserted row back
    res = _request(
        "POST",
        "/rest/v1/files",
        json=data,
        headers={"Prefer": "return=representation"},
    )
    return bool(res)


def insert_project(project_name: str, project_description: str, client_id: int | None = None) -> bool:
    """Insert a new project into the projects table."""
    data: dict[str, Any] = {
        "name": project_name,
        "description": project_description,
    }
    if client_id is not None:
        data["client_id"] = client_id
    res = _request(
        "POST",
        "/rest/v1/projects",
        json=data,
        headers={"Prefer": "return=representation"},
    )
    return bool(res)


def delete_questions_from_db(project_id: int) -> bool:
    """Remove all questions for the given project ID."""
    res = _request(
        "DELETE",
        f"/rest/v1/questions?project_id=eq.{project_id}",
    )
    # Supabase returns True on success when no body is returned
    return res is not None


def insert_questions_into_db(questions: Iterable[Any]) -> bool:
    """Insert a collection of question records into the questions table."""
    success = True
    for q in questions.questions:
        data = {
            "question": q.question,
            "answer": q.answer,
            "project_id": q.project_id,
            "embedding": q.embedding,
            "chat_history": q.chat_history,
        }
        res = _request(
            "POST",
            "/rest/v1/questions",
            json=data,
            headers={"Prefer": "return=representation"},
        )
        if res is None:
            success = False
    return success


def save_questions(project_id: int, questions: Any) -> bool:
    """Replace all questions for a project with the provided list."""
    if delete_questions_from_db(project_id):
        return insert_questions_into_db(questions)
    return False


def insert_file_chunks_into_db(chunks: Iterable[tuple[str, str, str]]) -> bool:
    """Insert file chunks and embeddings into the file_chunks table."""
    success = True
    for file_name, chunk_text, embedding in chunks:
        data = {
            "file_name": file_name,
            "chunk_text": chunk_text,
            "embedding": embedding,
        }
        res = _request(
            "POST",
            "/rest/v1/file_chunks",
            json=data,
            headers={"Prefer": "return=representation"},
        )
        if res is None:
            success = False
    return success


def insert_client(client: Any) -> bool:
    """Insert a new client into the clients table."""
    data = {
        "name": client.name,
        "organization": client.organization,
        "contact_info": client.contact_info,
        "demographics": client.demographics,
        "goals": client.goals,
    }
    res = _request(
        "POST",
        "/rest/v1/clients",
        json=data,
        headers={"Prefer": "return=representation"},
    )
    return bool(res)


def update_client(client_id: int, client: Any) -> bool:
    """Update an existing client's details."""
    # Build a dict of only the provided fields
    data: dict[str, Any] = {}
    if getattr(client, "name", None):
        data["name"] = client.name
    if getattr(client, "organization", None):
        data["organization"] = client.organization
    if getattr(client, "contact_info", None):
        data["contact_info"] = client.contact_info
    if getattr(client, "demographics", None):
        data["demographics"] = client.demographics
    if getattr(client, "goals", None):
        data["goals"] = client.goals
    if not data:
        return True  # nothing to update
    res = _request(
        "PATCH",
        f"/rest/v1/clients?id=eq.{client_id}",
        json=data,
        headers={"Prefer": "return=representation"},
    )
    return bool(res)


def rag_context(question: str, files: list[str]) -> Optional[str]:
    """Return the best matching context chunk for a question.

    Note: Supabase's REST API does not expose pgvector distance operators,
    so this function currently returns None.  Vector search should be
    implemented client‑side or via a dedicated service when using Supabase.
    """
    print(
        "rag_context is not implemented when using Supabase."
        " Consider performing vector search client‑side."
    )
    return None