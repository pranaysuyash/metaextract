# MetaExtract AI Coding Assistant Instructions

## Architecture Overview

MetaExtract is a **hybrid Node.js/Python monorepo** for comprehensive metadata extraction across 45,000+ fields from any file type.

### Core Components
- **Frontend** (`client/`): React 19 + TypeScript + Vite, TanStack Query, Radix UI
- **Backend** (`server/`): Express + TypeScript, PostgreSQL + Drizzle ORM
- **Extraction Engine** (`server/extractor/`): Python 3 with 240+ specialized modules
- **Shared** (`shared/`): TypeScript schemas and utilities

### Key Architectural Decisions
- **Credit-based access control** (not subscription tiers) with three modes:
  - `device_free`: First 2 extractions per device (high-value data, GPS redacted)
  - `trial_limited`: Email trials (<2 uses, "free" engine tier)
  - `paid`: Full access, 1 credit per extraction
- **Python bridge**: Node.js calls Python via subprocess for metadata extraction
- **WebSocket progress**: Real-time extraction updates
- **File validation**: MIME type + extension checks before disk writes

## Development Workflows

### Setup
```bash
npm install
# Use existing .venv - never create new venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt  # Use uv for package management
```

### Development Server
```bash
npm run dev  # Concurrent client (5173) + server
```

### Process management (dev servers only)
- Do NOT kill the global Node process or unrelated node jobs. Avoid commands like `killall node`.
- When you need a clean restart, stop only the running dev servers:
  - Prefer stopping the VS Code task/terminal that runs `npm run dev`.
  - If a port is stuck, kill by port (macOS example): `lsof -ti:5173 -sTCP:LISTEN | xargs kill -9` and/or `lsof -ti:3000 -sTCP:LISTEN | xargs kill -9`.
- Rationale: other Node processes (tools, scripts, debuggers) may be active; only terminate the Vite (5173) and Express (3000) dev servers when restarting.

### Build & Test
```bash
npm run build           # Production build
npm run test:ci         # TypeScript tests
pytest tests/           # Python tests
npm run lint            # ESLint + Prettier
```

### Database
```bash
npm run db:push         # Push schema changes
npm run db:studio       # Drizzle Studio
```

## Code Conventions

### Naming
- **Python**: `snake_case`, modules as `{domain}_{functionality}.py`
- **TypeScript/JavaScript**: `camelCase`, PascalCase for components/types
- **Files**: No Roman numerals, no superlatives ("ultimate", "complete", "mega")
- **Examples**: `cardiac_imaging.py`, `neuroimaging.py`, `forensic_security_advanced.py`

### Error Handling
- **Python**: Try-catch with detailed logging via `logging` module
- **TypeScript**: Async/await preferred, strict null checks
- **API**: Structured error responses with `send*Error` helpers

### Imports
- **Python**: Type hints everywhere (`Optional[Type]`, `Dict[str, Any]`)
- **TypeScript**: Grouped (builtin → external → internal), relative imports only in shared modules

### Security
- **File uploads**: Validate MIME type + extension BEFORE disk writes
- **Rate limiting**: Multi-layer (50/15min + 10/1min)
- **Access control**: Check credits, not user tiers
- **Temp files**: Automated cleanup on startup + hourly

## Key Files & Patterns

### Core Extraction Flow
- `server/routes/images-mvp.ts`: Main extraction endpoint with access control
- `server/extractor/comprehensive_metadata_engine.py`: Python extraction orchestrator
- `server/extractor/module_discovery.py`: Dynamic module loading system
- `server/utils/extraction-helpers.ts`: Python bridge and metadata transformation

### Access Control
- `server/routes/images-mvp.ts:1640-1750`: Access mode determination logic
- `server/utils/extraction-helpers.ts:558-694`: Redaction for device-free mode
- `shared/imagesMvpPricing.ts`: Credit calculation logic

### Database Schema
- `shared/schema.ts`: Drizzle ORM tables (users, extractions, analytics)
- `server/db.ts`: Database connection and utilities

### Testing
- `tests/e2e/images-mvp.smoke.spec.ts`: E2E smoke tests
- `server/routes/images-mvp.test.ts`: Route unit tests
- `pytest.ini`: Python test configuration

## Common Patterns

### Python Module Structure
```python
# server/extractor/modules/{domain}_{functionality}.py
def extract_{domain}_{functionality}(file_path: str, config: dict) -> dict:
    """Extract {domain} {functionality} metadata."""
    # Implementation with logging
    logger = logging.getLogger(__name__)
    try:
        # Extraction logic
        return {"field": "value"}
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return {}
```

### TypeScript API Route
```typescript
// server/routes/example.ts
import type { Express } from 'express';

export default function setupRoutes(app: Express) {
  app.post('/api/example', async (req, res) => {
    try {
      const result = await processRequest(req.body);
      res.json(result);
    } catch (error) {
      sendInternalServerError(res, 'Processing failed');
    }
  });
}
```

### Access Mode Checks
```typescript
// Always check credits, never user.tier
const accessMode = determineAccessMode(req, userCredits);
if (accessMode === 'paid' && credits < requiredCredits) {
  return sendQuotaExceededError(res);
}
```

## Integration Points

- **Python Bridge**: `extractMetadataWithPython()` calls Python subprocess
- **WebSocket**: Progress updates via `activeConnections` map
- **Payments**: Dodo Payments integration for credit purchases
- **File Storage**: Abstracted via `server/storage/` with multiple backends
- **Caching**: Redis for rate limiting and session management

## External Dependencies

- **ExifTool**: Core EXIF/IPTC/XMP extraction
- **FFmpeg/ffprobe**: Video/audio processing
- **OpenCV/Pillow**: Image analysis
- **Py3Exiv2**: Extended EXIF support
- **Mutagen**: Audio metadata
- **PyPDF**: PDF processing

## Work Management and Documentation

### Canonical workflow prompts

The repo’s evidence-tight workflows are stored in `doc/AUDIT_REMEDIATION_WORKFLOWS.md`.

- If the user invokes a workflow **without a version** (e.g. “run an audit”), use the **versionless alias mapping** in `doc/AUDIT_REMEDIATION_WORKFLOWS.md` and state which version you are applying.
- If the user invokes a workflow **with an explicit version**, follow that version exactly.
- Always honor required artifacts (e.g. `docs/audit/...` during audits).

### Canonical UI review prompts

UI review/audit/spec workflows are stored in `doc/UI_REVIEW_WORKFLOWS.md`.

- If the user invokes UI review **without a version** (e.g. “do a UI audit”), use the **versionless alias mapping** in `doc/UI_REVIEW_WORKFLOWS.md` and state which version you are applying.
- If the user invokes UI review **with an explicit version**, follow that version exactly.

### Ticketing / tracking (summary)

Canonical rules and templates live in `doc/AUDIT_REMEDIATION_WORKFLOWS.md`. Summary:
- Single source of truth: `docs/WORKLOG_TICKETS.md`
- Append-only: never rewrite old entries
- Every workflow run starts with: `Ticket action: ...` and ends with: `Ticket file touched: docs/WORKLOG_TICKETS.md`

## Gotchas

- **Python environment**: Always use existing `.venv` (find via `ls -la` or `which python3`), activate with `source .venv/bin/activate` (never create new venvs)
- **Python executable**: Always use `.venv/bin/python3`, never system Python
- **Python packages**: Prefer `uv` for installs when available (e.g. `uv pip install -r requirements.txt`)
- **Git hygiene**: Always run `git add -A` before commits to avoid leaving untracked/unstaged files
- **Access modes**: Device-free shows high-value data but redacts GPS/sensitive fields
- **Engine tiers**: "free" vs "super" (internal parameter), separate from user access modes
- **File validation**: Reject executables, scripts, documents at upload time
- **Temp cleanup**: Automatic, but manual endpoint available at `/api/health/cleanup`
