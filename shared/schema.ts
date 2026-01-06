import { sql } from 'drizzle-orm';
import {
  pgTable,
  text,
  varchar,
  integer,
  boolean,
  timestamp,
  bigint,
  jsonb,
} from 'drizzle-orm/pg-core';
import { createInsertSchema } from 'drizzle-zod';
import { z } from 'zod';

export const users = pgTable('users', {
  id: varchar('id')
    .primaryKey()
    .default(sql`gen_random_uuid()`),
  username: text('username').notNull().unique(),
  email: text('email').notNull().unique(),
  password: text('password').notNull(),
  tier: text('tier').notNull().default('free'),
  subscriptionId: text('subscription_id'),
  subscriptionStatus: text('subscription_status').default('none'),
  customerId: text('customer_id'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
});

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  email: true,
  password: true,
});

export const subscriptions = pgTable('subscriptions', {
  id: varchar('id')
    .primaryKey()
    .default(sql`gen_random_uuid()`),
  userId: varchar('user_id')
    .notNull()
    .references(() => users.id),
  dodoSubscriptionId: text('dodo_subscription_id').notNull().unique(),
  dodoCustomerId: text('dodo_customer_id').notNull(),
  tier: text('tier').notNull(),
  status: text('status').notNull().default('pending'),
  currentPeriodStart: timestamp('current_period_start'),
  currentPeriodEnd: timestamp('current_period_end'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
});

export const insertSubscriptionSchema = createInsertSchema(subscriptions).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export type InsertSubscription = z.infer<typeof insertSubscriptionSchema>;
export type Subscription = typeof subscriptions.$inferSelect;

export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;

export const extractionAnalytics = pgTable('extraction_analytics', {
  id: varchar('id')
    .primaryKey()
    .default(sql`gen_random_uuid()`),
  tier: text('tier').notNull().default('free'),
  fileExtension: text('file_extension').notNull(),
  mimeType: text('mime_type').notNull(),
  fileSizeBytes: bigint('file_size_bytes', { mode: 'number' }).notNull(),
  isVideo: boolean('is_video').notNull().default(false),
  isImage: boolean('is_image').notNull().default(false),
  isPdf: boolean('is_pdf').notNull().default(false),
  isAudio: boolean('is_audio').notNull().default(false),
  fieldsExtracted: integer('fields_extracted').notNull().default(0),
  processingMs: integer('processing_ms').notNull().default(0),
  success: boolean('success').notNull().default(true),
  failureReason: text('failure_reason'),
  ipAddress: text('ip_address'),
  userAgent: text('user_agent'),
  requestedAt: timestamp('requested_at').notNull().defaultNow(),
});

export const insertExtractionAnalyticsSchema = createInsertSchema(
  extractionAnalytics
).omit({
  id: true,
  requestedAt: true,
});

export type InsertExtractionAnalytics = z.infer<
  typeof insertExtractionAnalyticsSchema
>;
export type ExtractionAnalytics = typeof extractionAnalytics.$inferSelect;

// =====================================================================
// UI / Product Analytics Events
// =====================================================================

export const uiEvents = pgTable('ui_events', {
  id: varchar('id')
    .primaryKey()
    .default(sql`gen_random_uuid()`),
  product: text('product').notNull().default('core'),
  eventName: text('event_name').notNull(),
  sessionId: text('session_id'),
  userId: varchar('user_id').references(() => users.id),
  properties: jsonb('properties')
    .notNull()
    .default(sql`'{}'::jsonb`),
  ipAddress: text('ip_address'),
  userAgent: text('user_agent'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
});

export const insertUiEventSchema = createInsertSchema(uiEvents).omit({
  id: true,
  createdAt: true,
});

export type InsertUiEvent = z.infer<typeof insertUiEventSchema>;
export type UiEvent = typeof uiEvents.$inferSelect;

// Credits system for pay-as-you-go
export const creditBalances = pgTable('credit_balances', {
  id: varchar('id')
    .primaryKey()
    .default(sql`gen_random_uuid()`),
  userId: varchar('user_id').references(() => users.id),
  sessionId: text('session_id'),
  credits: integer('credits').notNull().default(0),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
});

// Credit grants ("lots") for safe refunding and FIFO consumption
export const creditGrants = pgTable('credit_grants', {
  id: varchar('id')
    .primaryKey()
    .default(sql`gen_random_uuid()`),
  balanceId: varchar('balance_id')
    .notNull()
    .references(() => creditBalances.id),
  amount: integer('amount').notNull(),
  remaining: integer('remaining').notNull(),
  description: text('description'),
  pack: text('pack'),
  dodoPaymentId: text('dodo_payment_id'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  expiresAt: timestamp('expires_at'),
});

export const creditTransactions = pgTable('credit_transactions', {
  id: varchar('id')
    .primaryKey()
    .default(sql`gen_random_uuid()`),
  balanceId: varchar('balance_id')
    .notNull()
    .references(() => creditBalances.id),
  grantId: varchar('grant_id').references(() => creditGrants.id),
  type: text('type').notNull(), // 'purchase', 'usage', 'refund'
  amount: integer('amount').notNull(), // positive for purchase/refund, negative for usage
  description: text('description'),
  fileType: text('file_type'),
  dodoPaymentId: text('dodo_payment_id'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
});

export const insertCreditBalanceSchema = createInsertSchema(
  creditBalances
).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export const insertCreditTransactionSchema = createInsertSchema(
  creditTransactions
).omit({
  id: true,
  createdAt: true,
});

export type InsertCreditBalance = z.infer<typeof insertCreditBalanceSchema>;
export type CreditBalance = typeof creditBalances.$inferSelect;
export type CreditGrant = typeof creditGrants.$inferSelect;
export type InsertCreditTransaction = z.infer<
  typeof insertCreditTransactionSchema
>;
export type CreditTransaction = typeof creditTransactions.$inferSelect;

// ============================================================================
// Metadata Storage Schema (Phase 1: Foundation)
// ============================================================================

export const metadataResults = pgTable('metadata_results', {
  id: varchar('id')
    .primaryKey()
    .default(sql`gen_random_uuid()`),
  userId: varchar('user_id').references(() => users.id),
  fileName: text('file_name').notNull(),
  fileSize: text('file_size'),
  mimeType: text('mime_type'),
  metadataSummary: jsonb('metadata_summary')
    .notNull()
    .default(sql`'{}'::jsonb`), // Capped summary for search/indexing
  metadataRef: jsonb('metadata_ref'), // Pointer to full blob in object storage
  metadataSha256: text('metadata_sha256'),
  metadataSizeBytes: bigint('metadata_size_bytes', { mode: 'number' }),
  metadataContentType: text('metadata_content_type'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
});

export const insertMetadataResultSchema = createInsertSchema(
  metadataResults
).omit({
  id: true,
  createdAt: true,
});

export type InsertMetadataResult = z.infer<typeof insertMetadataResultSchema>;
export type MetadataResult = typeof metadataResults.$inferSelect;
export type MetadataRef = {
  provider: string;
  bucket: string;
  key: string;
  sizeBytes: number;
  sha256: string;
  contentType?: string | null;
  encoding?: string | null;
  createdAt?: string | null;
};

// ============================================================================
// Extraction Jobs Schema (Async Processing)
// ============================================================================

export const extractionJobs = pgTable('extraction_jobs', {
  id: varchar('id')
    .primaryKey()
    .default(sql`gen_random_uuid()`),
  sessionId: varchar('session_id'),
  userId: varchar('user_id').references(() => users.id),
  fileName: text('file_name').notNull(),
  fileSize: bigint('file_size', { mode: 'number' }),
  mimeType: text('mime_type'),
  status: varchar('status', { length: 20 }).notNull().default('pending'), // pending, processing, complete, failed
  progress: integer('progress').notNull().default(0), // 0-100
  progressMessage: text('progress_message'),
  resultId: varchar('result_id').references(() => metadataResults.id), // Link to result when complete
  error: text('error'), // Error message if failed
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  completedAt: timestamp('completed_at'),
});

export const insertExtractionJobSchema = createInsertSchema(extractionJobs).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export type InsertExtractionJob = z.infer<typeof insertExtractionJobSchema>;
export type ExtractionJob = typeof extractionJobs.$inferSelect;

// ============================================================================
// Onboarding System Schema
// ============================================================================

export const onboardingSessions = pgTable('onboarding_sessions', {
  id: varchar('id')
    .primaryKey()
    .default(sql`gen_random_uuid()`),
  userId: varchar('user_id').references(() => users.id),
  startedAt: timestamp('started_at').notNull().defaultNow(),
  completedAt: timestamp('completed_at'),
  currentStep: integer('current_step').notNull().default(0),
  pathId: text('path_id').notNull(),
  userProfile: text('user_profile').notNull(), // JSON string
  progress: text('progress').notNull(), // JSON string
  interactions: text('interactions').notNull().default('[]'), // JSON array
  isActive: boolean('is_active').notNull().default(true),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
});

export const insertOnboardingSessionSchema = createInsertSchema(
  onboardingSessions
).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export type InsertOnboardingSession = z.infer<
  typeof insertOnboardingSessionSchema
>;
export type OnboardingSession = typeof onboardingSessions.$inferSelect;

// ============================================================================
// Trial Usage Tracking Schema
// ============================================================================

export const trialUsages = pgTable('trial_usages', {
  id: varchar('id')
    .primaryKey()
    .default(sql`gen_random_uuid()`),
  email: text('email').notNull().unique(),
  uses: integer('uses').notNull().default(1),
  usedAt: timestamp('used_at').notNull().defaultNow(),
  ipAddress: text('ip_address'),
  userAgent: text('user_agent'),
  sessionId: text('session_id'),
});

export const insertTrialUsageSchema = createInsertSchema(trialUsages).omit({
  id: true,
  usedAt: true,
  uses: true,
});

export type InsertTrialUsage = z.infer<typeof insertTrialUsageSchema>;
export type TrialUsage = typeof trialUsages.$inferSelect;

// Persona Interpretation Types
export interface PersonaInterpretation {
  persona: string;
  key_findings: string[];
  plain_english_answers: {
    when_taken: {
      answer: string;
      details: string;
      source: string;
      confidence: string;
    };
    location: {
      has_location: boolean;
      answer: string;
      details: string;
      confidence: string;
      coordinates?: {
        latitude: number;
        longitude: number;
        formatted: string;
      };
      readable_location?: string;
      possible_reasons?: string[];
    };
    device: {
      answer: string;
      device_type: string;
      details: {
        make: string | null;
        model: string | null;
        software: string | null;
      };
      confidence: string;
    };
    authenticity: {
      assessment: string;
      confidence: string;
      score: number;
      answer: string;
      checks_performed: Record<string, any>;
      reasons: string[];
    };
  };
  confidence_scores: Record<string, any>;
  warnings: string[];
  recommendations: string[];
}

// ============================================================================
// Free Quota Tracking Schema
// ============================================================================

export const clientUsage = pgTable('client_usage', {
  id: varchar('id')
    .primaryKey()
    .default(sql`gen_random_uuid()`),
  clientId: varchar('client_id').notNull().unique(),
  freeUsed: integer('free_used').notNull().default(0),
  lastIp: text('last_ip'),
  lastUserAgent: text('last_user_agent'),
  fingerprintHash: varchar('fingerprint_hash', { length: 64 }),
  abuseScore: text('abuse_score').default('0.00'),
  firstSeen: timestamp('first_seen').notNull().defaultNow(),
  lastUsed: timestamp('last_used').notNull().defaultNow(),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
});

export const insertClientUsageSchema = createInsertSchema(clientUsage).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export type InsertClientUsage = z.infer<typeof insertClientUsageSchema>;
export type ClientUsage = typeof clientUsage.$inferSelect;

// ============================================================================
// Client Activity Tracking (Abuse Detection - Tier 2 & 3)
// Best Practice: Serial ID for high-throughput append-only tables
// ============================================================================

export const clientActivity = pgTable('client_activity', {
  id: varchar('id')
    .primaryKey()
    .default(sql`gen_random_uuid()`),
  clientId: varchar('client_id', { length: 36 }).notNull(),
  ip: text('ip'),
  userAgent: text('user_agent'),
  fingerprintHash: varchar('fingerprint_hash', { length: 64 }),
  action: varchar('action', { length: 50 }).notNull(), // 'request', 'quota_hit', 'new_token', etc.
  abuseScore: text('abuse_score').default('0.00'),
  timestamp: timestamp('timestamp').notNull().defaultNow(),
  createdAt: timestamp('created_at').notNull().defaultNow(),
});

export const insertClientActivitySchema = createInsertSchema(clientActivity).omit({
  id: true,
  createdAt: true,
});

export type InsertClientActivity = z.infer<typeof insertClientActivitySchema>;
export type ClientActivity = typeof clientActivity.$inferSelect;

// ============================================================================
// IP Rate Limiting (Tier 2)
// ============================================================================

export const ipRateLimits = pgTable('ip_rate_limits', {
  id: varchar('id')
    .primaryKey()
    .default(sql`gen_random_uuid()`),
  ip: text('ip').notNull().unique(),
  dailyCount: integer('daily_count').notNull().default(0),
  minuteCount: integer('minute_count').notNull().default(0),
  lastReset: timestamp('last_reset').notNull().defaultNow(),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
});

export const insertIpRateLimitSchema = createInsertSchema(ipRateLimits).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export type InsertIpRateLimit = z.infer<typeof insertIpRateLimitSchema>;
export type IpRateLimit = typeof ipRateLimits.$inferSelect;

// ============================================================================
// Abuse Pattern Tracking (Tier 3 - Advanced Detection)
// ============================================================================

export const abusePatterns = pgTable('abuse_patterns', {
  id: varchar('id')
    .primaryKey()
    .default(sql`gen_random_uuid()`),
  patternType: varchar('pattern_type', { length: 50 }).notNull(), // 'multiple_clients_same_ip', 'high_velocity', etc.
  targetType: varchar('target_type', { length: 50 }).notNull(), // 'ip', 'fingerprint', 'client_id'
  targetValue: text('target_value').notNull(),
  abuseScore: text('abuse_score').notNull(),
  evidence: jsonb('evidence'),
  isActive: boolean('is_active').notNull().default(true),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  expiresAt: timestamp('expires_at').default(sql`NOW() + INTERVAL '24 hours'`),
});

export const insertAbusePatternSchema = createInsertSchema(abusePatterns).omit({
  id: true,
  createdAt: true,
});

export type InsertAbusePattern = z.infer<typeof insertAbusePatternSchema>;
export type AbusePattern = typeof abusePatterns.$inferSelect;

// ============================================================================
// Quota Analytics Summary (Monitoring & Reporting)
// ============================================================================

export const quotaAnalytics = pgTable('quota_analytics', {
  id: varchar('id')
    .primaryKey()
    .default(sql`gen_random_uuid()`),
  date: timestamp('date').notNull().default(sql`CURRENT_DATE`),
  totalRequests: integer('total_requests').notNull().default(0),
  freeRequests: integer('free_requests').notNull().default(0),
  paidRequests: integer('paid_requests').notNull().default(0),
  quotaHits: integer('quota_hits').notNull().default(0),
  uniqueClients: integer('unique_clients').notNull().default(0),
  uniqueIps: integer('unique_ips').notNull().default(0),
  abuseScoreAvg: text('abuse_score_avg').default('0.00'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
});

export const insertQuotaAnalyticsSchema = createInsertSchema(quotaAnalytics).omit({
  id: true,
  createdAt: true,
});

export type InsertQuotaAnalytics = z.infer<typeof insertQuotaAnalyticsSchema>;
export type QuotaAnalytics = typeof quotaAnalytics.$inferSelect;

// ============================================================================
// Batch Processing Schema (Phase 3.2)
// ============================================================================

export const batchJobs = pgTable('batch_jobs', {
  id: varchar('id')
    .primaryKey()
    .default(sql`gen_random_uuid()`),
  userId: varchar('user_id')
    .notNull()
    .references(() => users.id),
  name: text('name').notNull(),
  status: text('status')
    .notNull()
    .default('pending')
    .$type<'pending' | 'processing' | 'completed' | 'failed'>(),
  totalFiles: integer('total_files').notNull().default(0),
  processedFiles: integer('processed_files').notNull().default(0),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  completedAt: timestamp('completed_at'),
  errorMessage: text('error_message'),
});

export const batchResults = pgTable('batch_results', {
  id: varchar('id')
    .primaryKey()
    .default(sql`gen_random_uuid()`),
  batchId: varchar('batch_id')
    .notNull()
    .references(() => batchJobs.id),
  filename: text('filename').notNull(),
  status: text('status')
    .notNull()
    .default('pending')
    .$type<'success' | 'error' | 'processing' | 'pending'>(),
  extractionDate: timestamp('extraction_date').notNull().defaultNow(),
  fieldsExtracted: integer('fields_extracted').notNull().default(0),
  fileSize: bigint('file_size', { mode: 'number' }).notNull(),
  fileType: text('file_type').notNull(),
  authenticityScore: integer('authenticity_score'),
  metadata: jsonb('metadata').notNull().default(sql`'{}'::jsonb`),
  processingTime: integer('processing_time'),
  errorMessage: text('error_message'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
});

export const insertBatchJobSchema = createInsertSchema(batchJobs).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export const insertBatchResultSchema = createInsertSchema(batchResults).omit({
  id: true,
  createdAt: true,
});

export type InsertBatchJob = z.infer<typeof insertBatchJobSchema>;
export type BatchJob = typeof batchJobs.$inferSelect;
export type InsertBatchResult = z.infer<typeof insertBatchResultSchema>;
export type BatchResult = typeof batchResults.$inferSelect;
