# Audit: server/cache.ts

## Header

| Field | Value |
|-------|-------|
| Audit version | v1.5.1 |
| Date/time | 2026-01-15 |
| Audited file path | `server/cache.ts` |
| Base commit SHA | `23015036c4b2818dbbb1d64d59f1463d5701a2db` |
| Auditor identity | Amp Agent |

---

## Discovery Evidence (Raw Outputs)

### A) File Tracking & Context

```bash
$ git ls-files -- server/cache.ts
server/cache.ts

$ git status --porcelain -- server/cache.ts
(empty - file is tracked, no pending changes)
```

**Observed**: File is tracked by git with no uncommitted changes.

### B) Git History Discovery

```bash
$ git log -n 10 --oneline --follow -- server/cache.ts
8b54f13 Consolidate recent project updates and improvements
```

**Observed**: File has minimal git history (1 commit visible).

### C) Inbound/Outbound Dependencies

**Outbound (imports from this file):**
- `redis` - createClient, RedisClientType

**Inbound (files importing this file):**
```
server/cacheMiddleware.ts - imports cacheManager, CacheStrategy, CacheMetricsSnapshot
server/cacheExamples.ts - imports cacheManager
server/cache/metadata-cache.ts - imports cacheManager, CacheStrategy, DEFAULT_CACHE_CONFIG
```

**Observed**: This is load-bearing infrastructure - used by middleware and metadata cache subsystems.

### D) Test Discovery

```bash
$ rg -n "cache" tests/ --type ts
(no results)
```

**Observed**: No dedicated tests found for cache.ts.

---

## Findings

### CACHE-001: Fallback JWT Secrets in Production (HIGH)

| Field | Value |
|-------|-------|
| Severity | HIGH |
| Evidence label | Observed |
| Location | Lines 24-25 (DEFAULT_CACHE_CONFIG) |

**Evidence snippet:**
```typescript
export const DEFAULT_CACHE_CONFIG: CacheConfig = {
  enabled: process.env.REDIS_CACHE_ENABLED !== 'false',
  url: process.env.REDIS_URL || 'redis://localhost:6379',
```

**Failure mode**: If `REDIS_URL` is not set in production, the cache will attempt to connect to `localhost:6379` which will either fail or connect to an unintended Redis instance.

**Blast radius**: Cache operations fail silently or connect to wrong Redis instance, potentially exposing/mixing data.

**Suggested fix direction**: 
- Throw error if `REDIS_URL` not set and `NODE_ENV === 'production'`
- Or explicitly disable cache in production without valid config

**Invariant**: Production must not fall back to localhost Redis URL.

---

### CACHE-002: KEYS Command Used in Production (MEDIUM)

| Field | Value |
|-------|-------|
| Severity | MEDIUM |
| Evidence label | Observed |
| Location | Line 256 |

**Evidence snippet:**
```typescript
async invalidatePattern(pattern: string): Promise<number> {
  // ...
  const keys = await this.client.keys(pattern);
```

**Failure mode**: Redis `KEYS` command blocks the server and scans all keys. With large datasets, this causes latency spikes and potential timeouts.

**Blast radius**: All Redis operations blocked during KEYS execution; API latency spikes.

**Suggested fix direction**: Use `SCAN` command with cursor-based iteration instead of `KEYS`.

**Invariant**: Pattern invalidation must not block Redis for extended periods.

---

### CACHE-003: No Connection Pool / Retry Limits (MEDIUM)

| Field | Value |
|-------|-------|
| Severity | MEDIUM |
| Evidence label | Observed |
| Location | Lines 92-98 |

**Evidence snippet:**
```typescript
reconnectStrategy: (retries: number) => {
  if (retries > 10) {
    console.error('❌ Redis reconnection failed after 10 attempts');
    return new Error('Reconnection failed');
  }
  return Math.min(retries * 100, 3000);
},
```

**Failure mode**: After 10 retries fail, the error is returned but not handled - cache operations will fail silently. No circuit breaker pattern.

**Blast radius**: Continuous cache operation failures without recovery mechanism.

**Suggested fix direction**: 
- Add circuit breaker to prevent repeated failures
- Add health check endpoint for Redis connection
- Consider graceful degradation notification

**Invariant**: Cache failures must not cascade to application failures; degradation must be observable.

---

### CACHE-004: Tag Set Cleanup Missing (LOW)

| Field | Value |
|-------|-------|
| Severity | LOW |
| Evidence label | Observed |
| Location | Lines 328-336, 339-347 |

**Evidence snippet:**
```typescript
private async addToTags(key: string, tags: string[]): Promise<void> {
  for (const tag of tags) {
    await this.client.sAdd(`tag:${tag}`, key);
  }
}
```

**Failure mode**: When cache entries expire or are deleted, their keys remain in tag sets, causing stale references and memory growth.

**Blast radius**: Tag sets grow unbounded; `invalidateByTag` may attempt to delete non-existent keys.

**Suggested fix direction**: 
- Remove key from tag sets on delete
- Implement periodic tag set cleanup
- Use Redis key expiration callbacks or Lua scripts

**Invariant**: Tag sets must not contain references to expired/deleted keys.

---

### CACHE-005: Access Metadata Not Used (LOW)

| Field | Value |
|-------|-------|
| Severity | LOW |
| Evidence label | Observed |
| Location | Lines 318-326 |

**Evidence snippet:**
```typescript
private async updateAccessTime(key: string): Promise<void> {
  if (!this.client) return;
  try {
    await this.client.hSet(`access:${key}`, 'lastAccess', Date.now().toString());
  } catch (error) {
    // Silently fail to avoid impacting cache performance
  }
}
```

**Failure mode**: Access metadata is stored but never read or cleaned up. Creates orphaned `access:*` keys.

**Blast radius**: Memory growth from orphaned access metadata keys.

**Suggested fix direction**: Either use access metadata for analytics/LRU decisions, or remove the feature.

**Invariant**: Stored metadata must have a consumer or be removed.

---

### CACHE-006: Unused `reason` Parameter (LOW)

| Field | Value |
|-------|-------|
| Severity | LOW |
| Evidence label | Observed |
| Location | Line 393 |

**Evidence snippet:**
```typescript
incrementMiss(reason: string = 'unknown'): void {
  this.misses++;
}
```

**Failure mode**: The `reason` parameter is accepted but never stored or used, making miss debugging impossible.

**Blast radius**: Reduced observability; can't distinguish cache miss causes.

**Suggested fix direction**: Either track miss reasons in metrics or remove the parameter.

**Invariant**: Function parameters should be used or removed.

---

### CACHE-007: No Test Coverage (LOW)

| Field | Value |
|-------|-------|
| Severity | LOW |
| Evidence label | Observed |
| Location | N/A |

**Failure mode**: No automated tests for cache operations. Regressions may go undetected.

**Blast radius**: Cache bugs may reach production undetected.

**Suggested fix direction**: Add unit tests with Redis mock (ioredis-mock or similar).

**Invariant**: Critical infrastructure should have test coverage.

---

## Out-of-Scope Findings

### OOS-001: cacheMiddleware.ts Integration

**Observed**: `server/cacheMiddleware.ts` uses the singleton `cacheManager` export.

**Recommendation**: Audit `server/cacheMiddleware.ts` separately.

### OOS-002: metadata-cache.ts Integration

**Observed**: `server/cache/metadata-cache.ts` extends cache functionality.

**Recommendation**: Audit `server/cache/metadata-cache.ts` separately.

---

## Next Actions

| Finding ID | Recommended Action | Verification |
|------------|-------------------|--------------|
| CACHE-001 | Add production Redis URL validation | Test with missing REDIS_URL in prod mode |
| CACHE-002 | Replace KEYS with SCAN | Load test pattern invalidation |
| CACHE-003 | Add circuit breaker and health check | Test Redis disconnect scenarios |
| CACHE-004 | Implement tag cleanup on delete | Verify tag sets after key deletion |
| CACHE-005 | Remove unused access metadata feature | Verify no orphaned keys |
| CACHE-006 | Track miss reasons or remove param | Check metrics granularity |
| CACHE-007 | Add unit tests | CI test coverage |

**Priority for next remediation PR**: CACHE-003 (circuit breaker), CACHE-004 (tag cleanup)

---

## Remediation Log

### 2026-01-15: CACHE-001 & CACHE-002 Fix

**Commit**: `84debd6`
**Status**: FIXED

**CACHE-001 (Production Redis URL validation)**:
- Added `getRedisUrl()` helper function
- Returns empty string in production without REDIS_URL
- Cache disabled when URL is empty
- Warning logged for missing configuration

**CACHE-002 (KEYS → SCAN)**:
- Replaced blocking `KEYS` command with cursor-based `SCAN`
- Added batch deletion (100 keys per batch)
- Prevents Redis blocking on large datasets

**Tests added**: `server/cache.test.ts` (6 test cases)

**Behavior change**: NO - cache gracefully degrades

---

**Next audit queue**:
1. `server/cacheMiddleware.ts` (cache middleware integration)
2. `server/cache/metadata-cache.ts` (metadata-specific caching)
3. `server/db.ts` (database connection layer)
