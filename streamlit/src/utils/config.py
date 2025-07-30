"""Configuration for the Streamlit front‑end.

This module defines configuration values specific to the Streamlit
application.  In particular it determines the base URL of the FastAPI
service depending on whether the app is running inside Docker.
"""

import os

# Determine if we're running inside a Docker container.  When running
# via docker‑compose, the DOCKER_RUNNING environment variable should be
# set in the container.  In that case we refer to the FastAPI service
# by its docker service name (fastapi).  Otherwise, we default to
# localhost for development.
DOCKER_RUNNING = os.environ.get("DOCKER_RUNNING", False)

# Base URL for the FastAPI API.  When Docker is running, reference the
# service name so that Streamlit can reach FastAPI via the docker
# network.  Otherwise, assume both services run on the same host.
# In a single‑container deployment (e.g. Cloud Run), the FastAPI API runs
# alongside the Streamlit server on a different internal port (8000).  The
# external port (configured via $PORT) is served by Streamlit.  To
# access the API from within the Streamlit application, we default
# FASTAPI_URL to ``http://localhost:8000/``.  When running under
# docker‑compose with a separate FastAPI service, DOCKER_RUNNING is
# expected to be true and the URL will be "http://fastapi:80/".
FASTAPI_URL: str = "http://localhost:8000/"
if DOCKER_RUNNING:
    FASTAPI_URL = "http://fastapi:80/"

# When running in "single client" mode, the client selection UI is hidden
# in the Streamlit app.  A default client is automatically created (if
# none exist) and new projects are always linked to that client.  Set
# SINGLE_CLIENT_MODE=true in your environment to enable this behaviour.
SINGLE_CLIENT_MODE: bool = os.environ.get("SINGLE_CLIENT_MODE", "false").lower() == "true"

if __name__ == "__main__":
    pass