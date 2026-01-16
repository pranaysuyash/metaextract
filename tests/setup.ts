import '@testing-library/jest-dom';
import { TextEncoder, TextDecoder } from 'util';

// Polyfill for Node.js globals in server tests
(global as any).TextEncoder = TextEncoder;
(global as any).TextDecoder = TextDecoder;

// Mock environment variables
process.env.NODE_ENV = 'test';
process.env.DATABASE_URL =
  'postgresql://test:test@localhost:5432/metaextract_test';
process.env.SESSION_SECRET = 'test-session-secret-for-testing';
process.env.TOKEN_SECRET = 'test-token-secret-for-testing';
process.env.JWT_SECRET = 'test-jwt-secret-for-testing';

// Mock fetch globally
global.fetch = jest.fn();

// Mock crypto.randomUUID for Node.js environment
global.crypto = {
  randomUUID: () => 'test-uuid-' + Math.random().toString(36).substr(2, 9),
} as any;

// Mock document.cookie for auth system (jsdom only)
if (typeof document !== 'undefined') {
  Object.defineProperty(document, 'cookie', {
    writable: true,
    value: '',
  });
}

// Mock toast hook
jest.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: jest.fn(),
    dismiss: jest.fn(),
  }),
}));

// Mock field explanations utility
jest.mock('@/utils/fieldExplanations', () => ({
  getFieldExplanation: jest.fn(() => null),
  hasExplanation: jest.fn(() => false),
  FIELD_EXPLANATIONS: {},
  CATEGORY_EXPLANATIONS: {},
}));

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Polyfill setImmediate for environments that don't provide it (jsdom)
if (typeof (global as any).setImmediate === 'undefined') {
  (global as any).setImmediate = (fn: Function, ...args: any[]) =>
    setTimeout(() => fn(...args), 0);
}

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock window.matchMedia (jsdom only)
if (typeof window !== 'undefined') {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    })),
  });
}

// Reset mocks before each test
beforeEach(() => {
  jest.clearAllMocks();
  (global.fetch as jest.Mock).mockClear();
});

// ============================================================================
// Test-time database readiness: attempt to use local Postgres when available.
// If DATABASE_URL is set and reachable, ensure schema exists by applying
// `init.sql` when necessary. If DB is unreachable, we set a global flag and
// tests that require DB will skip. If DB exists but schema init fails, tests
// will fail with an actionable error so developers can fix their local setup.
// ============================================================================
import fs from 'fs/promises';
import { Client } from 'pg';

beforeAll(async () => {
  const dbUrl = process.env.DATABASE_URL;
  // Default: no DB
  (global as any).__TEST_DB_READY = false;
  (global as any).__TEST_DB_INIT_ERROR = null;

  if (!dbUrl) {
    console.log('No DATABASE_URL set; DB-dependent tests will be skipped');
    return;
  }

  const client = new Client({ connectionString: dbUrl });
  try {
    await client.connect();

    // Quick connectivity probe
    await client.query('SELECT 1');

    // Check for critical table used by tests
    const res = await client.query(
      "SELECT to_regclass('public.credit_grants') AS reg"
    );
    const reg = res.rows[0]?.reg;

    // Also ensure newer tables exist even if the DB was initialized previously.
    // This prevents noisy errors when modules run background cleanup tasks.
    const ensureUserSessionsTable = async (): Promise<void> => {
      const t = await client.query(
        "SELECT to_regclass('public.user_sessions') AS reg"
      );
      if (t.rows[0]?.reg) return;

      await client.query('SET search_path TO public');
      await client.query(`
        CREATE TABLE IF NOT EXISTS public.user_sessions (
          id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
          user_id VARCHAR NOT NULL REFERENCES public.users(id),
          session_id TEXT NOT NULL UNIQUE,
          token_hash TEXT NOT NULL,
          expires_at TIMESTAMP NOT NULL,
          user_agent TEXT,
          ip_address TEXT,
          revoked_at TIMESTAMP,
          created_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
      `);
      await client.query(
        'CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON public.user_sessions(user_id);'
      );
      await client.query(
        'CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON public.user_sessions(expires_at);'
      );
    };

    if (!reg) {
      // Try to load and run init.sql from repo root, executing statements
      // one-by-one so we can report which statement (if any) fails.
      try {
        const sql = await fs.readFile('./init.sql', 'utf8');
        console.log(
          'Applying init.sql to initialize test schema (statement-by-statement)...'
        );

        // Ensure public schema is the target
        await client.query('SET search_path TO public');

        const { splitStatements } = require('../scripts/sql-splitter.cjs');

        const statements = splitStatements(sql);

        for (let idx = 0; idx < statements.length; idx++) {
          const stmt = statements[idx].trim();
          if (!stmt) continue;
          try {
            await client.query(stmt);
          } catch (stmtErr) {
            console.error(
              `Failed to execute init.sql statement #${idx + 1}:`,
              stmt.slice(0, 400).replace(/\s+/g, ' '),
              stmtErr
            );
            throw stmtErr;
          }

          // Quick verification after DDL that could create the critical table
          if (
            stmt.toLowerCase().includes('create table') ||
            stmt.toLowerCase().includes('create index')
          ) {
            const r = await client.query(
              "SELECT to_regclass('public.credit_grants') AS reg"
            );
            if (r.rows[0]?.reg) break; // early exit if critical table is present
          }
        }

        // Verify table exists after init
        const verify = await client.query(
          "SELECT to_regclass('public.credit_grants') AS reg"
        );
        if (!verify.rows[0]?.reg) {
          throw new Error(
            'Schema init did not create expected tables (credit_grants missing)'
          );
        }
      } catch (initErr) {
        const msg =
          initErr instanceof Error ? initErr.message : String(initErr);
        (global as any).__TEST_DB_INIT_ERROR = msg;
        console.error(
          'Failed to initialize test database schema:',
          (global as any).__TEST_DB_INIT_ERROR
        );
        await client.end();
        return;
      }
    }

    await ensureUserSessionsTable();

    // If we reach here, DB is ready
    (global as any).__TEST_DB_READY = true;
    console.log('Test database is available and schema is ready');
    await client.end();
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    (global as any).__TEST_DB_INIT_ERROR = msg;
    console.warn('Postgres not reachable for tests:', msg);
    try {
      await client.end();
    } catch (e) {
      // ignore
    }
  }
});

// Custom matchers
expect.extend({
  toBeWithinRange(received: number, floor: number, ceiling: number) {
    const pass = received >= floor && received <= ceiling;
    if (pass) {
      return {
        message: () =>
          `expected ${received} not to be within range ${floor} - ${ceiling}`,
        pass: true,
      };
    } else {
      return {
        message: () =>
          `expected ${received} to be within range ${floor} - ${ceiling}`,
        pass: false,
      };
    }
  },
});

// Suppress console errors during tests (optional)
const originalError = console.error;
beforeAll(() => {
  console.error = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render is no longer supported')
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(async () => {
  console.error = originalError;
  // Cleanup database handles to allow Jest to exit
  try {
    const { closeDatabase } = require('../server/db');
    await closeDatabase();
  } catch (e) {
    // Ignore if not a server test or if db module not found
  }

  // Shutdown Redis-backed services (rate limiter) to avoid open TCP handles
  try {
    const { rateLimitManager } = require('../server/rateLimitRedis');
    if (rateLimitManager && typeof rateLimitManager.shutdown === 'function') {
      await rateLimitManager.shutdown();
    }
  } catch (e) {
    // Ignore if not initialized in this test run
  }
});
