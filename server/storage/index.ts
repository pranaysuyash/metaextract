import { IStorage } from './types';
import { MemStorage } from './mem';
import { DatabaseStorage } from './db';

// Use MemStorage for development when DATABASE_URL is placeholder or missing
const isDatabaseConfigured =
  process.env.DATABASE_URL &&
  !process.env.DATABASE_URL.includes('user:password@host');

export const storage: IStorage = isDatabaseConfigured
  ? new DatabaseStorage()
  : new MemStorage();

if (!isDatabaseConfigured) {
  console.log(
    '⚠️  DATABASE_URL not configured - using in-memory storage (data will not persist)'
  );
}

export * from './types';
export { MemStorage } from './mem';
export { DatabaseStorage } from './db';
