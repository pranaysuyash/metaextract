# Free Quota Enforcement Testing

This document explains how to exercise the **“2 free images per device”** protection locally. The enforcement is implemented by `server/utils/free-quota-enforcement.ts`.

## Background

- `FREE_LIMIT` is `2` images per signed client token.
- Tokens are stored in the `metaextract_client` cookie (signed HMAC + expiry).
- A soft bypass exists when `NODE_ENV=development` *and* `SKIP_FREE_LIMITS=true`.
- Exceeding the quota returns `429` with either `credits_required` or `requires_captcha`.

## Local Test Plan

### 1. Run with limits disabled (for general exploration)
```bash
SKIP_FREE_LIMITS=true NODE_ENV=development pnpm dev
```
- Allows unlimited uploads.
- Keeps the signed client token logic active, so you can verify cookies still get set.

### 2. Run with quota enforcement (for verification)
```bash
unset SKIP_FREE_LIMITS
NODE_ENV=development pnpm dev
```
- Upload the same device/browser image twice; both requests should succeed.
- On the third upload you should receive `HTTP 429` with body like:
  ```json
  {
    "error": "Quota exceeded",
    "message": "Free limit reached on this device. Purchase credits to continue.",
    "credits_required": 1,
    "current_usage": 2
  }
  ```
- The `metaextract_client` cookie contains the token; clearing it simulates a new device/token.

### 3. Testing abuse escalation
- After hitting the quota, inspect server logs for `abuse_score`.
- To force CAPTCHA responses, temporarily stub `calculateAbuseScore` (e.g., return `0.8`) and resend the request. The response should include:
  ```json
  {
    "requires_captcha": true,
    "abuse_score": 0.8
  }
  ```

### 4. Debug helpers

- To bypass SQL storage, set `USE_DB=false` (if your setup supports it) so the fallback storage path is exercised.
- Use Postman or cURL loops to simulate repeated requests instead of the UI.

## Observability

- Free usage is tracked via `client_usage` rows (field `free_used`).
- Logs include `Quota exceeded` errors; search `trackImagesMvpEvent` events if enabled.

## Notes

- The middleware still runs on all routes under `/api/images_mvp/extract`.
- Trial emails add `req.body.trial_email`, which bypasses the limit.
