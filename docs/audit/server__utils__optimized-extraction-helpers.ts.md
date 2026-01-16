# Audit v1.5.1 (Comprehensive File Audit)

- Date: Fri Jan 16 2026 12:30:23 GMT+0530 (India Standard Time)
- Audited file: `server/utils/optimized-extraction-helpers.ts`
- Base commit: `d1a4a704c56c5705e60c8f6c77bc6a24029fecc7`
- Auditor: GPT-5.2 (Codex CLI)

## Discovery Evidence (Raw)

### Commands executed

```bash
test -f server/utils/optimized-extraction-helpers.ts && echo "exists" || echo "missing"
git ls-files -- server/utils/optimized-extraction-helpers.ts
git status --porcelain -- server/utils/optimized-extraction-helpers.ts
git log -n 20 --follow -- server/utils/optimized-extraction-helpers.ts
git log --follow --name-status -- server/utils/optimized-extraction-helpers.ts | head -n 120
sed -n '1,260p' server/utils/optimized-extraction-helpers.ts
sed -n '260,620p' server/utils/optimized-extraction-helpers.ts
sed -n '620,980p' server/utils/optimized-extraction-helpers.ts
rg -n --hidden --no-ignore -S "optimized-extraction-helpers" .
rg -n --hidden --no-ignore -S "from '../utils/optimized-extraction-helpers'|from \"\\.\\./utils/optimized-extraction-helpers\"|optimizedExtraction" server .
rg -n --hidden --no-ignore -S "optimized-extraction-helpers\\.ts|getMetadataCacheMetrics|invalidateMetadataCache" tests test __tests__ .
rg -n --hidden --no-ignore -S "extractMetadataWithPythonOptimized" server .
git rev-parse HEAD
```

### High-signal outcomes (Observed)

- File exists and is tracked by git.
- `rg` did not find clear inbound imports of this module by path or exported symbol name (Observed from `rg` output).
- This module imports `metadataCacheManager` from `../cache/metadata-cache` and uses it as a caching layer for Python extraction (Observed in file).
- Test discovery search errored for missing `test/` and `__tests__/` directories; no direct references found under `tests/` by the searched patterns (Observed from command output).

### Raw outputs (excerpts)

```text
$ test -f server/utils/optimized-extraction-helpers.ts && echo "exists" || echo "missing"
exists

$ git ls-files -- server/utils/optimized-extraction-helpers.ts
server/utils/optimized-extraction-helpers.ts

$ git status --porcelain -- server/utils/optimized-extraction-helpers.ts
(no output)

$ git log --follow --name-status -- server/utils/optimized-extraction-helpers.ts | head -n 120
... (file added and modified; truncated)

$ rg -n --hidden --no-ignore -S "extractMetadataWithPythonOptimized" server .
server/utils/optimized-extraction-helpers.ts:61:export async function extractMetadataWithPythonOptimized(
```

## Findings

### OPTEX-001: Virtualenv python path appears to resolve outside repo (likely broken venv detection)

- Severity: HIGH
- Evidence: Observed
- Evidence snippet:
  - `const currentDirPath = path.join(projectRoot, 'server');`
  - `const venvPython = path.join(currentDirPath, '..', '..', '.venv', 'bin', 'python3');`
  - `existsSync(venvPython) ? venvPython : 'python3'`
- Failure mode:
  - With `currentDirPath = <repo>/server`, `venvPython` resolves to `<repo>/../.venv/bin/python3` (outside repo). This likely fails `existsSync` even when `<repo>/.venv/bin/python3` exists, causing fallback to system `python3`.
- Blast radius:
  - Extraction reliability (wrong python binary, missing dependencies, mismatched versions).
- Suggested minimal fix direction (no code):
  - Resolve `.venv/bin/python3` relative to the repo root deterministically (e.g., `path.join(projectRoot, '.venv', 'bin', 'python3')`) rather than navigating up from `server/` twice.
- Invariants to lock post-fix:
  - When `<repo>/.venv/bin/python3` exists, it must be selected deterministically unless `PYTHON_EXECUTABLE` overrides it (Inferred).

### OPTEX-002: Path resolution depends on `process.cwd()` and can break when run from non-root working directories

- Severity: HIGH
- Evidence: Observed
- Evidence snippet:
  - `const projectRoot = process.cwd();`
  - `const currentDirPath = path.join(projectRoot, 'server');`
  - `PYTHON_SCRIPT_PATH = path.join(currentDirPath, 'extractor', 'comprehensive_metadata_engine.py')`
- Failure mode:
  - If the server process CWD is not the repo root (e.g., started from `server/`), paths can become incorrect (e.g., `<repo>/server/server/...`) leading to Python script not found or wrong interpreter path.
- Blast radius:
  - All optimized extraction calls (hard failure at runtime if the script path is wrong).
- Suggested minimal fix direction (no code):
  - Resolve paths relative to module location (`__dirname`-style) or a single canonical app root configuration, not `process.cwd()` (Unknown existing conventions without auditing other files).
- Invariants to lock post-fix:
  - `PYTHON_SCRIPT_PATH` must resolve correctly regardless of the process working directory (Inferred).

### OPTEX-003: Repeated initialization attempts when caching is disabled (hot-path overhead + noisy logs)

- Severity: MED
- Evidence: Observed + Inferred
- Evidence snippet (Observed):
  - `if (!metadataCacheManager['initialized']) { await metadataCacheManager.initialize(); }`
- Failure mode (Inferred):
  - If `metadataCacheManager.initialize()` returns early when disabled and does not set the `initialized` flag, this guard will re-run every call, causing repeated init attempts and logs on the hot path.
- Blast radius:
  - Performance and log noise for extraction endpoints.
- Suggested minimal fix direction (no code):
  - Make initialization idempotent and ensure a stable “initialized attempted” state even when disabled, or gate the check by a public API rather than private property access (Unknown whether metadata cache exposes such API without auditing it further).
- Invariants to lock post-fix:
  - When caching is disabled, extraction must still work and must not repeatedly attempt cache initialization per request (Inferred).

### OPTEX-004: Logging includes full command + file paths (potential sensitive info leakage)

- Severity: MED
- Evidence: Observed
- Evidence snippet:
  - Logs: `Starting Python extraction process: ${pythonExecutable} ${args.join(' ')}`
  - Error details include `{ command, filePath, tier, stdout, stderr }`
  - Also logs partial Python stdout for chunks > 1000 chars.
- Failure mode:
  - File paths and potentially sensitive stdout content can be emitted to logs (including parts of extracted metadata if Python prints it).
- Blast radius:
  - Logs/observability systems; privacy risk.
- Suggested minimal fix direction (no code):
  - Redact file paths in logs (e.g., basename or hash) and avoid logging raw stdout except behind a debug flag.
- Invariants to lock post-fix:
  - Production logs must not include full file paths or raw extracted metadata payloads by default (Inferred).

### OPTEX-005: Tier name handling likely diverges from canonical tier labels in repo

- Severity: MED
- Evidence: Observed
- Evidence snippet:
  - `getCacheTTLForTier()` switches on `free`, `starter`, `pro`, `super`, `enterprise`.
- Failure mode:
  - If callers pass other tier labels (e.g., `professional`, `forensic`), TTL selection falls through to the default (30m), producing unintended caching behavior.
- Blast radius:
  - Cache TTL correctness across tiers.
- Suggested minimal fix direction (no code):
  - Normalize tier values using a shared canonical mapping before TTL selection (Unknown whether a canonical tier helper exists without auditing other files).
- Invariants to lock post-fix:
  - All supported tier labels map deterministically to a documented TTL strategy (Inferred).

## Out-of-scope Findings (Not Audited Here)

- OOS-OPTEX-001 (Unknown): Whether any production routes call `extractMetadataWithPythonOptimized()`. `rg` did not find obvious call sites by string search, but barrel exports or dynamic routing could exist (Unknown).

## Next Actions

- Recommended remediation targets:
  - HIGH: `OPTEX-001`, `OPTEX-002`
  - MED: `OPTEX-003`, `OPTEX-004`, `OPTEX-005`
- Verification notes (what to test to close):
  - `OPTEX-001`/`OPTEX-002`: Start the server from different working directories and verify extraction still locates the Python script and uses the intended interpreter (Inferred).
  - `OPTEX-003`: With caching disabled, verify extraction does not attempt cache initialization on each call (Inferred).
  - `OPTEX-004`: Verify logs do not include full file paths or raw extracted payloads under default log level (Inferred).
  - `OPTEX-005`: Verify TTL selection matches expected policy for all tier labels used by the app (Inferred).

