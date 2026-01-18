# Pricing Agent Brief: Credits Packs + Paid-First Images Launch

## Repo Guardrails (Non-negotiable)

- Follow `AGENTS.md` + `doc/AGENTS.md` (multi-agent safety: do not delete other agents’ work unless explicitly instructed).
- Pre-commit hook `scripts/precommit-check.cjs` blocks deletions/renames and requires `docs/change_reviews/` notes + semantic review for large diffs.

## Objective
Configure credits + UI so launch pricing is:
- Primary pack: `$3` for `25 images` (assume `1 image/jpeg|png = 1 credit`)
- No “free forever”; only a small trial exception (`2 images` total)
- Pricing must be isolated for the Images launch (do not reuse/overwrite existing “core app” packs).

## Current System (Repo Reality)
- Server credit checkout is implemented in `server/payments.ts` using Dodo products and a `CREDIT_PACKS` map.
- Credit charging happens in `server/routes/extraction.ts` using `getCreditCost(mimeType)` from `shared/tierConfig.ts`.
- The client shows credit packs in at least two places:
  - `client/src/pages/home.tsx` currently uses `client/src/lib/mockData.ts` packs
  - `client/src/lib/pricing.ts` also defines packs/costs (may not match server)

## Requirement: Keep Images Pricing Separate
The Images launch is an experiment and should not change global pricing surfaces.

Recommended (no DB schema changes):
- Use a dedicated credit “namespace” by prefixing the session id for Images MVP flows: `images_mvp:<sessionId>`.
  - This creates a separate `creditBalances` row while keeping the schema unchanged.
- Add product-specific routes so the UI can fetch/buy only Images packs:
  - `GET /api/images_mvp/credits/packs`
  - `POST /api/images_mvp/credits/purchase`
  - `GET /api/images_mvp/credits/balance`
- Enforce JPEG/PNG-only on the Images MVP extraction endpoint (ideally `POST /api/images_mvp/extract`).

## Key Risks to Fix
- Pack definitions are inconsistent across `server/payments.ts`, `shared/tierConfig.ts`, and `client/src/lib/*`.
- Server currently validates pack IDs as `single|batch|bulk`; client purchase flow also assumes `single|batch|bulk`.

## Required Decisions (confirm before coding)
1) Keep pack IDs as `single|batch|bulk` (recommended for minimum code churn), but repurpose values/names **for Images only**:
   - `single` => 25 credits, $3 (primary)
   - `batch` => 100 credits, $9 (optional upsell)
   - `bulk`  => 250 credits, $20–$25 (optional)
2) Trial: `2 images total` via `trial_email` (already exists), but ensure it can’t be used to obtain an enterprise/full report.

## Implementation Tasks
### A) Server (source of truth for purchasable packs)
1) Implement separate Images pack config alongside existing packs (do not overwrite global packs):
   - Add `IMAGES_CREDIT_PACKS` in `server/payments.ts` (same pack IDs, different pricing/credits).
   - Add `GET /api/images_mvp/credits/packs` returning Images MVP packs.
2) Implement product-specific purchase:
   - Add `POST /api/images_mvp/credits/purchase` that uses `images_mvp:<sessionId>` when calling `getOrCreateCreditBalance(...)`.
   - Keep `POST /api/credits/purchase` unchanged for the core app.
3) Verify the webhook credit addition path supports Images purchases:
   - Ensure purchase metadata includes `product=images_mvp` and uses the correct balance id.

### B) Credit Costs (images-only)
1) Confirm `shared/tierConfig.ts` credit costs:
   - `image/jpeg` => 1
   - `image/png`  => 1
2) Optional (recommended for images-only launch):
   - Ensure free-tier `allowedFileTypes` does not include GIF/WEBP if you don’t want them in v0.

### C) Client UI
1) Eliminate pack duplication:
   - For Images MVP UI, fetch packs from `GET /api/images_mvp/credits/packs` (recommended).
   - Avoid using `client/src/lib/mockData.ts` for Images pricing.
2) Update purchase button wiring:
   - The purchase call uses pack keys; ensure displayed names map to `single|batch|bulk` without fragile string-lowering assumptions.
   - Use product-specific purchase endpoint `POST /api/images_mvp/credits/purchase`.

### D) Trial Behavior (paid-first with a small exception)
Current behavior: `trial_email` bypasses credits in `server/routes/extraction.ts`.
Required: trial should also enforce “limited report” and “2 images total”.
Work options:
- Option 1 (recommended): force trial requests to `tier=free` and clamp response fields to a short “trial surface”.
- Option 2: keep tier requested, but strip the response down to the trial surface on the server before returning.

## Acceptance Criteria
- Packs shown in Images MVP UI exactly match `/api/images_mvp/credits/packs`.
- Buying the “$3 / 25 images” pack increases credit balance by 25.
- Uploading beyond trial requires sufficient credits and produces a clear paywall error state.
- Trial is limited to 2 images total and cannot be used to obtain a full enterprise report.
- Images credits cannot be accidentally purchased/shown on the core app pricing surfaces.

## Test Checklist
- Unit: `server/routes/tiers.test.ts` and client pricing tests remain aligned with new costs/packs.
- Manual:
  - Purchase flow -> success page -> balance updated.
  - Credit use endpoint decrements properly for JPEG/PNG.
  - Unsupported file types are rejected even if credits exist.
  - Images purchase does not affect core packs/routes.
