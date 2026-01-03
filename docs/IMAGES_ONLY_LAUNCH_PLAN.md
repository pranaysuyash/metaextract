# Images-Only Launch Plan (Paid-First)

## Goal
Ship a narrow, fast “Image Metadata Check” experience to validate PMF with minimal scope/risk.

## Launch Scope (v0)
- Supported uploads: `image/jpeg`, `image/png`, `image/heic`, `image/heif`, `image/webp` (common photo formats).
- Primary user promise: “Get a calm summary + privacy/authenticity signals in <10s, exportable as JSON after credits.”
- Monetization: credits (paid-first), with a small trial exception (see below).

## Explicit Non-Goals (v0)
- No video/audio/PDF/doc routes or marketing claims.
- No “45k fields”, “medical”, “scientific”, or “forensic suite” positioning on user-facing surfaces.
- No complex accounts/subscriptions required for the first PMF probe.

## UX Principles
- Calm report first, progressive disclosure later.
- Never show large empty sections; prefer “Not embedded” with a 1-line explanation.
- Don’t claim certainty for authenticity; present “signals” + “inconclusive” when appropriate.

## Information Architecture
### Routes
- `/images_mvp` (landing + upload)
- `/images_mvp/results/:id` (results)

### Pages
1) **Landing / Upload (`/images_mvp`)**
   - One-screen flow: drag/drop + file list + “Analyze” CTA.
   - Hard validation:
     - Format: JPEG/PNG only
     - Batch limit: start with `max 10` per submit (adjust later)
     - Size limit: match backend free-tier/credit gating limits

2) **Results (`/images_mvp/results/:id`)**
   - Header: filename, “Download JSON”, “Analyze next”.
   - Tabs (minimal): `Privacy` (default), `Authenticity`, `Photography`, `Raw` (locked/paid).
   - “Highlights” card always at top: 3–7 bullets, plain language, confidence chips.

## Trial + Paywall (Paid-First)
### Policy for launch
- Trial: allow up to `2 images` total via `trial_email` (not “free forever”).
- Paid: credits required for any additional files.

### What is visible without credits (trial)
- Highlights card.
- Privacy tab basics (time, location embedded?, device make/model, file hashes).
- Summary export (copy/download).
- No JSON export and no raw tables.

### What is paid (credits)
- JSON export.
- Raw tab (full EXIF/XMP tables + search).
- Any advanced/expensive analysis (e.g., OCR overlay extraction if enabled).

## Backend Contract (Existing)
- Images MVP extraction endpoint: `POST /api/images_mvp/extract`.
  - Uses the same extraction helpers as the core app; no separate backend service.
- Credit purchase (Images MVP):
  - `POST /api/images_mvp/credits/purchase`
  - `GET /api/images_mvp/credits/balance`
  - `GET /api/images_mvp/credits/packs`

## Pricing Separation (Images vs Core App)
For launch, keep “Images” pricing isolated from the rest of MetaExtract so experiments don’t break existing pricing.

Recommended approach (no DB schema change):
- Use a dedicated session namespace for Images MVP credits (e.g., `images_mvp:<sessionId>`), so it creates a separate `creditBalances` row.
- Add product-specific endpoints (or a required `product=images` parameter) so the client can’t accidentally show/buy the wrong packs:
  - `GET /api/images_mvp/credits/packs`
  - `POST /api/images_mvp/credits/purchase`
  - `GET /api/images_mvp/credits/balance`
- Enforce JPEG/PNG-only on the Images MVP extraction path (ideally a separate endpoint like `POST /api/images_mvp/extract`).

## UI Implementation Notes (Repo Mapping)
- Upload + extraction flow lives in the client app under `client/src/pages/` and API calls via existing utilities.
- Credit purchase is already wired via `/api/credits/purchase` and a success page (`client/src/pages/credits-success.tsx`).
- File-type + credit-cost logic exists in `shared/tierConfig.ts` and is used server-side in `server/routes/extraction.ts`.

## Required UI Work Items
1) **New “Images” product surface**
   - Add `/images` route and use a dedicated layout/copy (not the full product homepage).
   - Show a small “supported formats” note (JPG/PNG/HEIC/WebP) and batch/file size limits.

2) **Strict file filtering**
   - UI picker filters extensions and MIME.
   - Server rejects anything else (update `shared/tierConfig.ts`/tier settings as needed).

3) **Results “calm report”**
   - Highlights generation from the returned metadata:
     - Capture time present vs missing
     - Location embedded vs not embedded
     - Device make/model present vs missing
     - Editing software present vs missing (from XMP/EXIF “Software” style keys)
     - Hash computed (SHA-256)

4) **Gating**
   - If trial: show limited fields + prompt to buy credits to unlock export/raw.
   - If out of credits: show paywall modal; don’t hard-block upload selection.

5) **Instrumentation (minimum)**
   - `images_landing_viewed`
   - `upload_selected` (file metadata + size bucket)
   - `analysis_started` / `analysis_completed` (success/fail + processing_ms)
   - `results_viewed`
   - `paywall_viewed`
   - `purchase_completed`
   - `export_clicked`
   - `repeat_user_7d` (if tracking exists)

## Rollout Plan
- Phase 0 (internal): enable route, verify extraction speed + correctness on a small curated set.
- Phase 1 (soft launch): small traffic, watch completion rate + purchase conversion + repeat usage.
- Phase 2: iterate on copy + paywall moment + highlights quality; do not expand file types until signals exist.

## Acceptance Criteria (Launch)
- Uploading a JPEG/PNG results in a “Highlights” card within a single page load.
- Unsupported formats are rejected in UI and API with clear messaging.
- Trial enforces 2 images total and does not expose locked features.
- Credits purchase completes and returns to results with updated balance.
- No user-facing mentions of unsupported domains (video/audio/docs/medical/scientific).
