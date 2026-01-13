-- Free quota tracking tables (Images MVP)
-- Aligns with shared/schema.ts to persist device quota and abuse signals

-- Client usage tracking (Tier 1 - Device Quota)
CREATE TABLE IF NOT EXISTS client_usage (
  id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id VARCHAR NOT NULL UNIQUE,
  free_used INTEGER NOT NULL DEFAULT 0,
  last_ip TEXT,
  last_user_agent TEXT,
  fingerprint_hash VARCHAR(64),
  abuse_score TEXT DEFAULT '0.00',
  first_seen TIMESTAMP NOT NULL DEFAULT NOW(),
  last_used TIMESTAMP NOT NULL DEFAULT NOW(),
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_client_usage_client_id ON client_usage(client_id);
CREATE INDEX IF NOT EXISTS idx_client_usage_last_ip ON client_usage(last_ip);
CREATE INDEX IF NOT EXISTS idx_client_usage_last_used ON client_usage(last_used);

-- Request activity tracking (Tier 2 & 3 - Abuse Detection)
CREATE TABLE IF NOT EXISTS client_activity (
  id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id VARCHAR(36) NOT NULL,
  ip TEXT,
  user_agent TEXT,
  fingerprint_hash VARCHAR(64),
  action VARCHAR(50) NOT NULL, -- 'request', 'quota_hit', 'new_token', etc.
  abuse_score TEXT DEFAULT '0.00',
  timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_client_activity_client_id ON client_activity(client_id);
CREATE INDEX IF NOT EXISTS idx_client_activity_ip ON client_activity(ip);
CREATE INDEX IF NOT EXISTS idx_client_activity_timestamp ON client_activity(timestamp);
CREATE INDEX IF NOT EXISTS idx_client_activity_action ON client_activity(action);

-- IP rate limit tracking (Tier 2)
CREATE TABLE IF NOT EXISTS ip_rate_limits (
  id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
  ip TEXT NOT NULL UNIQUE,
  daily_count INTEGER NOT NULL DEFAULT 0,
  minute_count INTEGER NOT NULL DEFAULT 0,
  last_reset TIMESTAMP NOT NULL DEFAULT NOW(),
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ip_rate_limits_ip ON ip_rate_limits(ip);
CREATE INDEX IF NOT EXISTS idx_ip_rate_limits_last_reset ON ip_rate_limits(last_reset);

-- Abuse pattern tracking (Tier 3 - Advanced Detection)
CREATE TABLE IF NOT EXISTS abuse_patterns (
  id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
  pattern_type VARCHAR(50) NOT NULL, -- 'multiple_clients_same_ip', 'high_velocity', etc.
  target_type VARCHAR(50) NOT NULL, -- 'ip', 'fingerprint', 'client_id'
  target_value TEXT NOT NULL,
  abuse_score TEXT NOT NULL,
  evidence JSONB,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '24 hours')
);

CREATE INDEX IF NOT EXISTS idx_abuse_patterns_pattern_type ON abuse_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_abuse_patterns_target ON abuse_patterns(target_type, target_value);
CREATE INDEX IF NOT EXISTS idx_abuse_patterns_is_active ON abuse_patterns(is_active);
CREATE INDEX IF NOT EXISTS idx_abuse_patterns_expires_at ON abuse_patterns(expires_at);

-- Analytics summary table (Monitoring & Reporting)
CREATE TABLE IF NOT EXISTS quota_analytics (
  id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
  date TIMESTAMP NOT NULL DEFAULT CURRENT_DATE,
  total_requests INTEGER NOT NULL DEFAULT 0,
  free_requests INTEGER NOT NULL DEFAULT 0,
  paid_requests INTEGER NOT NULL DEFAULT 0,
  quota_hits INTEGER NOT NULL DEFAULT 0,
  unique_clients INTEGER NOT NULL DEFAULT 0,
  unique_ips INTEGER NOT NULL DEFAULT 0,
  abuse_score_avg TEXT DEFAULT '0.00',
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_quota_analytics_date ON quota_analytics(date);

-- Updated-at trigger support (kept local to quota tables)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_client_usage_updated_at
  BEFORE UPDATE ON client_usage
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ip_rate_limits_updated_at
  BEFORE UPDATE ON ip_rate_limits
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
