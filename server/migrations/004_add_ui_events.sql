-- UI / Product Analytics Events
CREATE TABLE IF NOT EXISTS ui_events (
  id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
  product TEXT NOT NULL DEFAULT 'core',
  event_name TEXT NOT NULL,
  session_id TEXT,
  user_id VARCHAR,
  properties JSONB NOT NULL DEFAULT '{}'::jsonb,
  ip_address TEXT,
  user_agent TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ui_events_product ON ui_events(product);
CREATE INDEX IF NOT EXISTS idx_ui_events_event_name ON ui_events(event_name);
CREATE INDEX IF NOT EXISTS idx_ui_events_created_at ON ui_events(created_at);
