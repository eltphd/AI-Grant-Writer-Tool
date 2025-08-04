-- Migration script to add project_id column to files table
-- This fixes the issue where files couldn't be associated with projects

-- Add project_id column to files table
ALTER TABLE files ADD COLUMN IF NOT EXISTS project_id TEXT;

-- Add project_id column to file_chunks table for consistency
ALTER TABLE file_chunks ADD COLUMN IF NOT EXISTS project_id TEXT;

-- Create index on project_id for better query performance
CREATE INDEX IF NOT EXISTS idx_files_project_id ON files(project_id);
CREATE INDEX IF NOT EXISTS idx_file_chunks_project_id ON file_chunks(project_id); 