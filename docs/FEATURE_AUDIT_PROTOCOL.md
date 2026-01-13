# Feature Audit Protocol (Trust Baseline)

This repo has had regressions introduced via “clean” merges (no conflicts) that still removed user-facing behavior. This protocol defines what counts as a verified feature and how we prevent silent regressions.

## What “Verified” Means

A feature is **verified** only if at least one of these is true:
- A test asserts the behavior (contract test preferred).
- A deterministic script checks the behavior and is run as part of CI/pre-commit (or explicitly run before claiming “no regressions”).
- A type-level contract prevents drift (shared constants/types between client/server).

“It compiles” or “it merged” does not count as verification.

## Audit Surfaces (Minimum Set)

### Images MVP (Pricing + Credits)
- Source of truth: `shared/imagesMvpPricing.ts`
- Server enforcement: `server/routes/images-mvp.ts`
- Packs/prices: `server/payments.ts`
- Tests: `server/routes/images-mvp.test.ts`

### Payments + Webhooks (Credits / Subscriptions)
- Routes: `server/payments.ts`
- Idempotency behavior: `server/payments.ts` (processed webhooks map)
- Tests: `server/routes/*` + any payment tests (add if missing)

### Quota / Abuse / Protection
- Middleware: `server/middleware/enhanced-protection.ts`
- Threat intelligence: `server/monitoring/production-validation.ts`
- Quota enforcement: `server/utils/free-quota-enforcement.ts`
- Tests: `server/__tests__/monitoring/*`, `server/routes/*`

## How We Run the Gate

Pre-commit runs `scripts/precommit-check.cjs`:
- Small diff: `npm run lint` + `npx jest client/src/__tests__/images-mvp.hook.test.tsx`
- Large diff: `npm run check` + `npm test`

Before stating “no regressions”, run:
- `npm run check`
- `npm run lint -- --quiet`
- `npm test` (or at least the impacted test subset)

## Restoration Workflow (When Something Was “Better” in Old Commits)

1. Identify the original introduction commit (via `git log -S` / `git blame`).
2. Extract the behavior as a contract (test) **first**.
3. Reintroduce the behavior behind stable interfaces (shared constants/types).
4. Ensure old and new flows agree (e.g., quote vs extract).
5. Keep checks green at each step; no “batch fixes” without tests.

