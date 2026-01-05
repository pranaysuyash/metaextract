-- Add missing index for user_id on trial_usages (identified in launch audit)
-- Note: code currently queries by email, but FK index is best practice for deletes/joins
CREATE INDEX IF NOT EXISTS idx_trial_usages_user 
  ON public.trial_usages (user_id);

-- Ensure critical indexes on underlying tables for views exist (redundancy check)
CREATE INDEX IF NOT EXISTS idx_ui_events_user_product
  ON public.ui_events (user_id, product);

-- Add composite index for common analytics filter pattern
CREATE INDEX IF NOT EXISTS idx_extraction_analytics_tier_success
  ON public.extraction_analytics (tier, success);
