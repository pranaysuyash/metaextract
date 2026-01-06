# Images MVP launch flows (and how they map to code)

This doc consolidates the **user flows + product decisions** for launch, with pointers to the current implementation.

## Experiences (frontend)

- **Core (legacy)**: `/` and `/results`
- **Core V2 (dev/internal)**: `/results-v2` (and related pages)
- **Images MVP (launch)**: `/images_mvp` and `/images_mvp/results`

All experiences share:
- One backend (`server/`) and one auth system (`server/auth.ts`).
- A shared “Credits” page for signed-in users: `/credits` (shows Core + Images MVP balances).

## Credits model (what users should expect)

There are **two credit ledgers**:
- **Core credits**: used by Core extractor flows (balances keyed as `credits:core:*`)
- **Images MVP credits**: used by Images MVP only (balances keyed as `images_mvp:*`)

Credits are stored as a balance + transactions. Purchases always create transactions; UI can display “recent credits activity”.

### Cross-browser / cross-device behavior (anti-“fraud” expectation)

- **Paid credits are account-based**. A user must be signed in to purchase so credits follow them across browsers/devices.
- **Anonymous credits are session-based** (only relevant for dev/testing grants or transitional flows). A signed-in user can “claim” those session credits into their account.

This avoids the “I paid but my other browser shows 0” scenario: the correct user expectation is:
- sign in → purchase → credits appear anywhere the user signs in.

## Free checks (trial) policy (launch decision)

**Decision:** the 2 free checks are **limited report** (high-value summary, but premium/raw exports are locked).

Rationale:
- avoids giving away full “exportable” value for free,
- reduces dispute risk (“I exported everything then refunded”),
- still lets users see meaningful results before paying.

In code, “trial”/free responses set `_trial_limited` (and/or `access.trial_granted`) and remove raw-heavy groups (IPTC/XMP, etc.). The UI disables raw exports and shows **field names + counts** while hiding values for locked sections.

## Purchase flow (Images MVP)

Goal: keep the user in the Images MVP flow, preserve context, and minimize abandonment.

Current flow:
1) User uploads an image.
2) If free checks available → analysis runs immediately.
3) If quota exhausted / insufficient credits → show pricing modal and keep a “resume” state so the same file can be processed after purchase.
4) Purchase opens Dodo checkout in a new tab.
5) Success page emits a completion signal (localStorage), and the original tab resumes automatically when focused.

### Important: return URL origin (dev multi-port)

In local dev, the app might run on multiple frontends (e.g. `5173`, `5174`, `5175`). Checkout success should return to the same origin that initiated the purchase (otherwise auth/context can look “lost”).

We compute a **trusted return origin** from the request `Origin`/`Referer`, and fall back to `BASE_URL` if missing.

## Refund policy (launch)

- Refunds are available within **7 days** of purchase for **unused credit packs only**.
- If **any credits are used**, the purchase is **non-refundable**.

For MVP, refunds remain manual (support-driven). Automated per-pack refunding requires credit “lots/grants” (FIFO consumption), which we defer until needed.

## Dev/testing helpers

- Seed test users (including an enterprise-tier “admin”): `npm run seed:test-users` (`scripts/seed_test_users.ts`)
- Seeded credentials (local/dev DB only):
  - `test@metaextract.com` / `TestPassword123!` (professional)
  - `forensic@metaextract.com` / `ForensicPassword123!` (forensic)
  - `admin@metaextract.com` / `AdminPassword123!` (enterprise/admin)
- Grant credits (dev-only):
  - Core: `POST /api/dev/credits/grant`
  - Images MVP: `POST /api/dev/images_mvp/credits/grant`

## Password reset + email delivery notes

- Passwords are **hashed**; they are never retrievable. Reset is the only supported path.
- Logged-in users can trigger resets from **Settings → Change Password** (routes to `/reset-password`).
- Reset flow (dev): `/api/auth/password-reset/request` returns a token in the JSON response when `NODE_ENV=development`.
- Reset flow (prod): must send the token via email; the API intentionally returns a generic message to avoid email enumeration.
- Email delivery still needs an SMTP provider (Gmail SMTP, SES, etc.). Python can send, but it cannot deliver on the public internet without SMTP credentials.
