import { IStorage } from './types';

/**
 * In-memory storage implementation for development and testing.
 * DO NOT use in production.
 */
export class MemStorage implements IStorage {
  private store = new Map<string, any>();
  
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
  
  async get(key: string) { return this.store.get(key); }
  async set(key: string, value: any) { this.store.set(key, value); }
  async incr(key: string) { return 0; }
  async expire(key: string, seconds: number) {}
  async lpush(key: string, ...values: any[]) { return 0; }
  async ltrim(key: string, start: number, stop: number) {}
  async lrange(key: string, start: number, stop: number) { return []; }
}
