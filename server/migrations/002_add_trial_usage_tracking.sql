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
-- 5. Provides analytics on trial conversion