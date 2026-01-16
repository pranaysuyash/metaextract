-- Migration 014: Add user_sessions table for session revocation and management
-- Date: 2026-01-16

DO $$
BEGIN
  -- Ensure extension for UUID if needed (gen_random_uuid)
  IF NOT EXISTS (
    SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto'
  ) THEN
    -- Optional, some environments use gen_random_uuid from pgcrypto
    -- CREATE EXTENSION IF NOT EXISTS pgcrypto;
    -- If not available, callers will supply ids explicitly
  END IF;
END$$;

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

-- Helpful indexes for cleanup and lookups
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON public.user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON public.user_sessions(expires_at);
