"""Configuration for the FastAPI service.

This module centralizes environment‑driven configuration values so they can be
easily overridden without editing source code.  If an environment variable is
unset, sensible defaults are used.  The database credentials here are used by
supabase_utils to connect to Supabase.  See README for instructions on
customizing these values in your deployment.
"""

import os

# Database connection parameters (legacy - now using Supabase)
# These are kept for backward compatibility but not used
DB_HOSTNAME: str = os.getenv("DB_HOSTNAME", "localhost")
DB_NAME: str = os.getenv("DB_NAME", "vectordb")
DB_USER: str = os.getenv("DB_USER", "testuser")
DB_PASSWORD: str = os.getenv("DB_PASSWORD", "testpwd")

# ---------------------------------------------------------------------------
# Supabase configuration
#
# These values are used when interacting with a Supabase backend instead of a
# local PostgreSQL database.  SUPABASE_URL should be the base URL of your
# Supabase project (e.g. "https://xyzcompany.supabase.co") and
# SUPABASE_KEY should be an API key (e.g. your anon or service role key).  If
# USE_SUPABASE is set to "true", the FastAPI service will import and use
# supabase_utils instead of pgvector_utils.  Otherwise it will fall back to
# direct PostgreSQL access via pgvector_utils.

# URL of your Supabase project; defaults to an empty string if not set.
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")

# API key (anon or service role) for authenticating with Supabase REST API.
# Accept either SUPABASE_KEY or SUPABASE_SERVICE_KEY for convenience
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_KEY", "")

# Flag indicating whether to use the Supabase API.  When set to "true"
# (case‑insensitive), the FastAPI app will route all database operations
# through the supabase_utils module.  Defaults to "true" since we're now fully Supabase-based.
USE_SUPABASE: bool = os.getenv("USE_SUPABASE", "true").lower() == "true"

# FastAPI base URL for use by the Streamlit front‑end.  This should include
# the trailing slash.  For example, if you are running the API on localhost
# port 8000 you might set FASTAPI_URL="http://localhost:8000/".
FASTAPI_URL: str = os.getenv("FASTAPI_URL", "http://fastapi:80/")

# Default chunk size for document splitting when embedding text.  This can be
# overridden via an environment variable if you wish to experiment with
# different sizes.
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))

# OpenAI embedding model name.  Replace with your desired model if you are
# using a different provider or a self‑hosted model.
OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")

# Vercel AI Gateway configuration
VERCEL_AI_KEY: str = os.getenv("VERCEL_AI_KEY", "")

# Generic error message to return to clients when an internal server error
# occurs.  Keeping this in one place makes it easy to update.
ERROR_MESSAGE: str = "An internal error occurred. Please try again later."