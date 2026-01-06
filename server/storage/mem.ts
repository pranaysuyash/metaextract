import {
  type User,
  type InsertUser,
  type InsertExtractionAnalytics,
  type ExtractionAnalytics,
  type CreditBalance,
  type CreditGrant,
  type CreditTransaction,
  type InsertUiEvent,
  type UiEvent,
  type OnboardingSession,
  type InsertOnboardingSession,
  type TrialUsage,
  type InsertTrialUsage,
} from '@shared/schema';
import { randomUUID, createHash } from 'crypto';
import {
  IStorage,
  AnalyticsSummary,
  SaveMetadataInput,
  StoredMetadata,
  MetadataObjectRef,
} from './types';
import { buildMetadataSummary, generateRecordId } from './metadataPartitioning';

// ============================================================================
// Types
// ============================================================================

interface CacheableAnalytics {
  data: AnalyticsSummary | null;
  lastComputed: Date | null;
  cacheMaxAge: number; // milliseconds
}

// ============================================================================
// Constants
// ============================================================================

const ANALYTICS_CACHE_MAX_AGE = 5 * 60 * 1000; // 5 minutes
const TIME_RANGES = {
  ONE_DAY_MS: 24 * 60 * 60 * 1000,
  SEVEN_DAYS_MS: 7 * 24 * 60 * 60 * 1000,
};

/**
 * Normalize email for consistent lookups
 */
function normalizeEmail(email: string): string {
  return email.trim().toLowerCase();
}

// ============================================================================
// In-Memory Storage Implementation
// ============================================================================

export class MemStorage implements IStorage {
  // User data
  private users: Map<string, User>;

  // Analytics data
  private analyticsLog: ExtractionAnalytics[];
  private analyticsCache: CacheableAnalytics;
  private uiEvents: UiEvent[];

  // Credit system
  private creditBalancesMap: Map<string, CreditBalance>;
  private creditBalancesBySessionId: Map<string, string>; // sessionId -> balanceId for O(1) lookups
  private creditTransactionsList: CreditTransaction[];
  private creditGrantsList: CreditGrant[];

  // Onboarding
  private onboardingSessionsMap: Map<string, OnboardingSession>;
  private onboardingSessionsByUserId: Map<string, string[]>; // userId -> [sessionIds] for O(1) lookups

  // Trial usage
  private trialUsagesMap: Map<string, TrialUsage>;

  // Metadata
  private metadataMap: Map<string, StoredMetadata & { metadata: any }>;

  constructor() {
    this.users = new Map();
    this.analyticsLog = [];
    this.analyticsCache = {
      data: null,
      lastComputed: null,
      cacheMaxAge: ANALYTICS_CACHE_MAX_AGE,
    };
    this.uiEvents = [];
    this.creditBalancesMap = new Map();
    this.creditBalancesBySessionId = new Map();
    this.creditTransactionsList = [];
    this.creditGrantsList = [];
    this.onboardingSessionsMap = new Map();
    this.onboardingSessionsByUserId = new Map();
    this.trialUsagesMap = new Map();
    this.metadataMap = new Map();
  }

  // ============================================================================
  // Helpers
  // ============================================================================

  /**
   * Check if analytics cache is still valid
   */
  private isAnalyticsCacheValid(): boolean {
    if (!this.analyticsCache.data || !this.analyticsCache.lastComputed) {
      return false;
    }
    const age = Date.now() - this.analyticsCache.lastComputed.getTime();
    return age < this.analyticsCache.cacheMaxAge;
  }

  /**
   * Validate credit amount is positive
   */
  private validateCreditAmount(amount: number): void {
    if (amount <= 0) {
      throw new Error('Credit amount must be positive');
    }
    if (!Number.isFinite(amount)) {
      throw new Error('Credit amount must be a finite number');
    }
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
    // Invalidate cache when new analytics are logged
    this.analyticsCache.data = null;
    this.analyticsCache.lastComputed = null;
  }

  async logUiEvent(data: InsertUiEvent): Promise<void> {
    const entry: UiEvent = {
      id: randomUUID(),
      product: data.product || 'core',
      eventName: data.eventName,
      sessionId: data.sessionId || null,
      userId: data.userId || null,
      properties: data.properties,
      ipAddress: data.ipAddress || null,
      userAgent: data.userAgent || null,
      createdAt: new Date(),
    };
    this.uiEvents.push(entry);
  }

  async getUiEvents(params?: {
    product?: string;
    since?: Date;
    limit?: number;
  }): Promise<UiEvent[]> {
    const product = params?.product;
    const since = params?.since;
    const limit = params?.limit;

    let results = this.uiEvents;
    if (product) {
      results = results.filter(event => event.product === product);
    }
    if (since) {
      results = results.filter(event => event.createdAt >= since);
    }

    const ordered = [...results].sort(
      (a, b) => b.createdAt.getTime() - a.createdAt.getTime()
    );

    if (!limit) {
      return ordered;
    }

    return ordered.slice(0, limit);
  }

  async getAnalyticsSummary(): Promise<AnalyticsSummary> {
    // ✅ Return cached result if still valid (5 minute TTL)
    if (this.isAnalyticsCacheValid() && this.analyticsCache.data) {
      return this.analyticsCache.data;
    }

    const now = new Date();
    const oneDayAgo = new Date(now.getTime() - TIME_RANGES.ONE_DAY_MS);
    const sevenDaysAgo = new Date(now.getTime() - TIME_RANGES.SEVEN_DAYS_MS);

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

    const result: AnalyticsSummary = {
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

    // ✅ Cache the result
    this.analyticsCache.data = result;
    this.analyticsCache.lastComputed = new Date();

    return result;
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
    // ✅ O(1) lookup using sessionId index
    const existingBalanceId = this.creditBalancesBySessionId.get(sessionId);
    if (existingBalanceId) {
      const existing = this.creditBalancesMap.get(existingBalanceId);
      if (existing) return existing;
    }

    const balance: CreditBalance = {
      id: randomUUID(),
      userId: userId || null,
      sessionId,
      credits: 0,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    this.creditBalancesMap.set(balance.id, balance);
    this.creditBalancesBySessionId.set(sessionId, balance.id);
    return balance;
  }

  async getCreditBalanceBySessionId(
    sessionId: string
  ): Promise<CreditBalance | undefined> {
    const balanceId = this.creditBalancesBySessionId.get(sessionId);
    if (!balanceId) return undefined;
    return this.creditBalancesMap.get(balanceId);
  }

  async getCreditBalance(
    balanceId: string
  ): Promise<CreditBalance | undefined> {
    return this.creditBalancesMap.get(balanceId);
  }

  async getCreditGrantByPaymentId(
    paymentId: string
  ): Promise<CreditGrant | undefined> {
    return this.creditGrantsList
      .filter(g => g.dodoPaymentId === paymentId)
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())[0];
  }

  async transferCredits(
    fromBalanceId: string,
    toBalanceId: string,
    amount: number,
    description: string
  ): Promise<void> {
    if (!Number.isFinite(amount) || amount <= 0) {
      throw new Error('Transfer amount must be positive');
    }

    const from = this.creditBalancesMap.get(fromBalanceId);
    const to = this.creditBalancesMap.get(toBalanceId);
    if (!from) throw new Error('Source balance not found');
    if (!to) throw new Error('Destination balance not found');
    if ((from.credits ?? 0) < amount) throw new Error('Insufficient credits');

    const remainingTotal = this.creditGrantsList
      .filter(g => g.balanceId === fromBalanceId && (g.remaining ?? 0) > 0)
      .reduce((sum, g) => sum + (g.remaining ?? 0), 0);
    if (remainingTotal !== amount) {
      const missing = amount - remainingTotal;
      if (missing <= 0) {
        throw new Error('Partial credit transfers are not supported');
      }
      this.creditGrantsList.push({
        id: randomUUID(),
        balanceId: fromBalanceId,
        amount: missing,
        remaining: missing,
        description: 'Legacy credits (unattributed)',
        pack: null,
        dodoPaymentId: null,
        createdAt: new Date(0),
        expiresAt: null,
      });
    }

    from.credits -= amount;
    from.updatedAt = new Date();
    to.credits += amount;
    to.updatedAt = new Date();

    // Move remaining grants to preserve refund eligibility.
    for (const grant of this.creditGrantsList) {
      if (grant.balanceId === fromBalanceId && (grant.remaining ?? 0) > 0) {
        grant.balanceId = toBalanceId;
      }
    }

    const now = new Date();
    this.creditTransactionsList.push(
      {
        id: randomUUID(),
        balanceId: fromBalanceId,
        type: 'transfer',
        amount: -amount,
        description,
        fileType: null,
        dodoPaymentId: null,
        createdAt: now,
      } as any,
      {
        id: randomUUID(),
        balanceId: toBalanceId,
        type: 'transfer',
        amount,
        description,
        fileType: null,
        dodoPaymentId: null,
        createdAt: now,
      } as any
    );
  }

  async addCredits(
    balanceId: string,
    amount: number,
    description: string,
    paymentId?: string
  ): Promise<CreditTransaction> {
    // ✅ Validate credit amount before processing
    this.validateCreditAmount(amount);

    const balance = this.creditBalancesMap.get(balanceId);
    if (!balance) {
      throw new Error(`Credit balance not found: ${balanceId}`);
    }

    if (paymentId) {
      const existing = this.creditTransactionsList.find(
        t =>
          t.balanceId === balanceId &&
          t.type === 'purchase' &&
          t.dodoPaymentId === paymentId
      );
      if (existing) return existing;
    }

    balance.credits += amount;
    balance.updatedAt = new Date();

    const grant: CreditGrant = {
      id: randomUUID(),
      balanceId,
      amount,
      remaining: amount,
      description,
      pack: null,
      dodoPaymentId: paymentId || null,
      createdAt: new Date(),
      expiresAt: null,
    };
    this.creditGrantsList.push(grant);

    const tx: CreditTransaction = {
      id: randomUUID(),
      balanceId,
      grantId: grant.id,
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
    // ✅ Validate credit amount
    this.validateCreditAmount(amount);

    const balance = this.creditBalancesMap.get(balanceId);
    // ✅ Atomic check: Verify balance is sufficient before deducting
    // This prevents negative credits even if async operations interleave
    if (!balance || balance.credits < amount) return null;

    balance.credits -= amount;
    balance.updatedAt = new Date();

    // FIFO consume from grants (oldest first)
    let remainingToCharge = amount;
    const now = new Date();
    const grants = this.creditGrantsList
      .filter(
        g =>
          g.balanceId === balanceId &&
          (g.remaining ?? 0) > 0 &&
          (!g.expiresAt || g.expiresAt.getTime() > now.getTime())
      )
      .sort((a, b) => {
        const timeDiff = a.createdAt.getTime() - b.createdAt.getTime();
        if (timeDiff !== 0) return timeDiff;
        // Fall back to insertion order based on internal list index to guarantee FIFO
        return (
          this.creditGrantsList.indexOf(a) - this.creditGrantsList.indexOf(b)
        );
      });

    const grantsTotal = grants.reduce((sum, g) => sum + (g.remaining ?? 0), 0);
    if (grantsTotal < amount) {
      const missing = amount - grantsTotal;
      const legacyGrant: CreditGrant = {
        id: randomUUID(),
        balanceId,
        amount: missing,
        remaining: missing,
        description: 'Legacy credits (unattributed)',
        pack: null,
        dodoPaymentId: null,
        createdAt: new Date(0),
        expiresAt: null,
      };
      this.creditGrantsList.push(legacyGrant);
      grants.unshift(legacyGrant);
    }

    let firstTx: CreditTransaction | null = null;
    for (const grant of grants) {
      if (remainingToCharge <= 0) break;
      const take = Math.min(grant.remaining, remainingToCharge);
      if (take <= 0) continue;
      grant.remaining -= take;
      remainingToCharge -= take;

      const tx: CreditTransaction = {
        id: randomUUID(),
        balanceId,
        grantId: grant.id,
        type: 'usage',
        amount: -take,
        description,
        fileType: fileType || null,
        dodoPaymentId: null,
        createdAt: new Date(),
      };
      this.creditTransactionsList.push(tx);
      if (!firstTx) firstTx = tx;
    }

    if (remainingToCharge > 0) {
      // Should not happen if balance and grants are consistent; revert balance defensively.
      balance.credits += amount;
      balance.updatedAt = new Date();
      return null;
    }

    return firstTx;
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
    // ✅ O(1) lookup using userId index, return most recent session
    const sessionIds = this.onboardingSessionsByUserId.get(userId);
    if (!sessionIds || sessionIds.length === 0) return undefined;

    // Get the last session (most recent)
    const lastSessionId = sessionIds[sessionIds.length - 1];
    return this.onboardingSessionsMap.get(lastSessionId);
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
    // ✅ Update userId index for fast lookups
    if (session.userId) {
      const sessions =
        this.onboardingSessionsByUserId.get(session.userId) ?? [];
      sessions.push(session.id);
      this.onboardingSessionsByUserId.set(session.userId, sessions);
    }
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
    const normalizedEmail = normalizeEmail(email);
    const usage = this.trialUsagesMap.get(normalizedEmail);
    return !!usage && usage.uses > 0;
  }

  async recordTrialUsage(data: InsertTrialUsage): Promise<TrialUsage> {
    const normalizedEmail = normalizeEmail(data.email);
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
    const normalizedEmail = normalizeEmail(email);
    return this.trialUsagesMap.get(normalizedEmail);
  }

  async saveMetadata(data: SaveMetadataInput): Promise<StoredMetadata> {
    const id = generateRecordId();
    const { summary } = buildMetadataSummary(data.metadata);
    const raw = Buffer.from(JSON.stringify(data.metadata), 'utf8');
    const metadataRef: MetadataObjectRef = {
      provider: 'memory',
      bucket: 'in-memory',
      key: id,
      sizeBytes: raw.byteLength,
      sha256: createHash('sha256').update(raw).digest('hex'),
      contentType: 'application/json',
      encoding: 'identity',
      createdAt: new Date().toISOString(),
    };

    const record: StoredMetadata & { metadata: any } = {
      id,
      userId: data.userId || null,
      fileName: data.fileName,
      fileSize: data.fileSize || null,
      mimeType: data.mimeType || null,
      metadataSummary: summary,
      metadataRef,
      metadataSha256: metadataRef.sha256,
      metadataSizeBytes: metadataRef.sizeBytes,
      metadataContentType: metadataRef.contentType,
      createdAt: new Date(),
      metadata: data.metadata,
    };

    this.metadataMap.set(id, record);
    return {
      ...record,
      metadata: undefined,
    };
  }

  async getMetadata(
    id: string
  ): Promise<(StoredMetadata & { metadata: any }) | undefined> {
    return this.metadataMap.get(id);
  }

  // Optional methods for compatibility
  async getExtractionHistoryByUser?(userId: string, limit?: number): Promise<any[]> {
    return [];
  }

  async anonymizeUserData?(userId: string): Promise<void> {
    // Implementation would go here
  }

  async incrementFailedLoginAttempts?(userId: string): Promise<void> {
    // Implementation would go here
  }

  async setTwoFactorSecret?(userId: string, secret: string): Promise<void> {
    // Implementation would go here
  }

  async clearTwoFactorSecret?(userId: string): Promise<void> {
    // Implementation would go here
  }

  async getExtractionHistoryByFile?(fileId: string): Promise<any[]> {
    return [];
  }

  async getExtractionHistoryByDateRange?(startDate: Date, endDate: Date): Promise<any[]> {
    return [];
  }

  async getExtractionHistoryByTier?(tier: string): Promise<any[]> {
    return [];
  }

  async getExtractionHistoryByFileType?(fileType: string): Promise<any[]> {
    return [];
  }

  async updatePassword?(userId: string, hashedPassword: string): Promise<void> {
    // Implementation would go here
  }

  async getUserById?(id: string): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByEmail?(email: string): Promise<User | undefined> {
    const normalizedEmail = email.toLowerCase();
    for (const [_, user] of this.users) {
      if (user.email.toLowerCase() === normalizedEmail) {
        return user;
      }
    }
    return undefined;
  }

  async updateUserPassword?(userId: string, newPassword: string): Promise<void> {
    const user = this.users.get(userId);
    if (user) {
      user.password = newPassword;
      user.updatedAt = new Date();
    }
  }

  async updateUserProfile?(userId: string, profile: Partial<User>): Promise<void> {
    const user = this.users.get(userId);
    if (user) {
      Object.assign(user, profile);
      user.updatedAt = new Date();
    }
  }

  async setPasswordResetToken?(userId: string, token: string, expiresAt: Date): Promise<void> {
    // Implementation would go here
  }

  async getUserByResetToken?(token: string): Promise<User | undefined> {
    // Implementation would go here
    return undefined;
  }

  async resetFailedLoginAttempts?(userId: string): Promise<void> {
    // Implementation would go here
  }

  async enableTwoFactor?(userId: string, secret: string): Promise<void> {
    // Implementation would go here
  }

  async disableTwoFactor?(userId: string): Promise<void> {
    // Implementation would go here
  }
}
