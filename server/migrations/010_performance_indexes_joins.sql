-- Migration 010: Performance Indexes for JOIN Operations
-- Date: 2026-01-06
-- Purpose: Optimize JOIN operations and foreign key relationships for better query performance

-- Foreign key relationship optimizations
-- users table indexes (if not already existing)
CREATE INDEX IF NOT EXISTS idx_users_email_lower
  ON public.users (LOWER(email));

CREATE INDEX IF NOT EXISTS idx_users_created
  ON public.users (created_at DESC);

-- credit_balances table optimizations
CREATE INDEX IF NOT EXISTS idx_credit_balances_user_created
  ON public.credit_balances (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_credit_balances_session_created
  ON public.credit_balances (session_id, created_at DESC)
  WHERE session_id IS NOT NULL;

-- credit_grants table optimizations
CREATE INDEX IF NOT EXISTS idx_credit_grants_user_expires
  ON public.credit_grants (balance_id, expires_at)
  WHERE expires_at IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_credit_grants_created
  ON public.credit_grants (created_at DESC);

-- trial_usages table optimizations
CREATE INDEX IF NOT EXISTS idx_trial_usages_email_lower
  ON public.trial_usages (LOWER(email));

CREATE INDEX IF NOT EXISTS idx_trial_usages_session_created
  ON public.trial_usages (session_id, used_at DESC)
  WHERE session_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_trial_usages_user_created
  ON public.trial_usages (user_id, used_at DESC)
  WHERE user_id IS NOT NULL;

-- Composite indexes for common JOIN patterns
-- Files + Metadata JOIN optimization
CREATE INDEX IF NOT EXISTS idx_files_metadata_join
  ON public.files (id, file_type)
  WHERE id IN (SELECT DISTINCT file_id FROM metadata);

-- Favorites + Files JOIN optimization
CREATE INDEX IF NOT EXISTS idx_favorites_files_join
  ON public.favorites (file_id, added_at DESC);

-- Version history + Files JOIN optimization
CREATE INDEX IF NOT EXISTS idx_version_history_files_join
  ON public.version_history (file_id, changed_at DESC);

-- Perceptual hashes + Files JOIN optimization
CREATE INDEX IF NOT EXISTS idx_perceptual_hashes_files_join
  ON public.perceptual_hashes (file_id);

-- Multi-table JOIN optimizations for analytics queries
-- Common pattern: files + metadata + version_history
CREATE INDEX IF NOT EXISTS idx_files_analytics
  ON public.files (file_type, extracted_at DESC);

-- Common pattern: ui_events + users + credit_balances
CREATE INDEX IF NOT EXISTS idx_ui_events_analytics
  ON public.ui_events (product, event_name, created_at DESC);

-- Common pattern: metadata_store + field_analytics
CREATE INDEX IF NOT EXISTS idx_metadata_store_analytics
  ON public.metadata_store (file_type, tier_used, extracted_at DESC);

-- Search optimization indexes
-- Full-text search preparation (if needed in future)
CREATE INDEX IF NOT EXISTS idx_files_path_gin
  ON public.files USING GIN(to_tsvector('english', file_path));

CREATE INDEX IF NOT EXISTS idx_metadata_value_gin
  ON public.metadata USING GIN(to_tsvector('english', value));

-- Range query optimizations
CREATE INDEX IF NOT EXISTS idx_files_size_range
  ON public.files (file_size)
  WHERE file_size > 0;

CREATE INDEX IF NOT EXISTS idx_files_time_range
  ON public.files (extracted_at, file_mtime);

-- Partial indexes for specific query patterns
CREATE INDEX IF NOT EXISTS idx_metadata_category_key_value
  ON public.metadata (category, key, value)
  WHERE value IS NOT NULL AND value != '';

CREATE INDEX IF NOT EXISTS idx_files_recent
  ON public.files (extracted_at DESC)
  WHERE extracted_at > NOW() - INTERVAL '30 days';

-- Bitmap index optimizations for low-cardinality columns
CREATE INDEX IF NOT EXISTS idx_files_type_bitmap
  ON public.files (file_type)
  WHERE file_type IN ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.svg', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx');

-- Notes:
-- - These indexes optimize the most common JOIN patterns identified in performance analysis
-- - Composite indexes are designed to support multi-table queries without full table scans
-- - Partial indexes reduce index size while targeting specific query patterns
-- - Bitmap indexes are used for low-cardinality columns to improve filter operations
-- - GIN indexes support full-text search capabilities for future enhancements