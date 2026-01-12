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
import { randomUUID } from 'crypto';
import { desc, sql, eq } from 'drizzle-orm';

export interface IStorage {
  getUser(id: string): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  logExtractionUsage(data: InsertExtractionAnalytics): Promise<void>;
  getAnalyticsSummary(): Promise<AnalyticsSummary>;
  getRecentExtractions(limit?: number): Promise<ExtractionAnalytics[]>;
  // Credits system
  getOrCreateCreditBalance(
    sessionId: string,
    userId?: string
  ): Promise<CreditBalance>;
  getCreditBalance(balanceId: string): Promise<CreditBalance | undefined>;
  addCredits(
    balanceId: string,
    amount: number,
    description: string,
    paymentId?: string
  ): Promise<CreditTransaction>;
  useCredits(
    balanceId: string,
    amount: number,
    description: string,
    fileType?: string
  ): Promise<CreditTransaction | null>;
  getCreditTransactions(
    balanceId: string,
    limit?: number
  ): Promise<CreditTransaction[]>;
  // Onboarding system
  getOnboardingSession(userId: string): Promise<OnboardingSession | undefined>;
  createOnboardingSession(
    data: InsertOnboardingSession
  ): Promise<OnboardingSession>;
  updateOnboardingSession(
    sessionId: string,
    updates: Partial<OnboardingSession>
  ): Promise<void>;
  // Trial system
  hasTrialUsage(email: string): Promise<boolean>;
  recordTrialUsage(data: InsertTrialUsage): Promise<TrialUsage>;
  getTrialUsageByEmail(email: string): Promise<TrialUsage | undefined>;
}

export interface AnalyticsSummary {
  totalExtractions: number;
  byTier: Record<string, number>;
  byFileType: Record<string, number>;
  byMediaType: {
    images: number;
    videos: number;
    pdfs: number;
    audio: number;
    other: number;
  };
  last24Hours: number;
  last7Days: number;
  averageProcessingMs: number;
  totalBytesProcessed: number;
  successRate: number;
}

export class MemStorage implements IStorage {
  private users: Map<string, User>;
  private analyticsLog: ExtractionAnalytics[];
  private creditBalancesMap: Map<string, CreditBalance> = new Map();
  private creditTransactionsList: CreditTransaction[] = [];
  private onboardingSessionsMap: Map<string, OnboardingSession> = new Map();
  private trialUsagesMap: Map<string, TrialUsage> = new Map();

  constructor() {
    this.users = new Map();
    this.analyticsLog = [];
  }

  async getUser(id: string): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = randomUUID();
    const user: User = {
      ...insertUser,
      id,
      tier: 'enterprise',
      subscriptionId: null,
      subscriptionStatus: null,
      customerId: null,
      emailVerified: false,
      createdAt: new Date(),
    };
    this.users.set(id, user);
    return user;
  }

  async logExtractionUsage(data: InsertExtractionAnalytics): Promise<void> {
    const entry: ExtractionAnalytics = {
      id: randomUUID(),
      tier: data.tier || 'enterprise',
      fileExtension: data.fileExtension,
      mimeType: data.mimeType,
      fileSizeBytes: data.fileSizeBytes,
      isVideo: data.isVideo || false,
      isImage: data.isImage || false,
      isPdf: data.isPdf || false,
      isAudio: data.isAudio || false,
      fieldsExtracted: data.fieldsExtracted || 0,
      processingMs: data.processingMs || 0,
      success: data.success !== undefined ? data.success : true,
      failureReason: data.failureReason || null,
      ipAddress: data.ipAddress || null,
      userAgent: data.userAgent || null,
      requestedAt: new Date(),
    };
    this.analyticsLog.push(entry);
  }

  async getAnalyticsSummary(): Promise<AnalyticsSummary> {
    const now = new Date();
    const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

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

    for (const entry of this.analyticsLog) {
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
      totalExtractions: this.analyticsLog.length,
      byTier,
      byFileType,
      byMediaType: { images, videos, pdfs, audio, other },
      last24Hours,
      last7Days,
      averageProcessingMs:
        this.analyticsLog.length > 0
          ? Math.round(totalProcessingMs / this.analyticsLog.length)
          : 0,
      totalBytesProcessed: totalBytes,
      successRate:
        this.analyticsLog.length > 0
          ? Math.round((successCount / this.analyticsLog.length) * 100)
          : 100,
    };
  }

  async getRecentExtractions(
    limit: number = 50
  ): Promise<ExtractionAnalytics[]> {
    return this.analyticsLog.slice(-limit).reverse();
  }

  async getOrCreateCreditBalance(
    sessionId: string,
    userId?: string
  ): Promise<CreditBalance> {
    const existing = Array.from(this.creditBalancesMap.values()).find(
      (b) => b.sessionId === sessionId
    );
    if (existing) return existing;

    const balance: CreditBalance = {
      id: randomUUID(),
      userId: userId || null,
      sessionId,
      credits: 0,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    this.creditBalancesMap.set(balance.id, balance);
    return balance;
  }

  async getCreditBalance(
    balanceId: string
  ): Promise<CreditBalance | undefined> {
    return this.creditBalancesMap.get(balanceId);
  }

  async addCredits(
    balanceId: string,
    amount: number,
    description: string,
    paymentId?: string
  ): Promise<CreditTransaction> {
    const balance = this.creditBalancesMap.get(balanceId);
    if (balance) {
      balance.credits += amount;
      balance.updatedAt = new Date();
    }

    const tx: CreditTransaction = {
      id: randomUUID(),
      balanceId,
      grantId: null,
      type: 'purchase',
      amount,
      description,
      fileType: null,
      dodoPaymentId: paymentId || null,
      createdAt: new Date(),
    };
    this.creditTransactionsList.push(tx);
    return tx;
  }

  async useCredits(
    balanceId: string,
    amount: number,
    description: string,
    fileType?: string
  ): Promise<CreditTransaction | null> {
    const balance = this.creditBalancesMap.get(balanceId);
    if (!balance || balance.credits < amount) return null;

    balance.credits -= amount;
    balance.updatedAt = new Date();

    const tx: CreditTransaction = {
      id: randomUUID(),
      balanceId,
      grantId: null,
      type: 'usage',
      amount: -amount,
      description,
      fileType: fileType || null,
      dodoPaymentId: null,
      createdAt: new Date(),
    };
    this.creditTransactionsList.push(tx);
    return tx;
  }

  async getCreditTransactions(
    balanceId: string,
    limit: number = 50
  ): Promise<CreditTransaction[]> {
    return this.creditTransactionsList
      .filter((t) => t.balanceId === balanceId)
      .slice(-limit)
      .reverse();
  }

  async getOnboardingSession(
    userId: string
  ): Promise<OnboardingSession | undefined> {
    return Array.from(this.onboardingSessionsMap.values())
      .filter((s) => s.userId === userId)
      .sort((a, b) => b.startedAt.getTime() - a.startedAt.getTime())[0];
  }

  async createOnboardingSession(
    data: InsertOnboardingSession
  ): Promise<OnboardingSession> {
    const session: OnboardingSession = {
      id: randomUUID(),
      userId: data.userId ?? null,
      startedAt: data.startedAt ?? new Date(),
      completedAt: data.completedAt ?? null,
      currentStep: data.currentStep ?? 0,
      pathId: data.pathId,
      userProfile: data.userProfile,
      progress: data.progress,
      interactions: data.interactions ?? '[]',
      isActive: data.isActive ?? true,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    this.onboardingSessionsMap.set(session.id, session);
    return session;
  }

  async updateOnboardingSession(
    sessionId: string,
    updates: Partial<OnboardingSession>
  ): Promise<void> {
    const session = this.onboardingSessionsMap.get(sessionId);
    if (session) {
      Object.assign(session, updates, { updatedAt: new Date() });
    }
  }

  async hasTrialUsage(email: string): Promise<boolean> {
    const normalizedEmail = email.trim().toLowerCase();
    const usage = this.trialUsagesMap.get(normalizedEmail);
    return !!usage && usage.uses > 0;
  }

  async recordTrialUsage(data: InsertTrialUsage): Promise<TrialUsage> {
    const normalizedEmail = data.email.trim().toLowerCase();
    const existing = this.trialUsagesMap.get(normalizedEmail);
    if (existing) {
      existing.uses += 1;
      existing.usedAt = new Date();
      existing.ipAddress = data.ipAddress ?? null;
      existing.userAgent = data.userAgent ?? null;
      existing.sessionId = data.sessionId ?? null;
      return existing;
    }

    const usage: TrialUsage = {
      id: randomUUID(),
      email: normalizedEmail,
      uses: 1,
      usedAt: new Date(),
      ipAddress: data.ipAddress ?? null,
      userAgent: data.userAgent ?? null,
      sessionId: data.sessionId ?? null,
    };

    this.trialUsagesMap.set(normalizedEmail, usage);
    return usage;
  }

  async getTrialUsageByEmail(email: string): Promise<TrialUsage | undefined> {
    const normalizedEmail = email.trim().toLowerCase();
    return this.trialUsagesMap.get(normalizedEmail);
  }
}

export class DatabaseStorage implements IStorage {
  private db: any;

  constructor() {
    // Lazy load database connection
    try {
      const { db } = require('./db');
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
      const normalizedEmail = data.email.toLowerCase();
      const [updated] = await this.db
        .update(trialUsages)
        .set({
          uses: sql`${trialUsages.uses} + 1`,
          usedAt: new Date(),
          ipAddress: data.ipAddress ?? null,
          userAgent: data.userAgent ?? null,
          sessionId: data.sessionId ?? null,
        })
        .where(eq(trialUsages.email, normalizedEmail))
        .returning();

      if (updated) {
        return updated;
      }

      const [trialUsage] = await this.db
        .insert(trialUsages)
        .values({
          ...data,
          email: normalizedEmail,
          uses: 1,
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
