import {
  type User,
  type InsertUser,
  type InsertExtractionAnalytics,
  type ExtractionAnalytics,
  type CreditBalance,
  type CreditTransaction,
  type OnboardingSession,
  type InsertOnboardingSession,
  type TrialUsage,
  type InsertTrialUsage,
  type InsertTrialUsage,
  metadataResults,
  type MetadataResult,
  type InsertMetadataResult,
} from '@shared/schema';
import { randomUUID } from 'crypto';
import { IStorage, AnalyticsSummary } from './types';

export class MemStorage implements IStorage {
  private users: Map<string, User>;
  private analyticsLog: ExtractionAnalytics[];
  private creditBalancesMap: Map<string, CreditBalance> = new Map();
  private creditTransactionsList: CreditTransaction[] = [];
  private onboardingSessionsMap: Map<string, OnboardingSession> = new Map();
  private creditBalancesMap: Map<string, CreditBalance> = new Map();
  private creditTransactionsList: CreditTransaction[] = [];
  private onboardingSessionsMap: Map<string, OnboardingSession> = new Map();
  private trialUsagesMap: Map<string, TrialUsage> = new Map();
  private metadataMap: Map<string, MetadataResult> = new Map();

  constructor() {
    this.users = new Map();
    this.analyticsLog = [];
  }

  async getUser(id: string): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      user => user.username === username
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = randomUUID();
    const user: User = {
      ...insertUser,
      id,
      tier: 'free',
      subscriptionId: null,
      subscriptionStatus: null,
      customerId: null,
      createdAt: new Date(),
    };
    this.users.set(id, user);
    return user;
  }

  async logExtractionUsage(data: InsertExtractionAnalytics): Promise<void> {
    const entry: ExtractionAnalytics = {
      id: randomUUID(),
      tier: data.tier || 'free',
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
      b => b.sessionId === sessionId
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
    // ✅ Atomic check: Verify balance is sufficient before deducting
    // This prevents negative credits even if async operations interleave
    if (!balance || balance.credits < amount) return null;

    balance.credits -= amount;
    balance.updatedAt = new Date();

    const tx: CreditTransaction = {
      id: randomUUID(),
      balanceId,
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
      .filter(t => t.balanceId === balanceId)
      .slice(-limit)
      .reverse();
  }

  async getOnboardingSession(
    userId: string
  ): Promise<OnboardingSession | undefined> {
    return Array.from(this.onboardingSessionsMap.values())
      .filter(s => s.userId === userId)
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

  // Metadata Persistence
  async saveMetadata(data: InsertMetadataResult): Promise<MetadataResult> {
    const id = randomUUID();
    const result: MetadataResult = {
      ...data,
      id,
      createdAt: new Date(),
    };
    this.metadataMap.set(id, result);
    return result;
  }

  async getMetadata(id: string): Promise<MetadataResult | undefined> {
    return this.metadataMap.get(id);
  }
}
