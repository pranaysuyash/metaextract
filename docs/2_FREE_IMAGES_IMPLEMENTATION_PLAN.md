# MetaExtract "2 Free Images" Implementation Plan

## 🎯 **CURRENT STATE ANALYSIS**

### **What You Have**
- ✅ Session-based tracking via cookies
- ✅ Credit balance system
- ✅ Trial email tracking
- ✅ IP logging in analytics
- ✅ File size/type validation
- ✅ Multi-tier system (free/pro/enterprise)

### **What's Missing**
- ❌ No explicit "2 free images per user" logic
- ❌ No signed client tokens (sessionIDs can be manipulated)
- ❌ No IP rate limiting
- ❌ No device fingerprinting
- ❌ No abuse detection
- ❌ No CAPTCHA escalation

---

## 🚀 **RECOMMENDED IMPLEMENTATION (Based on ChatGPT's Advice)**

### **PHASE 1: Immediate "2 Free" Logic (High Priority)**

#### **1. Add Free Usage Tracking to Storage**
Update `server/storage/mem.ts` to add free usage tracking:

```typescript
// Add to MemStorage class
private freeUsageMap: Map<string, FreeUsage>; // sessionId -> usage tracking

interface FreeUsage {
  sessionId: string;
  imagesProcessed: number;
  ipAddress: string;
  fingerprint?: string;
  firstSeen: Date;
  lastSeen: Date;
  suspicious: boolean;
}

async getFreeUsage(sessionId: string): Promise<FreeUsage | undefined> {
  return this.freeUsageMap.get(sessionId);
}

async incrementFreeUsage(sessionId: string, ipAddress: string, fingerprint?: string): Promise<number> {
  const existing = this.freeUsageMap.get(sessionId);
  if (existing) {
    existing.imagesProcessed += 1;
    existing.lastSeen = new Date();
    if (fingerprint) existing.fingerprint = fingerprint;
    return existing.imagesProcessed;
  }

  const newUsage: FreeUsage = {
    sessionId,
    imagesProcessed: 1,
    ipAddress,
    fingerprint,
    firstSeen: new Date(),
    lastSeen: new Date(),
    suspicious: false,
  };
  this.freeUsageMap.set(sessionId, newUsage);
  return 1;
}
```

#### **2. Update Extraction Route**
Modify `server/routes/extraction.ts` to enforce "2 free" logic:

```typescript
// Add after line 118 (creditCost calculation)
const FREE_IMAGE_LIMIT = 2;
const freeUsage = await storage.getFreeUsage(sessionId);
const imagesUsed = freeUsage?.imagesProcessed || 0;

// Only apply free logic if no trial email and no existing credits
if (!trialEmail && (!creditBalanceId || (creditBalanceId && balance?.credits === 0))) {
  if (imagesUsed >= FREE_IMAGE_LIMIT) {
    return sendQuotaExceededError(
      res,
      `Free limit reached (${FREE_IMAGE_LIMIT} images). Purchase credits to continue.`
    );
  }

  // Process as free image
  chargeCredits = false; // Don't charge credits
  await storage.incrementFreeUsage(sessionId, req.ip, req.fingerprint);
}
```

---

### **PHASE 2: Security Enhancements (Medium Priority)**

#### **3. Add Signed Client Token Middleware**
Create `server/middleware/signed-token.ts`:

```typescript
import crypto from 'crypto';
import { Request, Response, NextFunction } from 'express';

const TOKEN_SECRET = process.env.TOKEN_SECRET || crypto.randomBytes(32).toString('hex');
const TOKEN_EXPIRY_MS = 24 * 60 * 60 * 1000; // 24 hours

interface SignedToken {
  sessionId: string;
  expiry: number;
}

export function generateSignedToken(sessionId: string): string {
  const expiry = Date.now() + TOKEN_EXPIRY_MS;
  const payload = `${sessionId}.${expiry}`;
  const signature = crypto
    .createHmac('sha256', TOKEN_SECRET)
    .update(payload)
    .digest('base64');
  return Buffer.from(`${payload}.${signature}`).toString('base64');
}

export function verifySignedToken(token: string): string | null {
  try {
    const decoded = Buffer.from(token, 'base64').toString('utf-8');
    const [sessionId, expiry, signature] = decoded.split('.');

    // Verify signature
    const payload = `${sessionId}.${expiry}`;
    const expectedSignature = crypto
      .createHmac('sha256', TOKEN_SECRET)
      .update(payload)
      .digest('base64');

    if (signature !== expectedSignature) return null;
    if (Date.now() > parseInt(expiry)) return null;

    return sessionId;
  } catch {
    return null;
  }
}

export function signedTokenMiddleware(req: Request, res: Response, next: NextFunction) {
  const existingToken = req.cookies?.metaextract_session;
  if (existingToken) {
    const sessionId = verifySignedToken(existingToken);
    if (sessionId) {
      req.sessionId = sessionId;
      return next();
    }
  }

  // Generate new token
  const newSessionId = crypto.randomUUID();
  const newToken = generateSignedToken(newSessionId);
  res.cookie('metaextract_session', newToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    maxAge: TOKEN_EXPIRY_MS,
    sameSite: 'strict'
  });
  req.sessionId = newSessionId;
  next();
}
```

#### **4. Add Device Fingerprinting**
Create `server/middleware/fingerprint.ts`:

```typescript
import { Request } from 'express';

export function generateFingerprint(req: Request): string {
  const userAgent = req.headers['user-agent'] || '';
  const acceptLanguage = req.headers['accept-language'] || '';
  const acceptEncoding = req.headers['accept-encoding'] || '';

  // Basic fingerprint (can be enhanced with canvas data from frontend)
  const data = `${userAgent}|${acceptLanguage}|${acceptEncoding}`;
  return crypto.createHash('sha256').update(data).digest('hex');
}
```

---

### **PHASE 3: Rate Limiting & Abuse Detection (Medium Priority)**

#### **5. Add IP Rate Limiting**
Create `server/middleware/rate-limit.ts`:

```typescript
import { Request, Response, NextFunction } from 'express';

interface RateLimitEntry {
  count: number;
  resetTime: number;
}

const ipRateLimits = new Map<string, RateLimitEntry>();
const IP_LIMIT_PER_DAY = 10;
const IP_LIMIT_PER_MINUTE = 2;

export function ipRateLimitMiddleware(req: Request, res: Response, next: NextFunction) {
  const ip = req.ip;
  const now = Date.now();

  let entry = ipRateLimits.get(ip);

  // Reset if needed
  if (!entry || now > entry.resetTime) {
    entry = { count: 0, resetTime: now + 60 * 1000 }; // 1 minute window
    ipRateLimits.set(ip, entry);
  }

  entry.count++;

  if (entry.count > IP_LIMIT_PER_MINUTE) {
    return res.status(429).json({
      error: 'Too many requests from this IP. Please try again later.',
      retryAfter: Math.ceil((entry.resetTime - now) / 1000)
    });
  }

  next();
}
```

#### **6. Add Abuse Detection**
Create `server/middleware/abuse-detection.ts`:

```typescript
import { Request } from 'express';

interface AbuseScore {
  score: number;
  reasons: string[];
}

export function calculateAbuseScore(req: Request): AbuseScore {
  const score = { score: 0, reasons: [] as string[] };

  // Check for suspicious patterns
  if (req.headers['user-agent']?.includes('bot')) {
    score.score += 30;
    score.reasons.push('Bot-like user agent');
  }

  if (req.headers['referer']?.length === 0) {
    score.score += 10;
    score.reasons.push('No referer');
  }

  // Add more checks as needed

  return score;
}

export function abuseDetectionMiddleware(req: Request, res: Response, next: NextFunction) {
  const abuseScore = calculateAbuseScore(req);

  if (abuseScore.score > 50) {
    return res.status(403).json({
      error: 'Suspicious activity detected. Please complete CAPTCHA to continue.',
      requireCaptcha: true
    });
  }

  next();
}
```

---

### **PHASE 4: Integration & Testing**

#### **7. Update Main Server**
Apply all middlewares in proper order:

```typescript
// In server/index.ts or server.ts
import { signedTokenMiddleware } from './middleware/signed-token';
import { ipRateLimitMiddleware } from './middleware/rate-limit';
import { abuseDetectionMiddleware } from './middleware/abuse-detection';

// Apply middlewares in order
app.use(signedTokenMiddleware);
app.use(ipRateLimitMiddleware);
app.use(abuseDetectionMiddleware);
```

#### **8. Update Frontend to Support Fingerprinting**
Add basic fingerprint data collection:

```typescript
// In client/src/lib/auth.tsx or similar
export function collectFingerprintData(): string {
  const data = {
    userAgent: navigator.userAgent,
    language: navigator.language,
    platform: navigator.platform,
    screenResolution: `${screen.width}x${screen.height}`,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
  };

  return btoa(JSON.stringify(data)); // Basic encoding
}
```

---

## 🎯 **IMPLEMENTATION PRIORITIES**

### **IMMEDIATE (This Week)**
1. ✅ Add "2 free images" logic to extraction route
2. ✅ Add free usage tracking to storage
3. ✅ Test basic free limit enforcement

### **SHORT-TERM (Next 2 Weeks)**
4. ✅ Implement signed client tokens
5. ✅ Add basic device fingerprinting
6. ✅ Add IP rate limiting
7. ✅ Test security improvements

### **MEDIUM-TERM (Next Month)**
8. ✅ Add abuse detection scoring
9. ✅ Implement CAPTCHA integration (Cloudflare Turnstile)
10. ✅ Add monitoring/alerting for abuse patterns

---

## 🧪 **TESTING PLAN**

### **Functional Testing**
1. Test normal user gets 2 free images
2. Test 3rd image triggers paywall
3. Test cookie clear resets quota (expected behavior)
4. Test signed token prevents manipulation

### **Security Testing**
1. Test token manipulation attempts
2. Test IP rate limiting enforcement
3. Test abuse detection triggers
4. Test fingerprint consistency

### **UX Testing**
1. Test paywall messaging clarity
2. Test cross-session quota persistence
3. Test mobile browser compatibility
4. Test private browsing mode behavior

---

## 📊 **SUCCESS METRICS**

### **Conversion Metrics**
- Free → Paid conversion rate
- Average free images per user
- Paywall engagement rate

### **Security Metrics**
- Abuse attempts blocked
- IP ban rate
- CAPTCHA solve rate
- Token manipulation attempts

### **UX Metrics**
- Drop-off rate at paywall
- Session duration
- Return user rate
- Mobile vs desktop usage

---

**STATUS**: 🚀 **READY FOR IMPLEMENTATION**
**ESTIMATED EFFORT**: 2-3 weeks for complete implementation
**PRIORITY**: HIGH (Critical for monetization and abuse prevention)