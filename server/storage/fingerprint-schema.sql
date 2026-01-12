/**
 * Browser Fingerprinting and Advanced Protection Database Schema
 * 
 * Creates tables for storing browser fingerprints, device tracking,
 * session data, anomalies, and ML training data
 */

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Browser fingerprints table
CREATE TABLE IF NOT EXISTS browser_fingerprints (
    id VARCHAR(64) PRIMARY KEY, -- SHA256 hash of fingerprint
    device_id VARCHAR(64) NOT NULL,
    session_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64),
    fingerprint_data JSONB NOT NULL,
    ip_address INET NOT NULL,
    user_agent TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    confidence DECIMAL(3,2) CHECK (confidence >= 0 AND confidence <= 1),
    anomalies TEXT[],
    
    -- Indexes for performance
    INDEX idx_browser_fingerprints_device_id (device_id),
    INDEX idx_browser_fingerprints_session_id (session_id),
    INDEX idx_browser_fingerprints_user_id (user_id),
    INDEX idx_browser_fingerprints_timestamp (timestamp DESC),
    INDEX idx_browser_fingerprints_ip_address (ip_address),
    INDEX idx_browser_fingerprints_confidence (confidence),
    
    -- GIN index for JSONB queries
    INDEX idx_browser_fingerprints_fingerprint_data_gin (fingerprint_data)
);

-- Devices table for device-level tracking
CREATE TABLE IF NOT EXISTS devices (
    device_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64),
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    fingerprint_count INTEGER DEFAULT 1,
    session_count INTEGER DEFAULT 0,
    risk_score INTEGER DEFAULT 0 CHECK (risk_score >= 0 AND risk_score <= 100),
    risk_level VARCHAR(20) DEFAULT 'low' CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    is_blocked BOOLEAN DEFAULT FALSE,
    block_reason TEXT,
    block_expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexes
    INDEX idx_devices_user_id (user_id),
    INDEX idx_devices_last_seen (last_seen DESC),
    INDEX idx_devices_risk_level (risk_level),
    INDEX idx_devices_is_blocked (is_blocked)
);

-- Sessions table for session-level tracking
CREATE TABLE IF NOT EXISTS sessions (
    session_id VARCHAR(64) PRIMARY KEY,
    device_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64),
    ip_address INET NOT NULL,
    user_agent TEXT NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    request_count INTEGER DEFAULT 1,
    upload_count INTEGER DEFAULT 0,
    anomaly_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Foreign key
    CONSTRAINT fk_sessions_device_id 
        FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_sessions_device_id (device_id),
    INDEX idx_sessions_user_id (user_id),
    INDEX idx_sessions_last_activity (last_activity DESC),
    INDEX idx_sessions_ip_address (ip_address),
    INDEX idx_sessions_is_active (is_active)
);

-- Fingerprint anomalies table
CREATE TABLE IF NOT EXISTS fingerprint_anomalies (
    id VARCHAR(64) PRIMARY KEY DEFAULT uuid_generate_v4(),
    fingerprint_id VARCHAR(64) NOT NULL,
    session_id VARCHAR(64) NOT NULL,
    device_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64),
    anomaly_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    confidence DECIMAL(3,2) CHECK (confidence >= 0 AND confidence <= 1),
    metadata JSONB DEFAULT '{}',
    
    -- Foreign keys
    CONSTRAINT fk_anomalies_fingerprint_id 
        FOREIGN KEY (fingerprint_id) REFERENCES browser_fingerprints(id) ON DELETE CASCADE,
    CONSTRAINT fk_anomalies_session_id 
        FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    CONSTRAINT fk_anomalies_device_id 
        FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_anomalies_fingerprint_id (fingerprint_id),
    INDEX idx_anomalies_session_id (session_id),
    INDEX idx_anomalies_device_id (device_id),
    INDEX idx_anomalies_timestamp (timestamp DESC),
    INDEX idx_anomalies_severity (severity),
    INDEX idx_anomalies_anomaly_type (anomaly_type)
);

-- Protection feedback table for ML model improvement
CREATE TABLE IF NOT EXISTS protection_feedback (
    id VARCHAR(64) PRIMARY KEY DEFAULT uuid_generate_v4(),
    fingerprint_id VARCHAR(64) NOT NULL,
    session_id VARCHAR(64) NOT NULL,
    decision VARCHAR(20) NOT NULL CHECK (decision IN ('allow', 'challenge', 'block', 'monitor')),
    was_correct BOOLEAN,
    feedback TEXT,
    context JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id VARCHAR(64),
    ip_address INET NOT NULL,
    
    -- Foreign keys
    CONSTRAINT fk_feedback_fingerprint_id 
        FOREIGN KEY (fingerprint_id) REFERENCES browser_fingerprints(id) ON DELETE CASCADE,
    CONSTRAINT fk_feedback_session_id 
        FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_feedback_fingerprint_id (fingerprint_id),
    INDEX idx_feedback_session_id (session_id),
    INDEX idx_feedback_timestamp (timestamp DESC),
    INDEX idx_feedback_decision (decision),
    INDEX idx_feedback_was_correct (was_correct)
);

-- ML model training data table
CREATE TABLE IF NOT EXISTS ml_training_data (
    id VARCHAR(64) PRIMARY KEY DEFAULT uuid_generate_v4(),
    fingerprint_id VARCHAR(64) NOT NULL,
    session_id VARCHAR(64) NOT NULL,
    device_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64),
    features JSONB NOT NULL, -- Feature vector for ML model
    label VARCHAR(20) NOT NULL CHECK (label IN ('normal', 'anomalous')),
    confidence DECIMAL(3,2) CHECK (confidence >= 0 AND confidence <= 1),
    model_version VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign keys
    CONSTRAINT fk_training_fingerprint_id 
        FOREIGN KEY (fingerprint_id) REFERENCES browser_fingerprints(id) ON DELETE CASCADE,
    CONSTRAINT fk_training_session_id 
        FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    CONSTRAINT fk_training_device_id 
        FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_training_fingerprint_id (fingerprint_id),
    INDEX idx_training_session_id (session_id),
    INDEX idx_training_device_id (device_id),
    INDEX idx_training_timestamp (timestamp DESC),
    INDEX idx_training_label (label),
    INDEX idx_training_model_version (model_version)
);

-- ML model performance metrics table
CREATE TABLE IF NOT EXISTS ml_model_metrics (
    id VARCHAR(64) PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_version VARCHAR(20) NOT NULL,
    total_predictions INTEGER NOT NULL DEFAULT 0,
    true_positives INTEGER NOT NULL DEFAULT 0,
    false_positives INTEGER NOT NULL DEFAULT 0,
    true_negatives INTEGER NOT NULL DEFAULT 0,
    false_negatives INTEGER NOT NULL DEFAULT 0,
    accuracy DECIMAL(5,4),
    precision DECIMAL(5,4),
    recall DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    training_start TIMESTAMP WITH TIME ZONE,
    training_end TIMESTAMP WITH TIME ZONE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_metrics_model_version (model_version),
    INDEX idx_metrics_timestamp (timestamp DESC)
);

-- Device similarity table for detecting multi-account usage
CREATE TABLE IF NOT EXISTS device_similarities (
    id VARCHAR(64) PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id_1 VARCHAR(64) NOT NULL,
    device_id_2 VARCHAR(64) NOT NULL,
    similarity_score DECIMAL(5,4) NOT NULL CHECK (similarity_score >= 0 AND similarity_score <= 1),
    matching_features TEXT[],
    confidence DECIMAL(3,2) CHECK (confidence >= 0 AND confidence <= 1),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign keys
    CONSTRAINT fk_similarities_device_id_1 
        FOREIGN KEY (device_id_1) REFERENCES devices(device_id) ON DELETE CASCADE,
    CONSTRAINT fk_similarities_device_id_2 
        FOREIGN KEY (device_id_2) REFERENCES devices(device_id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_similarities_device_id_1 (device_id_1),
    INDEX idx_similarities_device_id_2 (device_id_2),
    INDEX idx_similarities_similarity_score (similarity_score DESC),
    INDEX idx_similarities_timestamp (timestamp DESC)
);

-- IP address tracking table
CREATE TABLE IF NOT EXISTS ip_tracking (
    id VARCHAR(64) PRIMARY KEY DEFAULT uuid_generate_v4(),
    ip_address INET NOT NULL,
    device_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64),
    session_id VARCHAR(64) NOT NULL,
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    request_count INTEGER DEFAULT 1,
    anomaly_count INTEGER DEFAULT 0,
    risk_score INTEGER DEFAULT 0 CHECK (risk_score >= 0 AND risk_score <= 100),
    geolocation JSONB DEFAULT '{}',
    
    -- Foreign keys
    CONSTRAINT fk_ip_tracking_device_id 
        FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
    CONSTRAINT fk_ip_tracking_session_id 
        FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_ip_tracking_ip_address (ip_address),
    INDEX idx_ip_tracking_device_id (device_id),
    INDEX idx_ip_tracking_user_id (user_id),
    INDEX idx_ip_tracking_last_seen (last_seen DESC),
    INDEX idx_ip_tracking_risk_score (risk_score DESC)
);

-- Create indexes for performance optimization
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_browser_fingerprints_trgm_user_agent 
    ON browser_fingerprints USING GIN (user_agent gin_trgm_ops);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_anomalies_trgm_description 
    ON fingerprint_anomalies USING GIN (description gin_trgm_ops);

-- Create composite indexes for common queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_browser_fingerprints_device_timestamp 
    ON browser_fingerprints (device_id, timestamp DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_device_activity 
    ON sessions (device_id, last_activity DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_anomalies_device_severity_timestamp 
    ON fingerprint_anomalies (device_id, severity, timestamp DESC);

-- Create materialized view for device statistics
CREATE MATERIALIZED VIEW IF NOT EXISTS device_statistics AS
SELECT 
    d.device_id,
    d.user_id,
    d.first_seen,
    d.last_seen,
    d.risk_score,
    d.risk_level,
    d.is_blocked,
    COUNT(DISTINCT f.id) as fingerprint_count,
    COUNT(DISTINCT s.session_id) as session_count,
    COUNT(DISTINCT a.id) as total_anomalies,
    COUNT(CASE WHEN a.severity = 'high' THEN 1 END) as high_severity_anomalies,
    COUNT(CASE WHEN a.severity = 'critical' THEN 1 END) as critical_severity_anomalies,
    COUNT(DISTINCT i.ip_address) as unique_ip_count,
    MAX(f.confidence) as max_fingerprint_confidence,
    AVG(f.confidence) as avg_fingerprint_confidence
FROM devices d
LEFT JOIN browser_fingerprints f ON d.device_id = f.device_id
LEFT JOIN sessions s ON d.device_id = s.device_id
LEFT JOIN fingerprint_anomalies a ON d.device_id = a.device_id
LEFT JOIN ip_tracking i ON d.device_id = i.device_id
GROUP BY d.device_id, d.user_id, d.first_seen, d.last_seen, d.risk_score, d.risk_level, d.is_blocked;

-- Create indexes on materialized view
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_device_statistics_device_id 
    ON device_statistics (device_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_device_statistics_risk_level 
    ON device_statistics (risk_level);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_device_statistics_user_id 
    ON device_statistics (user_id);

-- Create function to refresh materialized view
CREATE OR REPLACE FUNCTION refresh_device_statistics()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY device_statistics;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-refresh statistics
CREATE OR REPLACE FUNCTION trigger_refresh_device_statistics()
RETURNS trigger AS $$
BEGIN
    -- Refresh every 5 minutes
    IF (SELECT COUNT(*) FROM devices WHERE last_seen > NOW() - INTERVAL '5 minutes') > 10 THEN
        PERFORM refresh_device_statistics();
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_refresh_stats
    AFTER INSERT OR UPDATE ON devices
    FOR EACH STATEMENT
    EXECUTE FUNCTION trigger_refresh_device_statistics();

-- Create function to get device risk assessment
CREATE OR REPLACE FUNCTION get_device_risk_assessment(device_id_param VARCHAR)
RETURNS TABLE (
    device_id VARCHAR,
    risk_score INTEGER,
    risk_level VARCHAR,
    risk_factors TEXT[],
    recommendations TEXT[],
    confidence DECIMAL(3,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.device_id,
        d.risk_score,
        d.risk_level,
        ARRAY[
            CASE WHEN d.fingerprint_count > 10 THEN 'Multiple fingerprints' END,
            CASE WHEN d.session_count > 100 THEN 'High session count' END,
            CASE WHEN COUNT(CASE WHEN a.severity = 'high' THEN 1 END) > 5 THEN 'High severity anomalies' END,
            CASE WHEN COUNT(CASE WHEN a.severity = 'critical' THEN 1 END) > 0 THEN 'Critical anomalies present' END,
            CASE WHEN COUNT(DISTINCT i.ip_address) > 10 THEN 'Multiple IP addresses' END
        ] AS risk_factors,
        ARRAY[
            CASE WHEN d.risk_score > 70 THEN 'Consider blocking device' END,
            CASE WHEN COUNT(CASE WHEN a.severity = 'high' THEN 1 END) > 5 THEN 'Monitor closely' END,
            CASE WHEN COUNT(DISTINCT i.ip_address) > 10 THEN 'Investigate IP patterns' END
        ] AS recommendations,
        AVG(f.confidence) as confidence
    FROM devices d
    LEFT JOIN browser_fingerprints f ON d.device_id = f.device_id
    LEFT JOIN fingerprint_anomalies a ON d.device_id = a.device_id
    LEFT JOIN ip_tracking i ON d.device_id = i.device_id
    WHERE d.device_id = device_id_param
    GROUP BY d.device_id, d.risk_score, d.risk_level;
END;
$$ LANGUAGE plpgsql;

-- Create function to find similar devices
CREATE OR REPLACE FUNCTION find_similar_devices(
    target_device_id VARCHAR,
    similarity_threshold DECIMAL DEFAULT 0.8
)
RETURNS TABLE (
    similar_device_id VARCHAR,
    similarity_score DECIMAL,
    matching_features TEXT[],
    confidence DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d2.device_id as similar_device_id,
        0.9 as similarity_score, -- Simplified similarity calculation
        ARRAY['user_agent', 'screen_resolution', 'timezone'] as matching_features,
        0.85 as confidence
    FROM devices d1
    JOIN devices d2 ON d1.device_id != d2.device_id
    JOIN browser_fingerprints f1 ON d1.device_id = f1.device_id
    JOIN browser_fingerprints f2 ON d2.device_id = f2.device_id
    WHERE d1.device_id = target_device_id
    AND f1.fingerprint_data->>'userAgent' = f2.fingerprint_data->>'userAgent'
    AND f1.timestamp > NOW() - INTERVAL '30 days'
    AND f2.timestamp > NOW() - INTERVAL '30 days'
    LIMIT 10;
END;
$$ LANGUAGE plpgsql;

-- Create cleanup function for old data
CREATE OR REPLACE FUNCTION cleanup_old_fingerprint_data()
RETURNS TABLE (
    fingerprints_removed BIGINT,
    sessions_removed BIGINT,
    anomalies_removed BIGINT,
    feedback_removed BIGINT
) AS $$
DECLARE
    fp_count BIGINT;
    sess_count BIGINT;
    anom_count BIGINT;
    feed_count BIGINT;
BEGIN
    -- Clean up old fingerprints
    DELETE FROM browser_fingerprints
    WHERE timestamp < NOW() - INTERVAL '90 days'
    RETURNING id INTO fp_count;
    
    -- Clean up old sessions
    DELETE FROM sessions
    WHERE last_activity < NOW() - INTERVAL '30 days'
    RETURNING session_id INTO sess_count;
    
    -- Clean up old anomalies
    DELETE FROM fingerprint_anomalies
    WHERE timestamp < NOW() - INTERVAL '180 days'
    RETURNING id INTO anom_count;
    
    -- Clean up old feedback
    DELETE FROM protection_feedback
    WHERE timestamp < NOW() - INTERVAL '180 days'
    RETURNING id INTO feed_count;
    
    RETURN QUERY SELECT fp_count, sess_count, anom_count, feed_count;
END;
$$ LANGUAGE plpgsql;

-- Create scheduled job to cleanup old data (requires pg_cron extension)
-- This would be set up externally in production
-- SELECT cron.schedule('cleanup-fingerprint-data', '0 2 * * *', 'SELECT cleanup_old_fingerprint_data();');

-- Create indexes for ML model queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ml_training_data_label_timestamp 
    ON ml_training_data (label, timestamp DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ml_training_data_model_version 
    ON ml_training_data (model_version, timestamp DESC);

-- Create function to get training data for ML model
CREATE OR REPLACE FUNCTION get_ml_training_data(
    model_version_param VARCHAR DEFAULT '1.0.0',
    limit_param INTEGER DEFAULT 1000
)
RETURNS TABLE (
    features JSONB,
    label VARCHAR,
    confidence DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        mt.features,
        mt.label,
        mt.confidence
    FROM ml_training_data mt
    WHERE mt.model_version = model_version_param
    ORDER BY mt.timestamp DESC
    LIMIT limit_param;
END;
$$ LANGUAGE plpgsql;