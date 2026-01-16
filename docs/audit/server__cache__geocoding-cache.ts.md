# Audit v1.5.1 (Comprehensive File Audit)

- Date: Fri Jan 16 2026 12:25:14 GMT+0530 (India Standard Time)
- Audited file: `server/cache/geocoding-cache.ts`
- Base commit: `f4baadf387e9bf0d2eb9a40cb2fdc62ec4720bdc`
- Auditor: GPT-5.2 (Codex CLI)

## Discovery Evidence (Raw)

### Commands executed

```bash
test -f server/cache/geocoding-cache.ts && echo "exists" || echo "missing"
git ls-files -- server/cache/geocoding-cache.ts
git status --porcelain -- server/cache/geocoding-cache.ts
git log -n 20 --follow -- server/cache/geocoding-cache.ts
git log --follow --name-status -- server/cache/geocoding-cache.ts | head -n 120
rg -n --hidden --no-ignore -S "geocoding-cache" .
rg -n --hidden --no-ignore -S "from '../cache/geocoding-cache'|from \"\\.\\./cache/geocoding-cache\"|geocodingCache" server .
rg -n --hidden --no-ignore -S "geocoding-cache\\.ts|geocodingCache" tests test __tests__ .
```

### High-signal outcomes (Observed)

- File exists and is tracked by git.
- Git history indicates this file was added in commit `b91e9fad6dffc60d8c60e5652835c4019e76a5a5` (Observed from `git log --name-status`).
- `rg` inbound reference search did not find imports/usages of this file; it did find a `geocodingCache` in `server/routes/geocoding.ts` that is an in-memory `Map`, not this Redis cache class (Observed from `rg` output).
- Test discovery search errored for missing `test/` and `__tests__/` directories; no direct references found under `tests/` by that query (Observed from command output).

### Raw outputs (excerpts)

```text
$ test -f server/cache/geocoding-cache.ts && echo "exists" || echo "missing"
exists

$ git ls-files -- server/cache/geocoding-cache.ts
server/cache/geocoding-cache.ts

$ git status --porcelain -- server/cache/geocoding-cache.ts
(no output)

$ git log --follow --name-status -- server/cache/geocoding-cache.ts | head -n 120
commit b91e9fad6dffc60d8c60e5652835c4019e76a5a5
A	server/cache/geocoding-cache.ts

$ rg -n --hidden --no-ignore -S "from '../cache/geocoding-cache'|from \"\\.\\./cache/geocoding-cache\"|geocodingCache" server .
server/routes/geocoding.ts:22:const geocodingCache = new Map<string, any>();
...
```

## Findings

### GEOCCACHE-001: Uses Redis `KEYS` for invalidation (blocking + scalability risk)

- Severity: HIGH
- Evidence: Observed
- Evidence snippet:
  - `invalidateReverseGeocodeCache()` uses `const keys = await this.redis.keys(pattern);` then `await this.redis.del(...keys)`.
  - `invalidateForwardGeocodeCache()` uses `const keys = await this.redis.keys(pattern);` then `await this.redis.del(...keys)`.
- Failure mode:
  - `KEYS` is O(N) and can block Redis, causing latency spikes or timeouts under large keyspaces.
- Blast radius:
  - Redis instance used for caching; potentially affects unrelated workloads if shared.
- Suggested minimal fix direction (no code):
  - Replace `KEYS` with cursor-based `SCAN` + batched deletes.
- Invariants to lock post-fix:
  - Invalidation must not perform Redis-wide blocking operations proportional to total key count (Inferred).

### GEOCCACHE-002: Cache enablement flag exists but is not enforced in operations

- Severity: MED
- Evidence: Observed
- Evidence snippet:
  - `GeocodingCacheConfig extends CacheConfig` which includes `enabled`, but methods `set*`/`get*` do not check `this.config.enabled`.
- Failure mode:
  - Even if config indicates caching disabled, Redis read/write calls still occur.
- Blast radius:
  - Unexpected external calls; wasted Redis traffic; potential failures when Redis is intentionally absent.
- Suggested minimal fix direction (no code):
  - Gate all cache operations behind `this.config.enabled` consistently.
- Invariants to lock post-fix:
  - When caching is disabled, the cache layer must not execute Redis commands (Inferred).

### GEOCCACHE-003: Logs may leak sensitive inputs (addresses + coordinates)

- Severity: MED
- Evidence: Observed
- Evidence snippet:
  - Logs include `"${address}"` and `${latitude},${longitude}`.
- Failure mode:
  - Logs can capture user-provided addresses and locations (PII).
- Blast radius:
  - Observability systems; log retention compliance.
- Suggested minimal fix direction (no code):
  - Log redacted/hashed identifiers and avoid full address strings/precise coordinates unless explicitly in debug mode (Unknown logging framework/config without auditing elsewhere).
- Invariants to lock post-fix:
  - Production logs must not include full user-provided addresses or precise coordinates by default (Inferred).

### GEOCCACHE-004: `cacheHit` metadata is always `false` and never updated

- Severity: LOW
- Evidence: Observed
- Evidence snippet:
  - `metadata.cacheHit: false` is set on `set*` calls; `get*` does not update cached entry metadata.
- Failure mode:
  - Cached entries embed misleading metadata; metrics/inspection can be inaccurate.
- Blast radius:
  - Operational observability.
- Suggested minimal fix direction (no code):
  - Either remove `cacheHit` from stored metadata or update it via a separate metrics mechanism (Unknown whether `redis` values should be mutated without auditing usage patterns).

### GEOCCACHE-005: Broad `any` usage risks JSON serialization failures/lossiness

- Severity: LOW
- Evidence: Observed
- Evidence snippet:
  - `value: any`, `queryParams: any`, and several `options: any`, storing `JSON.stringify(entry)` into Redis.
- Failure mode:
  - Non-JSON-safe types in `options`/`results` can fail serialization or be lossy.
- Blast radius:
  - Cache set failures lead to degraded performance; silent misses.
- Suggested minimal fix direction (no code):
  - Narrow types to JSON-serializable contracts at the cache boundary.

## Out-of-scope Findings (Not Audited Here)

- OOS-GEOCCACHE-001 (Unknown): Whether this Redis geocoding cache is used in production. `server/routes/geocoding.ts` appears to use an in-memory `Map` for caching (Observed), but barrel exports/dynamic imports could bypass string search (Unknown).

## Next Actions

- Recommended remediation targets:
  - HIGH: `GEOCCACHE-001`
  - MED: `GEOCCACHE-002`, `GEOCCACHE-003`
- Verification notes (what to test to close):
  - `GEOCCACHE-001`: Run invalidation against a Redis instance with many keys; verify latency remains bounded and operations succeed reliably (Inferred).
  - `GEOCCACHE-002`: Verify disabled config causes no Redis calls and always returns cache misses (Inferred).
  - `GEOCCACHE-003`: Verify logs no longer include raw addresses/coordinates under default log level (Inferred).

