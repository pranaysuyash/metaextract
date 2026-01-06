/**
 * Onboarding Types - Interfaces for the intelligent onboarding system
 */

export interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  target?: string; // CSS selector for element
  position?: 'top' | 'bottom' | 'left' | 'right' | 'center';
  action?: 'click' | 'type' | 'select' | 'wait';
  actionTarget?: string;
  prerequisite?: string[];
  skippable: boolean;
  duration?: number; // seconds
}

export interface OnboardingTutorial {
  id: string;
  name: string;
  description: string;
  uiVersion: 'original' | 'v2' | 'images-mvp';
  steps: OnboardingStep[];
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedDuration: number; // minutes
}

export interface TutorialState {
  tutorialId: string;
  currentStepIndex: number;
  status: 'idle' | 'active' | 'paused' | 'completed' | 'dismissed';
  startTime: number;
  completedSteps: Set<string>;
  skippedSteps: Set<string>;
  totalSteps: number;
}

export interface OnboardingProgress {
  userId: string;
  uiVersion: string;
  completedTutorials: string[];
  activeTutorial: TutorialState | null;
  unlockedFeatures: string[];
  totalStepsCompleted: number;
  totalStepsSkipped: number;
  lastUpdated: number;
}

export type OnboardingEvent =
  | { type: 'tutorial:started'; tutorialId: string }
  | { type: 'step:completed'; tutorialId: string; stepId: string }
  | { type: 'step:skipped'; tutorialId: string; stepId: string }
  | { type: 'tutorial:completed'; tutorialId: string; duration: number }
  | { type: 'tutorial:dismissed'; tutorialId: string }
  | { type: 'feature:unlocked'; featureId: string }
  | { type: 'help:viewed'; helpId: string }
  | { type: 'progress:updated'; progress: OnboardingProgress };

export interface IStorage {
  // User system
  getUser(id: string): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;

  // Additional user methods needed by auth system
  getUserById?(id: string): Promise<User | undefined>;
  getUserByEmail?(email: string): Promise<User | undefined>;
  updateUserPassword?(userId: string, newPassword: string): Promise<void>;
  updateUserProfile?(userId: string, profile: Partial<User>): Promise<void>;
  setPasswordResetToken?(userId: string, token: string, expiresAt: Date): Promise<void>;
  getUserByResetToken?(token: string): Promise<User | undefined>;
  resetFailedLoginAttempts?(userId: string): Promise<void>;
  enableTwoFactor?(userId: string, secret: string): Promise<void>;
  disableTwoFactor?(userId: string): Promise<void>;

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
  getCreditBalanceBySessionId(
    sessionId: string
  ): Promise<CreditBalance | undefined>;
  getCreditBalance(balanceId: string): Promise<CreditBalance | undefined>;
  getCreditGrantByPaymentId(
    paymentId: string
  ): Promise<CreditGrant | undefined>;
  addCredits(
    balanceId: string,
    amount: number,
    description: string,
    paymentId?: string
  ): Promise<CreditTransaction>;
  transferCredits(
    fromBalanceId: string,
    toBalanceId: string,
    amount: number,
    description: string
  ): Promise<void>;
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
  saveMetadata(data: SaveMetadataInput): Promise<StoredMetadata>;
  getMetadata(
    id: string
  ): Promise<(StoredMetadata & { metadata: any }) | undefined>;

  // Additional methods that may be needed by various systems (optional for backward compatibility)
  getExtractionHistoryByUser?(userId: string, limit?: number): Promise<any[]>;
  anonymizeUserData?(userId: string): Promise<void>;
  incrementFailedLoginAttempts?(userId: string): Promise<void>;
  setTwoFactorSecret?(userId: string, secret: string): Promise<void>;
  clearTwoFactorSecret?(userId: string): Promise<void>;
  getExtractionHistoryByFile?(fileId: string): Promise<any[]>;
  getExtractionHistoryByDateRange?(startDate: Date, endDate: Date): Promise<any[]>;
  getExtractionHistoryByTier?(tier: string): Promise<any[]>;
  getExtractionHistoryByFileType?(fileType: string): Promise<any[]>;
  updatePassword?(userId: string, hashedPassword: string): Promise<void>;

  // Storage-specific methods for caching
  get?(key: string): Promise<any>;
  set?(key: string, value: any): Promise<void>;
  incr?(key: string): Promise<number>;
  expire?(key: string, seconds: number): Promise<void>;
  lpush?(key: string, ...values: any[]): Promise<number>;
  ltrim?(key: string, start: number, stop: number): Promise<void>;
  lrange?(key: string, start: number, stop: number): Promise<any[]>;

  // Additional storage methods that may be referenced
  getUserById?(id: string): Promise<User | undefined>;
  getUserByCustomerId?(customerId: string): Promise<User | undefined>;
  updateUserSubscription?(userId: string, subscriptionId: string, status: string): Promise<void>;
  updateUserTier?(userId: string, tier: string): Promise<void>;
  getExtractionHistoryByUser?(userId: string, limit?: number): Promise<any[]>;
  getExtractionHistoryByFileId?(fileId: string): Promise<any[]>;
  getExtractionHistoryByDateRange?(startDate: Date, endDate: Date): Promise<any[]>;
  getExtractionHistoryBySuccess?(success: boolean): Promise<any[]>;
  getExtractionHistoryByProcessingTime?(minTime: number, maxTime: number): Promise<any[]>;
  getExtractionHistoryByFileSize?(minSize: number, maxSize: number): Promise<any[]>;
  getExtractionHistoryByFieldsExtracted?(minFields: number, maxFields: number): Promise<any[]>;
  getExtractionHistoryByFailureReason?(reason: string): Promise<any[]>;
  getExtractionHistoryByIpAddress?(ipAddress: string): Promise<any[]>;
  getExtractionHistoryByUserAgentString?(userAgent: string): Promise<any[]>;
  getExtractionHistoryByRequestedAt?(date: Date): Promise<any[]>;
  getExtractionHistoryByCreatedAt?(date: Date): Promise<any[]>;
  getExtractionHistoryByUpdatedAt?(date: Date): Promise<any[]>;
  getExtractionHistoryByTierAndDateRange?(tier: string, startDate: Date, endDate: Date): Promise<any[]>;
  getExtractionHistoryByFileTypeAndDateRange?(fileType: string, startDate: Date, endDate: Date): Promise<any[]>;
  getExtractionHistoryBySuccessAndDateRange?(success: boolean, startDate: Date, endDate: Date): Promise<any[]>;
  getExtractionHistoryByProcessingTimeRange?(minTime: number, maxTime: number, startDate: Date, endDate: Date): Promise<any[]>;
  getExtractionHistoryByFileSizeRange?(minSize: number, maxSize: number, startDate: Date, endDate: Date): Promise<any[]>;
  getExtractionHistoryByFieldsExtractedRange?(minFields: number, maxFields: number, startDate: Date, endDate: Date): Promise<any[]>;
  getExtractionHistoryByFailureReasonAndDateRange?(reason: string, startDate: Date, endDate: Date): Promise<any[]>;
  getExtractionHistoryByIpAddressAndDateRange?(ipAddress: string, startDate: Date, endDate: Date): Promise<any[]>;
  getExtractionHistoryByUserAgentStringAndDateRange?(userAgent: string, startDate: Date, endDate: Date): Promise<any[]>;
  getExtractionHistoryByRequestedAtRange?(startDate: Date, endDate: Date): Promise<any[]>;
  getExtractionHistoryByCreatedAtRange?(startDate: Date, endDate: Date): Promise<any[]>;
  getExtractionHistoryByUpdatedAtRange?(startDate: Date, endDate: Date): Promise<any[]>;
  getExtractionHistoryByUserIdAndDateRange?(userId: string, startDate: Date, endDate: Date): Promise<any[]>;
  getExtractionHistoryByFileIdAndDateRange?(fileId: string, startDate: Date, endDate: Date): Promise<any[]>;
  getExtractionHistoryByTierAndUser?(tier: string, userId: string): Promise<any[]>;
  getExtractionHistoryByFileTypeAndUser?(fileType: string, userId: string): Promise<any[]>;
  getExtractionHistoryBySuccessAndUser?(success: boolean, userId: string): Promise<any[]>;
  getExtractionHistoryByProcessingTimeAndUser?(minTime: number, maxTime: number, userId: string): Promise<any[]>;
  getExtractionHistoryByFileSizeAndUser?(minSize: number, maxSize: number, userId: string): Promise<any[]>;
  getExtractionHistoryByFieldsExtractedAndUser?(minFields: number, maxFields: number, userId: string): Promise<any[]>;
  getExtractionHistoryByFailureReasonAndUser?(reason: string, userId: string): Promise<any[]>;
  getExtractionHistoryByIpAddressAndUser?(ipAddress: string, userId: string): Promise<any[]>;
  getExtractionHistoryByUserAgentStringAndUser?(userAgent: string, userId: string): Promise<any[]>;
  getExtractionHistoryByRequestedAtAndUser?(date: Date, userId: string): Promise<any[]>;
  getExtractionHistoryByCreatedAtAndUser?(date: Date, userId: string): Promise<any[]>;
  getExtractionHistoryByUpdatedAtAndUser?(date: Date, userId: string): Promise<any[]>;
  getExtractionHistoryByTierAndFile?(tier: string, fileId: string): Promise<any[]>;
  getExtractionHistoryByFileTypeAndFile?(fileType: string, fileId: string): Promise<any[]>;
  getExtractionHistoryBySuccessAndFile?(success: boolean, fileId: string): Promise<any[]>;
  getExtractionHistoryByProcessingTimeAndFile?(minTime: number, maxTime: number, fileId: string): Promise<any[]>;
  getExtractionHistoryByFileSizeAndFile?(minSize: number, maxSize: number, fileId: string): Promise<any[]>;
  getExtractionHistoryByFieldsExtractedAndFile?(minFields: number, maxFields: number, fileId: string): Promise<any[]>;
  getExtractionHistoryByFailureReasonAndFile?(reason: string, fileId: string): Promise<any[]>;
  getExtractionHistoryByIpAddressAndFile?(ipAddress: string, fileId: string): Promise<any[]>;
  getExtractionHistoryByUserAgentStringAndFile?(userAgent: string, fileId: string): Promise<any[]>;
  getExtractionHistoryByRequestedAtAndFile?(date: Date, fileId: string): Promise<any[]>;
  getExtractionHistoryByCreatedAtAndFile?(date: Date, fileId: string): Promise<any[]>;
  getExtractionHistoryByUpdatedAtAndFile?(date: Date, fileId: string): Promise<any[]>;
}

export interface MetadataObjectRef extends ObjectInfo {}

export interface SaveMetadataInput {
  userId?: string;
  fileName: string;
  fileSize?: string;
  mimeType?: string;
  metadata: any; // Full blob to persist
}

export interface StoredMetadata extends MetadataResult {
  metadataSummary: Record<string, unknown>;
  metadataRef: MetadataObjectRef | null;
}

// Missing types that were referenced
export interface User {
  id: string;
  email: string;
  password: string;
  username: string;
  tier: string;
  subscriptionId: string | null;
  subscriptionStatus: string | null;
  customerId: string | null;
  createdAt: Date;
  updatedAt?: Date;
  firstName?: string;
  lastName?: string;
  emailVerified?: boolean;
  twoFactorEnabled?: boolean;
  failedLoginAttempts?: number;
  lastFailedLoginAttempt?: Date;
  twoFactorSecret?: string;
}

export interface InsertUser {
  email: string;
  password: string;
  username: string;
  firstName?: string;
  lastName?: string;
  tier?: string;
  subscriptionId?: string | null;
  subscriptionStatus?: string | null;
  customerId?: string | null;
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

export interface InsertExtractionAnalytics {
  tier: string;
  fileExtension: string;
  mimeType: string;
  fileSizeBytes: number;
  isVideo: boolean;
  isImage: boolean;
  isPdf: boolean;
  isAudio: boolean;
  fieldsExtracted: number;
  processingMs: number;
  success: boolean;
  failureReason?: string;
  ipAddress?: string;
  userAgent?: string;
}

export interface ExtractionAnalytics {
  id: string;
  tier: string;
  fileExtension: string;
  mimeType: string;
  fileSizeBytes: number;
  isVideo: boolean;
  isImage: boolean;
  isPdf: boolean;
  isAudio: boolean;
  fieldsExtracted: number;
  processingMs: number;
  success: boolean;
  failureReason?: string;
  ipAddress?: string;
  userAgent?: string;
  requestedAt: Date;
}

export interface CreditBalance {
  id: string;
  userId: string | null;
  sessionId: string;
  credits: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreditGrant {
  id: string;
  balanceId: string;
  amount: number;
  remaining: number;
  description?: string;
  pack?: string;
  dodoPaymentId?: string;
  createdAt: Date;
  expiresAt?: Date;
}

export interface CreditTransaction {
  id: string;
  balanceId: string;
  grantId?: string;
  type: string; // 'purchase', 'usage', 'refund'
  amount: number;
  description?: string;
  fileType?: string;
  dodoPaymentId?: string;
  createdAt: Date;
}

export interface InsertUiEvent {
  product: string;
  eventName: string;
  sessionId?: string;
  userId?: string;
  properties: any;
  ipAddress?: string;
  userAgent?: string;
}

export interface UiEvent {
  id: string;
  product: string;
  eventName: string;
  sessionId?: string;
  userId?: string;
  properties: any;
  ipAddress?: string;
  userAgent?: string;
  createdAt: Date;
}

export interface OnboardingSession {
  id: string;
  userId: string;
  startedAt: Date;
  completedAt?: Date;
  currentStep: number;
  pathId: string;
  userProfile: string; // JSON string
  progress: string; // JSON string
  interactions: string; // JSON array
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface InsertOnboardingSession {
  userId?: string;
  startedAt?: Date;
  completedAt?: Date;
  currentStep?: number;
  pathId: string;
  userProfile: string; // JSON string
  progress: string; // JSON string
  interactions?: string; // JSON array
  isActive?: boolean;
}

export interface TrialUsage {
  id: string;
  email: string;
  uses: number;
  usedAt: Date;
  ipAddress?: string;
  userAgent?: string;
  sessionId?: string;
}

export interface InsertTrialUsage {
  email: string;
  ipAddress?: string;
  userAgent?: string;
  sessionId?: string;
}

export interface MetadataResult {
  id: string;
  userId: string | null;
  fileName: string;
  fileSize?: string;
  mimeType?: string;
  metadataSummary: Record<string, unknown>;
  metadataRef: any | null;
  metadataSha256?: string;
  metadataSizeBytes?: number;
  metadataContentType?: string;
  createdAt: Date;
}

export interface SaveMetadataInput {
  userId?: string;
  fileName: string;
  fileSize?: string;
  mimeType?: string;
  metadata: any;
}

export interface ObjectInfo {
  provider: string;
  bucket: string;
  key: string;
  sizeBytes: number;
  sha256: string;
  contentType?: string;
  encoding?: string;
  createdAt?: string;
}