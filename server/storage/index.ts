import { IStorage } from './types';
import { MemStorage } from './mem';
import { DatabaseStorage } from './db';
import { createObjectStorage, IObjectStorage } from './objectStorage';
import { isDatabaseConnected } from '../db';

// Use MemStorage for development when DATABASE_URL is placeholder or missing
const isDatabaseConfigured =
  process.env.DATABASE_URL &&
  !process.env.DATABASE_URL.includes('user:password@host');
const requireDatabase =
  process.env.STORAGE_REQUIRE_DATABASE?.toLowerCase() === 'true' ||
  process.env.NODE_ENV === 'production';
const isDatabaseReady = Boolean(isDatabaseConfigured && isDatabaseConnected());

const objectStorage: IObjectStorage = createObjectStorage();

if (requireDatabase && !isDatabaseReady) {
  throw new Error(
    'Database is required but not available. Check DATABASE_URL and connectivity. See docs/LOCAL_DB_SETUP.md for setup steps and troubleshooting.'
  );
}

export const storage: IStorage = isDatabaseReady
  ? new DatabaseStorage(objectStorage)
  : new MemStorage();

if (!isDatabaseReady) {
  console.log(
    '⚠️  Database not available - using in-memory storage (data will not persist)'
  );
}

export * from './types';
export { MemStorage } from './mem';
export { DatabaseStorage } from './db';
export { objectStorage };
