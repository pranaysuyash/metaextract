# AGENTS.md - MetaExtract Development Guide

## Build, Test & Lint Commands

**Install dependencies:**

```bash
npm install && pip install -r requirements.txt
```

**Run single test:**

```bash
# JavaScript tests
npm test -- --testNamePattern="test name"
# Python tests
pytest tests/ -k "test_name" -v
```

**Full test suites:** `npm run test:ci` (TypeScript), `pytest tests/` (Python)  
**Lint:** `npm run lint` | **Fix:** `npm run lint:fix`  
**Dev server:** `npm run dev` (Express + Vite on :5173)

### Server process management (important)

- Never kill the global Node runtime (e.g., avoid `killall node`).
- To restart, only stop the dev servers: terminate the terminal/task running `npm run dev`.
- If a port is stuck, kill by port instead of all Node (macOS):
  - `lsof -ti:5173 -sTCP:LISTEN | xargs kill -9` (Vite)
  - `lsof -ti:3000 -sTCP:LISTEN | xargs kill -9` (Express)
- This prevents disrupting other Node-based tools (linters, scripts, debuggers).

## Architecture

**Full-stack monorepo:**

- **Server** (TypeScript/Express): `server/` — REST API, auth, file uploads, OCR pipeline
- **Client** (React/Vite): `client/src/` — Web UI with real-time metadata display
- **Extractor** (Python): `server/extractor/` — 10 extraction engines for 7,000+ metadata fields

**Key subsystems:**

- `comprehensive_metadata_engine.py` — Multi-domain metadata extraction (Medical DICOM, Astronomical FITS, Geospatial GeoTIFF, Scientific HDF5/NetCDF, Video, Audio, AI detection)
- `module_discovery.py` — Dynamic plugin loading from `server/extractor/modules/`
- `server/routes/` — REST endpoints for file extraction (`/extract`, `/batch`)
- `server/auth.ts` — JWT + session-based authentication with tier system
- `shared/schema.ts` — Zod schemas for API validation

**Database:** PostgreSQL with Drizzle ORM (`server/db.ts`)

## Code Style

**TypeScript:** ESLint configured (`.eslintrc.json`) — `@typescript-eslint/recommended`, import ordering, no `any`. Use **strict null checks**, async/await over promises, `const` only.

**Python:** Type hints everywhere (`Optional[Type]`, `Dict[str, Any]`), docstrings for functions, logging via `logging` module (configured in modules). Error handling with try-catch + detailed logging.

**Naming:** `camelCase` for JS, `snake_case` for Python. Error classes end in `Error` (JS) / `Exception` (Python).

**Imports:** Group by builtin, external, internal (enforced by ESLint). Relative imports in shared modules only.

**Formatting:** Prettier for TypeScript/JavaScript (via npm run lint:fix).

## Agent Guidelines

**Python Execution:** Always use existing `.venv` (find via `ls -la` or `which python3`). Never create new venvs.

**Python Package Management:** Prefer `uv` for installs when available (e.g. `uv pip install -r requirements.txt`), and run Python via `.venv/bin/python3` (never system Python).

**Code Quality:** No tech debt. Before deleting code for issue resolution, implement missing or wrong code properly instead of removing functionality.

**Issue Resolution:** Prioritize fixing/implementing over deletion. Understand root cause before modifying code.

## Multi-agent safety (non-negotiable)

- Assume multiple agents may be working simultaneously; do not delete or discard work you did not create.
- If other agents added useful work, keep it in-tree. Do not delete/remove/revert other-agent code as a “cleanup” step unless the user explicitly instructs you to; prefer integrating, documenting, or deprecating behind a flag.
- Do not remove git worktrees, branches, or files created by other agents unless the user explicitly instructs you to.
- If you discover work in another branch/worktree (especially untracked files):
  - Prefer committing it on that branch, then merging as requested.
  - If you must move it to `main`, copy it into the main worktree and commit it with a clear message.
  - If you are unsure whether it belongs, create a TODO/checklist doc under `docs/` and commit it (do not delete the work).
- Exception: never commit secrets (e.g. `.env`, tokens, credentials) even if asked to “commit everything”.

**Git Hygiene (multi-agent safety):**

- **ALWAYS use `git add -A` before committing** (standard practice to avoid leaving untracked/modified files behind). This ensures all changes—staged and unstaged—are included in the commit, preventing workflow fragmentation across agent sessions.
- Alternative: Explicitly run `git stash push -u` if you need to preserve work without committing (keeps working tree clean).
- Never run destructive git/cleanup commands (e.g. `git clean`, `git reset --hard`, deleting files/folders) unless the user explicitly asks for it.

## Audit / Remediation Workflow Prompts

When a user asks for any of these workflows (by name or generically, e.g. “run an audit”), follow the **exact prompt structure and hard rules** in `doc/AUDIT_REMEDIATION_WORKFLOWS.md`:

- **Audit v1.5.1**: one file only; discovery-first; evidence labeling; mandatory `docs/audit/` artifact.
- **Implementation v1.6.1**: findings-driven; minimal scope; tests or deterministic verification for HIGH/MED; PR + VERIFIER PACK.
- **PR Review v1.6.1** / **Verification v1.2** / **Hardening v1.1** / **Out-of-scope triage v1.0**: run as written.

Ticketing/tracking is always append-only in `docs/WORKLOG_TICKETS.md` (audit artifacts in `docs/audit/` are still required for audits).

### Trigger Phrases (Mode Switch)

Treat any of the following as an explicit request to switch into that workflow and follow it verbatim.

Versionless calls must use the canonical mapping in `doc/AUDIT_REMEDIATION_WORKFLOWS.md` and the response must state which version was applied.

- `audit` / `file audit` / `comprehensive file audit` (uses canonical Audit version)
- `remediation` / `implementation` (uses canonical Implementation version)
- `pr review` / `review pr` (uses canonical PR Review version)
- `verify` / `verification` (uses canonical Verification version)
- `hardening` (uses canonical Hardening version)
- `out-of-scope triage` / `triage` (uses canonical triage version)
- `merge conflict resolution` (uses canonical conflict prompt)
- `post-merge validation` (uses canonical post-merge prompt)

Explicit version calls must be followed exactly (e.g., `Audit v1.5.1`, `Implementation v1.6.1`).

### UI Review Triggers

For UI work (review/audit/spec), use the canonical prompts in `doc/UI_REVIEW_WORKFLOWS.md`.

Treat any of the following as an explicit request to switch modes; versionless calls must use the alias mapping in `doc/UI_REVIEW_WORKFLOWS.md` and state which version was applied:

- `ui review` / `ux review` / `ui audit`
- `repo-aware ui audit` / `repo ui auditor`
- `ui deep dive` / `ui file audit` / `audit this component`
- `ui change spec` / `spec this ui change`
