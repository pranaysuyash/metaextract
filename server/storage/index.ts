import { IStorage } from './types';
import { MemStorage } from './mem';
import { DatabaseStorage } from './db';
import { createObjectStorage, IObjectStorage } from './objectStorage';
import { isDatabaseConnected } from '../db';

// ============================================================================
// Storage Mode Configuration
// ============================================================================
// STORAGE_MODE: explicit choice of storage backend
//   - 'db': PostgreSQL-backed storage (required for production, credits, holds)
//   - 'memory': in-memory storage (development/test only, data not persistent)
//
// In test environment, default to memory if not explicitly set to avoid DB dependency.
// RULE: No automatic fallback. If requested mode is unavailable, server fails.
// ============================================================================

const isProduction = process.env.NODE_ENV === 'production';
const isTestEnv = process.env.NODE_ENV === 'test';

// In test mode, default to memory unless explicitly set to db
let storageMode = (
  process.env.STORAGE_MODE || (isTestEnv ? 'memory' : 'db')
).toLowerCase() as 'db' | 'memory';

// Validate storage mode
if (!['db', 'memory'].includes(storageMode)) {
  throw new Error(
    `Invalid STORAGE_MODE="${process.env.STORAGE_MODE}". Must be 'db' or 'memory'. See docs/LOCAL_DB_SETUP.md`
  );
}

// Production guard: database required
if (isProduction && storageMode !== 'db') {
  throw new Error(
    `STORAGE_MODE='${storageMode}' is not allowed in production. Must use STORAGE_MODE=db. See docs/LOCAL_DB_SETUP.md`
  );
}

// Check database readiness
const isDatabaseConfigured =
  process.env.DATABASE_URL &&
  !process.env.DATABASE_URL.includes('user:password@host');
const isDatabaseReady = Boolean(isDatabaseConfigured && isDatabaseConnected());

const objectStorage: IObjectStorage = createObjectStorage();

// If database mode is requested, enforce it is available
if (storageMode === 'db' && !isDatabaseReady) {
  throw new Error(
    `STORAGE_MODE=db but database is not available. Check DATABASE_URL and connectivity. See docs/LOCAL_DB_SETUP.md for setup steps and troubleshooting.`
  );
}

// Instantiate storage backend based on explicit mode
const storage: IStorage = (() => {
  if (storageMode === 'memory') {
    if (isProduction) {
      throw new Error(
        'STORAGE_MODE=memory is not allowed in production. Must use STORAGE_MODE=db.'
      );
    }
    console.log(
      '⚠️  STORAGE_MODE=memory: using in-memory storage (data will NOT persist, not thread-safe, not for production)'
    );
    return new MemStorage();
  }

  // storageMode === 'db'
  if (!isDatabaseReady) {
    throw new Error(
      'STORAGE_MODE=db but database is not ready. Cannot initialize DatabaseStorage.'
    );
  }
  console.log('✅ STORAGE_MODE=db: using PostgreSQL-backed storage');
  return new DatabaseStorage(objectStorage);
})();

// ============================================================================
// Health Check & Fail-Closed Enforcement
// ============================================================================

/**
 * Check if storage is healthy for money-path operations (credits, quotes, holds).
 * If STORAGE_MODE=db, requires database connectivity.
 * This is called before any credit reservation or extraction processing.
 *
 * In memory mode, always returns healthy (dev/test only).
 * In db mode, checks actual database connectivity.
 *
 * @throws Error if in production/money-path and storage is unhealthy
 */
export function assertStorageHealthy(): void {
  const isMoney = true; // Always treat storage queries as critical

  // Memory mode is always acceptable (dev/test only); no health check needed
  if (storageMode === 'memory') {
    return;
  }

  // DB mode: check connectivity
  if (storageMode === 'db') {
    const isDatabaseHealthy = isDatabaseConnected();
    if (!isDatabaseHealthy) {
      const msg =
        'Database connectivity lost. Cannot process paid/trial extraction. Service unavailable.';
      console.error(`❌ Storage health check failed: ${msg}`);
      if (isProduction || isMoney) {
        throw new Error(msg);
      }
    }
  }
}

/**
 * Get current storage mode (for logging/debugging).
 */
export function getStorageMode(): string {
  return storageMode;
}

/**
 * Is storage configured to use database (safer, persistent)?
 */
export function isStorageDatabase(): boolean {
  return storageMode === 'db';
}

export { storage };

export * from './types';
export { MemStorage } from './mem';
export { DatabaseStorage } from './db';
export { objectStorage };
