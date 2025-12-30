-- Database Migration: Add Metadata Storage Tables
-- Phase 1: Foundation
-- Date: 2024-12-29

-- Add metadata_store table for comprehensive metadata
CREATE TABLE IF NOT EXISTS metadata_store (
  id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
  file_path TEXT NOT NULL UNIQUE,
  file_type TEXT NOT NULL, -- 'image', 'video', 'audio', 'pdf', 'svg'
  extracted_at TIMESTAMP NOT NULL DEFAULT NOW(),
  tier_used TEXT NOT NULL,
  total_fields_extracted INTEGER NOT NULL DEFAULT 0,
  fields_by_category JSONB NOT NULL DEFAULT '{}', -- {"exif": 45, "gps": 12, ...}
  metadata JSONB NOT NULL DEFAULT '{}', -- Full metadata as JSONB
  indexed_fields JSONB NOT NULL DEFAULT '{}' -- Fast-search indexed fields
);

-- Add field_analytics table for field-level analytics
CREATE TABLE IF NOT EXISTS field_analytics (
  id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
  field_name TEXT NOT NULL,
  field_type TEXT NOT NULL, -- 'string', 'number', 'date', 'boolean'
  file_types JSONB NOT NULL DEFAULT '[]', -- ['image', 'video']
  extraction_count INTEGER NOT NULL DEFAULT 0,
  last_extracted_at TIMESTAMP NOT NULL DEFAULT NOW(),
  example_values JSONB NOT NULL DEFAULT '[]' -- Top 5 values with counts
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_metadata_file_type ON metadata_store(file_type);
CREATE INDEX IF NOT EXISTS idx_metadata_extracted_at ON metadata_store(extracted_at DESC);
CREATE INDEX IF NOT EXISTS idx_metadata_indexed_fields ON metadata_store USING GIN(indexed_fields);

CREATE INDEX IF NOT EXISTS idx_field_analytics_name ON field_analytics(field_name);
CREATE INDEX IF NOT EXISTS idx_field_analytics_type ON field_analytics(field_type);
CREATE INDEX IF NOT EXISTS idx_field_analytics_count ON field_analytics(extraction_count DESC);

-- Grant permissions (adjust as needed)
-- GRANT SELECT, INSERT, UPDATE ON metadata_store, field_analytics TO your_user;
-- GRANT USAGE, SELECT ON SEQUENCES TO your_user;

-- Notes:
-- - metadata_store: Stores complete extraction results with fast GIN index for JSONB
-- - field_analytics: Tracks which fields are most commonly extracted for optimization
-- - Both tables support the Phase 1-3 metadata expansion plan
