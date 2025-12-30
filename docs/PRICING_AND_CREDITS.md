# Pricing & Credits (Launch Proposal)

This doc proposes a pricing model that matches: **1 free file (full report) after email → then paid**.

## What Not To Do (Strong Recommendation)

- Don’t price by “number of extracted fields”. It is:
  - unpredictable for users,
  - easy to game (some files explode field counts),
  - hard to estimate before processing,
  - tightly coupled to implementation details.

## Recommended v1 Model: Credits by File Class (+ optional size multiplier)

### Why it helps
- Predictable (“video costs more than jpg”).
- Easy to estimate before upload.
- Maps to compute cost and user value better than “fields extracted”.

### Suggested credit schedule (v1)
- **Standard images (JPG/PNG/WebP/TIFF/SVG)**: 1 credit
- **RAW images / HEIC**: 2 credits
- **Audio / PDF**: 2 credits
- **Scientific single-file (DICOM/FITS/HDF5/NetCDF)**: 3–5 credits (depending on typical runtime)
- **Video (MP4/MOV/MKV/WebM/AVI)**: 5 credits

Optional size multiplier (keep simple):
- +1 credit per started 250MB beyond the first 250MB (or disable for launch).

## “Taste” Free Offer (Server-Enforced)

### Rule
- After email capture: **1 free enterprise-level report** (any supported file type, up to launch size limit).

### Implementation notes (for pricing correctness)
- The “free” is not a tier; it’s a **trial entitlement**.
- After trial is used:
  - require purchase (credits/subscription),
  - or fall back to a **preview-only** response (locked categories/fields).

## Pack vs Subscription (Launch Path)

### Option A: Credit packs only (fastest launch)
- Sell packs (e.g. 10 credits, 50 credits).
- Each extraction consumes credits based on file class.
- No monthly commitments.

### Option B: Subscriptions only
- Enforce `free/professional/forensic/enterprise`.
- Simpler messaging but requires more gating complexity for file types + field locks.

### Option C: Hybrid
- Credits for casual users + enterprise subscription for agencies.

## What the code already suggests
- `shared/tierConfig.ts` already contains `CREDIT_COSTS` and `CREDIT_PACKS`.
- Current UI “payment modal” is demo; it does not decrement credits or create entitlements.

## Important Pricing Mismatches To Resolve

- `client/src/components/payment-modal.tsx` uses a hard-coded `$5` “Full Report Unlock”.
- `shared/tierConfig.ts` defines a `single` pack as **1 credit for $2**.

Pick one source of truth for launch (credits/pack pricing), then wire UI → backend entitlement checks.

## Decision Checklist (Pick before launch)
- Do we sell **packs** or **subscription** first?
- Do we allow “preview” without payment, or require payment up-front after the one trial?
- What’s the launch max file size (match frontend+backend)?
- Do we charge extra for batch uploads, or just by total file credits?
