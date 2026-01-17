# Production Hardening: PR Breakdown

**Both fixes implemented and tested in a single session.**

Recommend splitting into two PRs for cleaner review:

---

## PR #1: Gate C Hardening (Quote Cleanup & Rate Limiting)

**Title:** `feat: add scheduled cleanup and rate limiting for quote endpoint`

**Description:**
Prevents unbounded database growth from quote records and protects the quote endpoint from write amplification attacks.

### Changes

**server/startup-cleanup.ts**

- Added `startQuoteCleanup()` function
- Runs cleanup on boot and every 5 minutes
- One-line logging per run (non-intrusive)
- Allows graceful shutdown

**server/index.ts**

- Import `startQuoteCleanup` from startup-cleanup
- Call during server boot with 5-minute interval

**server/routes/images-mvp.ts**

- Add route-specific rate limiter to `/api/images_mvp/quote`
- Config: 30 requests/minute per IP
- Returns 429 when exceeded

### Tests

**tests/images-mvp-hardening.test.ts** (partial)

- Test rate limiting accepts normal traffic
- Test rate limiting rejects burst traffic
- Test returns 429 on limit exceeded
- Test cleanup removes expired quotes
- Test cleanup preserves non-expired quotes
- Test cleanup returns count

### Why This PR

- **Risk:** Quote table grows ~1000 rows/day with no cleanup → eventual database disk full
- **Fix:** Automatic cleanup prevents unbounded growth
- **Additional:** Rate limiter prevents abuse/DOS on write-heavy endpoint

### Testing

```bash
npm run test:ci -- tests/images-mvp-hardening.test.ts
```

### Deployment Notes

- No migration required
- Cleanup is safe (only deletes already-expired records)
- Rate limiter transparent to normal usage
- Observable via logs: `[quotes] cleanup ok ...`

---

## PR #2: Gate E Hardening (Schema Versioning)

**Title:** `feat: add schema versioning to quote response for contract stability`

**Description:**
Prevents silent contract drift between backend and frontend. Frontend now validates schema version and fails loudly if incompatible rather than silently breaking.

### Changes

**server/routes/images-mvp.ts**

- Add `schemaVersion: 'images_mvp_quote_v1'` to quote response
- Single line addition to response object

**client/src/lib/images-mvp-quote.ts**

- Add `IMAGES_MVP_QUOTE_SCHEMA_VERSION` constant
- Add `assertQuoteSchemaVersion()` validation function (type-safe)
- Update `ImagesMvpQuoteResponse` type to include `schemaVersion` field
- Update `fetchImagesMvpQuote()` to validate version before returning

### Tests

**tests/images-mvp-hardening.test.ts** (partial)

- Test quote response includes schemaVersion
- Test all required fields present
- Test field types are correct
- Test validation rejects missing schemaVersion
- Test validation rejects wrong schemaVersion
- Test validation accepts correct schemaVersion

**tests/images-mvp-contract-drift-guard.test.ts** (new)

- Comprehensive contract structure validation
- Validates all top-level fields
- Validates types for critical fields
- Validates sub-object structure
- Ensures no unexpected fields
- Validates expiresAt is future ISO date

### Why This PR

- **Risk:** Backend schema change breaks frontend UI silently → production incidents
- **Fix:** Versioned contract + frontend validation catches breaks immediately
- **Benefit:** Future schema changes can be versioned without breaking old clients

### Testing

```bash
npm run test:ci -- tests/images-mvp-hardening.test.ts
npm run test:ci -- tests/images-mvp-contract-drift-guard.test.ts
```

### Deployment Notes

- Fully backward compatible (only adds optional field to response)
- Old frontend clients ignore schemaVersion (works fine)
- New frontend clients validate and fail if version is wrong
- No database changes needed

---

## Recommended Review Order

1. **Review PR #1 first** (smaller, simpler)
   - Check `startQuoteCleanup()` pattern is acceptable
   - Verify rate limiter config matches your threat model
   - Run tests: `npm run test:ci -- tests/images-mvp-hardening.test.ts`

2. **Review PR #2 after** (contract changes)
   - Check schemaVersion field is in response
   - Check frontend validation logic is sound
   - Run full contract tests: `npm run test:ci -- tests/images-mvp-contract-drift-guard.test.ts`

3. **Together verify no regressions**
   - Run full test suite: `npm run test:ci`
   - Local dev test: `npm run dev` and check logs for `[quotes] cleanup ok`

---

## Commit Messages

### PR #1 Commit

```
feat: add scheduled quote cleanup and rate limiting

- Add startQuoteCleanup() scheduled job (runs every 5 minutes)
- Add route-specific rate limiter to /api/images_mvp/quote (30/min per IP)
- Prevents unbounded database growth from quote records
- Prevents write amplification attacks

Tests:
- Rate limiter accepts normal traffic, rejects bursts
- Cleanup removes expired quotes, preserves active ones
- Cleanup logs one line per run for observability
```

### PR #2 Commit

```
feat: add schema versioning to quote endpoint response

- Add schemaVersion field to quote response ('images_mvp_quote_v1')
- Add frontend validation that rejects unknown schema versions
- Prevents silent contract drift between backend and frontend

Tests:
- Comprehensive contract structure validation
- Type validation for all critical fields
- Schema version validation (rejects missing/wrong versions)
```

---

## Risk Assessment

### PR #1 Risk Level: **LOW**

- Cleanup function: Removes only expired records (safe)
- Rate limiter: Transparent to normal traffic, blocks abusers only
- Rollback: Remove 3 lines from server boot + route limiter
- Impact if reverted: DB growth resumes, but functionality unchanged

### PR #2 Risk Level: **MINIMAL**

- Only adds field to response (no removal/rename)
- Old clients ignore new field (backward compatible)
- Frontend validates but doesn't break existing functionality
- Rollback: Remove 1 line from response, revert frontend changes
- Impact if reverted: No schema version, but functionality unchanged

---

## Success Criteria

### PR #1 Success

- [ ] Rate limiter test passes
- [ ] Cleanup test passes
- [ ] Server boots and logs `[quotes] cleanup ok` within 5 minutes
- [ ] Manual test: 40 quote requests → first 30 succeed, rest return 429
- [ ] No regression in other quote endpoint functionality

### PR #2 Success

- [ ] Schema version validation test passes
- [ ] Contract drift guard test passes
- [ ] Quote response includes `schemaVersion: 'images_mvp_quote_v1'`
- [ ] Frontend type validation works in TypeScript
- [ ] Manual test: Frontend error if schemaVersion is wrong

---

## Future Improvements (Not In This PR)

1. Add monitoring alert if cleanup stops running
2. Implement type generation from shared schema (auto-sync frontend types)
3. Add Drizzle migration for DatabaseStorage backend
4. Document quote retention policy (15 min TTL + cleanup schedule)

These are optional hardening enhancements, not blocking.

---

**Status:** Both PRs ready for review and merge. No blocking dependencies between them.
