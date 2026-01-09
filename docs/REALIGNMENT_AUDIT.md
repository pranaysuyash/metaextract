# MetaExtract Realignment Audit

**Date:** January 9, 2026  
**Auditor:** Amp Agent  
**Status:** Evidence-Based Audit (No Implementation)

---

## One-Page Current Truth

### What It Is
MetaExtract is a **freemium metadata extraction web application** targeting forensics, journalism, and privacy-conscious users. It extracts metadata from images/video/audio/PDF/SVG using a Python backend (ExifTool + Pillow + Mutagen + specialized libraries) exposed via a TypeScript/Express server with a React frontend.

### What It Does Today
- **Image extraction works end-to-end**: Upload → Python extraction → JSON response → React display
- **Tiered access**: Free (200-300 fields), Professional ($19/mo, 2000+ fields), Forensic ($49/mo, 15000+ fields), Enterprise
- **Rate limiting and quota enforcement**: Redis-backed, device token system
- **831 passing JS tests, 45 test suites** (`npm test`)
- **CI pipeline**: GitHub Actions with frontend, backend, security, e2e smoke tests

### What It Cannot Do Yet
- **Python engine has syntax error** (`comprehensive_metadata_engine.py:3235`) blocking direct Python imports
- **No audio/video extraction evidence verified** in current session
- **Abuse resistance** (identity ladder, challenge system) is designed but not implemented
- **Batch processing** for Business tier is incomplete

### Next 3 Moves
1. Fix Python syntax error in `comprehensive_metadata_engine.py`
2. Verify end-to-end extraction for all 5 file types (image, video, audio, PDF, SVG)
3. Complete abuse resistance implementation (device tokens, cost calculator)

---

## Section A: Goal and Scope (What We Started To Build)

### 1. Stated Mission
**Verdict:** The repo is a metadata extraction SaaS product targeting forensics professionals.

**Authoritative source:** [docs/metaextract_design.md](file:///Users/pranay/Projects/metaextract/docs/metaextract_design.md)

> "**MetaExtract** is a lightweight, standalone web application that extracts comprehensive metadata from digital files. It leverages PhotoSearch's world-class `metadata_extractor.py` backend (320+ fields across images, videos, audio, PDFs, SVGs) to provide forensic-grade metadata extraction as a freemium service."

**Lines:** 1-13

### 2. Top 3 Authoritative Docs

| Rank | File | Why Authoritative |
|------|------|-------------------|
| 1 | `docs/metaextract_design.md` | Product Design Document v1.0 with pricing, architecture, roadmap |
| 2 | `shared/tierConfig.ts` | Production tier definitions with actual field counts, features, pricing |
| 3 | `package.json` | Description: "The world's most comprehensive metadata extraction system" |

### 3. Intended Users and Workflow
**Verdict:** "Me + agents" local development with cloud deployment on Railway.

**Evidence:**
- `docs/metaextract_design.md:25-60`: Five personas - Digital Forensics/Legal (PRIMARY), Journalists, Security/OSINT, Photographers, Privacy users
- `docs/README.md:1-5`: "Documentation for MetaExtract images_mvp"
- No mention of multi-tenant SaaS at scale yet; focused on MVP validation

**Workflow:** Single user uploads file → extracts metadata → views/exports results

### 4. Primary Decisions the Repo Helps Make

| Decision (Verb) | Citation |
|-----------------|----------|
| **Extract** metadata from any file type | `docs/metaextract_design.md:1-13` |
| **Verify** photo authenticity (forensics) | `docs/metaextract_design.md:28-40` |
| **Identify** device that created file | `docs/metaextract_design.md:34-39` |
| **Establish** timeline for evidence | `docs/metaextract_design.md:38` |
| **Export** court-ready documentation | `docs/metaextract_design.md:198-205` |

### 5. What Is Explicitly Out of Scope
**Verdict:** Not a leaderboard, not CI theater, not a multi-model comparison tool.

**Evidence:**
- No ASR/TTS/VAD/alignment/MT task types exist anywhere
- No "arsenal.json" or "DECISIONS.md" files exist
- This is NOT a speech/audio ML benchmarking repo
- `docs/README.md:227-231`: "No global caps that break for legit users" - explicitly against leaderboard-style limits

### 6. Minimal Golden Path Demo
**Verdict:** Start server, upload image, get metadata.

```bash
# 1. Start server
npm run dev:server

# 2. In another terminal, start client (optional)
npm run dev:client

# 3. Upload via curl or browser at http://127.0.0.1:3000/images-mvp

# Expected artifact: JSON with extracted metadata fields
```

**Evidence:** `npm run dev:server` output shows server starting on `127.0.0.1:3000`

### 7. Taxonomy of Tasks (File Types, NOT Speech)
**Verdict:** This repo handles file metadata extraction, not ASR/TTS/speech tasks.

**File types supported:** (from `shared/tierConfig.ts:88-300`)
- Images: JPEG, PNG, GIF, WebP, TIFF, BMP, HEIC/HEIF, SVG, RAW formats
- Documents: PDF, Office formats
- Video: MP4, QuickTime, AVI, WebM, MKV
- Audio: MPEG, WAV, FLAC, OGG
- Scientific: DICOM, FITS

**No TaskType enum exists** - this repo doesn't have ASR/TTS/VAD/diarization task definitions.

### 8. Decision Semantics
**Verdict:** Tier-based field gating, not recommended/acceptable/rejected.

**Evidence:** `shared/tierConfig.ts:77-460`
- Tiers: `free`, `professional`, `forensic`, `enterprise`
- Features gated by tier (e.g., `makerNotes: false` in free tier)
- No "evidence grades" or "gates" for model decisions
- Credit-based pay-as-you-go system

---

## Section B: Reality Snapshot (What We Have Now)

### 9. Top-Level Directories (Reality)

| Directory | Claimed Purpose | Reality |
|-----------|-----------------|---------|
| `server/` | Express backend | ✅ TypeScript Express server with routes, auth, extraction |
| `client/` | React frontend | ✅ Vite + React + Radix UI components |
| `docs/` | Documentation | ⚠️ **314 markdown files** - significant doc sprawl |
| `tests/` | Test suites | ⚠️ **1.4GB** - contains scientific-test-datasets, persona-files |
| `scripts/` | Utilities | ⚠️ **Many inventory_*.py files** - 100+ expansion scripts |
| `shared/` | Shared types | ✅ Schema + tier config |
| `server/extractor/` | Python extraction | ⚠️ **506 Python modules**, 177k total lines |
| `server/extractor/modules/` | Extraction modules | ⚠️ Massive module explosion with roman numeral extensions |

### 10. Real Entrypoints That Matter

| Entrypoint | Command | Works |
|------------|---------|-------|
| Dev server | `npm run dev:server` | ✅ Yes |
| Dev client | `npm run dev:client` | ✅ Yes (port 5173) |
| Full dev | `npm run dev` | ✅ Both concurrent |
| Tests | `npm test` | ✅ 831 tests pass |
| Gate | `npm run gate` | ✅ Runs CI checks |
| Build | `npm run build` | ⚠️ Not verified |

### 11. Single Command for Current Usage
**Verdict:** `npm run dev` is the closest.

```bash
npm run dev
# Starts both client (5173) and server (3000)
# Upload at http://localhost:5173
```

### 12. Core Contracts Between Harness and Models

**Evidence:** `server/utils/extraction-helpers.ts:51-100`

```typescript
export interface PythonMetadataResponse {
  extraction_info: { ... };
  file: { path, name, stem, extension, mime_type };
  summary: Record<string, any>;
  filesystem: Record<string, any>;
  hashes: Record<string, any>;
  image: Record<string, any> | null;
  exif: Record<string, any> | null;
  gps: Record<string, any> | null;
  video: Record<string, any> | null;
  audio: Record<string, any> | null;
  pdf: Record<string, any> | null;
  svg: Record<string, any> | null;
  // ... 20+ more categories
}
```

**Enforcement:** TypeScript interfaces, but no runtime validation beyond Zod for API inputs.

### 13. Registered Models/Extractors

**Verdict:** No "model registry" in ML sense. This is an extractor module system.

**Evidence:** `server/extractor/modules/` contains 506 Python files including:
- `exif.py`, `audio.py`, `video.py`, `pdf_metadata_complete.py`
- `forensic_*.py` (16+ variants)
- `scientific_dicom_fits_ultimate_advanced_extension_*.py` (190+ files with Roman numerals)

**Capabilities by module type:**
- Image: EXIF, ICC, MakerNotes, GPS
- Audio: ID3, Vorbis, AIFF, BWF, RF64
- Video: Container parsing, codec analysis
- Document: PDF, Office
- Scientific: DICOM, FITS

### 14. Canonical Adapter Code Paths

| File Type | Entry Module | Functions |
|-----------|--------------|-----------|
| Image | `server/extractor/modules/images.py` | `extract_image_metadata()` |
| Audio | `server/extractor/modules/audio.py` | `extract_audio_metadata()` |
| Video | `server/extractor/modules/video.py` | `extract_video_metadata()` |
| PDF | `server/extractor/modules/pdf_metadata_complete.py` | `extract_pdf_metadata()` |
| DICOM | `server/extractor/modules/dicom_extractor.py` | `extract_dicom_metadata()` |

**Main engine:** `server/extractor/comprehensive_metadata_engine.py` (3830 lines)

### 15. Production vs Candidate Classification
**Verdict:** No formal classification exists. All modules are implicitly "available".

- No `status: production|candidate|experimental` field in registry
- Modules exist as Python files with no metadata about readiness

### 16. Models Missing Evidence

| Issue | Reason |
|-------|--------|
| Python engine broken | **Syntax error at line 3235** - IndentationError |
| No extraction tests verified | Main engine can't be imported |
| Scientific modules untested | Roman numeral extensions likely generated, not tested |

**Error:**
```
File ".../comprehensive_metadata_engine.py", line 3236
    extractor = get_comprehensive_extractor()
    ^
IndentationError: expected an indented block after 'try' statement on line 3235
```

### 17. Model Outputs Persisted

| Artifact | Location | Updated |
|----------|----------|---------|
| `data/metadata.db` | SQLite database | Unknown |
| Analytics in PostgreSQL | `extractionAnalytics` table | Per request |
| No `runs/`, `reports/`, `arsenal.json` | Does not exist | N/A |

### 18. Evidence Grades
**Verdict:** No evidence grade system exists. This is not a benchmarking repo.

### 19. Datasets Under `data/`
**Verdict:** Minimal - only `metadata.db` exists.

```
data/
└── metadata.db
```

Test fixtures exist at:
- `tests/fixtures/` - 11 files (test images, DICOM, SPS samples)
- `tests/scientific-test-datasets/` - Unknown size
- `test_images/` - 1 large JPEG (9.5MB)

### 20. Relationship Between tests/ and Harness
**Verdict:** Parallel systems, loosely connected.

- `tests/*.py` - Python unit tests for extractors
- `tests/unit/`, `tests/integration/` - Jest tests for TypeScript
- `tests/e2e/` - Playwright E2E tests
- No shared test runner orchestrating both

### 21. WER Computation
**Verdict:** Not applicable. This is not a speech recognition repo. No WER calculation exists.

### 22. Gates Today

| Gate | Location | Threshold |
|------|----------|-----------|
| Rate limiting | `server/rateLimitMiddleware.ts` | Configurable per tier |
| File size | `shared/tierConfig.ts:462-470` | Max MB per tier |
| File type | `shared/tierConfig.ts:473-516` | MIME type whitelist |
| Circuit breaker | `server/utils/circuit-breaker.ts` | Failure threshold |

### 23-25. arsenal.json and DECISIONS.md
**Verdict:** Do not exist. This repo does not generate model comparison decisions.

### 26. Best Evidence Rule
**Verdict:** Not implemented. No tie-break logic for model comparison.

### 27. Setup Sequence

```bash
# Verified working:
npm install
npm run dev:server
# Server starts at 127.0.0.1:3000

# Python environment:
source .venv/bin/activate
pip list  # Shows 100+ packages including ExifTool, Pillow, Mutagen
```

### 28. Required Dependencies

**Node (required):**
- express, multer, exiftool-vendored, sharp, ioredis, pg

**Python (required):**
- PIL/Pillow, mutagen, pydicom, astropy, c2pa-python

**Optional but assumed:**
- Redis (for rate limiting) - falls back to in-memory
- PostgreSQL (for auth) - falls back to mock auth

### 29. Run Times
**Not measured** - main Python engine has syntax error preventing benchmarking.

### 30. Token Failures

| Service | Error | Location |
|---------|-------|----------|
| Database missing | "WARNING: DATABASE_URL not configured!" | `server/index.ts:91-100` |
| Redis missing | Falls back gracefully | `server/rateLimitRedis.ts` |
| Snyk token | CI continues on error | `.github/workflows/ci.yml:165` |

---

## Section C: Gap Analysis

### 31. Goal Completeness
**Verdict:** Repository is at ~70% completeness for core extraction functionality.

| Capability | Goal | Implemented |
|------------|------|-------------|
| Image extraction | 320+ fields | ✅ Yes (when Python works) |
| Tier gating | 4 tiers | ✅ Yes |
| Payment integration | Dodo Payments | ✅ Integrated |
| Abuse resistance | Identity ladder | ❌ Designed, not built |
| Batch upload | Business tier | ❌ Partial |
| API access | Business tier | ❌ Not exposed |
| PDF forensic reports | Pro tier | ❌ Not implemented |

### 32-33. Top 3 Use Cases

| Use Case | Defined Where | Can Output Decision |
|----------|---------------|---------------------|
| 1. Image forensics (GPS, hashes, timestamps) | `docs/metaextract_design.md:27-40` | ✅ Yes (via JSON export) |
| 2. Privacy checking (what data photos expose) | `docs/metaextract_design.md:55-58` | ✅ Yes |
| 3. Evidence verification (chain of custody) | `docs/metaextract_design.md:28-40` | ⚠️ Partial (no PDF reports) |

### 34-35. What's Missing Per Use Case

| Use Case | Missing | Why |
|----------|---------|-----|
| Image forensics | Nothing critical | Core flow works |
| Privacy checking | Metadata stripping tool | `processImageBuffer()` exists but not exposed |
| Evidence verification | PDF court-ready report | Designed but not implemented |

### 36. Gap Table

| Feature | Required | Implemented | Has Evidence | Emits Output |
|---------|----------|-------------|--------------|--------------|
| Image EXIF extraction | ✅ | ✅ | ✅ (tests pass) | ✅ JSON |
| Video metadata | ✅ | ✅ | ⚠️ Untested | ❓ Unknown |
| Audio metadata | ✅ | ✅ | ⚠️ Untested | ❓ Unknown |
| PDF metadata | ✅ | ✅ | ⚠️ Untested | ❓ Unknown |
| Batch processing | ✅ | ❌ | ❌ | ❌ |
| Abuse resistance | ✅ | ❌ | ❌ | ❌ |
| PDF reports | ✅ | ❌ | ❌ | ❌ |

### 37. Effort Estimates

| Missing Item | Effort (Agent Sessions) |
|--------------|------------------------|
| Fix Python syntax error | Small (1 session) |
| Verify all 5 file types work | Medium (2-3 sessions) |
| Implement abuse resistance | Large (5+ sessions) |
| Implement PDF reports | Medium (3 sessions) |
| Implement batch processing | Medium (3 sessions) |

---

## Section D: Strengths (Keep and Build On)

### 38. Best Working Loop
**Verdict:** TypeScript server + React client for image upload works reliably.

```bash
npm run dev
# Upload image at http://localhost:5173/images-mvp
# See extracted metadata in UI
```

### 39. Most Reliable Subsystem
**Verdict:** Tier configuration and rate limiting.

**Evidence:**
- `shared/tierConfig.ts` - 709 lines of clean, well-structured code
- `server/rateLimitMiddleware.ts` - Redis-backed with fallback
- 831 passing tests in TypeScript layer

### 40. Best "Boring Reliable" Artifact
**Verdict:** `shared/tierConfig.ts` - complete tier definitions, feature flags, credit costs.

### 41. Cleanest Interface Contract
**Verdict:** `server/utils/extraction-helpers.ts:51-100` - `PythonMetadataResponse` interface.

### 42. Highest Signal Dataset
**Verdict:** `tests/fixtures/test_comprehensive_v2.jpg` - used in multiple test suites.

---

## Section E: What Needs to Update

### MUST (Unblock Core Functionality)

| Priority | Item | Reason | Effort |
|----------|------|--------|--------|
| 1 | Fix Python syntax error | Blocks all Python extraction | Small |
| 2 | Verify video/audio/PDF extraction | No evidence they work | Medium |
| 3 | Create source of truth doc list | 314 docs, no index | Small |

### SHOULD (Reduce Confusion)

| Priority | Item | Reason | Effort |
|----------|------|--------|--------|
| 4 | Prune 190+ roman numeral extension files | Likely dead code | Medium |
| 5 | Consolidate extraction engine | Multiple engine variants | Large |
| 6 | Document which modules are active | No module status tracking | Medium |

### LATER (Nice to Have)

| Priority | Item | Reason | Effort |
|----------|------|--------|--------|
| 7 | Implement abuse resistance | Designed but not built | Large |
| 8 | Implement PDF reports | Feature gap | Medium |
| 9 | Implement batch processing | Business tier feature | Medium |

### 47. Source of Truth Doc List
**Proposal:** Create `docs/SOURCE_OF_TRUTH.md` with:
1. `docs/metaextract_design.md` - Product design
2. `shared/tierConfig.ts` - Tier definitions
3. `server/routes/images-mvp.ts` - Main extraction route
4. `server/utils/extraction-helpers.ts` - Python interface

### 48. Naming Inconsistencies

| Issue | Example | Fix |
|-------|---------|-----|
| Module explosion | `scientific_dicom_fits_ultimate_advanced_extension_clxxx.py` | Consolidate |
| .py.bak files | 20+ backup files in modules/ | Delete backups |
| Legacy routes | `routes_legacy.ts` vs `routes/` | Remove legacy |

### 49. Overlapping Scripts

| Script Type | Candidates | Authoritative |
|-------------|------------|---------------|
| Field counting | 8 variants (`field_count*.py`) | `scripts/true_field_count.py` |
| Inventory | 60+ `inventory_*.py` files | Unknown |
| Expansion | `mega_expansion_75k.py`, `ultra_massive_expansion.py` | All expansion scripts are questionable |

### 50. 3 Most Useful Make Targets

```makefile
# Proposed
dev:        npm run dev
test:       npm test
gate:       npm run gate
```

### 51. Minimal Local Gate

```bash
npm test                    # 831 tests
npm run check              # TypeScript
npm run lint               # ESLint
```

### 52. Minimal Artifact Checklist

After any run:
1. Check server logs for errors
2. Verify JSON response has expected categories
3. Check `fields_extracted` count matches tier

### 53. Risky Changes

| Change | Risk |
|--------|------|
| Changing tier field counts | Invalidates marketing claims |
| Modifying `PythonMetadataResponse` interface | Breaks frontend parsing |
| Changing hash algorithms | Breaks evidence verification |

### 54. Fragile Dependencies

| Dependency | Risk |
|------------|------|
| Redis URL | Falls back gracefully |
| PostgreSQL | Falls back to mock auth |
| Python venv | Specified in extraction-helpers.ts |
| ExifTool | External binary dependency |

### 55. Agent Footgun Examples

| Bad Action | Why Bad |
|------------|---------|
| Adding more roman numeral extensions | Increases bloat |
| Creating new extraction engine variant | Adds confusion |
| Changing tier pricing in code | Should be config-driven |
| Adding "improvements" to test data | Breaks baseline comparisons |
| Implementing features before fixing syntax error | Foundation is broken |

---

## Section F: Risks

### High Risk
1. **Python engine broken** - Can't test extraction without fixing syntax error
2. **Doc sprawl** - 314 markdown files with no index
3. **Module explosion** - 506 Python modules, many likely unused

### Medium Risk
4. **No verified video/audio/PDF extraction** - Claims may not hold
5. **Abuse resistance not implemented** - Vulnerable to abuse
6. **Tests directory bloat** - 1.4GB is excessive

### Low Risk
7. **CI passes but uses `|| true`** - Some failures hidden
8. **No production deployment verification** - Railway config exists but untested

---

## Section G: Recommended Next 7 Days

| Day | Action | Verification |
|-----|--------|--------------|
| 1 | Fix Python syntax error at line 3235 | `python -c "from server.extractor.metadata_engine import MetadataEngine"` succeeds |
| 2 | Verify image extraction end-to-end | Upload test.jpg, get JSON with GPS/EXIF |
| 3 | Verify video extraction | Upload .mp4, get codec/container info |
| 4 | Verify audio extraction | Upload .mp3, get ID3 tags |
| 5 | Verify PDF extraction | Upload .pdf, get page count/author |
| 6 | Create SOURCE_OF_TRUTH.md | Index of authoritative docs |
| 7 | Audit and document active modules | List which of 506 modules are actually used |

---

## Appendix: Commands Run and Key Outputs

### Environment Verification
```bash
$ npm run dev:server
> serving on 127.0.0.1:3000
✅ Rate limiter Redis connected
```

### Test Suite
```bash
$ npm test
Test Suites: 3 skipped, 45 passed, 45 of 48 total
Tests:       30 skipped, 831 passed, 861 total
```

### Python Import Failure
```bash
$ python -c "from server.extractor.metadata_engine import MetadataEngine"
IndentationError: expected an indented block after 'try' statement on line 3235
```

### Directory Sizes
```
client/: 16M
server/: 24M
docs/:   6.0M
tests/:  1.4G  # <-- Excessive
scripts/: 4.2M
```

### File Counts
```
docs/*.md: 314 files
server/extractor/modules/*.py: 506 files (177k lines)
```

---

## Claim Ledger

| Claim | Evidence | Confidence |
|-------|----------|------------|
| This is a metadata extraction SaaS | `docs/metaextract_design.md:1-13` | High |
| Target audience is forensics | `docs/metaextract_design.md:25-40` | High |
| 4 pricing tiers exist | `shared/tierConfig.ts:77-460` | High |
| 831 JS tests pass | `npm test` output | High |
| Python engine has syntax error | `python -c` import failure | High |
| Video/audio extraction works | No verification possible | Low |
| 320+ fields extracted | No test with working engine | Low |
| Abuse resistance implemented | Code review shows NOT built | High (not built) |

---

## Stop Doing List

1. **Stop creating more roman numeral extension files** - 190+ already exist
2. **Stop expanding field counts without testing** - Claims are unverified
3. **Stop creating new docs without index** - 314 files with no navigation
4. **Stop adding features before fixing core** - Python engine is broken
5. **Stop writing inventory_*.py expansion scripts** - 60+ already exist
