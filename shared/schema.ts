import { sql } from "drizzle-orm";
import { pgTable, text, varchar, integer, boolean, timestamp, bigint } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const users = pgTable("users", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  username: text("username").notNull().unique(),
  email: text("email").notNull().unique(),
  password: text("password").notNull(),
  tier: text("tier").notNull().default("enterprise"),
  subscriptionId: text("subscription_id"),
  subscriptionStatus: text("subscription_status").default("none"),
  customerId: text("customer_id"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  email: true,
  password: true,
});

export const subscriptions = pgTable("subscriptions", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  userId: varchar("user_id").notNull().references(() => users.id),
  dodoSubscriptionId: text("dodo_subscription_id").notNull().unique(),
  dodoCustomerId: text("dodo_customer_id").notNull(),
  tier: text("tier").notNull(),
  status: text("status").notNull().default("pending"),
  currentPeriodStart: timestamp("current_period_start"),
  currentPeriodEnd: timestamp("current_period_end"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
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

export const extractionAnalytics = pgTable("extraction_analytics", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  tier: text("tier").notNull().default("enterprise"),
  fileExtension: text("file_extension").notNull(),
  mimeType: text("mime_type").notNull(),
  fileSizeBytes: bigint("file_size_bytes", { mode: "number" }).notNull(),
  isVideo: boolean("is_video").notNull().default(false),
  isImage: boolean("is_image").notNull().default(false),
  isPdf: boolean("is_pdf").notNull().default(false),
  isAudio: boolean("is_audio").notNull().default(false),
  fieldsExtracted: integer("fields_extracted").notNull().default(0),
  processingMs: integer("processing_ms").notNull().default(0),
  success: boolean("success").notNull().default(true),
  failureReason: text("failure_reason"),
  ipAddress: text("ip_address"),
  userAgent: text("user_agent"),
  requestedAt: timestamp("requested_at").notNull().defaultNow(),
});

export const insertExtractionAnalyticsSchema = createInsertSchema(extractionAnalytics).omit({
  id: true,
  requestedAt: true,
});

export type InsertExtractionAnalytics = z.infer<typeof insertExtractionAnalyticsSchema>;
export type ExtractionAnalytics = typeof extractionAnalytics.$inferSelect;

// Credits system for pay-as-you-go
export const creditBalances = pgTable("credit_balances", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  userId: varchar("user_id").references(() => users.id),
  sessionId: text("session_id"),
  credits: integer("credits").notNull().default(0),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const creditTransactions = pgTable("credit_transactions", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  balanceId: varchar("balance_id").notNull().references(() => creditBalances.id),
  type: text("type").notNull(), // 'purchase', 'usage', 'refund'
  amount: integer("amount").notNull(), // positive for purchase/refund, negative for usage
  description: text("description"),
  fileType: text("file_type"),
  dodoPaymentId: text("dodo_payment_id"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export const insertCreditBalanceSchema = createInsertSchema(creditBalances).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export const insertCreditTransactionSchema = createInsertSchema(creditTransactions).omit({
  id: true,
  createdAt: true,
});

export type InsertCreditBalance = z.infer<typeof insertCreditBalanceSchema>;
export type CreditBalance = typeof creditBalances.$inferSelect;
export type InsertCreditTransaction = z.infer<typeof insertCreditTransactionSchema>;
export type CreditTransaction = typeof creditTransactions.$inferSelect;

// ============================================================================
// Metadata Storage Schema (Phase 1: Foundation)
// ============================================================================

// ============================================================================
// Onboarding System Schema
// ============================================================================

export const onboardingSessions = pgTable("onboarding_sessions", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  userId: varchar("user_id").references(() => users.id),
  startedAt: timestamp("started_at").notNull().defaultNow(),
  completedAt: timestamp("completed_at"),
  currentStep: integer("current_step").notNull().default(0),
  pathId: text("path_id").notNull(),
  userProfile: text("user_profile").notNull(), // JSON string
  progress: text("progress").notNull(), // JSON string
  interactions: text("interactions").notNull().default("[]"), // JSON array
  isActive: boolean("is_active").notNull().default(true),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const insertOnboardingSessionSchema = createInsertSchema(onboardingSessions).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export type InsertOnboardingSession = z.infer<typeof insertOnboardingSessionSchema>;
export type OnboardingSession = typeof onboardingSessions.$inferSelect;

// ============================================================================
// Trial Usage Tracking Schema
// ============================================================================

export const trialUsages = pgTable("trial_usages", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  email: text("email").notNull().unique(),
  usedAt: timestamp("used_at").notNull().defaultNow(),
  ipAddress: text("ip_address"),
  userAgent: text("user_agent"),
  sessionId: text("session_id"),
});

export const insertTrialUsageSchema = createInsertSchema(trialUsages).omit({
  id: true,
  usedAt: true,
});

export type InsertTrialUsage = z.infer<typeof insertTrialUsageSchema>;
export type TrialUsage = typeof trialUsages.$inferSelect;
