# Free Tier Abuse-Resistant Implementation Roadmap

**Status:** Design Complete, Implementation Pending
**Last Updated:** January 7, 2026
**Goal:** Implement progressive friction that makes "sign up" easier than "abuse"

---

## Philosophy

### The Free Tier Paradox

"I want virality and trust, but I don't want to subsidize attackers or power users."

**Solution:**

- Free tier = **demo that still feels real**
- Real usage = requires **identity or payment**
- System must **shed load gracefully** (no bill shock)

### Attacker Economics

We win when: **Abusing free tier > "Sign up for Google" (30 seconds)**
We lose when: **Legit users feel arbitrary denial**

### Core Principles

1. **No global caps** - Breaks for legit users, doesn't stop determined attackers
2. **Progressive friction** - 2 free → challenge → email → paid
3. **Cost-based budgeting** - Heavy files = more credits
4. **Graceful degradation** - Queue delays, not hard blocks
5. **Server-controlled identity** - Not client cookies

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT                                  │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────┐   │
│  │ Anonymous │───▶│ Challenge   │───▶│ Email/OAuth   │   │
│  │ 2 credits │    │  +3 credits │    │  +10-20 creds  │   │
│  └──────────┘    └──────────────┘    └───────────────┘   │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        SERVER                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           Identity Verification Ladder                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────┐  │
│  │  Device      │    │  Fingerprint │    │   Behavior   │  │
│  │  Token      │───▶│   Signal     │───▶│   Score     │  │
│  │  (primary)  │    │  (risk)     │    │  (velocity)  │  │
│  └──────────────┘    └──────────────┘    └─────────────┘  │
│                           │                                 │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Credit Budget & Cost Calc               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           Priority Queue with Load Shedding          │   │
│  │  Paid: instant  │  Email: normal  │  Anon: slow │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Components

### 1. Server-Issued Device Token (PRIORITY 1 - CRITICAL)

**Problem:** Server counts against `metaextract_client` cookie that attacker controls.

**Solution:** Server-issued httpOnly cookie that client cannot modify.

**Files to Create:**

#### `server/utils/device-token.ts`

```typescript
import crypto from 'crypto';
import type { Request, Response } from 'express';

const DEVICE_TOKEN_SECRET = process.env.DEVICE_TOKEN_SECRET || '';
const COOKIE_NAME = 'metaextract_device';

if (!DEVICE_TOKEN_SECRET) {
  throw new Error('DEVICE_TOKEN_SECRET environment variable required');
}

export interface DeviceToken {
  deviceId: string;
  createdAt: number;
  expiresAt: number;
}

export function getOrCreateDeviceToken(req: Request, res: Response): string {
  // Try to get existing server-issued token
  let deviceToken = req.cookies?.[COOKIE_NAME];

  if (deviceToken) {
    const decoded = verifyDeviceToken(deviceToken);
    if (decoded && !isTokenExpired(decoded)) {
      return decoded.deviceId;
    }
  }

  // Mint new server-issued token
  const deviceId = crypto.randomUUID();
  const createdAt = Date.now();
  const expiresAt = createdAt + 90 * 24 * 60 * 60 * 1000; // 90 days

  const payload = `${deviceId}.${createdAt}.${expiresAt}`;

  // Sign server-side
  const signature = crypto
    .createHmac('sha256', DEVICE_TOKEN_SECRET)
    .update(payload)
    .digest('hex');

  const token = `${payload}.${signature}`;

  // Set httpOnly cookie (client can't modify or read)
  res.cookie(COOKIE_NAME, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 90 * 24 * 60 * 60 * 1000,
    path: '/',
  });

  return deviceId;
}

export function verifyDeviceToken(token: string): DeviceToken | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 4) return null; // device.created.expires.signature

    const [deviceId, createdAtStr, expiresAtStr, signature] = parts;
    const payload = `${deviceId}.${createdAtStr}.${expiresAtStr}`;

    // Verify signature
    const expectedSignature = crypto
      .createHmac('sha256', DEVICE_TOKEN_SECRET)
      .update(payload)
      .digest('hex');

    if (signature !== expectedSignature) return null;

    // Parse timestamps
    const createdAt = parseInt(createdAtStr, 10);
    const expiresAt = parseInt(expiresAtStr, 10);

    if (isNaN(createdAt) || isNaN(expiresAt)) return null;

    // Check expiry
    if (Date.now() > expiresAt) return null;

    return { deviceId, createdAt, expiresAt };
  } catch {
    return null;
  }
}

function isTokenExpired(token: DeviceToken): boolean {
  return Date.now() > token.expiresAt;
}

export async function isDeviceTokenRevoked(deviceId: string): Promise<boolean> {
  // TODO: Implement token revocation list in Redis/DB
  // For now, always return false
  return false;
}

// Helper to get deviceId from request
export function getDeviceId(req: Request): string | null {
  const token = req.cookies?.[COOKIE_NAME];
  if (!token) return null;
  const decoded = verifyDeviceToken(token);
  if (!decoded) return null;
  return decoded.deviceId;
}
```

**Add to `.env`:**

```bash
# Generate with: openssl rand -hex 32
DEVICE_TOKEN_SECRET=<your-secret-here>
```

---

### 2. Cost-Based Credit Calculator (PRIORITY 1 - HIGH)

**Problem:** 1 request = 1 credit doesn't reflect compute cost.

**Solution:** Cost units based on file type and size.

#### `server/utils/cost-calculator.ts`

```typescript
export interface FileCost {
  creditCost: number;
  computeLevel: 'low' | 'medium' | 'high' | 'blocked';
  shouldDownscale: boolean;
  maxResolution: number;
  allowedTiers?: ('anonymous' | 'verified' | 'paid')[];
}

export const COST_MATRIX: Record<string, Partial<FileCost>> = {
  // Free tier: only JPG/PNG/WebP, cheap compute
  'image/jpeg': {
    creditCost: 1,
    computeLevel: 'low',
    shouldDownscale: true,
    maxResolution: 1600,
  },
  'image/png': {
    creditCost: 1,
    computeLevel: 'low',
    shouldDownscale: true,
    maxResolution: 1600,
  },
  'image/webp': {
    creditCost: 1,
    computeLevel: 'low',
    shouldDownscale: true,
    maxResolution: 1600,
  },
  'image/gif': {
    creditCost: 1,
    computeLevel: 'low',
    shouldDownscale: true,
    maxResolution: 1600,
  },

  // Blocked on free tier
  'image/heic': {
    creditCost: 3,
    computeLevel: 'medium',
    shouldDownscale: false,
    maxResolution: 2400,
    allowedTiers: ['verified', 'paid'],
  },
  'image/heif': {
    creditCost: 3,
    computeLevel: 'medium',
    shouldDownscale: false,
    maxResolution: 2400,
    allowedTiers: ['verified', 'paid'],
  },
  'image/x-canon-cr2': {
    creditCost: 3,
    computeLevel: 'high',
    shouldDownscale: false,
    maxResolution: 2400,
    allowedTiers: ['paid'],
  },
};

export function calculateFileCost(
  mimeType: string,
  sizeBytes: number,
  accessLevel: 'anonymous' | 'verified' | 'paid'
): FileCost {
  const baseCost = COST_MATRIX[mimeType] || {
    creditCost: 2,
    computeLevel: 'medium',
    shouldDownscale: true,
    maxResolution: 1600,
  };

  // Scale by size buckets
  const sizeMB = sizeBytes / (1024 * 1024);
  let sizeMultiplier = 1;

  if (sizeMB > 10) sizeMultiplier = 2;
  if (sizeMB > 25) sizeMultiplier = 3;
  if (sizeMB > 50) sizeMultiplier = 4;

  // Check tier restrictions
  if (baseCost.allowedTiers && !baseCost.allowedTiers.includes(accessLevel)) {
    return {
      creditCost: 0,
      computeLevel: 'blocked',
      shouldDownscale: false,
      maxResolution: 0,
    };
  }

  return {
    creditCost: Math.floor((baseCost.creditCost || 1) * sizeMultiplier),
    computeLevel: baseCost.computeLevel || 'medium',
    shouldDownscale: baseCost.shouldDownscale || false,
    maxResolution: baseCost.maxResolution || 2400,
  };
}

export function shouldAllowFileType(
  mimeType: string,
  accessLevel: 'anonymous' | 'verified' | 'paid'
): boolean {
  const cost = COST_MATRIX[mimeType];
  if (!cost) return accessLevel === 'paid';
  if (!cost.allowedTiers) return true;
  return cost.allowedTiers.includes(accessLevel as any);
}

export function getDownscaleSettings(
  mimeType: string,
  accessLevel: 'anonymous' | 'verified' | 'paid'
): { shouldDownscale: boolean; maxResolution: number } | null {
  const cost = calculateFileCost(mimeType, 0, accessLevel);
  if (cost.computeLevel === 'blocked') return null;
  return {
    shouldDownscale: cost.shouldDownscale,
    maxResolution: cost.maxResolution,
  };
}
```

---

### 3. Identity Ladder (PRIORITY 1 - HIGH)

**Problem:** No progressive friction, only "2 free or pay".

**Solution:** Identity tiers with increasing credit budgets.

#### `server/utils/identity-ladder.ts`

```typescript
export type IdentityTier =
  | 'anonymous'
  | 'challenge_verified'
  | 'email_verified'
  | 'oauth_verified'
  | 'paid';

export interface IdentityConfig {
  tier: IdentityTier;
  dailyCreditBudget: number;
  maxFileSizeMB: number;
  allowedFileTypes: string[];
  priorityQueue: boolean;
  downscaleEnabled: boolean;
  requiresChallenge: boolean;
}

export const IDENTITY_LADDER: Record<IdentityTier, IdentityConfig> = {
  anonymous: {
    tier: 'anonymous',
    dailyCreditBudget: 2, // 2 cheap files
    maxFileSizeMB: 4,
    allowedFileTypes: ['image/jpeg', 'image/png', 'image/webp', 'image/gif'],
    priorityQueue: false,
    downscaleEnabled: true,
    requiresChallenge: false,
  },

  challenge_verified: {
    tier: 'challenge_verified',
    dailyCreditBudget: 5, // +3 credits
    maxFileSizeMB: 4,
    allowedFileTypes: ['image/jpeg', 'image/png', 'image/webp', 'image/gif'],
    priorityQueue: false,
    downscaleEnabled: true,
    requiresChallenge: true,
  },

  email_verified: {
    tier: 'email_verified',
    dailyCreditBudget: 15, // +10 credits
    maxFileSizeMB: 8,
    allowedFileTypes: [
      'image/jpeg',
      'image/png',
      'image/webp',
      'image/gif',
      'image/heic',
      'image/heif',
    ],
    priorityQueue: true, // Better queue position
    downscaleEnabled: false, // Full resolution
    requiresChallenge: false,
  },

  oauth_verified: {
    tier: 'oauth_verified',
    dailyCreditBudget: 20, // +15 credits
    maxFileSizeMB: 10,
    allowedFileTypes: ['*'], // All formats
    priorityQueue: true,
    downscaleEnabled: false,
    requiresChallenge: false,
  },

  paid: {
    tier: 'paid',
    dailyCreditBudget: 999999, // Effectively unlimited per plan limits
    maxFileSizeMB: 100,
    allowedFileTypes: ['*'],
    priorityQueue: true,
    downscaleEnabled: false,
    requiresChallenge: false,
  },
};

export function getIdentityConfig(user: {
  tier: IdentityTier;
  emailVerified?: boolean;
  oauthProvider?: string;
}): IdentityConfig {
  if (user.tier === 'paid') return IDENTITY_LADDER.paid;
  if (user.oauthProvider) return IDENTITY_LADDER.oauth_verified;
  if (user.emailVerified) return IDENTITY_LADDER.email_verified;
  if (user.tier === 'challenge_verified')
    return IDENTITY_LADDER.challenge_verified;
  return IDENTITY_LADDER.anonymous;
}

export function canUpgradeTo(tier: IdentityTier, user: any): boolean {
  if (tier === 'paid') return !!user.subscriptionId;
  if (tier === 'oauth_verified') return !!user.oauthProvider;
  if (tier === 'email_verified') return !!user.emailVerified;
  if (tier === 'challenge_verified') return true; // Always available
  return false;
}

export function getNextTier(currentTier: IdentityTier): IdentityTier | null {
  const tiers: IdentityTier[] = [
    'anonymous',
    'challenge_verified',
    'email_verified',
    'oauth_verified',
    'paid',
  ];
  const currentIndex = tiers.indexOf(currentTier);
  if (currentIndex === -1 || currentIndex === tiers.length - 1) return null;
  return tiers[currentIndex + 1];
}
```

---

### 4. Priority Queue with Load Shedding (PRIORITY 1 - HIGH)

**Problem:** Free tier hits hard blocks under load.

**Solution:** Queue with priorities - paid stays fast, free slows down gracefully.

#### `server/utils/extraction-queue.ts`

```typescript
import { createClient, RedisClientType } from 'redis';
import type { AuthRequest } from '../auth';
import type { IdentityTier } from './identity-ladder';

export interface QueuedJob {
  jobId: string;
  deviceId: string;
  userId: string | null;
  userIdentityTier: IdentityTier;
  fileName: string;
  fileSize: number;
  creditCost: number;
  queuedAt: number;
  priority: number; // Lower = higher priority
}

export class ExtractionQueue {
  private redis: RedisClientType | null = null;
  private maxConcurrent: number = 50;
  private maxConcurrentFree: number = 10;
  private initialized: boolean = false;

  async init(): Promise<void> {
    if (this.initialized) return;

    const redisUrl = process.env.REDIS_URL;
    if (!redisUrl) {
      console.warn('[Queue] Redis not configured, queue disabled');
      return;
    }

    this.redis = createClient({ url: redisUrl });

    this.redis.on('error', err => {
      console.error('[Queue] Redis error:', err);
    });

    await this.redis.connect();
    this.initialized = true;
    console.log('[Queue] Initialized successfully');
  }

  async enqueue(
    job: Omit<QueuedJob, 'jobId' | 'queuedAt' | 'priority'>
  ): Promise<{
    jobId: string;
    position: number;
    estimatedWait: number;
  }> {
    if (!this.initialized) {
      throw new Error('Queue not initialized');
    }

    const jobId = crypto.randomUUID();
    const queueKey = 'extraction:queue';

    // Priority based on identity tier
    const priority = this.calculatePriority(job as QueuedJob);

    const queuedJob: QueuedJob = {
      ...job,
      jobId,
      queuedAt: Date.now(),
      priority,
    };

    // Add to Redis sorted set (score = priority)
    await this.redis.zadd(queueKey, priority, JSON.stringify(queuedJob));

    // Get position and estimated wait
    const position = await this.redis.zrank(
      queueKey,
      JSON.stringify(queuedJob)
    );
    const ahead = await this.redis.zcount(queueKey, 0, priority - 0.0001);

    // Free tier wait estimate is higher under load
    const estimatedWait =
      job.userIdentityTier === 'anonymous' ||
      job.userIdentityTier === 'challenge_verified'
        ? Math.min(120, ahead * 30) // Max 2 min wait per job ahead
        : Math.min(30, ahead * 10); // Paid faster

    return { jobId, position: position || 0, estimatedWait };
  }

  private calculatePriority(job: QueuedJob): number {
    // Paid = 0-10, Email = 11-20, Challenge = 21-30, Anonymous = 31-50
    const tierPriority: Record<IdentityTier, number> = {
      paid: 1,
      oauth_verified: 5,
      email_verified: 10,
      challenge_verified: 20,
      anonymous: 30,
    };

    return tierPriority[job.userIdentityTier] + Math.random() * 5; // Add jitter
  }

  async nextJob(): Promise<QueuedJob | null> {
    if (!this.initialized) return null;

    const activeFree = await this.getActiveJobs([
      'anonymous',
      'challenge_verified',
    ]);
    const activePaid = await this.getActiveJobs([
      'email_verified',
      'oauth_verified',
      'paid',
    ]);

    // Don't start free job if too many running
    if (
      activeFree >= this.maxConcurrentFree &&
      activePaid < this.maxConcurrent
    ) {
      return null; // Skip free tier jobs under load
    }

    // Get highest priority job
    const queueKey = 'extraction:queue';
    const result = await this.redis.zpopmin(queueKey);
    if (!result) return null;

    return JSON.parse(result.value);
  }

  private async getActiveJobs(tiers: IdentityTier[]): Promise<number> {
    if (!this.redis) return 0;

    const key = `extraction:active:${tiers.join('_')}`;
    const count = await this.redis.llen(key);
    return count;
  }

  async markJobStarted(jobId: string, tier: IdentityTier): Promise<void> {
    if (!this.initialized) return;

    const key = `extraction:active:${tier}`;
    await this.redis.lpush(key, jobId);
    await this.redis.expire(key, 3600); // Expire after 1 hour
  }

  async markJobComplete(jobId: string, tier: IdentityTier): Promise<void> {
    if (!this.initialized) return;

    const key = `extraction:active:${tier}`;
    await this.redis.lrem(key, 0, jobId);
  }

  async getQueueDepth(): Promise<{
    total: number;
    anonymous: number;
    paid: number;
  }> {
    if (!this.initialized) return { total: 0, anonymous: 0, paid: 0 };

    const all = await this.redis.zcard('extraction:queue');

    // Count by tier
    const jobs = await this.redis.zrange('extraction:queue', 0, -1);

    let anonymous = 0;
    let paid = 0;

    for (const jobStr of jobs) {
      const job: QueuedJob = JSON.parse(jobStr);
      if (
        job.userIdentityTier === 'anonymous' ||
        job.userIdentityTier === 'challenge_verified'
      ) {
        anonymous++;
      } else {
        paid++;
      }
    }

    return { total: all, anonymous, paid };
  }
}

export const extractionQueue = new ExtractionQueue();
```

---

### 5. Challenge System (PRIORITY 2 - HIGH)

**Problem:** No verification after 2 free checks.

**Solution:** Simple challenge (math or click) to prove human.

#### `server/middleware/challenge.ts`

```typescript
import { Request, Response, NextFunction } from 'express';
import crypto from 'crypto';
import { storage } from '../storage';
import { getDeviceId } from '../utils/device-token';

const CHALLENGE_COOKIE = 'metaextract_challenge';

export interface Challenge {
  challengeId: string;
  solution: string;
  expiresAt: number;
  difficulty: 'easy' | 'medium';
}

export async function requireChallenge(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  const deviceId = getDeviceId(req);
  if (!deviceId) {
    next();
    return;
  }

  // Skip challenge if device has been verified recently
  const recentChallenge = await storage.get(`challenge:verified:${deviceId}`);
  if (recentChallenge) {
    next();
    return;
  }

  // Check if device has used free quota
  const usage = await getClientUsage(deviceId);
  if (usage.freeUsed < 2) {
    next(); // First 2 extractions don't need challenge
    return;
  }

  // Need challenge - return 402 with challenge
  const challenge = generateSimpleChallenge();

  await storage.set(
    `challenge:${challenge.challengeId}`,
    JSON.stringify(challenge),
    60 // 60 second expiry
  );

  res.status(402).json({
    error: 'Verification required',
    challenge: {
      type: 'simple',
      challengeId: challenge.challengeId,
      question: `What is ${challenge.question}?`, // e.g., "What is 3 + 4?"
    },
    message: 'Complete a quick verification to continue (helps prevent abuse)',
  });
}

function generateSimpleChallenge(): Challenge {
  const a = Math.floor(Math.random() * 10);
  const b = Math.floor(Math.random() * 10);
  const sum = a + b;

  return {
    challengeId: crypto.randomUUID(),
    question: `${a} + ${b}`,
    solution: String(sum),
    expiresAt: Date.now() + 60000, // 1 minute
    difficulty: 'easy',
  };
}

export async function verifyChallenge(
  challengeId: string,
  solution: string
): Promise<boolean> {
  const challengeData = await storage.get(`challenge:${challengeId}`);
  if (!challengeData) return false;

  const challenge: Challenge = JSON.parse(challengeData);

  // Check expiry
  if (Date.now() > challenge.expiresAt) return false;

  // Verify solution
  return challenge.solution === solution;
}

export async function markChallengeVerified(deviceId: string): Promise<void> {
  // Mark device as verified for 24 hours
  await storage.set(`challenge:verified:${deviceId}`, 'true', 24 * 60 * 60);
}
```

---

## Database Schema Changes

### New Tables

```sql
-- Device tokens and identity tracking
CREATE TABLE device_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  device_id VARCHAR(64) UNIQUE NOT NULL,
  identity_tier VARCHAR(50) DEFAULT 'anonymous',
  email_verified BOOLEAN DEFAULT FALSE,
  oauth_provider VARCHAR(50),
  challenge_verified_until TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  last_used_at TIMESTAMP,
  daily_credits_used INTEGER DEFAULT 0,
  daily_credit_reset TIMESTAMP DEFAULT DATE_TRUNC('day', NOW())
);

CREATE INDEX idx_device_tokens_device_id ON device_tokens(device_id);
CREATE INDEX idx_device_tokens_last_used ON device_tokens(last_used_at);
CREATE INDEX idx_device_tokens_tier ON device_tokens(identity_tier);

-- Extraction queue (if using DB instead of Redis)
CREATE TABLE extraction_queue (
  job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  device_id VARCHAR(64) NOT NULL,
  user_id UUID REFERENCES users(id),
  identity_tier VARCHAR(50) NOT NULL,
  file_name VARCHAR(255),
  file_size BIGINT,
  credit_cost INTEGER NOT NULL,
  priority INTEGER NOT NULL,
  status VARCHAR(20) DEFAULT 'queued',
  queued_at TIMESTAMP DEFAULT NOW(),
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  result JSONB
);

CREATE INDEX idx_queue_status ON extraction_queue(status);
CREATE INDEX idx_queue_priority ON extraction_queue(priority);

-- Daily credit tracking
CREATE TABLE daily_credit_usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  device_id VARCHAR(64) NOT NULL,
  user_id UUID REFERENCES users(id),
  identity_tier VARCHAR(50) NOT NULL,
  credits_used INTEGER DEFAULT 0,
  date DATE DEFAULT CURRENT_DATE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(device_id, date, identity_tier)
);

CREATE INDEX idx_daily_usage_device_date ON daily_credit_usage(device_id, date);
```

---

## Integration Points

### Update `server/routes/images-mvp.ts`

**Replace `/api/images_mvp/extract` handler (lines 1074+):**

```typescript
app.post(
  '/api/images_mvp/extract',
  rateLimitExtraction(),
  upload.single('file'),
  async (req: Request, res: Response) => {
    const startTime = Date.now();
    const requestId = `req_${Date.now()}_${crypto.randomUUID().slice(0, 8)}`;
    res.setHeader('X-Request-Id', requestId);

    let tempPath: string | null = null;

    try {
      if (!req.file) {
        return sendInvalidRequestError(res, 'No file uploaded');
      }

      // 1. Get or create device token (server-issued)
      const deviceId = await getOrCreateDeviceToken(req, res);

      // 2. Get identity tier
      const user = await getIdentityForDevice(deviceId);
      const identityConfig = getIdentityConfig(user);

      // 3. Check challenge requirement
      if (identityConfig.requiresChallenge && !user.challengeVerified) {
        if (!req.body?.challenge_response) {
          return await requireChallenge(req, res);
        }
        const valid = await verifyChallenge(
          req.body.challenge_id,
          req.body.challenge_response
        );
        if (!valid) {
          return res.status(400).json({ error: 'Invalid challenge response' });
        }
        await markChallengeVerified(deviceId);
      }

      // 4. Validate file type for tier
      if (!shouldAllowFileType(req.file.mimetype, identityConfig.tier)) {
        return res.status(403).json({
          error: 'File type not allowed for your access level',
          allowedTypes: identityConfig.allowedFileTypes,
          upgradeRequired: true,
        });
      }

      // 5. Check file size
      if (req.file.size > identityConfig.maxFileSizeMB * 1024 * 1024) {
        return res.status(413).json({
          error: 'File too large',
          maxSizeMB: identityConfig.maxFileSizeMB,
        });
      }

      // 6. Calculate cost and check budget
      const cost = calculateFileCost(
        req.file.mimetype,
        req.file.size,
        identityConfig.tier
      );
      if (cost.creditCost === 0) {
        return res.status(403).json({
          error:
            'This file type requires a verified account or paid subscription',
          message: 'HEIC and RAW files need Pro or higher',
        });
      }

      const budget = await getDailyCreditBudget(deviceId, identityConfig.tier);
      if (budget.remaining < cost.creditCost) {
        return res.status(402).json({
          error: 'Daily credit budget exceeded',
          resetTime: budget.resetsAt,
          requiredCredits: cost.creditCost,
          availableCredits: budget.remaining,
          upgradeUrl: '/images_mvp?pricing=true',
        });
      }

      // 7. Check if file hash already processed (deduplication)
      const fileHash = await calculateFileHash(req.file.path);
      const recentResult = await getRecentResultByHash(fileHash, 24 * 60 * 60); // 24 hours
      if (recentResult && identityConfig.tier === 'anonymous') {
        // Return cached result for free tier
        console.log('[Dedup] Returning cached result for anonymous user');
        return res.json(recentResult.metadata);
      }

      // 8. Enqueue job (not execute immediately for queue system)
      await extractionQueue.init();

      const queued = await extractionQueue.enqueue({
        deviceId,
        userId: user.id,
        userIdentityTier: identityConfig.tier,
        fileName: req.file.originalname,
        fileSize: req.file.size,
        creditCost: cost.creditCost,
      });

      // 9. Deduct credits
      await deductDailyCredits(deviceId, identityConfig.tier, cost.creditCost);

      // 10. Return job ID + position
      res.json({
        jobId: queued.jobId,
        position: queued.position,
        estimatedWait: queued.estimatedWait,
        message: 'Your file is queued for processing',
      });
    } catch (error) {
      console.error('Images MVP extraction error:', error);
      sendInternalServerError(res, 'Failed to extract metadata');
    } finally {
      await cleanupTempFile(tempPath);
    }
  }
);

// New endpoint: Get job status (polling)
app.get('/api/images_mvp/jobs/:jobId', async (req: Request, res: Response) => {
  try {
    const job = await extractionQueue.getJobStatus(req.params.jobId);

    if (!job) {
      return res.status(404).json({ error: 'Job not found' });
    }

    if (job.status === 'completed') {
      return res.json({
        jobId: job.jobId,
        status: 'completed',
        metadata: job.result,
      });
    }

    res.json({
      jobId: job.jobId,
      status: job.status,
      position: job.position,
      estimatedWait: job.estimatedWait,
    });
  } catch (error) {
    console.error('Job status error:', error);
    res.status(500).json({ error: 'Failed to fetch job status' });
  }
});

// New endpoint: Submit challenge answer
app.post('/api/images_mvp/challenge', async (req: Request, res: Response) => {
  const { challengeId, response } = req.body;

  if (!challengeId || !response) {
    return res.status(400).json({ error: 'challengeId and response required' });
  }

  const valid = await verifyChallenge(challengeId, response);
  if (!valid) {
    return res
      .status(400)
      .json({ error: 'Incorrect answer, please try again' });
  }

  const deviceId = getDeviceId(req);
  if (!deviceId) {
    return res.status(400).json({ error: 'Device token not found' });
  }

  await markChallengeVerified(deviceId);

  res.json({ success: true, message: 'Verification successful' });
});
```

---

## Client-Side Changes

### Update `client/src/components/images-mvp/simple-upload.tsx`

Add challenge modal and queue polling:

```typescript
const [showChallenge, setShowChallenge] = useState(false);
const [challenge, setChallenge] = useState<any>(null);
const [isQueued, setIsQueued] = useState(false);

// In error handler for upload:
if (error.status === 402 && error.challenge) {
  setChallenge(error.challenge);
  setShowChallenge(true);
  return;
}

// Render challenge modal:
{showChallenge && challenge && (
  <ChallengeModal
    challenge={challenge}
    onResponse={async (response) => {
      // Verify challenge
      const verifyRes = await fetch('/api/images_mvp/challenge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          challengeId: challenge.challengeId,
          response,
        }),
      });

      if (verifyRes.ok) {
        setShowChallenge(false);
        // Retry upload automatically
        void uploadFile(file);
      }
    }}
  />
)}

// Queue polling
const uploadFile = async (file: File) => {
  setIsUploading(true);
  setShowProgressTracker(true);

  const formData = new FormData();
  formData.append('file', file);
  formData.append('session_id', getImagesMvpSessionId());

  try {
    const data = await fetch('/api/images_mvp/extract', {
      method: 'POST',
      credentials: 'include',
      body: formData,
    }).then(r => r.json());

    // If job is queued, poll for status
    if (data.jobId) {
      setIsQueued(true);
      const result = await pollJobStatus(data.jobId);
      if (result.status === 'completed') {
        navigate('/images_mvp/results', { state: { metadata: result.metadata } });
      }
      return;
    }

    // If immediate result (rare), use it
    if (data.fields_extracted) {
      navigate('/images_mvp/results', { state: { metadata: data } });
    }

  } catch (error) {
    console.error(error);
    toast({ title: 'Upload failed', variant: 'destructive' });
  } finally {
    setIsUploading(false);
    setIsQueued(false);
  }
};

const pollJobStatus = async (jobId: string, maxAttempts = 60): Promise<any> => {
  for (let i = 0; i < maxAttempts; i++) {
    const response = await fetch(`/api/images_mvp/jobs/${jobId}`);
    const data = await response.json();

    if (data.status === 'completed') {
      return data;
    }

    // Update progress based on position/estimatedWait
    setUploadProgress(100 - (data.estimatedWait / 2)); // Rough estimate

    // Wait before next poll
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  throw new Error('Job timeout');
};
```

---

## Deployment Sequence

1. **Add environment variables:**

   ```bash
   # Generate with: openssl rand -hex 32
   DEVICE_TOKEN_SECRET=<your-secret-here>
   ```

2. **Run database migrations:**

   ```bash
   # Create new tables
   npm run db:push
   ```

3. **Deploy new utility files:**
   - `server/utils/device-token.ts`
   - `server/utils/cost-calculator.ts`
   - `server/utils/identity-ladder.ts`
   - `server/utils/extraction-queue.ts`
   - `server/middleware/challenge.ts`

4. **Update routes:**
   - Replace `/api/images_mvp/extract` handler in `server/routes/images-mvp.ts`
   - Add `/api/images_mvp/jobs/:jobId` endpoint
   - Add `/api/images_mvp/challenge` endpoint

5. **Update client:**
   - Add challenge modal component
   - Update `simple-upload.tsx` with queue polling
   - Add challenge response submission logic

6. **Test deployment:**
   - Test anonymous flow (2 credits)
   - Test challenge flow (+3 credits)
   - Test email verification flow (+10 credits)
   - Test paid flow (unlimited)
   - Test queue priority (paid should be faster)

7. **Monitor and tune:**
   - Watch queue depth
   - Monitor wait times
   - Adjust credit budgets
   - Tune priority weights

---

## Success Metrics

- ✅ No global caps that break for legit users
- ✅ Server-controlled identity (not client cookies)
- ✅ Cost-based budgeting (bound compute exposure)
- ✅ Progressive friction (identity ladder)
- ✅ Load shedding via queue priorities
- ✅ Revenue-protecting (paid always faster)
- ✅ Abuse economics: "Sign up" < "Write abuse script"

---

## What This Protects Against

| Attack              | Before       | After                        |
| ------------------- | ------------ | ---------------------------- |
| Cookie clearing     | Unlimited    | Blocked (server token)       |
| IP rotation         | 2 checks/IP  | Device tracking + challenge  |
| Headless automation | Hundreds/day | Challenge + JS token         |
| File spam           | No limit     | Upload frequency limit       |
| Resource exhaustion | No limit     | Queue throttling + cost caps |

---

## Next Steps

See `IMPLEMENTATION_STATUS.md` for what has been implemented and what remains.
