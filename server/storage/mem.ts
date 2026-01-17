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
  type ImagesMvpQuote,
  type InsertImagesMvpQuote,
} from '@shared/schema';
import { randomUUID, createHash } from 'crypto';
import {
  IStorage,
  AnalyticsSummary,
  SaveMetadataInput,
  StoredMetadata,
  MetadataObjectRef,
  BatchJob,
  BatchResult,
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
  private securityEvents: any[];

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

  // Images MVP Quotes
  private quotesMap: Map<string, ImagesMvpQuote>;
  private quotesBySessionId: Map<string, string>; // sessionId -> quoteId

  // Lightweight cache + list storage (used by quota enforcement)
  private kvStore: Map<string, { value: string; expiresAt?: number }>;
  private listStore: Map<string, string[]>;
  private listExpiry: Map<string, number>;

  constructor() {
    this.users = new Map();
    this.analyticsLog = [];
    this.analyticsCache = {
      data: null,
      lastComputed: null,
      cacheMaxAge: ANALYTICS_CACHE_MAX_AGE,
    };
    this.uiEvents = [];
    this.securityEvents = [];
    this.creditBalancesMap = new Map();
    this.creditBalancesBySessionId = new Map();
    this.creditTransactionsList = [];
    this.creditGrantsList = [];
    this.onboardingSessionsMap = new Map();
    this.onboardingSessionsByUserId = new Map();
    this.trialUsagesMap = new Map();
    this.metadataMap = new Map();
    this.quotesMap = new Map();
    this.quotesBySessionId = new Map();
    this.kvStore = new Map();
    this.listStore = new Map();
    this.listExpiry = new Map();
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
      emailVerified: false,
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

  async logSecurityEvent(event: any): Promise<void> {
    this.securityEvents.push(event);
  }

  async getSecurityEvents(filters?: Record<string, any>): Promise<{
    events: any[];
    totalCount: number;
    hasMore: boolean;
  }> {
    const startTime =
      filters?.startTime instanceof Date ? filters.startTime : null;
    const endTime = filters?.endTime instanceof Date ? filters.endTime : null;
    const eventType =
      typeof filters?.eventType === 'string' ? filters.eventType : null;
    const severity =
      typeof filters?.severity === 'string' ? filters.severity : null;
    const ipAddress =
      typeof filters?.ipAddress === 'string' ? filters.ipAddress : null;
    const userId = typeof filters?.userId === 'string' ? filters.userId : null;
    const limit = typeof filters?.limit === 'number' ? filters.limit : 50;
    const offset = typeof filters?.offset === 'number' ? filters.offset : 0;

    let results = [...this.securityEvents];
    results.sort((a, b) => {
      const ta = new Date(a?.timestamp ?? 0).getTime();
      const tb = new Date(b?.timestamp ?? 0).getTime();
      return tb - ta;
    });

    if (startTime) {
      results = results.filter(e => new Date(e?.timestamp ?? 0) >= startTime);
    }
    if (endTime) {
      results = results.filter(e => new Date(e?.timestamp ?? 0) <= endTime);
    }
    if (eventType) {
      results = results.filter(e => e?.event === eventType);
    }
    if (severity) {
      results = results.filter(e => e?.severity === severity);
    }
    if (ipAddress) {
      results = results.filter(e => e?.ipAddress === ipAddress);
    }
    if (userId) {
      results = results.filter(e => e?.userId === userId);
    }

    const totalCount = results.length;
    const paged = results.slice(offset, offset + limit);
    return {
      events: paged,
      totalCount,
      hasMore: offset + limit < totalCount,
    };
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
      metadataContentType: metadataRef.contentType ?? null,
      createdAt: new Date(),
      metadata: data.metadata,
    };

    this.metadataMap.set(id, record);
    const { metadata, ...stored } = record;
    return stored;
  }

  async getMetadata(
    id: string
  ): Promise<(StoredMetadata & { metadata: any }) | undefined> {
    return this.metadataMap.get(id);
  }

  // ---------------------------------------------------------------------------
  // Cache helpers (quota enforcement / lightweight storage)
  // ---------------------------------------------------------------------------

  async get(key: string): Promise<string | null> {
    const entry = this.kvStore.get(key);
    if (!entry) return null;
    if (entry.expiresAt && entry.expiresAt <= Date.now()) {
      this.kvStore.delete(key);
      return null;
    }
    return entry.value;
  }

  async set(key: string, value: string): Promise<void> {
    this.kvStore.set(key, { value });
  }

  async incr(key: string): Promise<number> {
    const current = await this.get(key);
    const next = (Number(current) || 0) + 1;
    const entry = this.kvStore.get(key);
    this.kvStore.set(key, {
      value: String(next),
      expiresAt: entry?.expiresAt,
    });
    return next;
  }

  async expire(key: string, seconds: number): Promise<void> {
    const expiresAt = Date.now() + seconds * 1000;
    const entry = this.kvStore.get(key);
    if (entry) {
      entry.expiresAt = expiresAt;
    }
    if (this.listStore.has(key)) {
      this.listExpiry.set(key, expiresAt);
    }
  }

  async lpush(key: string, ...values: string[]): Promise<number> {
    const expiresAt = this.listExpiry.get(key);
    if (expiresAt && expiresAt <= Date.now()) {
      this.listStore.delete(key);
      this.listExpiry.delete(key);
    }
    const list = this.listStore.get(key) ?? [];
    list.unshift(...values);
    this.listStore.set(key, list);
    return list.length;
  }

  async ltrim(key: string, start: number, stop: number): Promise<void> {
    const list = this.listStore.get(key);
    if (!list) return;
    const normalizedStop = stop < 0 ? list.length + stop : stop;
    this.listStore.set(key, list.slice(start, normalizedStop + 1));
  }

  async lrange(key: string, start: number, stop: number): Promise<string[]> {
    const expiresAt = this.listExpiry.get(key);
    if (expiresAt && expiresAt <= Date.now()) {
      this.listStore.delete(key);
      this.listExpiry.delete(key);
      return [];
    }
    const list = this.listStore.get(key) ?? [];
    const normalizedStop = stop < 0 ? list.length + stop : stop;
    return list.slice(start, normalizedStop + 1);
  }

  // Optional methods for compatibility
  async getExtractionHistoryByUser?(
    userId: string,
    limit?: number
  ): Promise<any[]> {
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

  async getExtractionHistoryByDateRange?(
    startDate: Date,
    endDate: Date
  ): Promise<any[]> {
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

  async updateUserPassword?(
    userId: string,
    newPassword: string
  ): Promise<void> {
    const user = this.users.get(userId);
    if (user) {
      user.password = newPassword;
    }
  }

  async updateUserProfile?(
    userId: string,
    profile: Partial<User>
  ): Promise<User> {
    const user = this.users.get(userId);
    if (!user) {
      throw new Error('User not found');
    }
    Object.assign(user, profile);
    return user;
  }

  async setPasswordResetToken?(
    userId: string,
    token: string,
    expiresAt: Date
  ): Promise<void> {
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

  // ============================================================================
  // Batch Processing Methods (In-Memory Implementation)
  // ============================================================================

  private batchJobs: Map<string, BatchJob> = new Map();
  private batchJobsByUserId: Map<string, string[]> = new Map();
  private batchResults: Map<string, BatchResult> = new Map();
  private batchResultsByBatchId: Map<string, string[]> = new Map();

  async getBatchJobs(userId: string): Promise<BatchJob[]> {
    const jobIds = this.batchJobsByUserId.get(userId) || [];
    return jobIds
      .map(id => this.batchJobs.get(id))
      .filter((job): job is BatchJob => Boolean(job))
      .sort(
        (a, b) =>
          new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      );
  }

  async getBatchJob(jobId: string): Promise<BatchJob | undefined> {
    return this.batchJobs.get(jobId);
  }

  async createBatchJob(
    job: Omit<BatchJob, 'id' | 'createdAt' | 'updatedAt'>
  ): Promise<BatchJob> {
    const now = new Date().toISOString();
    const jobId = `batch_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const newJob: BatchJob = {
      ...job,
      id: jobId,
      createdAt: now,
      updatedAt: now,
    };

    this.batchJobs.set(jobId, newJob);

    // Add to user's job list
    const userJobs = this.batchJobsByUserId.get(job.userId) || [];
    userJobs.push(jobId);
    this.batchJobsByUserId.set(job.userId, userJobs);

    return newJob;
  }

  async updateBatchJob(
    jobId: string,
    updates: Partial<BatchJob>
  ): Promise<void> {
    const job = this.batchJobs.get(jobId);
    if (!job) return;

    const updatedJob: BatchJob = {
      ...job,
      ...updates,
      updatedAt: new Date().toISOString(),
    };

    this.batchJobs.set(jobId, updatedJob);
  }

  async getBatchResults(batchId: string): Promise<BatchResult[]> {
    const resultIds = this.batchResultsByBatchId.get(batchId) || [];
    return resultIds
      .map(id => this.batchResults.get(id))
      .filter((result): result is BatchResult => Boolean(result))
      .sort(
        (a, b) =>
          new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      );
  }

  async getBatchResult(resultId: string): Promise<BatchResult | undefined> {
    return this.batchResults.get(resultId);
  }

  async createBatchResult(
    result: Omit<BatchResult, 'id' | 'createdAt'>
  ): Promise<BatchResult> {
    const now = new Date().toISOString();
    const resultId = `result_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const newResult: BatchResult = {
      ...result,
      id: resultId,
      createdAt: now,
    };

    this.batchResults.set(resultId, newResult);

    // Add to batch's result list
    const batchResults = this.batchResultsByBatchId.get(result.batchId) || [];
    batchResults.push(resultId);
    this.batchResultsByBatchId.set(result.batchId, batchResults);

    return newResult;
  }

  async updateBatchResult(
    resultId: string,
    updates: Partial<BatchResult>
  ): Promise<void> {
    const result = this.batchResults.get(resultId);
    if (!result) return;

    const updatedResult: BatchResult = {
      ...result,
      ...updates,
    };

    this.batchResults.set(resultId, updatedResult);
  }

  async deleteBatchJob(jobId: string): Promise<void> {
    const job = this.batchJobs.get(jobId);
    if (!job) return;

    // Delete associated results first
    await this.deleteBatchResults(jobId);

    // Remove from user's job list
    const userJobs = this.batchJobsByUserId.get(job.userId) || [];
    const updatedUserJobs = userJobs.filter(id => id !== jobId);
    if (updatedUserJobs.length > 0) {
      this.batchJobsByUserId.set(job.userId, updatedUserJobs);
    } else {
      this.batchJobsByUserId.delete(job.userId);
    }

    // Delete the job
    this.batchJobs.delete(jobId);
  }

  async deleteBatchResults(batchId: string): Promise<void> {
    const resultIds = this.batchResultsByBatchId.get(batchId) || [];

    // Delete each result
    resultIds.forEach(resultId => {
      this.batchResults.delete(resultId);
    });

    // Remove from batch's result list
    this.batchResultsByBatchId.delete(batchId);
  }

  // ============================================================================
  // Images MVP Quote Storage Methods
  // ============================================================================

  async createQuote(quote: InsertImagesMvpQuote): Promise<ImagesMvpQuote> {
    const now = new Date();
    const quoteId = randomUUID();
    const createdQuote: ImagesMvpQuote = {
      id: quoteId,
      sessionId: quote.sessionId,
      userId: quote.userId || null,
      files: quote.files || [],
      ops: quote.ops || {},
      creditsTotal: quote.creditsTotal || 0,
      perFileCredits: quote.perFileCredits || {},
      perFile: quote.perFile || {},
      schedule: quote.schedule || {},
      createdAt: now,
      updatedAt: now,
      expiresAt: quote.expiresAt,
      usedAt: quote.usedAt || null,
      status: quote.status || 'active',
    };

    this.quotesMap.set(quoteId, createdQuote);
    
    // Store session ID mapping for quick lookup
    if (createdQuote.sessionId) {
      this.quotesBySessionId.set(createdQuote.sessionId, quoteId);
    }

    return createdQuote;
  }

  async getQuote(id: string): Promise<ImagesMvpQuote | undefined> {
    const quote = this.quotesMap.get(id);

    // Only return quotes that have not expired by time.
    // This allows callers/tests to retrieve quotes even after marking them "used" or "expired",
    // while still treating time-expired quotes as unavailable.
    if (!quote) return undefined;
    if (new Date() >= quote.expiresAt) {
      // Auto-prune time-expired quotes so they don't leak across tests/runs.
      this.quotesMap.delete(id);
      const sessionMapped = this.quotesBySessionId.get(quote.sessionId);
      if (sessionMapped === id) {
        this.quotesBySessionId.delete(quote.sessionId);
      }
      return undefined;
    }
    return quote;
  }

  async getQuoteBySessionId(sessionId: string): Promise<ImagesMvpQuote | undefined> {
    const now = new Date();
    let best: ImagesMvpQuote | undefined;

    for (const quote of this.quotesMap.values()) {
      if (quote.sessionId !== sessionId) continue;
      if (quote.status !== 'active') continue;
      if (now >= quote.expiresAt) continue;

      if (!best) {
        best = quote;
        continue;
      }

      // Use >= so ties (same ms) prefer the later-inserted quote.
      if (quote.createdAt.getTime() >= best.createdAt.getTime()) {
        best = quote;
      }
    }

    return best;
  }

  async updateQuote(id: string, updates: Partial<ImagesMvpQuote>): Promise<void> {
    const existingQuote = this.quotesMap.get(id);
    if (!existingQuote) {
      throw new Error('Quote not found');
    }
    const nextUpdatedAt = new Date(
      Math.max(Date.now(), existingQuote.updatedAt.getTime() + 1)
    );
    const updatedQuote: ImagesMvpQuote = {
      ...existingQuote,
      ...updates,
      updatedAt: nextUpdatedAt,
    };

    this.quotesMap.set(id, updatedQuote);
  }

  async expireQuote(id: string): Promise<void> {
    const quote = this.quotesMap.get(id);
    if (!quote) {
      throw new Error('Quote not found');
    }

    const updatedAt = new Date(Math.max(Date.now(), quote.updatedAt.getTime() + 1));
    const updatedQuote: ImagesMvpQuote = {
      ...quote,
      status: 'expired',
      updatedAt,
    };
    this.quotesMap.set(id, updatedQuote);
  }

  async cleanupExpiredQuotes(): Promise<number> {
    let cleanedCount = 0;
    const now = new Date();

    for (const [id, quote] of this.quotesMap.entries()) {
      if (now >= quote.expiresAt) {
        this.quotesMap.delete(id);
        const sessionMapped = this.quotesBySessionId.get(quote.sessionId);
        if (sessionMapped === id) {
          this.quotesBySessionId.delete(quote.sessionId);
        }
        cleanedCount += 1;
      }
    }

    return cleanedCount;
  }
}
