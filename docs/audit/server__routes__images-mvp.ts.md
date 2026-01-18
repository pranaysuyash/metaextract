# Audit: server/routes/images-mvp.ts

## Audit Header

- **Audit version**: Audit v1.5.1
- **Date/time**: 17 January 2026
- **Audited file path**: server/routes/images-mvp.ts
- **Base commit SHA**: 41be0fb1c9ca78b8037a9a96d32ef98c69be7aab
- **Auditor identity**: GitHub Copilot

## Discovery Evidence

### Commands Executed

1. `git rev-parse --is-inside-work-tree` - Confirmed in git repository
2. `git ls-files -- server/routes/images-mvp.ts` - File is tracked
3. `git status --porcelain -- server/routes/images-mvp.ts` - File not modified
4. `git log -n 20 --follow -- server/routes/images-mvp.ts` - Retrieved 20 commits of history
5. `git log --follow --name-status -- server/routes/images-mvp.ts | head -50` - Retrieved change history with file operations
6. `rg -n --hidden --no-ignore -S "images-mvp" . | head -20` - Found inbound references
7. `rg -n --hidden --no-ignore -S "images-mvp" test tests **tests** | head -20` - Found test references

### High-signal Outcomes

- File exists and is tracked in git
- 1864 lines, heavily modified in recent commits
- Multiple inbound references from docs, tests, and other modules
- Referenced in 20+ test files and documentation
- Recent changes include contract drift guards, deprecation warnings, and security fixes

## What This File Actually Does

This file implements the core Images MVP API routes for MetaExtract, handling quote generation, metadata extraction, analytics tracking, and credit management. It serves as the primary money path for the application, enforcing access controls, rate limits, and billing logic. The file integrates multiple security layers including free quota enforcement, enhanced protection middleware, and credit deduction with atomic transactions.

## Key Components

### Route Handlers

- `/api/images_mvp/quote` - Preflight credit calculation and quote generation
- `/api/images_mvp/extract` - Main extraction endpoint with full security stack
- `/api/images_mvp/analytics/track` - Analytics event logging
- `/api/images_mvp/credits/packs` - Credit pack information
- `/api/images_mvp/credits/purchase` - Payment processing
- `/api/images_mvp/credits/balance` - Balance checking

### Security Components

- Rate limiting (quote, extraction, analytics)
- Free quota middleware (2 extractions per device)
- Enhanced protection middleware
- Credit balance verification and atomic deduction
- File type validation (MIME + extension)
- Size limits enforcement

### Business Logic

- Credit cost calculation based on file dimensions and operations
- Trial email validation and usage tracking
- WebSocket progress broadcasting
- Quote expiration and lifecycle management

## Dependencies and Contracts

### Outbound Dependencies (Load-bearing)

**Database Operations:**

- `getDatabase()` - Database connection for trial usage queries
- `trialUsages` table queries for email-based trial tracking
- `storage.getOrCreateCreditBalance()` - Credit balance management
- `storage.useCredits()` - Atomic credit deduction
- `storage.logUiEvent()` - Analytics logging
- `storage.logExtractionUsage()` - Usage analytics
- `storage.recordTrialUsage()` - Trial usage recording

**External Services:**

- `extractMetadataWithPython()` - Core extraction via Python subprocess
- `DodoPayments` client for payment processing
- `sharp` for image dimension calculation

**Security Infrastructure:**

- `freeQuotaMiddleware` - Device-based free quota enforcement
- `enhancedProtectionMiddleware` - Advanced abuse detection
- `createRateLimiter()` - Multiple rate limiting layers
- `requireAuth()` - Authentication middleware

**Utilities:**

- `transformMetadataForFrontend()` - Response formatting
- `applyAccessModeRedaction()` - Data filtering based on access tier
- `getOrSetSessionId()` - Session management
- `broadcastProgress()` - WebSocket updates

### Inbound Dependencies

**Direct Callers:**

- Express app setup calls `registerImagesMvpRoutes(app)`
- Test files import and test individual routes
- Client-side code makes HTTP requests to these endpoints

**Assumptions Made by Callers:**

- Routes return consistent JSON schemas with `schemaVersion` fields
- Credit costs are calculated before extraction work begins
- File uploads are validated before expensive processing
- WebSocket connections are established for progress updates
- Error responses follow unified format with specific status codes

## Capability Surface

### Direct Capabilities

**Quote Generation:**

- Validates file lists and operation parameters
- Calculates credit costs based on dimensions and features
- Creates time-limited quotes with unique IDs
- Returns detailed per-file breakdowns

**Extraction Processing:**

- Accepts file uploads with multipart/form-data
- Validates file types against allowlists (MIME + extension)
- Enforces size limits (100MB per file)
- Runs Python extraction with configurable tiers
- Applies access-mode based redaction
- Charges credits atomically after successful extraction

**Access Control:**

- Supports anonymous, trial, and paid access modes
- Enforces device-based free quotas (2 extractions)
- Validates trial email usage limits
- Checks credit balances before processing
- Handles authenticated user credit deduction

**Analytics & Monitoring:**

- Logs UI events for product analytics
- Tracks extraction usage and performance metrics
- Records security events and abuse patterns
- Provides real-time progress updates via WebSocket

### Implied Capabilities

**Business Logic:**

- Implements credit-based monetization model
- Supports freemium conversion funnel (anonymous → trial → paid)
- Handles payment processing integration
- Manages quote lifecycle and expiration

**Security Posture:**

- Multi-layer abuse prevention (rate limiting, fingerprinting, circuit breaker)
- File upload security with type validation
- Credit system prevents overspending
- Audit trail for all monetization events

## Gaps and Missing Functionality

**Observability:**

- No structured logging for business metrics
- Limited error telemetry for debugging failures
- No performance monitoring for extraction times

**Resilience:**

- No retry logic for transient Python extraction failures
- Limited handling of database connection issues during credit operations
- No circuit breaker for Python subprocess failures

**Security:**

- No explicit bounds checking on uploaded file dimensions before processing
- Limited validation of client-provided metadata in quotes

## Problems and Risks

### Logic and Correctness

**HIGH: Credit Enforcement Timing (Money Path Critical)**

- Evidence: Credit balance check happens at lines 1490-1520, but extraction work begins at line 1560
- Failure mode: Server could perform expensive Python extraction work before discovering insufficient credits
- Blast radius: Wasted compute resources, potential DoS vector, billing inconsistencies

**MEDIUM: Race Condition in Credit Deduction**

- Evidence: Credit deduction uses `storage.useCredits()` with atomic WHERE clause, but concurrent requests could both pass initial balance check
- Failure mode: Double-spending if race condition window exists between balance check and deduction
- Blast radius: Financial loss, customer disputes, system instability

**MEDIUM: Trial Email Validation Bypass**

- Evidence: Trial email validation only checks database if `isDatabaseConnected()`, falls back to storage layer
- Failure mode: Inconsistent trial limits if database unavailable
- Blast radius: Unlimited free usage during database outages

### Edge Cases and Undefined Behavior

**MEDIUM: File Size Validation Gap**

- Evidence: Quote endpoint validates per-file size (line 768), but extraction endpoint relies on multer limits
- Failure mode: Inconsistent size enforcement between quote and extract
- Blast radius: Unexpected rejections, user confusion

**LOW: WebSocket Progress Without Session**

- Evidence: Progress broadcasting checks for sessionId but continues if missing
- Failure mode: Silent failures in progress updates
- Blast radius: Poor user experience, no visible feedback

### Coupling and Hidden Dependencies

**HIGH: Hardcoded Credit Limits**

- Evidence: Free quota hardcoded to 2 extractions per device
- Failure mode: Business rule changes require code deployment
- Blast radius: Inflexible pricing strategy, delayed feature updates

**MEDIUM: Environment-Specific Behavior**

- Evidence: Rate limiting and quota checks disabled in test environment
- Failure mode: Test environment doesn't match production security
- Blast radius: False confidence in security testing

### Security and Data Exposure

**MEDIUM: File Type Validation Logic**

- Evidence: Requires BOTH MIME type AND extension to be supported (AND logic)
- Failure mode: Overly restrictive for legitimate files, potential bypass attempts
- Blast radius: User friction, support burden

**LOW: Client Token in Cookies**

- Evidence: Server-issued tokens stored in httpOnly cookies
- Failure mode: Token theft via XSS if httpOnly not properly enforced
- Blast radius: Quota bypass, abuse potential

### Observability and Debuggability

**MEDIUM: Limited Error Context**

- Evidence: Generic error messages without request IDs or timestamps
- Failure mode: Difficult debugging of production issues
- Blast radius: Slower incident response, poor developer experience

## Extremes and Abuse Cases

**Large Scale:**

- 1000+ concurrent extractions could overwhelm Python subprocess pool
- Database connection exhaustion during high credit transaction volume
- WebSocket connection limits for progress broadcasting

**Adversarial Inputs:**

- Malformed multipart uploads bypassing file validation
- Race condition exploitation between quote creation and extraction
- Session fixation attacks via cookie manipulation

**Failure Scenarios:**

- Python extraction process hangs, consuming server resources
- Database unavailability during credit operations
- Redis failure causing rate limit bypass

## Inter-file Impact Analysis

### Inbound Impact

**Caller Breakage Risk:**

- Client applications expect specific JSON response schemas
- Breaking changes to quote or extraction responses could break UI
- Credit calculation changes affect pricing transparency

**Contract Preservation Needs:**

- `schemaVersion` fields must remain stable for API versioning
- Error response formats must be consistent across endpoints
- WebSocket message formats must not change without client updates

### Outbound Impact

**Dependency Failure Risk:**

- `storage.useCredits()` failure could leave extractions unpaid
- `extractMetadataWithPython()` failures waste credits
- Database unavailability breaks trial validation

**Unsafe Assumptions:**

- Assumes Python extraction always succeeds after file validation
- Assumes credit balances remain stable between check and deduction
- Assumes WebSocket connections are reliable for progress updates

### Change Impact per Finding

**Credit Timing Issue:**

- Could break callers: No, internal optimization
- Could invalidate fix: Concurrent requests could still race
- Contract lock needed: Credit deduction must be atomic
- Test proof: Concurrent extraction test with same balance

**Race Condition:**

- Could break callers: No, improves reliability
- Could invalidate fix: Database-level locking needed
- Contract lock needed: Balance check + deduction atomicity
- Test proof: Stress test with concurrent requests

## Clean Architecture Fit

**Core Responsibilities (Belongs Here):**

- HTTP request/response handling
- Input validation and sanitization
- Business rule enforcement (credits, quotas)
- Integration coordination (Python, database, storage)

**Responsibility Leakage (Should Move):**

- Credit calculation logic could be extracted to pricing service
- File validation could be shared utility
- WebSocket broadcasting could be separate service

## Patch Plan

### HIGH: Fix Credit Enforcement Timing

**Where:** server/routes/images-mvp.ts:1490-1520 (credit balance check), 1700-1720 (credit deduction)

**What:** Move credit balance verification to occur immediately after file validation but before Python extraction call

**Why:** Prevents wasted compute on insufficient credit scenarios

**Failure Prevented:** Resource exhaustion, billing inconsistencies

**Invariant:** Credit balance must be verified and reserved before any expensive operations

**Test:** Add test case where insufficient credits cause early rejection without Python call

### MEDIUM: Add Atomic Credit Reservation

**Where:** server/routes/images-mvp.ts:1700-1720 (credit deduction)

**What:** Implement credit reservation pattern - check and decrement atomically in single database transaction

**Why:** Eliminates race condition window between balance check and deduction

**Failure Prevented:** Double-spending, financial loss

**Invariant:** Credit deduction must be atomic with balance verification

**Test:** Concurrent extraction test ensuring no double charges

### MEDIUM: Strengthen Trial Validation

**Where:** server/routes/images-mvp.ts:1470-1480 (trial email check)

**What:** Add fallback trial validation when database unavailable, ensure consistent limits

**Why:** Prevents unlimited free usage during outages

**Failure Prevented:** Abuse during service degradation

**Invariant:** Trial limits must be enforced regardless of database availability

**Test:** Database outage simulation test

## Verification and Test Coverage

**Existing Tests:**

- Contract tests for response schemas
- Unit tests for credit calculation
- Integration tests for extraction flow
- Free quota enforcement tests

**Critical Gaps:**

- Concurrent credit deduction stress tests
- Database outage scenario tests
- Race condition exploitation tests

**Assumed Invariants Not Enforced:**

- Credit atomicity during concurrent requests
- Consistent behavior during partial failures
- Performance bounds for extraction operations

## Risk Rating

**HIGH Risk**

**Why at least HIGH:**

- Handles money path with credit transactions
- Complex security stack with multiple enforcement layers
- Race conditions in financial operations
- Potential for resource exhaustion attacks

**Why not CRITICAL:**

- Has multiple security layers (rate limiting, quota, validation)
- Atomic credit operations in storage layer
- Comprehensive error handling for most failure modes

## Regression Analysis

**Commands Executed:**

- `git log --follow --name-status -- server/routes/images-mvp.ts`
- `git show <recent-commits>` for specific changes

**Concrete Deltas Observed:**

- Recent commits added contract drift guards and deprecation warnings
- Security hardening with enhanced protection middleware
- Trial system integration with email validation
- WebSocket progress broadcasting implementation
- Credit system integration with atomic deductions

**Classification:**

- **Fixed:** Contract drift issues, middleware ordering
- **Regression:** None identified in recent changes
- **Unknown:** Long-term evolution from initial MVP implementation

## Next Actions

**Recommended for Next Remediation PR:**

1. Fix credit enforcement timing (HIGH priority)
2. Implement atomic credit reservation (HIGH priority)
3. Strengthen trial validation consistency (MEDIUM priority)

**Verification Notes:**

- Test concurrent extractions with shared credit balance
- Verify Python extraction not called when credits insufficient
- Confirm consistent trial limits during database outages
- Validate atomicity of credit operations under load
