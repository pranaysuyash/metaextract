# Storage Mode Implementation: Explicit Configuration & Fail-Closed Design

## Problem Statement

Previously, the system had an implicit **fallback from database to in-memory storage** when the database was unavailable. This created a **fail-open security vulnerability**:

- Outages could silently downgrade to insecure mode
- Credits might not be charged correctly (in-memory stubs)
- Quotas could be bypassed (multi-instance losses)
- Billing inconsistencies across deployments

## Solution: Explicit Storage Mode

Replaced the implicit fallback with an explicit `STORAGE_MODE` environment variable that forces a deliberate choice.

## Configuration

### Environment Variable

```bash
STORAGE_MODE=db       # Production (default): PostgreSQL-backed, persistent, safe for money
STORAGE_MODE=memory   # Dev/Test only: In-memory, not persistent, not thread-safe
```

### Defaults & Guards

**Test Environment** (`NODE_ENV=test`):

- Default: `STORAGE_MODE=memory` (auto-enables in-memory for unit tests without DB dependency)
- Override: Set `STORAGE_MODE=db` to test with real database

**Production** (`NODE_ENV=production`):

- Enforced: `STORAGE_MODE=db` **only**
- If `STORAGE_MODE!=db` on boot: **server crashes immediately** (fail-fast)
- If `STORAGE_MODE=db` but DB unavailable: **server crashes immediately** (no fallback)

**Development** (`NODE_ENV=development`):

- Default: `STORAGE_MODE=db` (use Postgres locally)
- Optional: `STORAGE_MODE=memory` if explicitly configured (for quick unit tests)

## Implementation Details

### 1. Storage Initialization

**Location**: `server/storage/index.ts`

```typescript
// Auto-default memory mode in test environment
const storageMode = (
  process.env.STORAGE_MODE || (isTestEnv ? 'memory' : 'db')
).toLowerCase();

// Production guard
if (isProduction && storageMode !== 'db') {
  throw new Error('STORAGE_MODE=db required in production');
}

// Enforce requested mode (no fallback)
if (storageMode === 'db' && !isDatabaseReady) {
  throw new Error('STORAGE_MODE=db but database unavailable');
}

// Instantiate chosen backend
const storage = storageMode === 'db' ? new DatabaseStorage() : new MemStorage();
```

### 2. Runtime Health Check (Fail-Closed)

**Location**: `server/storage/index.ts` + `server/routes/images-mvp.ts`

**Function**: `assertStorageHealthy()`

- Called **before any credit reservation** (money-path operations)
- In `db` mode: checks `isDatabaseConnected()` dynamically
- In `memory` mode: always passes (dev/test only, no check needed)
- **Throws error** if DB required but unhealthy

**Usage in Route**:

```typescript
// Before credit reservation
try {
  assertStorageHealthy();  // Fail-closed: 503 if DB unhealthy
} catch (error) {
  return sendServiceUnavailableError(res, 'Database unavailable...');
}

// Safe to proceed with credit operations
await storage.reserveCredits(...);
```

### 3. Exports

**Location**: `server/storage/index.ts`

```typescript
export { storage }; // Active storage instance
export function assertStorageHealthy(): void; // Health check
export function getStorageMode(): string; // For logging/debugging
export function isStorageDatabase(): boolean; // Is it DB-backed?
```

## Test Integration

**File**: `server/routes/images-mvp.test.ts`

Updated mock to include `assertStorageHealthy`:

```typescript
jest.mock('../storage/index', () => ({
  storage: {
    /* ... */
  },
  assertStorageHealthy: jest.fn(), // No-op in tests
}));
```

**Result**: All 18 tests pass with mocked health checks.

## Migration from Old System

### Old (Implicit Fallback)

```env
STORAGE_REQUIRE_DATABASE=true  # Fallback if false
DATABASE_URL=...
# If DB down → automatically use in-memory (unsafe!)
```

### New (Explicit Mode)

```env
STORAGE_MODE=db  # Explicit choice
DATABASE_URL=...
# If DB down → server crashes on boot (safe!)
```

### Backward Compatibility

- Old `STORAGE_REQUIRE_DATABASE` env var is **ignored** (use `STORAGE_MODE` instead)
- `.env` files updated from `STORAGE_REQUIRE_DATABASE=true` to `STORAGE_MODE=db`
- All routes automatically use new health check before money operations

## Guarantees & Invariants

### ✅ No Silent Downgrades

- Outages appear as **503 Service Unavailable**, not "free usage"
- Client knows extraction failed, doesn't assume credits were charged

### ✅ Production Safety

- `NODE_ENV=production` + `STORAGE_MODE!=db` → crash on boot (non-negotiable)
- DB connectivity checked at startup and before each money operation

### ✅ Development Flexibility

- Unit tests auto-use in-memory mode (fast, no DB needed)
- Integration tests can opt-in to `STORAGE_MODE=db` with real DB

### ✅ Fail-Closed Money Path

- Credit operations are gated by `assertStorageHealthy()`
- If DB fails at runtime, extraction returns **503** (not charged, not queued)

### ✅ Idempotent Retries Still Work

- In-memory mode: uses stubs (basic, not atomic)
- DB mode: atomic holds with `requestId` UNIQUE constraint (truly idempotent)

## Files Modified

1. **server/storage/index.ts**
   - Added `STORAGE_MODE` config parsing
   - Production/test guards
   - `assertStorageHealthy()` function
   - Helper exports: `getStorageMode()`, `isStorageDatabase()`

2. **server/routes/images-mvp.ts**
   - Import `assertStorageHealthy` from storage module
   - Call health check before credit reservation (fail-closed)

3. **docs/LOCAL_DB_SETUP.md**
   - Updated with `STORAGE_MODE` explanation
   - Removed references to fallback behavior
   - Clarified when `STORAGE_MODE=memory` is allowed

4. **server/routes/images-mvp.test.ts**
   - Mock `assertStorageHealthy` in test jest.mock()

5. **.env**
   - Changed `STORAGE_REQUIRE_DATABASE=true` → `STORAGE_MODE=db`

## Testing

**Command**:

```bash
npm test -- server/routes/images-mvp.test.ts
```

**Result**: ✅ 18/18 tests passing

- Tests auto-use `STORAGE_MODE=memory` (no DB dependency)
- Health check is mocked (no-op) during tests
- All credit reservation logic tested via mocked storage

## Production Deployment Checklist

- [ ] Update environment: `STORAGE_MODE=db` in prod config
- [ ] Verify `DATABASE_URL` is set and reachable
- [ ] Remove old `STORAGE_REQUIRE_DATABASE` if still present
- [ ] Test startup: server should boot immediately with DB, crash quickly if DB unavailable
- [ ] Monitor: watch for 503 responses on extraction (indicates DB unhealthy at runtime)
- [ ] Alert: set up monitoring if extraction endpoints return 503 (money-path failure)

## Future Enhancements

1. **Partial Degradation** (optional):
   - Device-free extractions could fall back to memory if quota tracking is token-based
   - But keep fail-closed for trial/paid modes (require DB)

2. **Metrics**:
   - Track how often `assertStorageHealthy()` catches DB failures
   - Alert if failures exceed threshold

3. **Graceful Degradation** (advanced):
   - Queue failed extractions when DB is down (requires message queue)
   - Retry when DB comes back
   - Track refunds/credits owed

---

**Status**: Production-ready  
**Test Result**: ✅ All passing  
**Security**: Fail-closed, no silent downgrades  
**Deployment**: Requires `STORAGE_MODE=db` in production
