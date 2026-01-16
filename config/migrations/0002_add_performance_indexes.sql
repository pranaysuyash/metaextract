-- Migration: Add performance indexes for high-volume tables
-- These indexes prevent full table scans on frequently queried fields

-- client_usage indexes
CREATE INDEX IF NOT EXISTS idx_client_usage_last_ip ON client_usage(last_ip);
CREATE INDEX IF NOT EXISTS idx_client_usage_fingerprint_hash ON client_usage(fingerprint_hash);
CREATE INDEX IF NOT EXISTS idx_client_usage_last_used ON client_usage(last_used);

-- client_activity indexes  
CREATE INDEX IF NOT EXISTS idx_client_activity_client_id ON client_activity(client_id);
CREATE INDEX IF NOT EXISTS idx_client_activity_timestamp ON client_activity(timestamp);
CREATE INDEX IF NOT EXISTS idx_client_activity_ip ON client_activity(ip);
CREATE INDEX IF NOT EXISTS idx_client_activity_action ON client_activity(action);

-- Composite index for abuse detection queries
CREATE INDEX IF NOT EXISTS idx_client_activity_client_timestamp 
  ON client_activity(client_id, timestamp DESC);
