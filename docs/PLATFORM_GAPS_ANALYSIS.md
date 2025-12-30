# Hidden Requirements - Platform Gaps Analysis

**Date**: 2025-12-29
**Scope**: Backend/infrastructure, security, performance, and UI/UX gaps not captured in current docs.
**Purpose**: Make implicit platform requirements explicit and actionable.

---

## 1) Backend / Infrastructure Gaps

### 1.1 Batch Processing API
**Gap**: No documented endpoint or job model for processing multiple files.
**Impact**: Users cannot submit bulk files or retrieve per-file results reliably.
**Proposed**:
- `POST /api/extract/batch` accepts multiple files or signed upload references.
- `GET /api/extract/batch/{job_id}` for job status and results.
- Job record stored with per-file status and error details.
**Acceptance**:
- Batch job supports 50-100 files with partial failures handled.

### 1.2 Webhook Notifications (Async)
**Gap**: No standard webhook model for async processing completion.
**Impact**: Business-tier integrations cannot automate downstream processing.
**Proposed**:
- Webhook events: `extraction.completed`, `extraction.failed`, `batch.completed`.
- HMAC signature, retry policy, and dead-letter handling.
**Acceptance**:
- Webhook delivery with retries and idempotency keys.

### 1.3 Rate Limiting
**Gap**: No enforced rate limits on API routes.
**Impact**: Abuse/flooding risk and cost blowups.
**Proposed**:
- IP + user_id rate limiting (Upstash Redis or equivalent).
- Tier-specific quotas.
**Acceptance**:
- 429 responses with reset headers and documented limits.

### 1.4 Caching Layer
**Gap**: No centralized cache strategy documented.
**Impact**: Repeated schema/geo lookups and repeated extraction results are expensive.
**Proposed**:
- Redis cache for schema, geocoding, and recent extraction results.
**Acceptance**:
- Configurable TTLs and cache hit/miss metrics.

### 1.5 Database Schema Mismatch
**Gap**: Docs describe SQLite schemas, but implementation uses PostgreSQL (Drizzle).
**Impact**: Migration risk, onboarding confusion, inaccurate assumptions.
**Proposed**:
- Document actual PostgreSQL schema and migrations.
- Provide ERD and schema diff vs legacy SQLite docs.
**Acceptance**:
- Single source of truth for schema with migration steps.

---

## 2) Security Gaps

### 2.1 File Type Validation
**Gap**: No strict file type validation before processing.
**Impact**: File spoofing and parser attacks.
**Proposed**:
- Validate MIME + magic bytes + extension allowlist.
**Acceptance**:
- Reject mismatches with clear error messages.

### 2.2 Memory Limits
**Gap**: No explicit memory/size constraints per upload.
**Impact**: Large file attacks and OOM crashes.
**Proposed**:
- Enforce max upload size per tier and per request.
- Stream to disk or object storage for large files.
**Acceptance**:
- Hard caps enforced server-side with predictable errors.

### 2.3 Output Sanitization
**Gap**: Metadata display lacks HTML/XSS sanitization rules.
**Impact**: Stored or reflected XSS via metadata fields.
**Proposed**:
- Escape output at render time.
- Use sanitization for any rich text rendering.
**Acceptance**:
- No HTML injection possible in metadata UI.

### 2.4 Audit Logging
**Gap**: No comprehensive logging of extraction events.
**Impact**: No audit trail for abuse, compliance, or debugging.
**Proposed**:
- Log request metadata, user_id, file hash, duration, status.
**Acceptance**:
- Queryable logs with retention policy.

---

## 3) Performance Gaps

### 3.1 Large File Handling (>1GB)
**Gap**: No streaming/chunked processing strategy.
**Impact**: Timeouts and memory blowups.
**Proposed**:
- Stream uploads to disk/object storage.
- Process with chunked readers where supported.
**Acceptance**:
- Stable extraction on 1-5GB files with bounded memory.

### 3.2 Timeout Management
**Gap**: No documented timeouts for slow external tools.
**Impact**: Hung workers and queue backlog.
**Proposed**:
- Tool-level timeouts (ffprobe, exiftool, OCR).
- Job-level timeout with cancellation.
**Acceptance**:
- Jobs fail fast with clear timeout errors.

### 3.3 Resource Cleanup
**Gap**: Temporary files not guaranteed to be cleaned on all errors.
**Impact**: Disk leakage and privacy risks.
**Proposed**:
- `try/finally` cleanup and periodic sweeper for orphan files.
**Acceptance**:
- Zero temp files after failed runs in soak tests.

---

## 4) UI/UX Gaps

### 4.1 Mobile Responsiveness
**Gap**: Complex UI components break on small screens.
**Impact**: Poor usability and conversion drop-off on mobile.
**Proposed**:
- Mobile-first layout checks and component adjustments.
**Acceptance**:
- Key flows usable on 360px width.

### 4.2 Accessibility
**Gap**: Low contrast and missing ARIA labels.
**Impact**: WCAG non-compliance and poor usability.
**Proposed**:
- Contrast audit, ARIA labels, keyboard focus styles.
**Acceptance**:
- Meets WCAG AA for key screens.

### 4.3 Error States
**Gap**: Incomplete UI messaging for failures.
**Impact**: Users cannot recover or understand failures.
**Proposed**:
- Standard error states with retry guidance.
**Acceptance**:
- All API failures show actionable messaging.

### 4.4 Loading States
**Gap**: No progress indicators for long-running extraction.
**Impact**: Users abandon before completion.
**Proposed**:
- Progress UI for uploads and processing.
**Acceptance**:
- Progress visible for all multi-second tasks.

---

## 5) Platform Phase Checklists

### P0: Safety Baseline (Q1 2026)
- [ ] File type validation (magic bytes + MIME + extension allowlist)
- [ ] Upload size caps per tier
- [ ] Parser/tool timeouts (ffprobe, exiftool, OCR)
- [ ] Temp file cleanup in all error paths + orphan sweeper
- [ ] Output escaping/sanitization in UI
- [ ] Standardized error responses for extraction failures
- [ ] Basic request metrics logged (duration, size, status)

### P1: Async + Abuse Protection (Q2 2026)
- [ ] Batch job model + API endpoints
- [ ] Background worker/queue for async extraction
- [ ] Webhook delivery (HMAC signature, retries, idempotency keys)
- [ ] Rate limiting (IP + user_id) and tier quotas
- [ ] Redis cache for schema/geocoding/recent results
- [ ] Progress reporting (server status + UI progress)
- [ ] Audit log retention policy

### P2: Scale + UX Polish (Q3 2026)
- [ ] Streaming/chunked upload path and large-file processing
- [ ] Object storage integration for temp files (S3/R2)
- [ ] Performance soak tests on 1-5GB files
- [ ] Mobile layout fixes for complex views
- [ ] Accessibility pass (contrast, ARIA, focus)
- [ ] Schema docs alignment (Postgres as source of truth)
- [ ] Regression tests for timeouts and cleanup
