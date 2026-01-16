# Audit v1.5.1 (Comprehensive File Audit)

- Date: Thu Jan 15 2026 23:25:31 GMT+0530 (India Standard Time)
- Audited file: `server/cache/metadata-cache.ts`
- Base commit: `f4baadf387e9bf0d2eb9a40cb2fdc62ec4720bdc`
- Auditor: GPT-5.2 (Codex CLI)

## Discovery Evidence (Raw)

### Commands executed

```bash
test -f server/cache/metadata-cache.ts && echo "exists" || echo "missing"
git rev-parse --is-inside-work-tree
git ls-files -- server/cache/metadata-cache.ts
git status --porcelain -- server/cache/metadata-cache.ts
git log -n 20 --follow -- server/cache/metadata-cache.ts
git log --follow --name-status -- server/cache/metadata-cache.ts | head -n 120
rg -n --hidden --no-ignore -S "metadata-cache" .
rg -n --hidden --no-ignore -S "from './metadata-cache'|from \"\\./metadata-cache\"|metadataCache|getMetadataCache\" server .
rg -n --hidden --no-ignore -S "metadata-cache\\.ts|metadataCache|getMetadataCache" test tests __tests__ .
git rev-parse HEAD
```

### High-signal outcomes (Observed)

- File exists and is tracked by git.
- Inbound reference: `server/utils/optimized-extraction-helpers.ts` imports `metadataCacheManager` from `../cache/metadata-cache`.
- `rg` test discovery errored for missing `test/` and `__tests__/` directories; it did find `tests/` hits for the symbol via the repo-wide search term, but no direct unit tests were identified (details below).

### Raw outputs (excerpts)

```text
$ test -f server/cache/metadata-cache.ts && echo "exists" || echo "missing"
exists

$ git rev-parse --is-inside-work-tree
true

$ git ls-files -- server/cache/metadata-cache.ts
server/cache/metadata-cache.ts

$ git status --porcelain -- server/cache/metadata-cache.ts
(no output)

$ git log --follow --name-status -- server/cache/metadata-cache.ts | head -n 120
commit 597b9c27caf1f580cd9d8723d353761db21c23ef
...
M	server/cache/metadata-cache.ts
...
commit 0ef8ca6d82613ae57f33e2b516ec4fc2785f9c94
...
A	server/cache/metadata-cache.ts

$ rg -n --hidden --no-ignore -S "metadata-cache" .
server/utils/optimized-extraction-helpers.ts:18:import { metadataCacheManager } from '../cache/metadata-cache';
...

$ rg -n --hidden --no-ignore -S "metadata-cache\\.ts|metadataCache|getMetadataCache" test tests __tests__ .
rg: test: No such file or directory (os error 2)
rg: __tests__: No such file or directory (os error 2)
./server/utils/optimized-extraction-helpers.ts:18:import { metadataCacheManager } from '../cache/metadata-cache';
...

$ git rev-parse HEAD
f4baadf387e9bf0d2eb9a40cb2fdc62ec4720bdc
```

## Findings

### METACACHE-001: Redis URL defaults to localhost (prod safety mismatch)

- Severity: HIGH
- Evidence: Observed
- Evidence snippet:
  - `DEFAULT_METADATA_CACHE_CONFIG.url: process.env.REDIS_URL || 'redis://localhost:6379'`
  - `DEFAULT_METADATA_CACHE_CONFIG.enabled: process.env.METADATA_CACHE_ENABLED !== 'false'`
- Failure mode:
  - If `METADATA_CACHE_ENABLED` is not explicitly disabled and `REDIS_URL` is unset in production, this config selects `redis://localhost:6379`.
- Blast radius:
  - Metadata responses (potentially sensitive) could be cached into an unintended Redis instance (e.g., a local/shared Redis on the host) and behave inconsistently across environments.
- Suggested minimal fix direction (no code):
  - Align production behavior with the central cache config behavior in `server/cache.ts` (Observed: that file contains a production guard). Ensure metadata-cache does not silently default to localhost in production.
- Invariants to lock post-fix:
  - In production, if `REDIS_URL` is unset, metadata caching must be disabled rather than connecting to localhost (Inferred).

### METACACHE-002: Cache key is derived from file path, not file content

- Severity: MED
- Evidence: Observed
- Evidence snippet:
  - `generateCacheKey()` hashes `filePath` and combines `tier` + options.
- Failure mode:
  - If the same `filePath` is reused for different file contents over time, cached metadata can be stale/incorrect for subsequent requests.
- Blast radius:
  - Incorrect metadata returned to callers; potential user-facing integrity issue depending on how file paths are allocated.
- Suggested minimal fix direction (no code):
  - Incorporate a content-derived component (e.g., stable file hash or upload id) into the key, or ensure callers only pass stable, content-unique paths (Unknown which is true without auditing callers).
- Invariants to lock post-fix:
  - The cache key must change when the underlying file content changes (Inferred).

### METACACHE-003: “Compression” is configured but not implemented in stored value

- Severity: MED
- Evidence: Observed
- Evidence snippet:
  - `shouldCompress` is computed and recorded as `metadata.compressed`, but `entry.value` is always the original `metadata` object.
- Failure mode:
  - Large metadata payloads are always stored uncompressed despite configuration and comments, risking higher Redis memory usage and degraded performance.
- Blast radius:
  - Increased memory pressure in Redis; eviction churn; increased serialization costs.
- Suggested minimal fix direction (no code):
  - Either implement actual compression at the boundary (store compressed payload and decompress on read) or remove/disable the compression configuration flags to avoid false assurance (pick one; do not leave partially-implemented behavior).
- Invariants to lock post-fix:
  - If `compression` is enabled and payload exceeds threshold, the stored representation must actually be compressed (Inferred).

### METACACHE-004: Tier → cache strategy mapping may not match repo tier names

- Severity: MED
- Evidence: Observed
- Evidence snippet:
  - `getCacheStrategyForTier()` handles `free`, `starter`, `pro`, `super`, `enterprise`, else default.
- Failure mode:
  - If the system uses other tier names (e.g. `professional`, `forensic`) callers may hit default strategy unexpectedly.
- Blast radius:
  - TTL/retention behavior diverges from expected tier policy; could increase costs or reduce cache effectiveness.
- Suggested minimal fix direction (no code):
  - Confirm canonical tier names used at call sites (Observed inbound reference: `server/utils/optimized-extraction-helpers.ts`) and normalize tier values before strategy selection.
- Invariants to lock post-fix:
  - All supported tier labels must map deterministically to a documented cache strategy (Inferred).

### METACACHE-005: `updateAccessTime()` is a no-op but called on HIT

- Severity: LOW
- Evidence: Observed
- Evidence snippet:
  - `get()` calls `await this.updateAccessTime(key);`
  - `updateAccessTime()` contains no logic.
- Failure mode:
  - Per-entry `accessedAt` / `hitCount` in `MetadataCacheEntry` are not updated by this class.
- Blast radius:
  - Metrics/observability inaccuracies; could confuse operational decisions.
- Suggested minimal fix direction (no code):
  - Either remove the call, or implement updating via `cacheManager` if supported (Unknown without auditing `cacheManager`).

## Out-of-scope Findings (Not Audited Here)

- OOS-METACACHE-001 (Unknown): Whether `cacheManager.initialize()` guarantees readiness when `metadataCacheManager.initialize()` sets `this.initialized = true`. This depends on `server/cache.ts` / `cacheManager` internals (out of scope).

## Next Actions

- Recommended remediation targets:
  - HIGH: `METACACHE-001`
  - MED: `METACACHE-002`, `METACACHE-003`, `METACACHE-004`
- Verification notes (what to test to close):
  - `METACACHE-001`: In production-mode configuration, verify that missing `REDIS_URL` results in caching disabled (no connection attempts, no cache hits) (Inferred).
  - `METACACHE-002`: Verify distinct cache keys for distinct file contents (or enforce path uniqueness) and confirm no stale hits when content changes (Inferred).
  - `METACACHE-003`: Verify stored payload size decreases when compression is enabled and threshold exceeded; verify get() returns original metadata (Inferred).
  - `METACACHE-004`: Verify tier normalization maps all supported tier names to intended strategies (Inferred).

