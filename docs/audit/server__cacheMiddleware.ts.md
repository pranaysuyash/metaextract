# Audit: server/cacheMiddleware.ts

## Header

| Field | Value |
|-------|-------|
| Audit version | Audit v1.5.1 (invoked as `audit`) |
| Date/time (local) | 2026-01-15 23:14 IST |
| Audited file path | `server/cacheMiddleware.ts` |
| Base commit SHA | `4b19ae97e2ff886992b0478dc07f0a66cc6ac0fc` |
| Auditor identity | GPT-5.2 (Codex CLI) |

---

## Discovery evidence (raw outputs)

### A) File tracking and context

```bash
$ git rev-parse --is-inside-work-tree
true

$ git ls-files -- server/cacheMiddleware.ts
server/cacheMiddleware.ts

$ git status --porcelain -- server/cacheMiddleware.ts
(empty)
```

**Observed**: `server/cacheMiddleware.ts` exists, is tracked by git, and has no uncommitted changes at the time of audit.

### B) Git history discovery (required)

```bash
$ git log -n 20 --follow -- server/cacheMiddleware.ts
commit 8b54f13eaf08f19293dccac7d021a231bd26ad33
Author: Pranay Suyash <pranay.suyash@gmail.com>
Date:   Fri Jan 2 10:55:21 2026 +0530

    Consolidate recent project updates and improvements
```

```bash
$ git log --follow --name-status -- server/cacheMiddleware.ts | sed -n '1,160p'
commit 8b54f13eaf08f19293dccac7d021a231bd26ad33
Author: Pranay Suyash <pranay.suyash@gmail.com>
Date:   Fri Jan 2 10:55:21 2026 +0530

    Consolidate recent project updates and improvements

A	server/cacheMiddleware.ts
```

**Observed**: The file appears to have a single visible commit in history (file addition). Earlier ancestry for this file is not evidenced by `git log --follow` output.

### C) Inbound and outbound reference discovery (required)

```bash
$ rg -n --hidden --no-ignore -S "from ['\\\"]\\./cacheMiddleware['\\\"]|from ['\\\"]\\.\\.\\/cacheMiddleware['\\\"]|cacheResponseMiddleware\\(|cacheInvalidationMiddleware\\(" server . | head -n 80
server/cacheExamples.ts:27:} from './cacheMiddleware';
./server/cacheExamples.ts:27:} from './cacheMiddleware';
```

```bash
$ rg -n --hidden --no-ignore -S "cacheManager|DEFAULT_CACHE_CONFIG|getRedisUrl|CacheStrategy" server client . | head -n 40
server/cacheMiddleware.ts:9:import { cacheManager, CacheStrategy, CacheMetricsSnapshot } from './cache';
server/cacheMiddleware.ts:68:    strategy = CacheStrategy.SHORT_TERM,
server/cacheMiddleware.ts:134:    strategy: CacheStrategy.MEDIUM_TERM,
server/cacheMiddleware.ts:146:    strategy: CacheStrategy.LONG_TERM,
server/cacheMiddleware.ts:162:    strategy: CacheStrategy.SHORT_TERM,
server/cacheMiddleware.ts:187:          cacheManager.invalidateByTag(tag)
server/cacheMiddleware.ts:232:    const metrics = await cacheManager.getMetrics();
server/cacheMiddleware.ts:255:    const warmed = await cacheManager.warmup(keys);
server/cacheMiddleware.ts:274:    const success = await cacheManager.clear();
```

**Observed (outbound dependencies used by this file)**:
- `express` (`Request`, `Response`, `NextFunction`)
- `./cache` (`cacheManager`, `CacheStrategy`, `CacheMetricsSnapshot`) — load-bearing (used for runtime caching calls)

**Observed (inbound references to this file)**:
- `server/cacheExamples.ts` imports symbols from `./cacheMiddleware` (example/usage surface)

**Unknown**: Whether production routes mount these middleware and endpoints, and whether they are behind auth/role gating (this requires auditing route registration files).

### D) Test discovery scoped to this file (required)

```bash
$ rg -n --hidden --no-ignore -S "cacheMiddleware|cacheResponseMiddleware|cacheInvalidationMiddleware|cacheMetricsMiddleware" tests test __tests__ server | head -n 120
rg: test: No such file or directory (os error 2)
rg: __tests__: No such file or directory (os error 2)
server/cacheExamples.ts:19:  cacheMiddleware,
server/cacheExamples.ts:27:} from './cacheMiddleware';
server/cacheExamples.ts:171:    cacheMiddleware({
...
server/cacheMiddleware.ts:63:export function cacheMiddleware(options: CacheMiddlewareOptions = {}) {
```

**Observed**: No separate `test/` or `__tests__/` directories exist in this repo root (per rg errors). No tests were found that directly reference this middleware by name beyond `server/cacheExamples.ts` usage.

### E) Audit artifact path resolution (required)

**Observed**: Deterministic artifact path is `docs/audit/server__cacheMiddleware.ts.md`.

---

## Findings (numbered)

### CACHEMW-001 — Cache key generation for GET querystring is likely incorrect (MED)

- Severity: MED
- Evidence label: Observed
- Evidence snippet:
  - `server/cacheMiddleware.ts`:
    ```ts
    req.method === 'GET' ? new URLSearchParams(req.url as string).toString() : '',
    ```
- Failure mode: `URLSearchParams` expects a query string like `"a=1&b=2"`. Passing `req.url` (which includes a leading path like `"/route?x=1"`) can produce a malformed/unstable query serialization, leading to cache key mismatches and incorrect cache hit/miss behavior.
- Blast radius: Any endpoint using `cacheMiddleware()` with `defaultKeyGenerator` for GET requests.
- Suggested minimal fix direction (no code):
  - Parse the URL with `new URL(req.url, base)` and use `url.searchParams.toString()` for the query component.
- Post-fix invariant(s) to lock:
  - Inferred: For GET requests, two different query strings must not collide into the same cache key when `req.path` is the same.
  - Inferred: Query parameter ordering differences should not change cache keys if `URLSearchParams` normalization is relied upon.

### CACHEMW-002 — Middleware caches responses for non-GET methods by default (HIGH)

- Severity: HIGH
- Evidence label: Observed
- Evidence snippet:
  - `server/cacheMiddleware.ts`:
    ```ts
    // Skip caching if disabled or should skip
    if (!enabled || skipCache(req)) {
      return next();
    }
    ```
    (no method guard before caching)
- Failure mode: If a caller accidentally mounts `cacheMiddleware()` on POST/PUT/DELETE routes (or routes supporting multiple verbs), the middleware will cache mutation responses, risking stale or incorrect behavior for subsequent requests.
- Blast radius: Any route that mounts this middleware without an explicit `skipCache` or method guard; risk is highest for mutation endpoints.
- Suggested minimal fix direction (no code):
  - Default to caching only idempotent reads (GET/HEAD) unless an explicit option allows other methods.
- Post-fix invariant(s) to lock:
  - Inferred: Non-GET/HEAD requests must never be served from cache unless explicitly opted in by the route.
  - Inferred: Cache must not cause mutation routes to return stale prior responses.

### CACHEMW-003 — Middleware caches error responses and/or partial failures (MED)

- Severity: MED
- Evidence label: Observed
- Evidence snippet:
  - `server/cacheMiddleware.ts`:
    ```ts
    res.json = (data: any) => {
      cacheManager.set(cacheKey, { data, etag: res.getHeader('ETag') }, { ttl, tags })
        .catch((err) => console.error('Cache set error:', err));
      return originalJson(data);
    };
    ```
    (no status-code gating before caching)
- Failure mode: If a handler uses `res.status(4xx/5xx).json(...)`, the middleware will cache that error payload under the same key, potentially turning transient errors into persistent cached failures until TTL expires.
- Blast radius: Any cached endpoint experiencing transient upstream failures.
- Suggested minimal fix direction (no code):
  - Gate caching on response status (e.g., only cache 2xx) and/or on explicit allowlist.
- Post-fix invariant(s) to lock:
  - Inferred: Error responses (4xx/5xx) must not be cached by default.

### CACHEMW-004 — `X-Cache-Key` header can leak sensitive info via querystrings (MED)

- Severity: MED
- Evidence label: Observed (leak surface) + Inferred (sensitive content)
- Evidence snippet:
  - `server/cacheMiddleware.ts`:
    ```ts
    res.setHeader('X-Cache-Key', cacheKey);
    ```
- Failure mode: The cache key includes request path and (intended) query string; if any endpoint uses query params carrying sensitive values (tokens, emails, IDs), those can be reflected to clients in `X-Cache-Key` and also stored in Redis keys.
- Blast radius: Any client receiving response headers; any Redis instance storing keys.
- Suggested minimal fix direction (no code):
  - Default to not returning the full cache key to clients; expose a stable hash or omit in production.
- Post-fix invariant(s) to lock:
  - Unknown: Whether any external clients rely on `X-Cache-Key` being present and readable.

### CACHEMW-005 — `strategy` and `varyOn` options are currently unused (LOW)

- Severity: LOW
- Evidence label: Observed
- Evidence snippet:
  - `server/cacheMiddleware.ts`:
    ```ts
    strategy?: CacheStrategy;
    varyOn?: string[];
    ```
    (and `strategy` is not used in middleware logic; `varyOn` is not used at all)
- Failure mode: Callers may believe these options affect behavior (TTL, key variance) when they do not, causing incorrect caching assumptions.
- Blast radius: Any route using these options expecting behavior changes.
- Suggested minimal fix direction (no code):
  - Either implement their behavior (key variance + TTL selection) or remove them from the public options contract.
- Post-fix invariant(s) to lock:
  - Inferred: Config options exposed in `CacheMiddlewareOptions` must correspond to observable runtime behavior.

### CACHEMW-006 — Exported cache control endpoints have unknown auth/gating (MED)

- Severity: MED
- Evidence label: Unknown
- Evidence snippet:
  - `server/cacheMiddleware.ts` exports:
    - `getCacheMetrics`, `warmCache`, `clearCache`
- Failure mode: If these handlers are mounted on public routes without auth/role checks, they can expose internal cache metrics and allow cache manipulation (warm/clear), impacting availability and observability hygiene.
- Blast radius: Whole API performance and cache integrity (depending on routing).
- Suggested minimal fix direction (no code):
  - Ensure route registration gates these endpoints behind admin auth and disables them in production if not needed.
- Post-fix invariant(s) to lock:
  - Unknown: The intended audience/contract for these endpoints (internal-only vs public API).

---

## Out-of-scope findings (if any)

- **Observed**: Route wiring and authorization for these middleware/handlers are not visible in this file. Determining whether `getCacheMetrics`/`warmCache`/`clearCache` are protected requires auditing whichever file mounts these exports into Express routes.

---

## Next actions

- Recommended next remediation PR targets (by ID): `CACHEMW-002`, `CACHEMW-001`, `CACHEMW-003`, `CACHEMW-004`.
- Verification notes (per HIGH/MED):
  - `CACHEMW-002`: Add integration/unit tests proving POST responses are not cached by default; add one “GET is cached” test.
  - `CACHEMW-001`: Add unit tests for `defaultKeyGenerator` to assert query extraction correctness.
  - `CACHEMW-003`: Add a test ensuring `res.status(500).json(...)` does not populate cache.
  - `CACHEMW-004`: Add a test asserting `X-Cache-Key` is omitted or redacted in production mode (if changed).

---

## Regression analysis (mandatory if git history exists and file is tracked)

### Commands executed

```bash
$ git log -n 20 --follow -- server/cacheMiddleware.ts
... (see Discovery Evidence)
```

### Concrete deltas observed

- **Observed**: No prior version of this file is visible via `git log --follow` beyond its initial add (`8b54f13...`), so a before/after delta cannot be computed from available evidence in this audit run.

### Classification (file-level only)

- Regression status: **Unknown** (Observed: insufficient prior version evidence for this file in git history output).

