import {
  type User,
  type InsertUser,
  type InsertExtractionAnalytics,
  type ExtractionAnalytics,
  type CreditBalance,
  type CreditTransaction,
  type InsertUiEvent,
  type UiEvent,
  type OnboardingSession,
  type InsertOnboardingSession,
  type TrialUsage,
  type InsertTrialUsage,
  type MetadataResult,
  type InsertMetadataResult,
} from '@shared/schema';

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

export interface IStorage {
  // User system
  getUser(id: string): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;

  // Analytics system
  logExtractionUsage(data: InsertExtractionAnalytics): Promise<void>;
  getAnalyticsSummary(): Promise<AnalyticsSummary>;
  getRecentExtractions(limit?: number): Promise<ExtractionAnalytics[]>;
  logUiEvent(data: InsertUiEvent): Promise<void>;
  getUiEvents(params?: {
    product?: string;
    since?: Date;
    limit?: number;
  }): Promise<UiEvent[]>;

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

  // Metadata Persistence
  saveMetadata(data: InsertMetadataResult): Promise<MetadataResult>;
  getMetadata(id: string): Promise<MetadataResult | undefined>;
}
