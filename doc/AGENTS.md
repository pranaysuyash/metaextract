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

**Code Quality:** No tech debt. Before deleting code for issue resolution, implement missing or wrong code properly instead of removing functionality.

**Issue Resolution:** Prioritize fixing/implementing over deletion. Understand root cause before modifying code.
