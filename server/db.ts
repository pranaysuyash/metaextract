import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';
import * as schema from '@shared/schema';
import { config as loadEnv } from 'dotenv';

// ============================================================================
// Types
// ============================================================================

interface DatabaseConfig {
  url: string;
  maxConnections?: number;
  idleTimeout?: number;
  connectionTimeout?: number;
}

interface DatabaseInstance {
  client: ReturnType<typeof drizzle>;
  pool: Pool;
  isConnected: boolean;
}

// ============================================================================
// Configuration
// ============================================================================

const DEFAULT_POOL_CONFIG = {
  max: 25, // Increased connections for better concurrency under load
  idleTimeoutMillis: 60000, // 60 seconds (increased from 30s to reduce reconnections)
  connectionTimeoutMillis: 5000, // 5 seconds
  statement_timeout: 30000, // 30 second statement timeout
  query_timeout: 30000, // 30 second query timeout
};

/**
 * Load and validate environment variables
 * @throws Error if .env file cannot be loaded
 */
function loadEnvironment(): void {
  const result = loadEnv({ path: './.env' });
  if (result.error && (result.error as any).code !== 'ENOENT') {
    throw new Error(`Failed to load environment: ${result.error.message}`);
  }
}

/**
 * Validate DATABASE_URL format
 * @throws Error if DATABASE_URL is missing or invalid
 */
function validateDatabaseUrl(): string {
  const dbUrl = process.env.DATABASE_URL;

  const requireDatabase =
    process.env.STORAGE_REQUIRE_DATABASE?.toLowerCase() === 'true' ||
    process.env.NODE_ENV === 'production';

  if (!dbUrl) {
    if (requireDatabase) {
      throw new Error(
        'DATABASE_URL environment variable is not set. STORAGE_REQUIRE_DATABASE is true; please configure it in .env file.'
      );
    }

    // DB not required, return empty string to allow in-memory fallback
    return '';
  }

  // Check for placeholder pattern
  if (dbUrl.includes('user:password@host')) {
    throw new Error(
      'DATABASE_URL contains placeholder values. Please update with actual database credentials.'
    );
  }

  // Validate PostgreSQL URL format
  if (!dbUrl.startsWith('postgresql://') && !dbUrl.startsWith('postgres://')) {
    throw new Error(
      'DATABASE_URL must be a valid PostgreSQL connection string (postgresql:// or postgres://)'
    );
  }

  return dbUrl;
}

/**
 * Initialize database connection with validation
 * @throws Error if connection fails
 */
function initializeDatabase(): DatabaseInstance | null {
  const dbUrl = validateDatabaseUrl();

  // If dbUrl is empty and DB is not required, return null to indicate no DB configured
  if (!dbUrl) {
    return null;
  }

  const pool = new Pool({
    connectionString: dbUrl,
    ...DEFAULT_POOL_CONFIG,
  });

  // Set up error listeners for the pool
  // Only log errors if explicitly debugging, as many "errors" are expected
  // (e.g., idle connection drops, transient network issues)
  if (process.env.DEBUG_DB_POOL) {
    pool.on('error', error => {
      console.debug('[DB Pool] Connection error:', error);
    });
  } else {
    // In production/test, just silently handle errors - the pool will reconnect automatically
    pool.on('error', () => {
      // Suppress logging for idle connection errors
    });
  }

  // Create Drizzle client
  const client = drizzle(pool, { schema });

  return {
    client,
    pool,
    isConnected: false,
  };
}

/**
 * Verify database connectivity by running a test query
 * @throws Error if connection test fails
 */
async function testDatabaseConnection(db: DatabaseInstance): Promise<void> {
  try {
    // Simple test query to verify connection
    await db.pool.query('SELECT 1');
    db.isConnected = true;
  } catch (error: unknown) {
    throw new Error(
      `Failed to connect to database: ${error instanceof Error ? error.message : String(error)}`
    );
  }
}

// ============================================================================
// Database Initialization
// ============================================================================

let dbInstance: DatabaseInstance | null = null;
let initError: Error | null = null;

try {
  loadEnvironment();
  dbInstance = initializeDatabase();

  if (!dbInstance) {
    console.log(
      '⚠️  Database not configured. STORAGE_REQUIRE_DATABASE is not set or DATABASE_URL missing; using in-memory storage if available.'
    );
  } else {
    // Optimistically mark connected so downstream modules (e.g., storage index) don't throw
    dbInstance.isConnected = true;

    const requireDb =
      process.env.STORAGE_REQUIRE_DATABASE?.toLowerCase() === 'true' ||
      process.env.NODE_ENV === 'production';

    // Verify connection asynchronously; if verification fails and DB is required, exit fast
    if (process.env.NODE_ENV === 'test') {
      // Skip real DB connection tests in unit tests to avoid opening real DB sockets
      dbInstance.isConnected = true;
      console.log('⚠️ Skipping database verification in test environment');
    } else {
      testDatabaseConnection(dbInstance)
        .then(() => {
          console.log('✅ Database connection verified');
        })
        .catch((error: unknown) => {
          initError = error as Error;
          console.error(
            `❌ Failed to verify database connection: ${initError.message}`
          );
          if (requireDb) {
            console.error(
              '❌ STORAGE_REQUIRE_DATABASE=true and database verification failed. Exiting.'
            );
            process.exit(1);
          } else {
            // Mark disconnected but allow the app to continue using in-memory storage
            dbInstance!.isConnected = false;
          }
        });
    }
  }

  console.log('✅ Database initialization complete');
} catch (error) {
  initError = error as Error;
  console.error(`❌ Failed to initialize database: ${initError.message}`);
}

// ============================================================================
// Exports
// ============================================================================

/**
 * Get the Drizzle ORM client
 * @throws Error if database failed to initialize
 */
export function getDatabase(): ReturnType<typeof drizzle> {
  if (!dbInstance) {
    throw new Error(
      'Database is not initialized. Check console for initialization errors.'
    );
  }
  return dbInstance.client;
}

/**
 * Check if database is connected
 */
export function isDatabaseConnected(): boolean {
  return dbInstance?.isConnected ?? false;
}

/**
 * Get the underlying PostgreSQL connection pool
 * Useful for raw queries or advanced operations
 */
export function getDatabasePool(): Pool {
  if (!dbInstance) {
    throw new Error('Database is not initialized');
  }
  return dbInstance.pool;
}

/**
 * Close database connection gracefully
 * Should be called during application shutdown
 */
export async function closeDatabase(): Promise<void> {
  if (dbInstance?.pool) {
    try {
      await dbInstance.pool.end();
      console.log('✅ Database connection closed');
    } catch (error: unknown) {
      console.error(
        `❌ Error closing database: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }
}

/**
 * For backward compatibility with code using `db` directly
 * Returns the Drizzle ORM client that can be used for queries
 */
export function getDb(): ReturnType<typeof drizzle> {
  return getDatabase();
}

/**
 * Direct export for code that imports `db` directly
 * This is the actual Drizzle client instance
 */
const _db: ReturnType<typeof drizzle> | null = null;

export const db = new Proxy({} as any, {
  get: (target, prop) => {
    if (!dbInstance) {
      throw new Error(
        'Database is not initialized. Check console for initialization errors.'
      );
    }
    return (dbInstance.client as any)[prop];
  },
});
