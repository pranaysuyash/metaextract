-- Migration: Add processed_webhooks table for webhook idempotency
-- This table persists webhook processing state across server restarts
-- to prevent double-processing when payment providers retry webhooks

CREATE TABLE IF NOT EXISTS processed_webhooks (
  id VARCHAR PRIMARY KEY,                    -- webhook ID from payment provider
  processed_at TIMESTAMP NOT NULL DEFAULT NOW(),
  event_type TEXT
);

-- Index for cleanup queries (delete old entries)
CREATE INDEX IF NOT EXISTS idx_processed_webhooks_processed_at 
  ON processed_webhooks(processed_at);
