# Images MVP (Split Deploy)

This folder holds configuration for deploying the Images MVP as a separate service from the same monorepo.

## Railway setup

Create a new Railway service pointing at this GitHub repo and set:

- `NIXPACKS_CONFIG_FILE=apps/images-mvp/nixpacks.toml`
- `DATABASE_URL=...` (required for credits/auth persistence)
- `DODO_PAYMENTS_API_KEY=...` (required for checkout)
- `DODO_WEBHOOK_SECRET=...` (if using webhooks)
- `BASE_URL=https://...` (used for checkout return URLs)
- Optional: `REDIS_URL=...` (not required; disabled by default in this config)

This config installs `requirements.images_mvp.txt` instead of `requirements.txt` and starts the server with `IMAGES_MVP_ONLY=true` so only `/api/images_mvp/*` and `/api/health` are exposed.

## Why this exists

- Keeps the Images MVP deploy small and cheap.
- Lets you keep developing in the monorepo while shipping a focused product service.
- Makes future extraction into a standalone repo easier (all Images MVP deploy knobs live here).
