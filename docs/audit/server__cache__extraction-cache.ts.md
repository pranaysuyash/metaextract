# Audit v1.5.1 (Comprehensive File Audit)

- Date: Thu Jan 15 2026 23:27:23 GMT+0530 (India Standard Time)
- Audited file: `server/cache/extraction-cache.ts`
- Base commit: `f4baadf387e9bf0d2eb9a40cb2fdc62ec4720bdc`
- Auditor: GPT-5.2 (Codex CLI)

## Discovery Evidence (Raw)

### Commands executed

```bash
test -f server/cache/extraction-cache.ts && echo "exists" || echo "missing"
git ls-files -- server/cache/extraction-cache.ts
git status --porcelain -- server/cache/extraction-cache.ts
git log -n 20 --follow -- server/cache/extraction-cache.ts
git log --follow --name-status -- server/cache/extraction-cache.ts | head -n 120
rg -n --hidden --no-ignore -S "extraction-cache" .
rg -n --hidden --no-ignore -S "from '../cache/extraction-cache'|from \"\\.\\./cache/extraction-cache\"|extractionCacheManager|getExtractionCache" server .
rg -n --hidden --no-ignore -S "extraction-cache\\.ts|extractionCacheManager|getExtractionCache" tests test __tests__ .
```

### High-signal outcomes (Observed)

- File exists and is tracked by git.
- No inbound references were found via `rg` for `extraction-cache` (Observed: `rg -S "extraction-cache" .` returned no hits).
- Test discovery search errored for missing `test/` and `__tests__/` directories; no direct references found under `tests/` by that query (Observed from command output).

### Raw outputs (excerpts)

```text
$ test -f server/cache/extraction-cache.ts && echo "exists" || echo "missing"
exists

$ git ls-files -- server/cache/extraction-cache.ts
server/cache/extraction-cache.ts

$ git status --porcelain -- server/cache/extraction-cache.ts
(no output)

$ git log --follow --name-status -- server/cache/extraction-cache.ts | head -n 120
commit b91e9fad6dffc60d8c60e5652835c4019e76a5a5
A	server/cache/extraction-cache.ts

$ rg -n --hidden --no-ignore -S "extraction-cache" .
(no output)

$ rg -n --hidden --no-ignore -S "extraction-cache\\.ts|extractionCacheManager|getExtractionCache" tests test __tests__ .
rg: test: No such file or directory (os error 2)
rg: __tests__: No such file or directory (os error 2)
```

## Findings

### EXTCACHE-001: Uses `Redis.keys()` for invalidation (blocking + scalability risk)

- Severity: HIGH
- Evidence: Observed
- Evidence snippet:
  - `invalidateExtractionCache()` uses `const keys = await this.redis.keys(pattern);` then `await this.redis.del(...keys)`.
- Failure mode:
  - `KEYS` is O(N) and can block Redis, causing latency spikes or timeouts under production keyspace sizes.
- Blast radius:
  - Impacts Redis instance used for caching; can degrade unrelated cache operations if shared.
- Suggested minimal fix direction (no code):
  - Replace `KEYS` with a cursor-based scan (`SCAN`) and batched deletes; or use tag-based invalidation via the shared cache layer if available (Unknown without auditing other files).
- Invariants to lock post-fix:
  - Invalidation must not perform Redis-wide blocking operations proportional to total key count (Inferred).

### EXTCACHE-002: Tier-filter keys include raw `filePath` (PII leakage + key validity risk)

- Severity: HIGH
- Evidence: Observed
- Evidence snippet:
  - `setTierFilteredResult()` / `getTierFilteredResult()` use `key = \`tier-filter:${filePath}:${originalTier}:${targetTier}\``.
- Failure mode:
  - If `filePath` contains user identifiers or sensitive path segments, that data becomes part of Redis keys (often logged/observable).
  - Raw paths can include characters that are awkward for key patterns/limits.
- Blast radius:
  - Data exposure via logs/metrics; potential key collisions or operational issues depending on path format.
- Suggested minimal fix direction (no code):
  - Hash/normalize `filePath` consistently across all key generators (Observed: other keys hash `filePath`).
- Invariants to lock post-fix:
  - Redis keys must not embed sensitive raw user-controlled path strings (Inferred).

### EXTCACHE-003: Cache key derived from `filePath`, not content (staleness risk)

- Severity: MED
- Evidence: Observed
- Evidence snippet:
  - `generateExtractionKey()` hashes `filePath` and `JSON.stringify(options)`; `generateFieldKey()` hashes `filePath`.
- Failure mode:
  - Reuse of the same `filePath` for different file contents can return stale results.
- Blast radius:
  - Incorrect extraction results returned to callers; integrity issues.
- Suggested minimal fix direction (no code):
  - Include a content-derived identifier (hash/upload id) or ensure `filePath` is content-unique (Unknown without auditing call sites).
- Invariants to lock post-fix:
  - Cache key changes when underlying content changes (Inferred).

### EXTCACHE-004: Unstructured `any` types + JSON encoding loses non-JSON values

- Severity: MED
- Evidence: Observed
- Evidence snippet:
  - `value: any`, `options: any`, `result: any`; stores `JSON.stringify(entry)` and `JSON.parse(cached)`.
- Failure mode:
  - If `result` contains non-JSON-safe types (e.g., `BigInt`, `Date`, `Buffer`, `Map`), serialization fails or produces lossy output.
- Blast radius:
  - Cache set errors (catch + log) leading to degraded performance; silent misses.
- Suggested minimal fix direction (no code):
  - Narrow result types to a JSON-serializable contract or enforce serialization at call boundary.
- Invariants to lock post-fix:
  - Cached payload must be JSON-serializable or consistently encoded/decoded without loss (Inferred).

### EXTCACHE-005: Logging includes raw `filePath` (possible sensitive info leakage)

- Severity: LOW
- Evidence: Observed
- Evidence snippet:
  - Logs: `Cached extraction result for ${filePath}`; `Cache hit ... ${filePath}`; `Cached tier-filtered result for ${filePath}`.
- Failure mode:
  - Logs can capture sensitive filesystem paths/user content identifiers.
- Blast radius:
  - Observability systems.
- Suggested minimal fix direction (no code):
  - Log a safe identifier (basename, hash prefix) rather than full `filePath`.

## Out-of-scope Findings (Not Audited Here)

- OOS-EXTCACHE-001 (Unknown): Whether this class is used in production paths. `rg` did not find inbound references by string search; it could still be referenced via barrel exports or dynamic imports (Unknown).

## Next Actions

- Recommended remediation targets:
  - HIGH: `EXTCACHE-001`, `EXTCACHE-002`
  - MED: `EXTCACHE-003`, `EXTCACHE-004`
- Verification notes (what to test to close):
  - `EXTCACHE-001`: Exercise invalidation with many keys; verify Redis latency remains bounded and operation completes reliably (Inferred).
  - `EXTCACHE-002`: Verify tier-filter keys no longer contain raw paths and remain unique/stable (Inferred).
  - `EXTCACHE-003`: Verify no stale hits when same logical path changes content (Inferred).
  - `EXTCACHE-004`: Verify cache set/get round-trip for representative extraction payloads (Inferred).

