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
FROM node:18 AS frontend-build

# Create app directory for front‑end build
WORKDIR /app/frontend

# Install front‑end dependencies first to leverage cached layers
COPY frontend/package.json ./
COPY frontend/package-lock.json ./
RUN npm install

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

# Install system dependencies needed for psycopg2 and optional Whisper support
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends build-essential libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY fastapi ./fastapi
COPY pgvector ./pgvector

# Copy built React assets from the previous stage into the image.  These
# static files will be served by FastAPI under the ``/static`` path and
# as the catch‑all route for the root path.
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Set PYTHONPATH to include back‑end src folder
ENV PYTHONPATH="/app/fastapi/src"

# Default configuration values.  These can be overridden at run time via
# environment variables.  ``FASTAPI_URL`` is unused in the combined
# container but remains for backward compatibility.
ENV USE_SUPABASE=false
ENV FASTAPI_URL=http://localhost:8080/
ENV SINGLE_CLIENT_MODE=false

# Expose the port used by Uvicorn.  When deploying to Cloud Run, this
# internal port is mapped automatically to the service's external URL.
EXPOSE 8080

# Start the FastAPI application.  The React front‑end is served via
# FastAPI's static file mount and catch‑all route in ``fastapi/src/main.py``.
CMD ["uvicorn", "fastapi.src.main:app", "--host", "0.0.0.0", "--port", "8080"]