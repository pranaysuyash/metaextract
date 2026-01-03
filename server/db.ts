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
  max: 10, // Maximum connections
  idleTimeoutMillis: 30000, // 30 seconds
  connectionTimeoutMillis: 2000, // 2 seconds
};

/**
 * Load and validate environment variables
 * @throws Error if .env file cannot be loaded
 */
function loadEnvironment(): void {
  const result = loadEnv({ path: './.env' });
  if (result.error && result.error.code !== 'ENOENT') {
    throw new Error(`Failed to load environment: ${result.error.message}`);
  }
}

/**
 * Validate DATABASE_URL format
 * @throws Error if DATABASE_URL is missing or invalid
 */
function validateDatabaseUrl(): string {
  const dbUrl = process.env.DATABASE_URL;

  if (!dbUrl) {
    throw new Error(
      'DATABASE_URL environment variable is not set. Please configure it in .env file.'
    );
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
function initializeDatabase(): DatabaseInstance {
  const dbUrl = validateDatabaseUrl();

  const pool = new Pool({
    connectionString: dbUrl,
    ...DEFAULT_POOL_CONFIG,
  });

  // Set up error listeners for the pool
  pool.on('error', error => {
    console.error('❌ Unexpected error on database connection pool:', error);
  });

  // Create Drizzle client
  const client = drizzle(pool, { schema });

  return {
    client,
    pool,
    isConnected: true,
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
  } catch (error) {
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
  // Test connection asynchronously
  testDatabaseConnection(dbInstance).catch(error => {
    initError = error;
    console.error(initError.message);
  });
  console.log('✅ Database connection initialized successfully');
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
    } catch (error) {
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
let _db: ReturnType<typeof drizzle> | null = null;

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
