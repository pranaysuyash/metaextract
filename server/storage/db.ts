import {
  type User,
  type InsertUser,
  type InsertExtractionAnalytics,
  type ExtractionAnalytics,
  extractionAnalytics,
  creditBalances,
  creditTransactions,
  type CreditBalance,
  type CreditTransaction,
  onboardingSessions,
  type OnboardingSession,
  type InsertOnboardingSession,
  trialUsages,
  type TrialUsage,
  type InsertTrialUsage,
} from '@shared/schema';
import { desc, sql, eq } from 'drizzle-orm';
import { IStorage, AnalyticsSummary } from './types';

export class DatabaseStorage implements IStorage {
  private db: any;

  constructor() {
    // Lazy load database connection
    try {
      const { db } = require('../db');
      this.db = db;
    } catch (error) {
      console.error('Failed to connect to database:', error);
      this.db = null;
    }
  }

  async getUser(_id: string): Promise<User | undefined> {
    return undefined;
  }

  async getUserByUsername(_username: string): Promise<User | undefined> {
    return undefined;
  }

  async createUser(_insertUser: InsertUser): Promise<User> {
    throw new Error('Not implemented');
  }

  async logExtractionUsage(data: InsertExtractionAnalytics): Promise<void> {
    if (!this.db) return;
    try {
      await this.db.insert(extractionAnalytics).values(data);
    } catch (error) {
      console.error('Failed to log extraction usage:', error);
    }
  }

  async getAnalyticsSummary(): Promise<AnalyticsSummary> {
    if (!this.db) {
      return {
        totalExtractions: 0,
        byTier: {},
        byFileType: {},
        byMediaType: { images: 0, videos: 0, pdfs: 0, audio: 0, other: 0 },
        last24Hours: 0,
        last7Days: 0,
        averageProcessingMs: 0,
        totalBytesProcessed: 0,
        successRate: 100,
      };
    }

    try {
      const now = new Date();
      const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

      const allEntries = await this.db.select().from(extractionAnalytics);

      const byTier: Record<string, number> = {};
      const byFileType: Record<string, number> = {};
      let images = 0,
        videos = 0,
        pdfs = 0,
        audio = 0,
        other = 0;
      let last24Hours = 0,
        last7Days = 0;
      let totalProcessingMs = 0;
      let totalBytes = 0;
      let successCount = 0;

      for (const entry of allEntries) {
        byTier[entry.tier] = (byTier[entry.tier] || 0) + 1;
        byFileType[entry.fileExtension] =
          (byFileType[entry.fileExtension] || 0) + 1;

        if (entry.isImage) images++;
        else if (entry.isVideo) videos++;
        else if (entry.isPdf) pdfs++;
        else if (entry.isAudio) audio++;
        else other++;

        if (entry.requestedAt >= oneDayAgo) last24Hours++;
        if (entry.requestedAt >= sevenDaysAgo) last7Days++;

        totalProcessingMs += entry.processingMs;
        totalBytes += entry.fileSizeBytes;
        if (entry.success) successCount++;
      }

      return {
        totalExtractions: allEntries.length,
        byTier,
        byFileType,
        byMediaType: { images, videos, pdfs, audio, other },
        last24Hours,
        last7Days,
        averageProcessingMs:
          allEntries.length > 0
            ? Math.round(totalProcessingMs / allEntries.length)
            : 0,
        totalBytesProcessed: totalBytes,
        successRate:
          allEntries.length > 0
            ? Math.round((successCount / allEntries.length) * 100)
            : 100,
      };
    } catch (error) {
      console.error('Failed to get analytics summary:', error);
      return {
        totalExtractions: 0,
        byTier: {},
        byFileType: {},
        byMediaType: { images: 0, videos: 0, pdfs: 0, audio: 0, other: 0 },
        last24Hours: 0,
        last7Days: 0,
        averageProcessingMs: 0,
        totalBytesProcessed: 0,
        successRate: 100,
      };
    }
  }

  async getRecentExtractions(
    limit: number = 50
  ): Promise<ExtractionAnalytics[]> {
    if (!this.db) return [];
    try {
      return await this.db
        .select()
        .from(extractionAnalytics)
        .orderBy(desc(extractionAnalytics.requestedAt))
        .limit(limit);
    } catch (error) {
      console.error('Failed to get recent extractions:', error);
      return [];
    }
  }

  async getOrCreateCreditBalance(
    sessionId: string,
    userId?: string
  ): Promise<CreditBalance> {
    if (!this.db) throw new Error('Database not available');
    try {
      const existing = await this.db
        .select()
        .from(creditBalances)
        .where(eq(creditBalances.sessionId, sessionId))
        .limit(1);

      if (existing.length > 0) return existing[0];

      const [newBalance] = await this.db
        .insert(creditBalances)
        .values({ sessionId, userId, credits: 0 })
        .returning();
      return newBalance;
    } catch (error) {
      console.error('Failed to get/create credit balance:', error);
      throw error;
    }
  }

  async getCreditBalance(
    balanceId: string
  ): Promise<CreditBalance | undefined> {
    if (!this.db) return undefined;
    try {
      const [balance] = await this.db
        .select()
        .from(creditBalances)
        .where(eq(creditBalances.id, balanceId))
        .limit(1);
      return balance;
    } catch (error) {
      console.error('Failed to get credit balance:', error);
      return undefined;
    }
  }

  async addCredits(
    balanceId: string,
    amount: number,
    description: string,
    paymentId?: string
  ): Promise<CreditTransaction> {
    if (!this.db) throw new Error('Database not available');
    try {
      await this.db
        .update(creditBalances)
        .set({
          credits: sql`${creditBalances.credits} + ${amount}`,
          updatedAt: new Date(),
        })
        .where(eq(creditBalances.id, balanceId));

      const [tx] = await this.db
        .insert(creditTransactions)
        .values({
          balanceId,
          type: 'purchase',
          amount,
          description,
          dodoPaymentId: paymentId,
        })
        .returning();
      return tx;
    } catch (error) {
      console.error('Failed to add credits:', error);
      throw error;
    }
  }

  async useCredits(
    balanceId: string,
    amount: number,
    description: string,
    fileType?: string
  ): Promise<CreditTransaction | null> {
    if (!this.db) return null;
    try {
      const [balance] = await this.db
        .select()
        .from(creditBalances)
        .where(eq(creditBalances.id, balanceId))
        .limit(1);

      if (!balance || balance.credits < amount) return null;

      await this.db
        .update(creditBalances)
        .set({
          credits: sql`${creditBalances.credits} - ${amount}`,
          updatedAt: new Date(),
        })
        .where(eq(creditBalances.id, balanceId));

      const [tx] = await this.db
        .insert(creditTransactions)
        .values({
          balanceId,
          type: 'usage',
          amount: -amount,
          description,
          fileType,
        })
        .returning();
      return tx;
    } catch (error) {
      console.error('Failed to use credits:', error);
      return null;
    }
  }

  async getCreditTransactions(
    balanceId: string,
    limit: number = 50
  ): Promise<CreditTransaction[]> {
    if (!this.db) return [];
    try {
      return await this.db
        .select()
        .from(creditTransactions)
        .where(eq(creditTransactions.balanceId, balanceId))
        .orderBy(desc(creditTransactions.createdAt))
        .limit(limit);
    } catch (error) {
      console.error('Failed to get credit transactions:', error);
      return [];
    }
  }

  async getOnboardingSession(
    userId: string
  ): Promise<OnboardingSession | undefined> {
    if (!this.db) return undefined;
    try {
      const [session] = await this.db
        .select()
        .from(onboardingSessions)
        .where(eq(onboardingSessions.userId, userId))
        .orderBy(desc(onboardingSessions.startedAt))
        .limit(1);
      return session;
    } catch (error) {
      console.error('Failed to get onboarding session:', error);
      return undefined;
    }
  }

  async createOnboardingSession(
    data: InsertOnboardingSession
  ): Promise<OnboardingSession> {
    if (!this.db) throw new Error('Database not available');
    try {
      const [session] = await this.db
        .insert(onboardingSessions)
        .values(data)
        .returning();
      return session;
    } catch (error) {
      console.error('Failed to create onboarding session:', error);
      throw error;
    }
  }

  async updateOnboardingSession(
    sessionId: string,
    updates: Partial<OnboardingSession>
  ): Promise<void> {
    if (!this.db) return;
    try {
      await this.db
        .update(onboardingSessions)
        .set({ ...updates, updatedAt: new Date() })
        .where(eq(onboardingSessions.id, sessionId));
    } catch (error) {
      console.error('Failed to update onboarding session:', error);
    }
  }

  // Trial system methods
  async hasTrialUsage(email: string): Promise<boolean> {
    if (!this.db) return false;
    try {
      const result = await this.db
        .select({ id: trialUsages.id })
        .from(trialUsages)
        .where(eq(trialUsages.email, email.toLowerCase()))
        .limit(1);
      return result.length > 0;
    } catch (error) {
      console.error('Failed to check trial usage:', error);
      return false;
    }
  }

  async recordTrialUsage(data: InsertTrialUsage): Promise<TrialUsage> {
    if (!this.db) throw new Error('Database not available');
    try {
      const [trialUsage] = await this.db
        .insert(trialUsages)
        .values({
          ...data,
          email: data.email.toLowerCase(),
        })
        .returning();
      return trialUsage;
    } catch (error) {
      console.error('Failed to record trial usage:', error);
      throw error;
    }
  }

  async getTrialUsageByEmail(email: string): Promise<TrialUsage | undefined> {
    if (!this.db) return undefined;
    try {
      const [trialUsage] = await this.db
        .select()
        .from(trialUsages)
        .where(eq(trialUsages.email, email.toLowerCase()))
        .limit(1);
      return trialUsage;
    } catch (error) {
      console.error('Failed to get trial usage:', error);
      return undefined;
    }
  }
}
