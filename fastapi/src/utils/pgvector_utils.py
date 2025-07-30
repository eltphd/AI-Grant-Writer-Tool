"""Utility functions for interacting with the PostgreSQL vector database.

This module wraps all of the low‑level SQL statements required by the
FastAPI service.  Keeping the database code here means the rest of the
application can remain agnostic about how data is persisted.  The
functions defined here should return simple Python objects (or True/False
for writes) and should raise no exceptions — errors are logged and
rolled back internally.
"""

import psycopg2
from typing import Any, Iterable

try:
    # Attempt to import config from the src package when running under
    # FastAPI.  If that fails (e.g. during local script execution), fall
    # back to relative imports.
    import src.utils.config as config  # type: ignore
except Exception:
    import utils.config as config  # type: ignore

# Establish a connection to PostgreSQL.  The connection details come
# from environment variables defined in config.py.  Note that
# psycopg2.connect() will raise an exception if the database is
# unreachable; in that case FastAPI will fail on startup with a clear
# traceback.
conn = psycopg2.connect(
    host=config.DB_HOSTNAME,
    database=config.DB_NAME,
    user=config.DB_USER,
    password=config.DB_PASSWORD,
)

# Whitelist of allowed table names to prevent SQL injection
ALLOWED_TABLES = {
    "clients", "projects", "files", "file_chunks", "questions", "chat_sessions", "chat_messages"
}

def _log_and_rollback(e: Exception) -> None:
    """Helper to log an exception and roll back the current transaction."""
    print(e)
    try:
        conn.rollback()
    except Exception:
        pass

def query_data(table_name: str) -> Any:
    """Return all rows from the specified table.

    Args:
        table_name: The name of the table to query.

    Returns:
        A list of rows, or False if an error occurred.
    """
    # Validate table name against whitelist to prevent SQL injection
    if table_name not in ALLOWED_TABLES:
        print(f"Invalid table name: {table_name}")
        return False
        
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table_name}")
        results = cur.fetchall()
        cur.close()
        return results
    except Exception as e:
        _log_and_rollback(e)
        return False

def query_questions(project_id: str) -> Any:
    """Return all question records for a given project ID."""
    try:
        cur = conn.cursor()
        cur.execute(
            f"SELECT * FROM questions WHERE project_id = %s",
            (project_id,),
        )
        results = cur.fetchall()
        cur.close()
        return results
    except Exception as e:
        _log_and_rollback(e)
        return False

def insert_file(filename: str) -> bool:
    """Insert a file record into the files table."""
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO files (file_name) VALUES (%s)", (filename,))
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        _log_and_rollback(e)
        return False

def insert_project(project_name: str, project_description: str, client_id: int | None = None) -> bool:
    """Insert a new project into the projects table.

    Args:
        project_name: The name of the project.
        project_description: A short description of the project.
        client_id: Optional ID of the client associated with this project.
    """
    try:
        cur = conn.cursor()
        if client_id is not None:
            cur.execute(
                "INSERT INTO projects (name, description, client_id) VALUES (%s, %s, %s)",
                (project_name, project_description, client_id),
            )
        else:
            cur.execute(
                "INSERT INTO projects (name, description) VALUES (%s, %s)",
                (project_name, project_description),
            )
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        _log_and_rollback(e)
        return False

def delete_questions_from_db(project_id: int) -> bool:
    """Remove all questions for the given project ID."""
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM questions WHERE project_id = %s", (project_id,))
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        _log_and_rollback(e)
        return False

def escape_single_quote_helper(text: str) -> str:
    """Escape single quotes for SQL insertion."""
    return text.replace("'", "''")

def insert_questions_into_db(questions: Iterable[Any]) -> bool:
    """Insert a collection of question records into the questions table."""
    try:
        cur = conn.cursor()
        for q in questions.questions:
            cur.execute(
                "INSERT INTO questions (question, answer, project_id, embedding, chat_history)"
                " VALUES (%s, %s, %s, %s, %s)",
                (
                    escape_single_quote_helper(q.question),
                    escape_single_quote_helper(q.answer),
                    q.project_id,
                    q.embedding,
                    escape_single_quote_helper(q.chat_history),
                ),
            )
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        _log_and_rollback(e)
        return False

def save_questions(project_id: int, questions: Any) -> bool:
    """Replace all questions for a project with the provided list."""
    if delete_questions_from_db(project_id):
        return insert_questions_into_db(questions)
    return False

def insert_file_chunks_into_db(chunks: Iterable[tuple[str, str, str]]) -> bool:
    """Insert file chunks and embeddings into the file_chunks table.

    Args:
        chunks: Iterable of tuples (file_name, chunk_text, embedding)
    """
    try:
        cur = conn.cursor()
        for file_name, chunk_text, embedding in chunks:
            cur.execute(
                "INSERT INTO file_chunks (file_name, chunk_text, embedding) VALUES (%s, %s, %s)",
                (
                    escape_single_quote_helper(file_name),
                    escape_single_quote_helper(chunk_text),
                    embedding,
                ),
            )
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        _log_and_rollback(e)
        return False

def insert_client(client: Any) -> bool:
    """Insert a new client into the clients table.

    Args:
        client: A pydantic Client model with the new client information.
    """
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO clients (name, organization, contact_info, demographics, goals) VALUES (%s, %s, %s, %s, %s)",
            (
                client.name,
                client.organization,
                client.contact_info,
                client.demographics,
                client.goals,
            ),
        )
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        _log_and_rollback(e)
        return False

def update_client(client_id: int, client: Any) -> bool:
    """Update an existing client's details.

    Only the provided fields on the client object will be updated.
    """
    try:
        cur = conn.cursor()
        updates: list[str] = []
        values: list[Any] = []
        if getattr(client, "name", None):
            updates.append("name = %s")
            values.append(client.name)
        if getattr(client, "organization", None):
            updates.append("organization = %s")
            values.append(client.organization)
        if getattr(client, "contact_info", None):
            updates.append("contact_info = %s")
            values.append(client.contact_info)
        if getattr(client, "demographics", None):
            updates.append("demographics = %s")
            values.append(client.demographics)
        if getattr(client, "goals", None):
            updates.append("goals = %s")
            values.append(client.goals)
        if not updates:
            return True  # nothing to update
        # Build the SQL statement dynamically
        sql = f"UPDATE clients SET {', '.join(updates)} WHERE id = %s"
        values.append(client_id)
        cur.execute(sql, tuple(values))
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        _log_and_rollback(e)
        return False

def rag_context(question: str, files: list[str]) -> Any:
    """Return the best matching context chunk for a question given a list of files."""
    try:
        file_names = ",".join(["%s" for _ in files])
        cur = conn.cursor()
        cur.execute(
            f"SELECT chunk_text FROM file_chunks WHERE file_name IN ({file_names}) ORDER BY embedding <-> %s LIMIT 1",
            (*files, question),
        )
        result = cur.fetchone()
        cur.close()
        return result[0] if result else None
    except Exception as e:
        _log_and_rollback(e)
        return None


# Chat-related database functions
def save_chat_message(project_id: int, user_message: str, ai_response: str) -> bool:
    """Save a chat message and AI response to the database."""
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO chat_messages (project_id, user_message, ai_response, created_at) VALUES (%s, %s, %s, NOW())",
            (project_id, user_message, ai_response),
        )
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        _log_and_rollback(e)
        return False


def get_chat_sessions(project_id: int) -> Any:
    """Get all chat sessions for a project."""
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT DISTINCT session_id FROM chat_messages WHERE project_id = %s ORDER BY created_at DESC",
            (project_id,),
        )
        results = cur.fetchall()
        cur.close()
        return results
    except Exception as e:
        _log_and_rollback(e)
        return []


def get_chat_messages(session_id: int) -> Any:
    """Get all messages for a specific chat session."""
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM chat_messages WHERE session_id = %s ORDER BY created_at ASC",
            (session_id,),
        )
        results = cur.fetchall()
        cur.close()
        return results
    except Exception as e:
        _log_and_rollback(e)
        return []