"""Helper functions for interacting with the FastAPI client endpoints.

This module mirrors the existing fast_api_utils but focuses on client
operations (creating clients, retrieving a list of clients, etc.).  By
isolating HTTP calls here we keep the Streamlit code clean and make it
easy to adjust endpoint URLs in a single location.
"""

import requests
import streamlit as st  # noqa: F401 for side effects of session state

try:
    import utils.config as config  # type: ignore
except Exception:
    from . import config  # type: ignore

def _parse_result(response: requests.Response, default=None):
    """Parse a JSON response, handling errors."""
    if response.status_code == 200:
        try:
            return response.json()
        except Exception:
            return default or {}
    else:
        st.error(f"Status code {response.status_code}", icon="🚨")
        return default or {}

def create_client(name: str, organization: str, contact_info: str, demographics: str, goals: str) -> int:
    """Call the API to create a new client record.

    Returns the HTTP status code for the operation.
    """
    payload = {
        "name": name,
        "organization": organization,
        "contact_info": contact_info,
        "demographics": demographics,
        "goals": goals,
    }
    try:
        response = requests.post(f"{config.FASTAPI_URL}create_client", json=payload)
        return response.status_code
    except Exception as e:
        print(f"ERROR create_client: {e}")
        return 500

def get_clients():
    """Retrieve all clients from the API.

    Returns a list of client records or an empty list on error.
    """
    try:
        response = requests.get(f"{config.FASTAPI_URL}get_clients")
        return _parse_result(response, default=[])
    except Exception as e:
        print(f"ERROR get_clients: {e}")
        return []

def update_client(client_id: int, updates: dict) -> int:
    """Update an existing client via the API.

    Args:
        client_id: The ID of the client to update.
        updates: A dict of fields to update.

    Returns:
        The HTTP status code returned by the API.
    """
    try:
        response = requests.put(f"{config.FASTAPI_URL}update_client/{client_id}", json=updates)
        return response.status_code
    except Exception as e:
        print(f"ERROR update_client: {e}")
        return 500