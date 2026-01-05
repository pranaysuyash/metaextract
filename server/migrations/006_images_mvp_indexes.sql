-- Ensure image_mvp_events exists (as a view filtered from ui_events)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relkind IN ('v','m')
      AND n.nspname = 'public'
      AND c.relname = 'image_mvp_events'
  ) THEN
    EXECUTE $createview$
      CREATE VIEW public.image_mvp_events AS
      SELECT *
      FROM public.ui_events
      WHERE product = 'images_mvp';
    $createview$;
  END IF;
END
$$;

-- Indexes for ui_events to support images_mvp queries
CREATE INDEX IF NOT EXISTS idx_ui_events_product_created
  ON public.ui_events (product, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ui_events_product_event
  ON public.ui_events (product, event_name);
CREATE INDEX IF NOT EXISTS idx_ui_events_user
  ON public.ui_events (user_id);

-- Indexes for extraction_analytics (high read volume)
CREATE INDEX IF NOT EXISTS idx_extraction_analytics_requested_at
  ON public.extraction_analytics (requested_at DESC);
CREATE INDEX IF NOT EXISTS idx_extraction_analytics_tier
  ON public.extraction_analytics (tier);
CREATE INDEX IF NOT EXISTS idx_extraction_analytics_success
  ON public.extraction_analytics (success);

-- Indexes for trial_usages to speed lookups by email/session
CREATE INDEX IF NOT EXISTS idx_trial_usages_email
  ON public.trial_usages (email);
CREATE INDEX IF NOT EXISTS idx_trial_usages_session
  ON public.trial_usages (session_id);
