import { IStorage } from './types';
import { MemStorage } from './mem';
import { createObjectStorage, IObjectStorage } from './objectStorage';
import { isDatabaseConnected } from '../db';

// DatabaseStorage is disabled - use MemStorage instead
class DatabaseStorage implements IStorage {
  constructor(objectStorage: IObjectStorage) {
    throw new Error('DatabaseStorage is disabled');
  }
  async getUser(id: string) { return undefined; }
  async getUserByUsername(username: string) { return undefined; }
  async createUser(user: any) { return null as any; }
  async logExtractionUsage(data: any) {}
  async getAnalyticsSummary() { return {} as any; }
  async getRecentExtractions(limit?: number) { return []; }
  async logUiEvent(data: any) {}
  async getUiEvents(params?: any) { return []; }
  async getOrCreateCreditBalance(sessionId: string, userId?: string) { return {} as any; }
  async getCreditBalanceBySessionId(sessionId: string) { return undefined; }
  async getCreditBalance(balanceId: string) { return undefined; }
  async getCreditGrantByPaymentId(paymentId: string) { return undefined; }
  async addCredits(balanceId: string, amount: number, description: string, paymentId?: string) { return {} as any; }
  async transferCredits(fromBalanceId: string, toBalanceId: string, amount: number, description: string) {}
  async useCredits(balanceId: string, amount: number, description: string, fileType?: string) { return null; }
  async getCreditTransactions(balanceId: string, limit?: number) { return []; }
  async getOnboardingSession(userId: string) { return undefined; }
  async createOnboardingSession(data: any) { return null as any; }
  async updateOnboardingSession(sessionId: string, updates: any) {}
  async hasTrialUsage(email: string) { return false; }
  async recordTrialUsage(data: any) { return {} as any; }
  async getTrialUsageByEmail(email: string) { return undefined; }
  async saveMetadata(data: any) { return {} as any; }
  async getMetadata(id: string) { return undefined; }
  async get(key: string) { return undefined; }
  async set(key: string, value: any) {}
  async incr(key: string) { return 0; }
  async expire(key: string, seconds: number) {}
  async lpush(key: string, ...values: any[]) { return 0; }
  async ltrim(key: string, start: number, stop: number) {}
  async lrange(key: string, start: number, stop: number) { return []; }
}

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
