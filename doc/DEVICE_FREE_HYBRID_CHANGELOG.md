Device-free Hybrid Access (2026-01-12)

Summary:
- Introduced `access.mode = "device_free" | "trial_limited" | "paid"` in Images MVP responses.
- Implemented hybrid redaction for `device_free`: high-value fields (EXIF, calculated, hashes, thumbnails presence, perceptual hashes, metadata_comparison) are shown; sensitive identifiers (exact GPS, owner fields, extended attribute values, burned OCR text and precise parsed locations) are redacted or coarsened.
- `trial_limited` retains heavy redaction behavior.
- Frontend: lock UI now checks `access.mode` instead of credit heuristics; device_free shows a banner explaining what is hidden and free usage count.
- Tests: backend + frontend unit tests added for acceptance criteria.

Implementation details & developer notes:
- Backend: added `applyAccessModeRedaction()` in `server/utils/extraction-helpers.ts` and applied redaction in `server/routes/images-mvp.ts` after transformation.
- Engine tier: `device_free` uses the full engine tier for higher fidelity; `trial_limited` uses `free` tier.
- Acceptance tests added in `server/routes/images-mvp.test.ts` and `client/src/__tests__/images-mvp.device-free.test.tsx`.

Policy implication: device free checks now provide meaningful value while protecting PII. If you prefer a different coarsening approach (e.g., remove GPS entirely vs rounding), adjust `applyAccessModeRedaction()` accordingly.
