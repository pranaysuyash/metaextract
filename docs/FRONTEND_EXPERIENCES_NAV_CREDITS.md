# Frontend Experiences, Navigation, and Credits (Decisions)

## Context

- The backend is a **single system** (one API, one auth, one database-backed source of truth).
- The frontend has **three experiences** that share the same backend:
  1) **Core (original)**: legacy flow (results/original UI).
  2) **Core V2**: internal/dev-only variant accessed via a V2 button.
  3) **Images MVP**: the **launch target** experience and the only one intended for current public launch.

The goal is to keep these experiences consistent where it matters (auth, account, credits visibility, share links), while allowing each experience to have its own UX.

## Decisions

### 1) Routing / Launch Surface

- The app should **not** forcibly route `/` to Images MVP.
- Images MVP remains reachable via the explicit Images MVP route (`/images_mvp`) and is treated as the launch surface.
- Core + V2 remain available for internal/dev use and future phased launch.

### 2) Navigation Model

- We will add **predictable traversal** for authenticated users with a small set of entry points:
  - `Dashboard` (account hub)
  - `Credits` (shared)
  - `Images MVP` (primary action)
  - `Core V2` (dev-only, hidden in prod)
  - `Core (legacy)` (optional link; can remain hidden in prod if desired)

This does not merge experiences; it provides an explicit, consistent way to move between them.

### 3) Credits Page: Shared Visibility, Separate Ledgers

- Implement a **shared** credits/account surface (`/credits`) that shows both:
  - **Images MVP credits** (used by `/api/images_mvp/extract`)
  - **Core credits** (used by `/api/extract`)
- Credits will remain **separate ledgers** for now (no automatic pooling/transfer), because:
  - It avoids “I paid but it didn’t work here” confusion.
  - It keeps spend rules and costs independent per experience.
  - A future “unified wallet” can be introduced intentionally later with explicit rules.

### 4) Auth Consistency Across Experiences

- Auth (login/register/logout) must behave consistently in all experiences.
- Password reset should exist as a first-class flow, not hidden behind support/manual work.

## Why This Helps (User Value)

- Users can always answer:
  - “Am I signed in?”
  - “What did I buy?”
  - “Where are my credits and what are they for?”
- The launch UX (Images MVP) stays focused, while account/credits are still discoverable.

## Implementation Notes (High-Level)

- `/credits` should be protected (requires auth).
- The page should clearly label balances as:
  - “Images credits (Images MVP)”
  - “Core credits (Legacy/Core)”
- Core V2 navigation should be hidden unless `NODE_ENV=development` (or a dedicated feature flag).

