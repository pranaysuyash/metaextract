-- Migration: Add credit holds for reserve-commit-release pattern
-- Date: 2026-01-17
-- Purpose: Implement atomic credit reservation with idempotency for money-path safety

-- Create credit_holds table
CREATE TABLE IF NOT EXISTS credit_holds (
  id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
  request_id VARCHAR(255) NOT NULL,
  balance_id VARCHAR NOT NULL REFERENCES credit_balances(id),
  amount INTEGER NOT NULL,
  state TEXT NOT NULL, -- 'HELD', 'COMMITTED', 'RELEASED'
  description TEXT,
  quote_id VARCHAR(255),
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMP NOT NULL,
  committed_at TIMESTAMP,
  released_at TIMESTAMP
);

-- Create unique index for idempotency (same balance + requestId can't create multiple holds)
-- This ensures retries with the same Idempotency-Key don't double-charge
CREATE UNIQUE INDEX IF NOT EXISTS credit_holds_balance_request_idx ON credit_holds(balance_id, request_id);

-- Create composite index for cleanup queries (find expired HELD records)
CREATE INDEX IF NOT EXISTS credit_holds_state_expires_idx ON credit_holds(state, expires_at);

-- Create function to release expired holds
CREATE OR REPLACE FUNCTION release_expired_credit_holds()
RETURNS INTEGER AS $$
DECLARE
  released_count INTEGER;
BEGIN
  -- Mark expired HELD credits as RELEASED
  UPDATE credit_holds
  SET 
    state = 'RELEASED',
    released_at = NOW()
  WHERE state = 'HELD' 
    AND expires_at < NOW();
  
  GET DIAGNOSTICS released_count = ROW_COUNT;
  RETURN released_count;
END;
$$ LANGUAGE plpgsql;

-- Note: To set up automated cleanup, install pg_cron and run:
-- SELECT cron.schedule('release-expired-holds', '*/5 * * * *', 'SELECT release_expired_credit_holds()');

