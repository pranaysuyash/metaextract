-- Migration 008: Update metadata_results table schema
-- Adds new columns for metadata summary, object storage refs, and size tracking
-- Date: 2026-01-06

-- Add new columns if they don't exist
ALTER TABLE metadata_results
ADD COLUMN IF NOT EXISTS metadata_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS metadata_ref JSONB,
ADD COLUMN IF NOT EXISTS metadata_sha256 TEXT,
ADD COLUMN IF NOT EXISTS metadata_size_bytes BIGINT,
ADD COLUMN IF NOT EXISTS metadata_content_type TEXT;

-- Create index on metadata_summary for fast searches
CREATE INDEX IF NOT EXISTS idx_metadata_results_summary 
  ON metadata_results USING GIN(metadata_summary);

-- Migrate existing data: copy 'metadata' column to 'metadata_summary' if metadata exists
UPDATE metadata_results
SET metadata_summary = metadata
WHERE metadata IS NOT NULL AND metadata_summary = '{}'::jsonb;

-- Optional: Keep old metadata column for backward compatibility, or drop it after migration
-- COMMENT ON COLUMN metadata_results.metadata IS 'DEPRECATED: Use metadata_summary and metadata_ref instead';

-- Add comment for documentation
COMMENT ON COLUMN metadata_results.metadata_summary IS 'Capped metadata summary for search and indexing';
COMMENT ON COLUMN metadata_results.metadata_ref IS 'Pointer to full metadata blob in object storage';
COMMENT ON COLUMN metadata_results.metadata_sha256 IS 'SHA256 hash of stored metadata';
COMMENT ON COLUMN metadata_results.metadata_size_bytes IS 'Size of metadata blob in bytes';
COMMENT ON COLUMN metadata_results.metadata_content_type IS 'Content type of stored metadata (e.g., application/json)';
