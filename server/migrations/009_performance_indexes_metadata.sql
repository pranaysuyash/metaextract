-- Migration 009: Performance Indexes for Metadata Operations
-- Date: 2026-01-06
-- Purpose: Optimize frequently queried metadata tables for better performance

-- metadata_store table optimizations
-- Add user_id column if it doesn't exist (for future user-based queries)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema='public' AND table_name='metadata_store' AND column_name='user_id'
  ) THEN
    ALTER TABLE public.metadata_store
      ADD COLUMN IF NOT EXISTS user_id VARCHAR;
  END IF;
END
$$;

-- Create composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_metadata_store_file_hash
  ON public.metadata_store (file_path);

CREATE INDEX IF NOT EXISTS idx_metadata_store_user_created
  ON public.metadata_store (user_id, extracted_at DESC)
  WHERE user_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_metadata_store_type_tier
  ON public.metadata_store (file_type, tier_used);

CREATE INDEX IF NOT EXISTS idx_metadata_store_extracted_fields
  ON public.metadata_store (extracted_at DESC, total_fields_extracted DESC);

-- GIN index for metadata JSONB field (improves nested queries)
CREATE INDEX IF NOT EXISTS idx_metadata_store_metadata_gin
  ON public.metadata_store USING GIN(metadata);

-- field_analytics table optimizations
CREATE INDEX IF NOT EXISTS idx_field_analytics_name_type
  ON public.field_analytics (field_name, field_type);

CREATE INDEX IF NOT EXISTS idx_field_analytics_count_date
  ON public.field_analytics (extraction_count DESC, last_extracted_at DESC);

CREATE INDEX IF NOT EXISTS idx_field_analytics_file_types
  ON public.field_analytics USING GIN(file_types);

-- GIN index for example_values JSONB field
CREATE INDEX IF NOT EXISTS idx_field_analytics_examples_gin
  ON public.field_analytics USING GIN(example_values);

-- extraction_analytics table optimizations (if table exists)
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
    -- Composite indexes for common analytics queries
    CREATE INDEX IF NOT EXISTS idx_extraction_analytics_time_tier
      ON public.extraction_analytics (requested_at DESC, tier);
    
    CREATE INDEX IF NOT EXISTS idx_extraction_analytics_tier_success_time
      ON public.extraction_analytics (tier, success, requested_at DESC);
    
    IF EXISTS (
      SELECT 1 FROM information_schema.columns
      WHERE table_schema='public'
        AND table_name='extraction_analytics'
        AND column_name='user_id'
    ) THEN
      CREATE INDEX IF NOT EXISTS idx_extraction_analytics_user_time
        ON public.extraction_analytics (user_id, requested_at DESC)
        WHERE user_id IS NOT NULL;
    END IF;
  END IF;
END
$$;

-- ui_events table optimizations for analytics queries
CREATE INDEX IF NOT EXISTS idx_ui_events_time_product
  ON public.ui_events (created_at DESC, product);

CREATE INDEX IF NOT EXISTS idx_ui_events_user_product_time
  ON public.ui_events (user_id, product, created_at DESC)
  WHERE user_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_ui_events_session_time
  ON public.ui_events (session_id, created_at DESC)
  WHERE session_id IS NOT NULL;

-- GIN index for properties JSONB field
CREATE INDEX IF NOT EXISTS idx_ui_events_properties_gin
  ON public.ui_events USING GIN(properties);

-- credit_transactions table optimizations
CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_time
  ON public.credit_transactions (balance_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_credit_transactions_type_time
  ON public.credit_transactions (type, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_credit_transactions_file_type
  ON public.credit_transactions (file_type)
  WHERE file_type IS NOT NULL;

-- metadata_results table optimizations (if table exists)
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relname = 'metadata_results' AND n.nspname = 'public'
  ) THEN
    -- Optimize the metadata_summary searches
    CREATE INDEX IF NOT EXISTS idx_metadata_results_summary_gin
      ON public.metadata_results USING GIN(metadata_summary);
    
    CREATE INDEX IF NOT EXISTS idx_metadata_results_sha256
      ON public.metadata_results (metadata_sha256)
      WHERE metadata_sha256 IS NOT NULL;
    
    CREATE INDEX IF NOT EXISTS idx_metadata_results_content_type
      ON public.metadata_results (metadata_content_type)
      WHERE metadata_content_type IS NOT NULL;
  END IF;
END
$$;

-- Notes:
-- - These indexes target the most common query patterns identified in performance profiling
-- - Composite indexes are used for multi-column queries to avoid index intersection
-- - GIN indexes are used for JSONB fields to enable efficient nested property searches
-- - Partial indexes (WHERE clauses) are used to optimize for specific query patterns
-- - DESC ordering is used for time-based queries to optimize recent-data retrieval
