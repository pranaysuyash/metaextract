# Audit v1.5.1 (Comprehensive File Audit)

- Date: Fri Jan 16 2026 12:23:51 GMT+0530 (India Standard Time)
- Audited file: `server/cache/cache-config.ts`
- Base commit: `f4baadf387e9bf0d2eb9a40cb2fdc62ec4720bdc`
- Auditor: GPT-5.2 (Codex CLI)

## Discovery Evidence (Raw)

### Commands executed

```bash
test -f server/cache/cache-config.ts && echo "exists" || echo "missing"
git ls-files -- server/cache/cache-config.ts
git status --porcelain -- server/cache/cache-config.ts
git log -n 20 --follow -- server/cache/cache-config.ts
git log --follow --name-status -- server/cache/cache-config.ts | head -n 120
rg -n --hidden --no-ignore -S "cache-config" .
rg -n --hidden --no-ignore -S "from './cache-config'|from \"\\./cache-config\"|DEFAULT_CACHE_CONFIG|CacheConfig" server .
rg -n --hidden --no-ignore -S "cache-config\\.ts|DEFAULT_CACHE_CONFIG|CacheConfig" tests test __tests__ .
```

### High-signal outcomes (Observed)

- File exists and is tracked by git.
- Git history indicates this file was added in commit `b91e9fad6dffc60d8c60e5652835c4019e76a5a5` (Observed from `git log --name-status`).
- Repository contains another cache config in `server/cache.ts` (Observed by repo context; this file defines `redisUrl` whereas `server/cache.ts` defines `url`), implying multiple competing cache config shapes (Inferred).

### Raw outputs (excerpts)

```text
$ test -f server/cache/cache-config.ts && echo "exists" || echo "missing"
exists

$ git ls-files -- server/cache/cache-config.ts
server/cache/cache-config.ts

$ git status --porcelain -- server/cache/cache-config.ts
(no output)

$ git log --follow --name-status -- server/cache/cache-config.ts | head -n 120
commit b91e9fad6dffc60d8c60e5652835c4019e76a5a5
A	server/cache/cache-config.ts

$ rg -n --hidden --no-ignore -S "cache-config" .
... (multiple matches across repo; not reproduced in full)

$ rg -n --hidden --no-ignore -S "cache-config\\.ts|DEFAULT_CACHE_CONFIG|CacheConfig" tests test __tests__ .
rg: test: No such file or directory (os error 2)
rg: __tests__: No such file or directory (os error 2)
```

## Findings

### CACHECFG-001: Redis URL defaults to localhost with no production guard

- Severity: HIGH
- Evidence: Observed
- Evidence snippet:
  - `redisUrl: process.env.REDIS_URL || 'redis://localhost:6379'`
- Failure mode:
  - When `REDIS_URL` is unset in production, this config selects localhost, which can cause unintended connections and unsafe cache behavior depending on deployment topology.
- Blast radius:
  - Any code path using this `DEFAULT_CACHE_CONFIG` for Redis connectivity.
- Suggested minimal fix direction (no code):
  - Apply the same production guard pattern as used in `server/cache.ts` (Observed in that file) so production does not fall back to localhost.
- Invariants to lock post-fix:
  - In production, if `REDIS_URL` is unset, caching must be disabled rather than connecting to localhost (Inferred).

### CACHECFG-002: Environment variable name differs from other cache configs (`CACHE_ENABLED` vs `REDIS_CACHE_ENABLED`)

- Severity: MED
- Evidence: Observed
- Evidence snippet:
  - `enabled: process.env.CACHE_ENABLED === 'true'`
- Failure mode:
  - Operators may set `REDIS_CACHE_ENABLED` (Observed: used by `server/cache.ts`) and expect caching to enable/disable globally, but this config uses a different toggle.
- Blast radius:
  - Partial enablement/disablement across cache subsystems, causing inconsistent behavior and hard-to-debug cache state.
- Suggested minimal fix direction (no code):
  - Consolidate on one canonical env var name for cache enablement, or clearly scope and document per-subsystem env vars (Unknown where docs live without auditing docs).
- Invariants to lock post-fix:
  - A single, documented env var must deterministically control Redis cache enablement across server cache layers (Inferred).

### CACHECFG-003: CacheConfig shape differs from other cache layer (`redisUrl` vs `url`, `maxMemory` type)

- Severity: MED
- Evidence: Observed
- Evidence snippet:
  - `CacheConfig.redisUrl: string`, `CacheConfig.maxMemory: number`
- Failure mode:
  - Callers expecting `url` or `maxMemory` as a string (Observed: `server/cache.ts` uses `maxMemory: '256mb'`) may misconfigure Redis or fail type-checking if types drift.
- Blast radius:
  - Any code path sharing config objects between these two config systems.
- Suggested minimal fix direction (no code):
  - Choose one canonical config interface (and property names/types) and ensure all cache subsystems consume it consistently.
- Invariants to lock post-fix:
  - Cache configuration keys and types must be consistent across server cache modules (Inferred).

## Out-of-scope Findings (Not Audited Here)

- OOS-CACHECFG-001 (Unknown): Exact runtime impact of config divergence depends on which cache subsystem is wired into production routes (requires auditing call sites).

## Next Actions

- Recommended remediation targets:
  - HIGH: `CACHECFG-001`
  - MED: `CACHECFG-002`, `CACHECFG-003`
- Verification notes (what to test to close):
  - `CACHECFG-001`: In production-mode config, verify missing `REDIS_URL` disables caching and avoids connection attempts (Inferred).
  - `CACHECFG-002`: Verify a single env var reliably enables/disables caches that rely on this config (Inferred).
  - `CACHECFG-003`: Verify cache config consumers accept the unified config shape and do not regress serialization/TTL behavior (Inferred).

