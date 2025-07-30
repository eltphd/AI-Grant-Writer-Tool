-- Initialize the PostgreSQL database for the AI Grant Writer tool.
--
-- This script sets up the required tables for projects, clients,
-- files, file chunks and questions.  It also installs the pgvector
-- extension which is required for vector embeddings.  When this
-- script is mounted into the Postgres container at
-- `/docker-entrypoint-initdb.d/init.sql`, it will be executed on
-- container start to prepare the database.

CREATE EXTENSION IF NOT EXISTS vector;

-- Clients table stores information about each client.  A client
-- represents an organization or individual for whom grant projects
-- are being created.  Demographics and goals help with culturally
-- competent content generation.
CREATE TABLE IF NOT EXISTS clients (
  id SERIAL PRIMARY KEY,
  name TEXT,
  organization TEXT,
  contact_info TEXT,
  demographics TEXT,
  goals TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Projects table stores each grant project.  A project may be
-- associated with a client via the client_id foreign key.  If no
-- client is associated, client_id will be NULL.
CREATE TABLE IF NOT EXISTS projects (
  id SERIAL PRIMARY KEY,
  name TEXT,
  description TEXT,
  client_id INTEGER REFERENCES clients(id),
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Seed some example projects.  Note that these are generic and not
-- linked to any client.
INSERT INTO projects (name, description) VALUES ('Project A','I am A test description');
INSERT INTO projects (name, description) VALUES ('Project B','I am B test description');

-- Questions table stores each Q&A entry along with an embedding
-- (vector) and chat history.  The project_id foreign key links
-- questions back to a specific project.
CREATE TABLE IF NOT EXISTS questions (
  id SERIAL PRIMARY KEY,
  question TEXT,
  answer TEXT,
  project_id INTEGER REFERENCES projects(id),
  embedding VECTOR,
  chat_history TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Files table stores metadata about uploaded files.  The file name is
-- used as a key when retrieving context for the RAG agent.
CREATE TABLE IF NOT EXISTS files (
  id SERIAL PRIMARY KEY,
  file_name TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- File chunks table stores individual chunks of text extracted from
-- uploaded files along with their embeddings.  The RAG pipeline
-- retrieves the best matching chunk for a given question.
CREATE TABLE IF NOT EXISTS file_chunks (
  id SERIAL PRIMARY KEY,
  file_name TEXT,
  chunk_text TEXT,
  embedding VECTOR,
  created_at TIMESTAMPTZ DEFAULT now()
);