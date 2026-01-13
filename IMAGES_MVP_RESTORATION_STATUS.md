# Images MVP Restoration Status

This document tracks the **Images MVP** regressions that were identified and the fixes applied to restore the “comprehensive/better” behavior without breaking tests.

## Restored / Fixed

- **Comprehensive upload flow restored**: `client/src/components/images-mvp/simple-upload.tsx`
  - Real-time quote fetching and per-file cost display.
  - Auth-aware purchase flow via `PricingModal` (no email-gating on upload).
  - Resume after purchase: listens for `metaextract_images_mvp_purchase_completed`.
  - OCR UX improvements:
    - OCR auto-suggestion for GPS/map-like filenames.
    - `?ocr=1` query param enables OCR.
    - OCR “auto-applied vs user override” tracking and hint text.

- **Progress bar regression fixed**: `server/routes/images-mvp.ts`
  - WebSocket progress payload now includes both `progress` and `percentage` (client tracker expects `percentage`).

- **Quote API made backward compatible**: `server/routes/images-mvp.ts`
  - Returns both the current server shape (`quoteId`, `creditsTotal`, `perFile` map, `schedule`) and the older client shape (`limits`, `creditSchedule`, `quote.perFile[]`, `expiresAt`, `warnings`).

- **Credits schedule matches Images MVP expectations**: `shared/imagesMvpPricing.ts`
  - Base = `1` + embedding = `3` → **4 credits**
  - Megapixel bucket add-on (e.g. “large” adds `+1`)
  - OCR add-on = `+5`

## Test Gate (Passed)

- `./.venv/bin/python -m pytest -q`
- `npm -s run check`
- `npm test -- -i --runInBand`
- `npm -s run lint` (warnings only; exit 0)

## Notes / Clarifications

- `client/src/lib/pricing.ts` contains **legacy tier definitions** marked **obsolete for Images MVP** (credit packs are used in Images MVP).
- If local development is unexpectedly using in-memory storage, confirm `DATABASE_URL` is real (not placeholder) and the DB is reachable; otherwise the app intentionally falls back to memory.

