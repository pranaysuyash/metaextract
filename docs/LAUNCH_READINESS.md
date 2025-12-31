# Launch Readiness (Pending + Decisions)

This doc is the launch checklist for MetaExtract. It focuses on **server‑enforced** gating, abuse prevention, and “does the product behave the way pricing implies?”.

## Current Reality (Important)

- **Tier defaults to `enterprise` on the backend** when `?tier=` is omitted, and the frontend currently omits it (`/api/extract`). This effectively grants enterprise behavior by default.
- The **payment UI is demo/mock** (no real billing enforcement). Any “unlock” today is UI-only.
- Frontend upload is **hard‑capped at 100MB** (`client/src/components/upload-zone.tsx`) while backend multer allows **2GB**. This mismatch will confuse users and hide bugs.
- Backend file-type gating is **MIME-based** (`req.file.mimetype`). Browsers often send `application/octet-stream`, so strict tiering can be bypassed or accidentally block legitimate files unless we add signature/extension validation.
- Upload is **memory-based** (`multer.memoryStorage()`), which is risky for large files and DoS.
- Trial enforcement currently uses an **in-memory email map** (process-local). It must move to DB for production durability.

## Launch Offer Decision (Recommended v1)

### “Taste” free offer (what you described)
- **1 free file → full report** after email capture (no other free).
- All subsequent analyses require payment (credits or subscription).

**Key implication:** this must be enforced server-side. UI gating alone is not launch-ready.

## Must-Have Before Launch

### 1) Server-side enforcement for “1 free full report per email”
- Create a minimal **User/Trial** record (email, created_at, last_used_at, trial_used boolean).
- Add an endpoint to **start trial** (email capture) that returns a short-lived token/session.
- Require that token/session for “free full report” requests; enforce **trial-used**.
- Decide whether “free full report” can be:
  - **one-time ever**, or
  - **one per day/week** (less strict, but more abuse risk).
- Add IP + user-agent tracking for abuse signals.

### 2) Abuse protection / rate limiting
- Add global and per-route rate limits (`/api/extract`, `/api/extract/batch`, `/api/extract/advanced`).
- Add a cheap “cooldown” on repeated failures (bad files, timeouts).
- Consider CAPTCHA only for trial/email capture if bots become a problem.

### 3) File validation hardening (beyond MIME)
- Validate using:
  - **magic bytes/signatures** (JPEG/PNG/PDF/DICOM/FITS/ZIP/MP4/…)
  - **extension fallback** (already done client-side; replicate server-side)
  - keep MIME as a hint, not the source of truth.
- Enforce:
  - max decompressed/parsed sizes where relevant,
  - rejection for empty files,
  - safe temp-file naming (already uses UUID).

### 4) Resource limits and safety
- Replace `multer.memoryStorage()` with disk streaming for non-trivial sizes, or cap uploads to a small size for launch.
- Add Python extractor limits:
  - a hard **timeout** already exists (180s),
  - add **max file size** enforced before write (already tier-based),
  - consider process-level CPU/memory constraints (container limits at minimum).
- Ensure temp files are always cleaned up (the `finally cleanupTempFile()` path is good; audit batch errors too).

### 5) Billing/entitlements integration (pick one for launch)
You can launch with either:
- **Credits** (pay-per-file), or
- **Subscriptions** (tiers).

Either way you need:
- a server-side entitlement check (trial / credits / subscription),
- a purchase flow (Stripe Checkout or similar),
- webhook handling for payment success + fraud/chargeback scenarios.

### 6) UX truthfulness
- The UI should reflect real limits:
  - max upload size,
  - supported types per plan,
  - whether “batch” is available.
- Avoid showing “enterprise counts” unless the backend will actually deliver it for that user.

## Important “Soon After Launch”

### Batch processing UX
- Backend has `/api/extract/batch`; frontend currently doesn’t expose it.
- For DICOM and scientific datasets, batch/archives matter (a “study” is many files).
- Add: batch upload UI + progress + partial failures.

### Async processing + webhooks
- If extraction time is long, add:
  - job queue (BullMQ/Redis or similar),
  - `/api/extract/status/:jobId`,
  - optional webhooks for enterprise.

### Caching
- Add content-hash based caching for repeat uploads (opt-in, privacy aware).

### Audit logging
- Current usage logging exists (`storage.logExtractionUsage`) but “audit logging” for evidence workflows may require:
  - immutable event log,
  - actor identity (user/session),
  - request metadata and export actions.

## Known Doc/Config Inconsistencies
- `server/openapi.yaml` says batch is “Professional+” in the top-level description, but the batch endpoint itself and code gate it to Forensic/Enterprise. Align docs and behavior.
