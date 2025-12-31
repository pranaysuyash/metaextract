# Trial + Credits DB Plan

This plan replaces the **in‑memory trial map** with durable DB tables and wires credits to real user/session state.

## Goals

- Persist trial usage per email (+ IP + user agent) across restarts.
- Prevent repeat “free full report” attempts.
- Keep credits tied to session or user (and merge on login).
- Enable server‑side entitlement checks for `/api/extract`.

## Schema Additions (Drizzle)

### 1) `trial_usages`
Fields:
- `id` UUID PK
- `email` text (normalized lowercase)
- `used_at` timestamp
- `ip_address` text (nullable)
- `user_agent` text (nullable)
- `session_id` text (nullable)

Indexes:
- unique index on `email`
- index on `used_at`

### 2) `credit_balances` (already exists)
Fields:
- `session_id` already present
- `user_id` already present

**Plan:** Add `unique` on `session_id` to avoid duplicates (if not already).

### 3) `credit_transactions` (already exists)
No change required.

## Server Changes

### Extraction gating
- Replace `trialUsageByEmail` with DB lookup:
  - `SELECT * FROM trial_usages WHERE email = ?`
  - if none: allow trial and insert
- On successful extraction:
  - insert trial usage if trial used
  - if credits used: `useCredits()` by balance ID

### Session ID
- Require `session_id` in extraction requests (already added on frontend).
- If user logged in, link `credit_balances.user_id` on first request.

## Migration Steps

1) Add `trial_usages` table to `shared/schema.ts`.
2) Add migration file in `server/migrations/`.
3) Run `npm run db:push`.

## Edge Cases

- Allow one trial per email **ever** (v1), or allow re‑trial after X days (later).
- If user uses trial without session_id, still record trial usage by email.
- If user later logs in, link session credits to user (merge balances).

