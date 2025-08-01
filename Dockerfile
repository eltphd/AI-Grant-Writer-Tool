# Multi‑stage Dockerfile for the AI Grant Writer micro‑SaaS.
#
# Stage 1 builds the React front‑end into static assets under ``frontend/build``.
# Stage 2 installs Python dependencies, copies the FastAPI back‑end and
# integrates the built front‑end into the image.  The container runs a
# single Uvicorn process on port 8080, serving both API endpoints and
# static files.  The React app communicates with the API at the same
# origin via relative paths.

###########################
# Stage 1: Build React UI #
###########################
FROM node:18-alpine AS frontend-build

# Ensure reproducible, minimal dependency install
ENV NODE_ENV=production

# Create app directory for front‑end build
WORKDIR /app/frontend

# Install front‑end dependencies first to leverage cached layers
COPY frontend/package.json ./
COPY frontend/package-lock.json ./

# Use npm install with reduced memory usage
RUN npm ci --silent --no-audit --no-fund

# Copy the rest of the front‑end source and build the production assets
COPY frontend/ ./
RUN npm run build

################################
# Stage 2: Build Python back‑end #
################################
FROM python:3.11-slim AS backend

# Avoid writing pyc files to disk and ensure stdout/stderr is unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies for scientific packages
# Install system and Python build dependencies, then clean up to reduce image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy backend source code
COPY src ./src
COPY pgvector ./pgvector

# Strip Python bytecode cache to keep image lean
RUN find /app/src -name '__pycache__' -exec rm -rf {} + || true

# Drop privileges – run as non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Copy built React assets from the previous stage into the image.  These
# static files will be served by FastAPI under the ``/static`` path and
# as the catch‑all route for the root path.
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Set PYTHONPATH to include back‑end src folder
ENV PYTHONPATH="/app"

# Default configuration values.  These can be overridden at run time via
# environment variables.  ``FASTAPI_URL`` is unused in the combined
# container but remains for backward compatibility.
ENV USE_SUPABASE=false
ENV FASTAPI_URL=http://localhost:8080/
ENV SINGLE_CLIENT_MODE=false

# Expose the port used by Uvicorn.  When deploying to Cloud Run, this
# internal port is mapped automatically to the service's external URL.
EXPOSE 8080

# Start the FastAPI application.  The React front‑end is served via
# FastAPI's static file mount and catch‑all route in ``src/main.py``.
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]