-- MetaExtract Quota Enforcement Database Schema
-- Implements "2 Free Images per Device" tracking

-- Client usage tracking (Tier 1 - Device Quota)
CREATE TABLE IF NOT EXISTS client_usage (
    id SERIAL PRIMARY KEY,
    client_id VARCHAR(36) NOT NULL UNIQUE,
    free_used INTEGER DEFAULT 0 NOT NULL CHECK (free_used >= 0),
    last_ip INET,
    last_user_agent TEXT,
    fingerprint_hash VARCHAR(64),
    abuse_score DECIMAL(3,2) DEFAULT 0.00 CHECK (abuse_score >= 0 AND abuse_score <= 1.0),
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_client_usage_client_id ON client_usage(client_id);
CREATE INDEX IF NOT EXISTS idx_client_usage_last_ip ON client_usage(last_ip);
CREATE INDEX IF NOT EXISTS idx_client_usage_last_used ON client_usage(last_used);

-- Request activity tracking (for abuse detection - Tier 2 & 3)
CREATE TABLE IF NOT EXISTS client_activity (
    id SERIAL PRIMARY KEY,
    client_id VARCHAR(36) NOT NULL,
    ip INET,
    user_agent TEXT,
    fingerprint_hash VARCHAR(64),
    action VARCHAR(50) NOT NULL, -- 'request', 'quota_hit', 'new_token', etc.
    abuse_score DECIMAL(3,2) DEFAULT 0.00,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for abuse detection queries
CREATE INDEX IF NOT EXISTS idx_client_activity_client_id ON client_activity(client_id);
CREATE INDEX IF NOT EXISTS idx_client_activity_ip ON client_activity(ip);
CREATE INDEX IF NOT EXISTS idx_client_activity_timestamp ON client_activity(timestamp);
CREATE INDEX IF NOT EXISTS idx_client_activity_action ON client_activity(action);

-- IP rate limit tracking (Tier 2 - Rate Limiting)
CREATE TABLE IF NOT EXISTS ip_rate_limits (
    id SERIAL PRIMARY KEY,
    ip INET NOT NULL,
    daily_count INTEGER DEFAULT 0,
    minute_count INTEGER DEFAULT 0,
    last_reset TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(ip)
);

-- Create indexes for rate limiting queries
CREATE INDEX IF NOT EXISTS idx_ip_rate_limits_ip ON ip_rate_limits(ip);
CREATE INDEX IF NOT EXISTS idx_ip_rate_limits_last_reset ON ip_rate_limits(last_reset);

-- Abuse pattern tracking (Tier 3 - Advanced Detection)
CREATE TABLE IF NOT EXISTS abuse_patterns (
    id SERIAL PRIMARY KEY,
    pattern_type VARCHAR(50) NOT NULL, -- 'multiple_clients_same_ip', 'high_velocity', etc.
    target_type VARCHAR(50) NOT NULL, -- 'ip', 'fingerprint', 'client_id'
    target_value TEXT NOT NULL,
    abuse_score DECIMAL(3,2) NOT NULL,
    evidence JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '24 hours')
);

-- Create indexes for abuse pattern queries
CREATE INDEX IF NOT EXISTS idx_abuse_patterns_pattern_type ON abuse_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_abuse_patterns_target ON abuse_patterns(target_type, target_value);
CREATE INDEX IF NOT EXISTS idx_abuse_patterns_is_active ON abuse_patterns(is_active);
CREATE INDEX IF NOT EXISTS idx_abuse_patterns_expires_at ON abuse_patterns(expires_at);

-- Analytics summary table (for monitoring and reporting)
CREATE TABLE IF NOT EXISTS quota_analytics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    total_requests INTEGER DEFAULT 0,
    free_requests INTEGER DEFAULT 0,
    paid_requests INTEGER DEFAULT 0,
    quota_hits INTEGER DEFAULT 0,
    unique_clients INTEGER DEFAULT 0,
    unique_ips INTEGER DEFAULT 0,
    abuse_score_avg DECIMAL(3,2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(date)
);

-- Create indexes for analytics queries
CREATE INDEX IF NOT EXISTS idx_quota_analytics_date ON quota_analytics(date);

-- Function to update timestamps automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_client_usage_updated_at
    BEFORE UPDATE ON client_usage
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ip_rate_limits_updated_at
    BEFORE UPDATE ON ip_rate_limits
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();