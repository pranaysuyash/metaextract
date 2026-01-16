-- Migration: Add persistent quote storage for Images MVP
-- Date: 2026-01-16
-- Purpose: Replace in-memory quote storage with database persistence

-- Create quotes table for persistent quote storage
CREATE TABLE IF NOT EXISTS images_mvp_quotes (
  id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id TEXT NOT NULL,
  user_id VARCHAR REFERENCES users(id),
  files JSONB NOT NULL DEFAULT '[]'::jsonb,
  ops JSONB NOT NULL DEFAULT '{}'::jsonb,
  credits_total INTEGER NOT NULL DEFAULT 0,
  per_file_credits JSONB NOT NULL DEFAULT '{}'::jsonb,
  per_file JSONB NOT NULL DEFAULT '{}'::jsonb,
  schedule JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMP NOT NULL,
  used_at TIMESTAMP,
  status VARCHAR(20) NOT NULL DEFAULT 'active' -- active, used, expired
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_images_mvp_quotes_session_id ON images_mvp_quotes(session_id);
CREATE INDEX IF NOT EXISTS idx_images_mvp_quotes_user_id ON images_mvp_quotes(user_id);
CREATE INDEX IF NOT EXISTS idx_images_mvp_quotes_expires_at ON images_mvp_quotes(expires_at);
CREATE INDEX IF NOT EXISTS idx_images_mvp_quotes_status ON images_mvp_quotes(status);
CREATE INDEX IF NOT EXISTS idx_images_mvp_quotes_created_at ON images_mvp_quotes(created_at DESC);

-- Create composite index for common lookup patterns
CREATE INDEX IF NOT EXISTS idx_images_mvp_quotes_session_status 
  ON images_mvp_quotes(session_id, status) 
  WHERE status = 'active';

-- Create function to clean up expired quotes
CREATE OR REPLACE FUNCTION cleanup_expired_quotes()
RETURNS INTEGER AS $$
DECLARE
  deleted_count INTEGER;
BEGIN
  DELETE FROM images_mvp_quotes 
  WHERE expires_at < NOW() 
    AND status = 'active';
  
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create scheduled cleanup job (requires pg_cron extension)
-- This will run every hour to clean up expired quotes
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_extension WHERE extname = 'pg_cron'
  ) THEN
    PERFORM cron.schedule('cleanup-expired-quotes', '0 * * * *', 'SELECT cleanup_expired_quotes();');
  END IF;
END
$$;

-- Add comments for documentation
COMMENT ON TABLE images_mvp_quotes IS 'Persistent storage for Images MVP quotes';
COMMENT ON COLUMN images_mvp_quotes.id IS 'Unique quote identifier (UUID)';
COMMENT ON COLUMN images_mvp_quotes.session_id IS 'Session ID for quote association';
COMMENT ON COLUMN images_mvp_quotes.user_id IS 'User ID (optional, for authenticated users)';
COMMENT ON COLUMN images_mvp_quotes.files IS 'Array of file metadata for quote calculation';
COMMENT ON COLUMN images_mvp_quotes.ops IS 'Processing operations configuration';
COMMENT ON COLUMN images_mvp_quotes.credits_total IS 'Total credits required for this quote';
COMMENT ON COLUMN images_mvp_quotes.per_file_credits IS 'Per-file credit breakdown';
COMMENT ON COLUMN images_mvp_quotes.per_file IS 'Per-file processing details';
COMMENT ON COLUMN images_mvp_quotes.schedule IS 'Credit schedule used for calculation';
COMMENT ON COLUMN images_mvp_quotes.created_at IS 'Quote creation timestamp';
COMMENT ON COLUMN images_mvp_quotes.expires_at IS 'Quote expiration timestamp (15 minutes)';
COMMENT ON COLUMN images_mvp_quotes.used_at IS 'Timestamp when quote was used for extraction';
COMMENT ON COLUMN images_mvp_quotes.status IS 'Quote status: active, used, or expired';

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE ON images_mvp_quotes TO your_app_user;
-- GRANT USAGE, SELECT ON SEQUENCE images_mvp_quotes_id_seq TO your_app_user;