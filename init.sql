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
-- Database Migration: Add Trial Usage Tracking
-- Date: 2026-01-01
-- Purpose: Replace in-memory trial tracking with persistent database storage

-- Add trial_usages table for persistent trial tracking
CREATE TABLE IF NOT EXISTS trial_usages (
  id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL UNIQUE,
  used_at TIMESTAMP NOT NULL DEFAULT NOW(),
  ip_address TEXT,
  user_agent TEXT,
  session_id TEXT
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_trial_usages_email ON trial_usages(email);
CREATE INDEX IF NOT EXISTS idx_trial_usages_used_at ON trial_usages(used_at DESC);
CREATE INDEX IF NOT EXISTS idx_trial_usages_session ON trial_usages(session_id);

-- Add unique constraint on email (already in table definition, but explicit for clarity)
-- This prevents duplicate trial usage per email address

-- Notes:
-- - trial_usages: Replaces in-memory Map for tracking trial usage
-- - email UNIQUE constraint: Ensures one trial per email address
-- - ip_address & user_agent: For fraud detection and analytics
-- - session_id: Links trial usage to session for user account merging
-- - used_at DESC index: For recent trial lookups and cleanup

-- Benefits over in-memory storage:
-- 1. Persistent across server restarts
-- 2. Prevents trial abuse (can't restart server to reset trials)
-- 3. Enables fraud detection (IP/User-Agent tracking)
-- 4. Supports session-to-user account merging
-- 5. Provides analytics on trial conversion-- Database Migration: Add trial usage count
-- Date: 2026-01-02
-- Purpose: Track multiple trial uses per email for Images MVP (2 uses max)

ALTER TABLE trial_usages
ADD COLUMN IF NOT EXISTS uses INTEGER NOT NULL DEFAULT 1;

UPDATE trial_usages
SET uses = 1
WHERE uses IS NULL;

-- UI / Product Analytics Events
CREATE TABLE IF NOT EXISTS ui_events (
  id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
  product TEXT NOT NULL DEFAULT 'core',
  event_name TEXT NOT NULL,
  session_id TEXT,
  user_id VARCHAR,
  properties JSONB NOT NULL DEFAULT '{}'::jsonb,
  ip_address TEXT,
  user_agent TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ui_events_product ON ui_events(product);
CREATE INDEX IF NOT EXISTS idx_ui_events_event_name ON ui_events(event_name);
CREATE INDEX IF NOT EXISTS idx_ui_events_created_at ON ui_events(created_at);
-- User accounts table
CREATE TABLE IF NOT EXISTS users (
  id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR NOT NULL UNIQUE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- User sessions table (session revocation and management)
CREATE TABLE IF NOT EXISTS public.user_sessions (
  id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id VARCHAR NOT NULL REFERENCES public.users(id),
  session_id TEXT NOT NULL UNIQUE,
  token_hash TEXT NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  user_agent TEXT,
  ip_address TEXT,
  revoked_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON public.user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON public.user_sessions(expires_at);

-- Credit balance tracking
CREATE TABLE IF NOT EXISTS credit_balances (
  id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id VARCHAR REFERENCES users(id),
  session_id TEXT,
  credits INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_credit_balances_user_id ON credit_balances(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_balances_session_id ON credit_balances(session_id);

-- Credit grants (lots) for safe refunding and FIFO consumption
CREATE TABLE IF NOT EXISTS credit_grants (
  id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
  balance_id VARCHAR NOT NULL REFERENCES credit_balances(id),
  amount INTEGER NOT NULL,
  remaining INTEGER NOT NULL,
  description TEXT,
  pack TEXT,
  dodo_payment_id TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_credit_grants_balance_id ON credit_grants(balance_id);

-- Credit transactions
CREATE TABLE IF NOT EXISTS credit_transactions (
  id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
  balance_id VARCHAR NOT NULL REFERENCES credit_balances(id),
  grant_id VARCHAR REFERENCES credit_grants(id),
  type TEXT NOT NULL,
  amount INTEGER NOT NULL,
  description TEXT,
  file_type TEXT,
  dodo_payment_id TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_credit_transactions_balance_id ON credit_transactions(balance_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_type ON credit_transactions(type);
-- Ensure image_mvp_events exists (as a view filtered from ui_events)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relkind IN ('v','m')
      AND n.nspname = 'public'
      AND c.relname = 'image_mvp_events'
  ) THEN
    EXECUTE $createview$
      CREATE VIEW public.image_mvp_events AS
      SELECT *
      FROM public.ui_events
      WHERE product = 'images_mvp';
    $createview$;
  END IF;
END
$$;

-- Indexes for ui_events to support images_mvp queries
CREATE INDEX IF NOT EXISTS idx_ui_events_product_created
  ON public.ui_events (product, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ui_events_product_event
  ON public.ui_events (product, event_name);
CREATE INDEX IF NOT EXISTS idx_ui_events_user
  ON public.ui_events (user_id);

-- Indexes for extraction_analytics (high read volume)
DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relkind IN ('r','v','m')
      AND n.nspname = 'public'
      AND c.relname = 'extraction_analytics'
  ) THEN
    CREATE INDEX IF NOT EXISTS idx_extraction_analytics_requested_at
      ON public.extraction_analytics (requested_at DESC);
    CREATE INDEX IF NOT EXISTS idx_extraction_analytics_tier
      ON public.extraction_analytics (tier);
    CREATE INDEX IF NOT EXISTS idx_extraction_analytics_success
      ON public.extraction_analytics (success);
  END IF;
END
$$;

-- Indexes for trial_usages to speed lookups by email/session
CREATE INDEX IF NOT EXISTS idx_trial_usages_email
  ON public.trial_usages (email);
CREATE INDEX IF NOT EXISTS idx_trial_usages_session
  ON public.trial_usages (session_id);
-- Add missing index for user_id on trial_usages (identified in launch audit)
-- Note: ensure user_id exists before attempting index creation
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema='public' AND table_name='trial_usages' AND column_name='user_id'
  ) THEN
    ALTER TABLE public.trial_usages
      ADD COLUMN IF NOT EXISTS user_id VARCHAR;
  END IF;
  -- Add FK constraint if users table exists
  IF EXISTS (
    SELECT 1 FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relname = 'users' AND n.nspname = 'public'
  ) THEN
    -- Only add the constraint if it doesn't already exist (Postgres ALTER TABLE doesn't support IF NOT EXISTS for constraints)
    IF NOT EXISTS (
      SELECT 1 FROM pg_constraint WHERE conname = 'trial_usages_user_id_fkey'
    ) THEN
      ALTER TABLE public.trial_usages
        ADD CONSTRAINT trial_usages_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);
    END IF;
  END IF;
  -- Create index only if column exists
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema='public' AND table_name='trial_usages' AND column_name='user_id'
  ) THEN
    CREATE INDEX IF NOT EXISTS idx_trial_usages_user 
      ON public.trial_usages (user_id);
  END IF;
END
$$;

-- Ensure critical indexes on underlying tables for views exist (redundancy check)
CREATE INDEX IF NOT EXISTS idx_ui_events_user_product
  ON public.ui_events (user_id, product);

-- Add composite index for common analytics filter pattern
DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relkind IN ('r','v','m')
      AND n.nspname = 'public'
      AND c.relname = 'extraction_analytics'
  ) THEN
    CREATE INDEX IF NOT EXISTS idx_extraction_analytics_tier_success
      ON public.extraction_analytics (tier, success);
  END IF;
END
$$;
-- Migration 008: Update metadata_results table schema
-- Adds new columns for metadata summary, object storage refs, and size tracking
-- Date: 2026-01-06

-- Guarded migration in case metadata_results table does not exist in older schemas
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relname = 'metadata_results' AND n.nspname = 'public'
  ) THEN
    -- Add new columns if they don't exist (separate ALTERs to be explicit)
    ALTER TABLE public.metadata_results
      ADD COLUMN IF NOT EXISTS metadata_summary JSONB NOT NULL DEFAULT '{}'::jsonb;
    ALTER TABLE public.metadata_results
      ADD COLUMN IF NOT EXISTS metadata_ref JSONB;
    ALTER TABLE public.metadata_results
      ADD COLUMN IF NOT EXISTS metadata_sha256 TEXT;
    ALTER TABLE public.metadata_results
      ADD COLUMN IF NOT EXISTS metadata_size_bytes BIGINT;
    ALTER TABLE public.metadata_results
      ADD COLUMN IF NOT EXISTS metadata_content_type TEXT;

    -- Create index on metadata_summary for fast searches
    CREATE INDEX IF NOT EXISTS idx_metadata_results_summary 
      ON public.metadata_results USING GIN(metadata_summary);

    -- Migrate existing data: copy 'metadata' column to 'metadata_summary' if metadata exists
    UPDATE public.metadata_results
    SET metadata_summary = metadata
    WHERE metadata IS NOT NULL AND metadata_summary = '{}'::jsonb;

    -- Optional: Keep old metadata column for backward compatibility, or drop it after migration
    -- COMMENT ON COLUMN metadata_results.metadata IS 'DEPRECATED: Use metadata_summary and metadata_ref instead';

    -- Add comment for documentation
    COMMENT ON COLUMN public.metadata_results.metadata_summary IS 'Capped metadata summary for search and indexing';
    COMMENT ON COLUMN public.metadata_results.metadata_ref IS 'Pointer to full metadata blob in object storage';
    COMMENT ON COLUMN public.metadata_results.metadata_sha256 IS 'SHA256 hash of stored metadata';
    COMMENT ON COLUMN public.metadata_results.metadata_size_bytes IS 'Size of metadata blob in bytes';
    COMMENT ON COLUMN public.metadata_results.metadata_content_type IS 'Content type of stored metadata (e.g., application/json)';
  END IF;
END
$$;
