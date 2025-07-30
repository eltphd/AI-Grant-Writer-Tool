"""Utility functions for file handling and other common operations."""

import os
import tempfile
from typing import Any


def save_file_locally(file_name: str, file_bytes: bytes) -> str:
    """Save a file locally and return the file path."""
    try:
        # Create a temporary directory if it doesn't exist
        temp_dir = os.path.join(os.getcwd(), "temp_files")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(temp_dir, file_name)
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        
        return file_path
    except Exception as e:
        print(f"Error saving file: {e}")
        return ""


def save_file_chunks(file_name: str, file_obj: Any, open_api_key: str) -> str:
    """Save file chunks for processing."""
    try:
        # For demo mode, just return the file name
        # In a real implementation, this would process the file into chunks
        return file_name
    except Exception as e:
        print(f"Error saving file chunks: {e}")
        return ""


def delete_list_from_state_helper(list_names: list) -> None:
    """Helper function to delete lists from session state."""
    # This is a placeholder for Streamlit functionality
    pass


def get_data_from_db(table_name: str) -> Any:
    """Get data from database."""
    # This is a placeholder - actual implementation would query the database
    return []


def submit_manual_text() -> None:
    """Submit manual text."""
    # This is a placeholder for manual text submission
    pass


def handle_project() -> None:
    """Handle project operations."""
    # This is a placeholder for project handling
    pass


def handle_project_select_callback() -> None:
    """Handle project selection callback."""
    # This is a placeholder for project selection
    pass


def add_question_helper(project_dict: dict, new_question: str) -> None:
    """Add question helper."""
    # This is a placeholder for adding questions
    pass


def format_questions(questions: list) -> list:
    """Format questions for API."""
    # This is a placeholder for question formatting
    return questions 