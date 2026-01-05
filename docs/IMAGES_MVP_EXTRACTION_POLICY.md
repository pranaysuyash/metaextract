# Images MVP Extraction Policy

Decision: **No pared-down extractor for MVP**. We keep the full Python-based pipeline (EXIF/RAW/MakerNotes) to preserve comprehensive coverage and avoid regressions when usage scales.

Health verification:
- Endpoint: `GET /api/extract/health/image`
- Default sample: `sample_with_meta.jpg` in the repo. Override with `IMAGE_HEALTHCHECK_PATH` if you deploy without that asset.
- Expected: HTTP 200 with `status: "healthy"`, non-zero `exif_fields`, and an engine version present.

Operational notes:
- If the sample is missing, the endpoint returns 503 with `reason: sample_not_found`.
- This health check ensures the full extractor (not a JS-only fallback) is alive on the deploy target. Use it in readiness checks after deploys.
