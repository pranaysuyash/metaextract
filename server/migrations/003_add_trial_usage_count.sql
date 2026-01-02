-- Database Migration: Add trial usage count
-- Date: 2026-01-02
-- Purpose: Track multiple trial uses per email for Images MVP (2 uses max)

ALTER TABLE trial_usages
ADD COLUMN IF NOT EXISTS uses INTEGER NOT NULL DEFAULT 1;

UPDATE trial_usages
SET uses = 1
WHERE uses IS NULL;

