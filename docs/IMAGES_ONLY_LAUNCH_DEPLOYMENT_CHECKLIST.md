# Images-Only Launch & Deployment Checklist

## Product Readiness
- `/images` route exists and does not mention non-image domains.
- Upload accepts only `jpeg/png` in UI and API.
- Trial behavior is enforced (2 images total) and produces a limited report.
- Paid behavior is enforced via credits; paywall error states are clear.

## Pricing Readiness
- Images pricing is isolated:
  - `/api/images_mvp/credits/packs` returns Images MVP packs (primary: `$3 / 25 credits`).
  - Core app packs remain unchanged at `/api/credits/packs`.
- Dodo products configured to match Images pack IDs and prices.
- Images UI uses server-provided pack definitions (no stale mock packs).

## Observability
- Events logged for: upload, results viewed, paywall viewed, purchase completed, export clicked.
- Basic dashboards/queries exist for:
  - conversion rate (paywall -> purchase)
  - time-to-first-value (upload -> highlights)
  - repeat usage (7d)

## Security / Trust
- Clear retention policy displayed (only if true).
- Clear “we don’t train on uploads” statement (only if true).
- No hidden “forensic verdict” language; authenticity is presented as “signals”.

## Deployment (Railway/Replit/Custom)
- Env vars configured:
  - `DATABASE_URL` (if credits/subscriptions storage depends on DB)
  - `DODO_PAYMENTS_API_KEY`
  - `DODO_WEBHOOK_SECRET`
  - `DODO_ENV=live` (when going live)
  - `BASE_URL` or platform domain variables (used to build return URLs)
- Webhooks:
  - Dodo webhook endpoint reachable at `/api/webhooks/dodo`
  - Signature verification headers present in production requests
- Storage:
  - Temp upload directory writable (`/tmp/metaextract` in `server/routes/extraction.ts`)
  - Cleanup policy verified (avoid disk growth)

## Launch Day Steps
- Smoke test:
  - Upload 1 JPEG -> results render
  - Trial gating works
  - Purchase credits works
  - Paid extraction decrements credits
  - JSON export works (paid)
- Enable marketing entry point to `/images_mvp`.
- Monitor error rates and payment webhook logs for the first hour.
