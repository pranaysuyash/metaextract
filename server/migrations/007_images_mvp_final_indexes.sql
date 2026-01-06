-- Add missing index for user_id on trial_usages (identified in launch audit)
-- Note: ensure user_id exists before attempting index creation
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema='public' AND table_name='trial_usages' AND column_name='user_id'
  ) THEN
    ALTER TABLE public.trial_usages
      ADD COLUMN IF NOT EXISTS user_id VARCHAR;
  END IF;
  -- Add FK constraint if users table exists
  IF EXISTS (
    SELECT 1 FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relname = 'users' AND n.nspname = 'public'
  ) THEN
    BEGIN
      IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'trial_usages_user_id_fkey'
          AND conrelid = 'public.trial_usages'::regclass
      ) THEN
        ALTER TABLE public.trial_usages
          ADD CONSTRAINT trial_usages_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);
      END IF;
    EXCEPTION WHEN OTHERS THEN
      -- Ignore if constraint cannot be added (e.g., missing users table)
      NULL;
    END;
  END IF;
  -- Create index only if column exists
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema='public' AND table_name='trial_usages' AND column_name='user_id'
  ) THEN
    CREATE INDEX IF NOT EXISTS idx_trial_usages_user 
      ON public.trial_usages (user_id);
  END IF;
END
$$;

-- Ensure critical indexes on underlying tables for views exist (redundancy check)
CREATE INDEX IF NOT EXISTS idx_ui_events_user_product
  ON public.ui_events (user_id, product);

-- Add composite index for common analytics filter pattern
DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relkind IN ('r','v','m')
      AND n.nspname = 'public'
      AND c.relname = 'extraction_analytics'
  ) THEN
    CREATE INDEX IF NOT EXISTS idx_extraction_analytics_tier_success
      ON public.extraction_analytics (tier, success);
  END IF;
END
$$;
