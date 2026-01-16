import {
  type User,
  type InsertUser,
  type InsertExtractionAnalytics,
  type ExtractionAnalytics,
  extractionAnalytics,
  uiEvents,
  type InsertUiEvent,
  type UiEvent,
  users,
  creditBalances,
  creditGrants,
  creditTransactions,
  type CreditBalance,
  type CreditGrant,
  type CreditTransaction,
  onboardingSessions,
  type OnboardingSession,
  type InsertOnboardingSession,
  type InsertTrialUsage,
  type TrialUsage,
  trialUsages,
  metadataResults,
  type MetadataResult,
  imagesMvpQuotes,
  type ImagesMvpQuote,
  type InsertImagesMvpQuote,
} from '@shared/schema';
import { and, asc, desc, eq, gte, gt, lt, isNull, or, sql } from 'drizzle-orm';
import { db } from '../db';
import {
  IStorage,
  AnalyticsSummary,
  SaveMetadataInput,
  StoredMetadata,
  MetadataObjectRef,
  BatchJob,
  BatchResult,
} from './types';
import { IObjectStorage } from './objectStorage';
import {
  buildMetadataSummary,
  buildObjectKey,
  decompressMetadata,
  generateRecordId,
  prepareMetadataObject,
} from './metadataPartitioning';

export class DatabaseStorage implements IStorage {
  private db: any;
  private objectStorage: IObjectStorage;
  private kvStore: Map<string, { value: string; expiresAt?: number }>;
  private listStore: Map<string, string[]>;
  private listExpiry: Map<string, number>;
  private securityEvents: any[];

  constructor(objectStorage: IObjectStorage) {
    // Use the imported db connection
    this.db = db;
    this.objectStorage = objectStorage;
    this.kvStore = new Map();
    this.listStore = new Map();
    this.listExpiry = new Map();
    this.securityEvents = [];
  }

  // Test helpers: expose recent abort/fallback information in tests without
  // relying on internal properties. These are intentionally simple and only
  // available for tests (no-op in production use).
  /**
   * getLastAbort
   * Returns the last recorded transaction abort information captured during tests.
   * Only populated when NODE_ENV === 'test'. Useful for assertions in unit tests.
   * @returns { op: string, error: any } | null
   */
  getLastAbort(): { op: string; error: any } | null {
    return (this as any).__lastAbort ?? null;
  }

  /**
   * getCreditGrantsFallback
   * Returns the last message captured when the credit_grants flow fell back to
   * legacy behavior during a transfer. Populated only in test environment.
   */
  getCreditGrantsFallback(): string | null {
    return (this as any).__creditGrantsFallback ?? null;
  }

  /**
   * clearTestState
   * Clears internal test-only state. Safe to call in tests to reset between runs.
   */
  clearTestState(): void {
    try {
      delete (this as any).__lastAbort;
      delete (this as any).__creditGrantsFallback;
    } catch (e) {
      // ignore
    }
  }

  async getUser(id: string): Promise<User | undefined> {
    if (!this.db) return undefined;
    try {
      const [user] = await this.db
        .select()
        .from(users)
        .where(eq(users.id, id))
        .limit(1);
      return user;
    } catch (error) {
      console.error('Failed to get user:', error);
      return undefined;
    }
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    if (!this.db) return undefined;
    try {
      const [user] = await this.db
        .select()
        .from(users)
        .where(eq(users.username, username))
        .limit(1);
      return user;
    } catch (error) {
      console.error('Failed to get user by username:', error);
      return undefined;
    }
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    if (!this.db) throw new Error('Database not available');
    try {
      const [created] = await this.db
        .insert(users)
        .values(insertUser)
        .returning();
      return created;
    } catch (error) {
      console.error('Failed to create user:', error);
      throw error;
    }
  }

  async getUserById?(id: string): Promise<User | undefined> {
    return this.getUser(id);
  }

  async getUserByEmail?(email: string): Promise<User | undefined> {
    if (!this.db) return undefined;
    try {
      const normalized = email.toLowerCase();
      const [user] = await this.db
        .select()
        .from(users)
        .where(eq(users.email, normalized))
        .limit(1);
      return user;
    } catch (error) {
      console.error('Failed to get user by email:', error);
      return undefined;
    }
  }

  async updateUserPassword?(
    userId: string,
    newPassword: string
  ): Promise<void> {
    if (!this.db) return;
    try {
      await this.db
        .update(users)
        .set({ password: newPassword })
        .where(eq(users.id, userId));
    } catch (error) {
      console.error('Failed to update user password:', error);
    }
  }

  async updateUserProfile?(
    userId: string,
    profile: Partial<User>
  ): Promise<User> {
    if (!this.db) throw new Error('Database not available');
    try {
      const updates: Partial<User> = {};
      if (profile.username !== undefined) updates.username = profile.username;
      if (profile.email !== undefined)
        updates.email = profile.email.toLowerCase();

      if (Object.keys(updates).length === 0) {
        const [existing] = await this.db
          .select()
          .from(users)
          .where(eq(users.id, userId))
          .limit(1);
        if (!existing) {
          throw new Error('User not found');
        }
        return existing;
      }

      const [updated] = await this.db
        .update(users)
        .set(updates)
        .where(eq(users.id, userId))
        .returning();
      if (!updated) {
        throw new Error('User not found');
      }
      return updated;
    } catch (error) {
      console.error('Failed to update user profile:', error);
      throw error;
    }
  }

  async anonymizeUserData?(userId: string): Promise<void> {
    if (!this.db) return;
    try {
      const anonymizedEmail = `anonymized+${userId}@example.com`;
      const anonymizedUsername = `anonymized_${userId.slice(0, 8)}`;
      await this.db
        .update(users)
        .set({
          email: anonymizedEmail,
          username: anonymizedUsername,
          subscriptionId: null,
          subscriptionStatus: 'none',
          customerId: null,
        })
        .where(eq(users.id, userId));
    } catch (error) {
      console.error('Failed to anonymize user data:', error);
    }
  }

  async logExtractionUsage(data: InsertExtractionAnalytics): Promise<void> {
    if (!this.db) return;
    try {
      await this.db.insert(extractionAnalytics).values(data);
    } catch (error) {
      console.error('Failed to log extraction usage:', error);
    }
  }

  async logUiEvent(data: InsertUiEvent): Promise<void> {
    if (!this.db) return;
    try {
      await this.db.insert(uiEvents).values(data);
    } catch (error) {
      console.error('Failed to log UI event:', error);
    }
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

  async getUiEvents(params?: {
    product?: string;
    since?: Date;
    limit?: number;
  }): Promise<UiEvent[]> {
    if (!this.db) return [];
    const limit = params?.limit ?? 1000;
    const product = params?.product;
    const since = params?.since;
    try {
      const conditions: any[] = [];
      if (product) {
        conditions.push(eq(uiEvents.product, product));
      }
      if (since) {
        conditions.push(gte(uiEvents.createdAt, since));
      }

      let query = this.db.select().from(uiEvents);
      if (conditions.length > 0) {
        query = query.where(and(...conditions));
      }

      return await query.orderBy(desc(uiEvents.createdAt)).limit(limit);
    } catch (error) {
      console.error('Failed to get UI events:', error);
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

  async getCreditBalanceBySessionId(
    sessionId: string
  ): Promise<CreditBalance | undefined> {
    if (!this.db) return undefined;
    try {
      const [balance] = await this.db
        .select()
        .from(creditBalances)
        .where(eq(creditBalances.sessionId, sessionId))
        .limit(1);
      return balance;
    } catch (error: any) {
      if (error?.message?.includes('aborted transaction')) {
        console.error('❌ Critical: Database transaction aborted. Connection may be poisoned.', error);
      } else {
        console.error('Failed to get credit balance by sessionId:', error);
      }
      return undefined;
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

  async getCreditGrantByPaymentId(
    paymentId: string
  ): Promise<CreditGrant | undefined> {
    if (!this.db) return undefined;
    try {
      const [grant] = await this.db
        .select()
        .from(creditGrants)
        .where(eq(creditGrants.dodoPaymentId, paymentId))
        .orderBy(desc(creditGrants.createdAt))
        .limit(1);
      return grant;
    } catch (error) {
      // If schema isn't migrated yet, treat as unsupported.
      console.warn(
        'Credit grants not available:',
        (error as Error)?.message || error
      );
      return undefined;
    }
  }

  async transferCredits(
    fromBalanceId: string,
    toBalanceId: string,
    amount: number,
    description: string
  ): Promise<void> {
    if (!this.db) throw new Error('Database not available');
    if (!Number.isFinite(amount) || amount <= 0) {
      throw new Error('Transfer amount must be positive');
    }

    let lastOp: string | null = null;
    let hasCreditGrantsTable = true;

    // Check table existence once before transaction to avoid aborting it
    try {
      await this.db.execute(sql`SELECT 1 FROM credit_grants LIMIT 1`);
    } catch (e: any) {
      if (e?.code === '42P01') {
        hasCreditGrantsTable = false;
      }
    }

    const run = async (client: any) => {
      lastOp = `select from creditBalances (from ${fromBalanceId})`;
      const [from] = await client
        .select()
        .from(creditBalances)
        .where(eq(creditBalances.id, fromBalanceId))
        .limit(1);

      lastOp = `select from creditBalances (to ${toBalanceId})`;
      const [to] = await client
        .select()
        .from(creditBalances)
        .where(eq(creditBalances.id, toBalanceId))
        .limit(1);

      if (!from) throw new Error('Source balance not found');
      if (!to) throw new Error('Destination balance not found');
      if ((from.credits ?? 0) < amount) throw new Error('Insufficient credits');

      // Only proceed with grants if table exists
      if (hasCreditGrantsTable) {
        try {
          const remainingGrants = await client
            .select({ remaining: creditGrants.remaining })
            .from(creditGrants)
            .where(
              and(
                eq(creditGrants.balanceId, fromBalanceId),
                gt(creditGrants.remaining, 0)
              )
            );
          const remainingTotal = remainingGrants.reduce(
            (sum: number, g: any) => sum + Number(g.remaining || 0),
            0
          );
          if (remainingTotal !== amount) {
            const missing = amount - remainingTotal;
            if (missing > 0) {
              lastOp = `insert legacy credit_grant (from ${fromBalanceId} amount ${missing})`;
              await client.insert(creditGrants).values({
                balanceId: fromBalanceId,
                amount: missing,
                remaining: missing,
                description: 'Legacy credits (unattributed)',
                createdAt: new Date(0),
              });
            }
          }

          // Move grants that still have remaining credits so refund eligibility is preserved.
          lastOp = `update credit_grants set balanceId = ${toBalanceId} from ${fromBalanceId}`;
          await client
            .update(creditGrants)
            .set({ balanceId: toBalanceId })
            .where(
              and(
                eq(creditGrants.balanceId, fromBalanceId),
                gt(creditGrants.remaining, 0)
              )
            );
        } catch (error) {
          console.warn(
            '[Credits] Transfer grants failed (likely table missing):',
            error
          );
        }
      }

      lastOp = `update creditBalances subtract from ${fromBalanceId}`;
      const fromUpdate = await client
        .update(creditBalances)
        .set({
          credits: sql`${creditBalances.credits} - ${amount}`,
          updatedAt: new Date(),
        })
        .where(eq(creditBalances.id, fromBalanceId))
        .returning();
      if (fromUpdate.length === 0) throw new Error('Transfer failed');

      lastOp = `update creditBalances add to ${toBalanceId}`;
      await client
        .update(creditBalances)
        .set({
          credits: sql`${creditBalances.credits} + ${amount}`,
          updatedAt: new Date(),
        })
        .where(eq(creditBalances.id, toBalanceId));

      lastOp = `insert transfer credit_transactions from ${fromBalanceId} to ${toBalanceId} amount ${amount}`;
      await client.insert(creditTransactions).values([
        {
          balanceId: fromBalanceId,
          type: 'transfer',
          amount: -amount,
          description,
        },
        {
          balanceId: toBalanceId,
          type: 'transfer',
          amount,
          description,
        },
      ]);
    };

    try {
      const tx = (this.db as any).transaction;
      if (typeof tx === 'function') {
        await tx.call(this.db, async (client: any) => run(client));
        return;
      }
      await run(this.db);
    } catch (error) {
      const pgError = error as any;
      if (pgError?.code === '25P02') {
        if (process.env.NODE_ENV === 'test') {
          try {
            (this as any).__lastAbort = {
              op: lastOp ?? '<unknown>',
              error: pgError,
            };
          } catch (e) {
            /* ignore */
          }
        } else {
          console.warn(
            'Transaction aborted (25P02) during transferCredits; this usually means a prior statement aborted the transaction. Last operation before abort: ' +
              (lastOp ?? '<unknown>') +
              '. Check earlier ERROR logs for the root cause. If this happened during tests, run `npm run db:init-debug` to locate the failing SQL statement.',
            pgError
          );
        }
      } else {
        console.error('Failed to transfer credits:', error);
      }
      throw error;
    }
  }

  async addCredits(
    balanceId: string,
    amount: number,
    description: string,
    paymentId?: string
  ): Promise<CreditTransaction> {
    if (!this.db) throw new Error('Database not available');
    let lastOp: string | null = null;
    try {
      const creditTransactionReturning = {
        id: creditTransactions.id,
        balanceId: creditTransactions.balanceId,
        type: creditTransactions.type,
        amount: creditTransactions.amount,
        description: creditTransactions.description,
        fileType: creditTransactions.fileType,
        dodoPaymentId: creditTransactions.dodoPaymentId,
        createdAt: creditTransactions.createdAt,
      };

      // Idempotency: if we already recorded this payment for this balance, return existing tx.
      // Select only legacy-safe columns to remain compatible if DB hasn't been migrated yet.
      if (paymentId) {
        const existing = await this.db
          .select(creditTransactionReturning)
          .from(creditTransactions)
          .where(
            and(
              eq(creditTransactions.balanceId, balanceId),
              eq(creditTransactions.dodoPaymentId, paymentId),
              eq(creditTransactions.type, 'purchase')
            )
          )
          .limit(1);
        if (existing.length > 0) return existing[0];
      }

      lastOp = `update creditBalances add ${amount} to ${balanceId}`;
      await this.db
        .update(creditBalances)
        .set({
          credits: sql`${creditBalances.credits} + ${amount}`,
          updatedAt: new Date(),
        })
        .where(eq(creditBalances.id, balanceId));

      // Create a credit grant ("lot") so refunds and FIFO usage are safe.
      // If the DB schema hasn't been migrated yet, fail open to legacy behavior.
      let grantId: string | null = null;
      try {
        lastOp = `insert credit_grant (balance ${balanceId} amount ${amount})`;
        const [grant] = await this.db
          .insert(creditGrants)
          .values({
            balanceId,
            amount,
            remaining: amount,
            description,
            dodoPaymentId: paymentId,
          })
          .returning();
        grantId = grant?.id ?? null;
      } catch (error) {
        console.warn(
          '[Credits] credit_grants unavailable; falling back to legacy credits:',
          (error as Error)?.message || error
        );
      }

      try {
        lastOp = `insert credit_transaction purchase (balance ${balanceId} amount ${amount})`;
        const [tx] = await this.db
          .insert(creditTransactions)
          .values({
            balanceId,
            ...(grantId ? { grantId } : {}),
            type: 'purchase',
            amount,
            description,
            dodoPaymentId: paymentId,
          })
          .returning(creditTransactionReturning);
        return tx as any;
      } catch (error) {
        // Legacy DB may not have grant_id column. If Drizzle still generates SQL that
        // references it, fall back to a raw SQL insert that only uses legacy columns.
        const pgError = error as any;
        if (pgError?.code === '42703') {
          lastOp = `raw insert credit_transaction purchase (balance ${balanceId} amount ${amount})`;
          const result = await this.db.execute(sql`
            insert into credit_transactions
              (balance_id, type, amount, description, file_type, dodo_payment_id)
            values
              (${balanceId}, ${'purchase'}, ${amount}, ${description}, ${null}, ${paymentId ?? null})
            returning
              id,
              balance_id as "balanceId",
              type,
              amount,
              description,
              file_type as "fileType",
              dodo_payment_id as "dodoPaymentId",
              created_at as "createdAt"
          `);
          return (result.rows?.[0] ?? null) as any;
        }

        // Otherwise retry without grantId via Drizzle.
        lastOp = `insert credit_transaction purchase fallback (balance ${balanceId} amount ${amount})`;
        const [tx] = await this.db
          .insert(creditTransactions)
          .values({
            balanceId,
            type: 'purchase',
            amount,
            description,
            dodoPaymentId: paymentId,
          })
          .returning(creditTransactionReturning);
        return tx as any;
      }
    } catch (error) {
      const pgError = error as any;
      if (pgError?.code === '25P02') {
        if (process.env.NODE_ENV === 'test') {
          try {
            (this as any).__lastAbort = {
              op: lastOp ?? '<unknown>',
              error: pgError,
            };
          } catch (e) {
            /* ignore */
          }
        } else {
          console.warn(
            'Transaction aborted (25P02) during addCredits; this usually means a prior statement aborted the transaction. Last operation before abort: ' +
              (lastOp ?? '<unknown>') +
              '. Check earlier ERROR logs for the root cause. If this happened during tests, run `npm run db:init-debug` to locate the failing SQL statement.',
            pgError
          );
        }
      } else {
        console.error('Failed to add credits:', error);
      }
      throw error;
    }
  }

  async useCredits(
    balanceId: string,
    amount: number,
    description: string,
    fileType?: string
  ): Promise<CreditTransaction | null> {
    let lastOp: string | null = null;
    if (!this.db) return null;
    const creditTransactionReturning = {
      id: creditTransactions.id,
      balanceId: creditTransactions.balanceId,
      type: creditTransactions.type,
      amount: creditTransactions.amount,
      description: creditTransactions.description,
      fileType: creditTransactions.fileType,
      dodoPaymentId: creditTransactions.dodoPaymentId,
      createdAt: creditTransactions.createdAt,
    };

    let hasCreditGrantsTable = true;
    try {
      await this.db.execute(sql`SELECT 1 FROM credit_grants LIMIT 1`);
    } catch (e: any) {
      if (e?.code === '42P01') {
        hasCreditGrantsTable = false;
      }
    }

    // If credit-grants schema isn't present yet, fall back to legacy behavior.
    const legacyUse = async (
      client: any
    ): Promise<CreditTransaction | null> => {
      const updateResult = await client
        .update(creditBalances)
        .set({
          credits: sql`${creditBalances.credits} - ${amount}`,
          updatedAt: new Date(),
        })
        .where(
          sql`${eq(creditBalances.id, balanceId)} AND ${creditBalances.credits} >= ${amount}`
        )
        .returning();

      if (updateResult.length === 0) return null;

      try {
        const [tx] = await client
          .insert(creditTransactions)
          .values({
            balanceId,
            type: 'usage',
            amount: -amount,
            description,
            ...(fileType ? { fileType } : {}),
          })
          .returning(creditTransactionReturning);
        return (tx as any) ?? null;
      } catch (error) {
        const pgError = error as any;
        if (pgError?.code === '42703') {
          const result = await client.execute(sql`
            insert into credit_transactions
              (balance_id, type, amount, description, file_type, dodo_payment_id)
            values
              (${balanceId}, ${'usage'}, ${-amount}, ${description}, ${fileType ?? null}, ${null})
            returning
              id,
              balance_id as "balanceId",
              type,
              amount,
              description,
              file_type as "fileType",
              dodo_payment_id as "dodoPaymentId",
              created_at as "createdAt"
          `);
          return (result.rows?.[0] ?? null) as any;
        }
        throw error;
      }
    };

    const run = async (client: any): Promise<CreditTransaction | null> => {
      lastOp = 'update creditBalances (subtract)';
      const updateResult = await client
        .update(creditBalances)
        .set({
          credits: sql`${creditBalances.credits} - ${amount}`,
          updatedAt: new Date(),
        })
        .where(
          sql`${eq(creditBalances.id, balanceId)} AND ${creditBalances.credits} >= ${amount}`
        )
        .returning();

      if (updateResult.length === 0) return null;

      if (!hasCreditGrantsTable) {
        return legacyUse(client);
      }

      // FIFO consume from grants (oldest first). If legacy credits exist without grants,
      // synthesize a non-refundable grant so the ledger stays consistent.
      let availableGrants: CreditGrant[];
      try {
        lastOp = 'select available credit_grants';
        availableGrants = await client
          .select()
          .from(creditGrants)
          .where(
            and(
              eq(creditGrants.balanceId, balanceId),
              gt(creditGrants.remaining, 0),
              or(
                isNull(creditGrants.expiresAt),
                gt(creditGrants.expiresAt, new Date())
              )
            )
          )
          .orderBy(asc(creditGrants.createdAt), asc(creditGrants.id));
      } catch {
        // This should not happen if hasCreditGrantsTable was true, but handle anyway
        return legacyUse(client);
      }

      const grantsTotal = availableGrants.reduce(
        (sum, grant) => sum + Number(grant.remaining || 0),
        0
      );
      if (grantsTotal < amount) {
        const missing = amount - grantsTotal;
        lastOp = 'insert legacy credit_grant';
        const [legacyGrant] = await client
          .insert(creditGrants)
          .values({
            balanceId,
            amount: missing,
            remaining: missing,
            description: 'Legacy credits (unattributed)',
            createdAt: new Date(0),
          })
          .returning();
        availableGrants = [legacyGrant, ...availableGrants];
      }

      let remainingToCharge = amount;
      const usageRows: Array<{
        balanceId: string;
        grantId: string | null;
        type: string;
        amount: number;
        description: string;
        fileType?: string;
      }> = [];

      for (const grant of availableGrants) {
        if (remainingToCharge <= 0) break;
        const take = Math.min(grant.remaining, remainingToCharge);
        if (take <= 0) continue;

        lastOp = `update credit_grants set remaining -= ${take} (grant id ${grant.id})`;
        const updated = await client
          .update(creditGrants)
          .set({
            remaining: sql`${creditGrants.remaining} - ${take}`,
          })
          .where(
            sql`${eq(creditGrants.id, grant.id)} AND ${creditGrants.remaining} >= ${take}`
          )
          .returning();

        if (updated.length === 0) {
          // Concurrent modification; fail safe by aborting transaction
          throw new Error('Credit grant consumption race detected');
        }

        usageRows.push({
          balanceId,
          grantId: grant.id,
          type: 'usage',
          amount: -take,
          description,
          ...(fileType ? { fileType } : {}),
        });

        remainingToCharge -= take;
      }

      if (remainingToCharge > 0) {
        throw new Error('Credit grants insufficient for balance');
      }

      let inserted: CreditTransaction[];
      try {
        lastOp = 'insert credit_transactions usage rows';
        inserted = (await client
          .insert(creditTransactions)
          .values(usageRows)
          .returning(creditTransactionReturning)) as any;
      } catch (error) {
        const pgError = error as any;
        if (pgError?.code !== '42703') throw error;
        // Legacy DB: insert usage transactions without grant_id via raw SQL.
        const insertedRows: any[] = [];
        for (const row of usageRows) {
          lastOp = `raw insert credit_transactions (balance ${row.balanceId} amount ${row.amount})`;
          const result = await client.execute(sql`
            insert into credit_transactions
              (balance_id, type, amount, description, file_type, dodo_payment_id)
            values
              (${row.balanceId}, ${row.type}, ${row.amount}, ${row.description}, ${row.fileType ?? null}, ${null})
            returning
              id,
              balance_id as "balanceId",
              type,
              amount,
              description,
              file_type as "fileType",
              dodo_payment_id as "dodoPaymentId",
              created_at as "createdAt"
          `);
          if (result.rows?.[0]) insertedRows.push(result.rows[0]);
        }
        inserted = insertedRows as any;
      }

      // Return a representative tx (the first usage record)
      return (inserted[0] as any) ?? null;
    };

    try {
      if (typeof (this.db as any).transaction === 'function') {
        return await (this.db as any).transaction(async (client: any) =>
          run(client)
        );
      }
      return await run(this.db);
    } catch (error) {
      const pgError = error as any;
      if (pgError?.code === '25P02') {
        if (process.env.NODE_ENV === 'test') {
          try {
            (this as any).__lastAbort = {
              op: lastOp ?? '<unknown>',
              error: pgError,
            };
          } catch (e) {
            /* ignore */
          }
        } else {
          console.warn(
            'Transaction aborted (25P02) during useCredits; this usually means a prior statement aborted the transaction. Last operation before abort: ' +
              (lastOp ?? '<unknown>') +
              '. Check earlier ERROR logs for the root cause. If this happened during tests, run `npm run db:init-debug` to locate the failing SQL statement.',
            pgError
          );
        }
      } else {
        console.error('Failed to use credits:', error);
      }
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
        .select({
          id: creditTransactions.id,
          balanceId: creditTransactions.balanceId,
          type: creditTransactions.type,
          amount: creditTransactions.amount,
          description: creditTransactions.description,
          fileType: creditTransactions.fileType,
          dodoPaymentId: creditTransactions.dodoPaymentId,
          createdAt: creditTransactions.createdAt,
        })
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

  // Metadata Persistence
  async saveMetadata(data: SaveMetadataInput): Promise<StoredMetadata> {
    if (!this.db) throw new Error('Database not available');

    const recordId = generateRecordId();
    const bucket = process.env.OBJECT_STORAGE_BUCKET || 'metadata-results';

    const { summary } = buildMetadataSummary(data.metadata);
    const objectKey = buildObjectKey(recordId, data.fileName);
    const prepared = await prepareMetadataObject(data.metadata);

    let metadataRef: MetadataObjectRef | null = null;

    try {
      metadataRef = await this.objectStorage.putObject({
        bucket,
        key: objectKey,
        body: prepared.body,
        contentType: prepared.contentType,
        encoding: prepared.encoding,
      });
    } catch (error) {
      console.error('[MetadataStorage] Failed to upload metadata blob:', error);
      throw error;
    }

    try {
      const [result] = await this.db
        .insert(metadataResults)
        .values({
          id: recordId,
          userId: data.userId,
          fileName: data.fileName,
          fileSize: data.fileSize,
          mimeType: data.mimeType,
          metadataSummary: summary,
          metadataRef,
          metadataSha256: metadataRef?.sha256 ?? prepared.sha256,
          metadataSizeBytes: metadataRef?.sizeBytes ?? prepared.sizeBytes,
          metadataContentType: metadataRef?.contentType ?? prepared.contentType,
        })
        .returning();

      return {
        ...result,
        metadataSummary: summary,
        metadataRef,
      };
    } catch (error) {
      console.error('Failed to save metadata:', error);
      if (metadataRef) {
        this.objectStorage
          .deleteObject(metadataRef)
          .catch(cleanupError =>
            console.error(
              '[MetadataStorage] Failed to cleanup uploaded metadata blob after DB error:',
              cleanupError
            )
          );
      }
      throw error;
    }
  }

  async getMetadata(
    id: string
  ): Promise<(StoredMetadata & { metadata: any }) | undefined> {
    if (!this.db) return undefined;
    try {
      const [result] = await this.db
        .select()
        .from(metadataResults)
        .where(eq(metadataResults.id, id))
        .limit(1);

      if (!result) return undefined;

      const metadataRef =
        (result.metadataRef as MetadataObjectRef | null) ?? null;
      let metadataPayload: any = result.metadataSummary ?? {};

      if (metadataRef) {
        try {
          const object = await this.objectStorage.getObject(metadataRef);
          if (object?.body) {
            metadataPayload = await decompressMetadata(
              object.body,
              object.encoding || metadataRef.encoding
            );
          }
        } catch (error) {
          console.error(
            '[MetadataStorage] Failed to fetch metadata blob, falling back to summary:',
            error
          );
        }
      }

      return {
        ...result,
        metadataSummary: result.metadataSummary ?? {},
        metadataRef,
        metadata: metadataPayload,
      };
    } catch (error) {
      console.error('Failed to get metadata:', error);
      return undefined;
    }
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

  // ============================================================================
  // Batch Processing Methods
  // ============================================================================

  async getBatchJobs(userId: string): Promise<BatchJob[]> {
    try {
      const jobs = await this.db
        .selectFrom('batch_jobs')
        .selectAll()
        .where('userId', '=', userId)
        .orderBy('createdAt', 'desc')
        .execute();

      return jobs.map((job: any) => ({
        ...job,
        status: job.status as BatchJob['status'],
      }));
    } catch (error) {
      console.error('Error fetching batch jobs:', error);
      return [];
    }
  }

  async getBatchJob(jobId: string): Promise<BatchJob | undefined> {
    try {
      const job = await this.db
        .selectFrom('batch_jobs')
        .selectAll()
        .where('id', '=', jobId)
        .executeTakeFirst();

      if (!job) return undefined;

      return {
        ...job,
        status: job.status as BatchJob['status'],
      };
    } catch (error) {
      console.error('Error fetching batch job:', error);
      return undefined;
    }
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

    try {
      await this.db.insertInto('batch_jobs').values(newJob).execute();

      return newJob;
    } catch (error) {
      console.error('Error creating batch job:', error);
      throw new Error('Failed to create batch job');
    }
  }

  async updateBatchJob(
    jobId: string,
    updates: Partial<BatchJob>
  ): Promise<void> {
    try {
      await this.db
        .updateTable('batch_jobs')
        .set({
          ...updates,
          updatedAt: new Date().toISOString(),
        })
        .where('id', '=', jobId)
        .execute();
    } catch (error) {
      console.error('Error updating batch job:', error);
      throw new Error('Failed to update batch job');
    }
  }

  async getBatchResults(batchId: string): Promise<BatchResult[]> {
    try {
      const results = await this.db
        .selectFrom('batch_results')
        .selectAll()
        .where('batchId', '=', batchId)
        .orderBy('createdAt', 'desc')
        .execute();

      return results.map((result: any) => ({
        ...result,
        status: result.status as BatchResult['status'],
        metadata: result.metadata ? JSON.parse(result.metadata as string) : {},
      }));
    } catch (error) {
      console.error('Error fetching batch results:', error);
      return [];
    }
  }

  async getBatchResult(resultId: string): Promise<BatchResult | undefined> {
    try {
      const result = await this.db
        .selectFrom('batch_results')
        .selectAll()
        .where('id', '=', resultId)
        .executeTakeFirst();

      if (!result) return undefined;

      return {
        ...result,
        status: result.status as BatchResult['status'],
        metadata: result.metadata ? JSON.parse(result.metadata as string) : {},
      };
    } catch (error) {
      console.error('Error fetching batch result:', error);
      return undefined;
    }
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

    try {
      await this.db
        .insertInto('batch_results')
        .values({
          ...newResult,
          metadata: JSON.stringify(newResult.metadata),
        })
        .execute();

      return newResult;
    } catch (error) {
      console.error('Error creating batch result:', error);
      throw new Error('Failed to create batch result');
    }
  }

  async updateBatchResult(
    resultId: string,
    updates: Partial<BatchResult>
  ): Promise<void> {
    try {
      const updateData: any = { ...updates };

      // Handle metadata serialization if it's being updated
      if (updates.metadata) {
        updateData.metadata = JSON.stringify(updates.metadata);
      }

      await this.db
        .updateTable('batch_results')
        .set(updateData)
        .where('id', '=', resultId)
        .execute();
    } catch (error) {
      console.error('Error updating batch result:', error);
      throw new Error('Failed to update batch result');
    }
  }

  async deleteBatchJob(jobId: string): Promise<void> {
    try {
      // Delete associated results first
      await this.deleteBatchResults(jobId);

      // Delete the job
      await this.db.deleteFrom('batch_jobs').where('id', '=', jobId).execute();
    } catch (error) {
      console.error('Error deleting batch job:', error);
      throw new Error('Failed to delete batch job');
    }
  }

  async deleteBatchResults(batchId: string): Promise<void> {
    try {
      await this.db
        .deleteFrom('batch_results')
        .where('batchId', '=', batchId)
        .execute();
    } catch (error) {
      console.error('Error deleting batch results:', error);
      throw new Error('Failed to delete batch results');
    }
  }

  // ============================================================================
  // Images MVP Quote Storage Methods
  // ============================================================================

  async createQuote(quote: InsertImagesMvpQuote): Promise<ImagesMvpQuote> {
    try {
      const [createdQuote] = await this.db
        .insert(imagesMvpQuotes)
        .values(quote)
        .returning();
      return createdQuote;
    } catch (error) {
      console.error('Error creating quote:', error);
      throw new Error('Failed to create quote');
    }
  }

  async getQuote(id: string): Promise<ImagesMvpQuote | undefined> {
    try {
      const [quote] = await this.db
        .select()
        .from(imagesMvpQuotes)
        .where(eq(imagesMvpQuotes.id, id))
        .limit(1);
      return quote;
    } catch (error) {
      console.error('Error getting quote:', error);
      return undefined;
    }
  }

  async getQuoteBySessionId(sessionId: string): Promise<ImagesMvpQuote | undefined> {
    try {
      const [quote] = await this.db
        .select()
        .from(imagesMvpQuotes)
        .where(
          and(
            eq(imagesMvpQuotes.sessionId, sessionId),
            eq(imagesMvpQuotes.status, 'active'),
            gt(imagesMvpQuotes.expiresAt, new Date())
          )
        )
        .orderBy(desc(imagesMvpQuotes.createdAt))
        .limit(1);
      return quote;
    } catch (error) {
      console.error('Error getting quote by session ID:', error);
      return undefined;
    }
  }

  async updateQuote(id: string, updates: Partial<ImagesMvpQuote>): Promise<void> {
    try {
      await this.db
        .update(imagesMvpQuotes)
        .set({
          ...updates,
          updatedAt: new Date(),
        })
        .where(eq(imagesMvpQuotes.id, id));
    } catch (error) {
      console.error('Error updating quote:', error);
      throw new Error('Failed to update quote');
    }
  }

  async expireQuote(id: string): Promise<void> {
    try {
      await this.db
        .update(imagesMvpQuotes)
        .set({
          status: 'expired',
          updatedAt: new Date(),
        })
        .where(eq(imagesMvpQuotes.id, id));
    } catch (error) {
      console.error('Error expiring quote:', error);
      throw new Error('Failed to expire quote');
    }
  }

  async cleanupExpiredQuotes(): Promise<number> {
    try {
      const result = await this.db
        .update(imagesMvpQuotes)
        .set({
          status: 'expired',
          updatedAt: new Date(),
        })
        .where(
          and(
            eq(imagesMvpQuotes.status, 'active'),
            lt(imagesMvpQuotes.expiresAt, new Date())
          )
        );
      
      return result.rowCount || 0;
    } catch (error) {
      console.error('Error cleaning up expired quotes:', error);
      return 0;
    }
  }
}
