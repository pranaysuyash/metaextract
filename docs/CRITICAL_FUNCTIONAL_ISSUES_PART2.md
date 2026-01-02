# Critical Functional Issues - Part 2
## Authentication, Extraction Routes, and Database

Analysis of critical issues in server-side authentication, file extraction, and database management.

---

## 1. server/auth.ts

**Description**: JWT-based authentication system with registration, login, session management, and tier enforcement (564 lines).

**Critical Functional Issues**:

### 1. **Unauthenticated Users Default to Enterprise Tier**
   - **Location**: Line 174-179 (`getEffectiveTier`)
   - **Issue**: 
     ```typescript
     export function getEffectiveTier(req: AuthRequest): string {
       if (req.user && req.user.subscriptionStatus === "active") {
         return req.user.tier;
       }
       return "enterprise"; // DEFAULT TO ENTERPRISE!
     }
     ```
   - **Impact**: Any unauthenticated request gets full enterprise access. This defeats the entire payment model and trial system.
   - **Severity**: **CRITICAL** - Business model breaking issue
   - **Recommendation**: Change default to "free" or "trial" tier, require authentication for paid features.

### 2. **Tier Override in Production (SECURITY)**
   - **Location**: Line 340-353 (login handler)
   - **Issue**: 
     ```typescript
     const allowTierOverride = 
       process.env.ALLOW_TIER_OVERRIDE === "true" || 
       process.env.NODE_ENV === "development";
     
     if (allowTierOverride && tier) {
       currentTier = overrideTier; // User-controlled tier override!
     }
     ```
   - **Impact**: Users can send `?tier=enterprise` in login requests and get upgraded silently if `ALLOW_TIER_OVERRIDE` is enabled.
   - **Severity**: **CRITICAL** - Security vulnerability
   - **Recommendation**: Remove tier override capability from login endpoint; only allow via webhooks/internal APIs.

### 3. **Update Tier Endpoint Has No Authentication**
   - **Location**: Line 535-564 (`/api/auth/update-tier`)
   - **Issue**: 
     ```typescript
     app.post("/api/auth/update-tier", async (req: Request, res: Response) => {
       // This should only be called internally by webhook handlers
       // In production, add additional security (internal API key, etc.)
       const { userId, tier, subscriptionId, subscriptionStatus } = req.body;
     ```
   - **Impact**: Anyone can POST to this endpoint to upgrade any user to any tier.
   - **Severity**: **CRITICAL** - Unauthenticated privilege escalation
   - **Recommendation**: 
     - Add `requireAuth` middleware
     - Add webhook signature validation
     - Use internal API key (environment-based)
     - Restrict to POST from specific IP/origin

### 4. **No Rate Limiting on Auth Endpoints**
   - **Location**: Lines 190, 271, 400, 408, 464, 535
   - **Issue**: Register, login, and logout endpoints have no rate limiting. Brute force attacks possible.
   - **Impact**: Email enumeration, password guessing, DoS attacks.
   - **Severity**: **HIGH** - Security/abuse risk
   - **Recommendation**: Add rate limiting middleware (e.g., 5 attempts per 15 minutes per IP).

### 5. **JWT Secret Hard-coded for Development**
   - **Location**: Line 24
   - **Issue**: 
     ```typescript
     const JWT_SECRET = process.env.SESSION_SECRET || 
       "metaextract-dev-secret-change-in-production";
     ```
   - **Impact**: If `SESSION_SECRET` not set, all tokens are signed with a public default secret. Tokens can be forged.
   - **Severity**: **CRITICAL** - Broken authentication
   - **Recommendation**: Require `SESSION_SECRET` to be set; throw error on startup if missing in production.

### 6. **Password Verification Doesn't Reject on bcrypt Failure**
   - **Location**: Line 317-322
   - **Issue**: 
     ```typescript
     const isValid = await bcrypt.compare(password, user.password);
     if (!isValid) {
       return res.status(401).json({ error: "Invalid credentials" });
     }
     ```
   - **Impact**: If `user.password` is null/undefined/corrupted, `bcrypt.compare` may throw, returning 500 instead of 401.
   - **Severity**: **MEDIUM** - Information disclosure, error handling
   - **Recommendation**: Wrap in try-catch, return 401 on any comparison failure.

### 7. **Subscription Status Refresh Can Fail Silently**
   - **Location**: Line 329-338 (login)
   - **Issue**: 
     ```typescript
     if (user.subscriptionId) {
       const [sub] = await db.select().from(subscriptions)...
       if (sub) {
         currentTier = sub.tier;
         subscriptionStatus = sub.status;
       }
     }
     ```
   - **Impact**: If subscription DB lookup fails, user's tier defaults to their old cached tier (may be outdated). No error handling or logging.
   - **Severity**: **HIGH** - Inconsistent billing enforcement
   - **Recommendation**: Log failures, consider failing login if subscription lookup fails for paid users.

### 8. **No Token Expiry Validation Before Use**
   - **Location**: Line 79-86 (`verifyToken`)
   - **Issue**: `jwt.verify` checks expiry, but no handling for expired tokens in middleware. Middleware accepts null as valid user.
   - **Impact**: Already checked by `jwt.verify`, but the `null` case isn't properly handled downstream.
   - **Severity**: **LOW** - Minor edge case
   - **Recommendation**: Add explicit check in `authMiddleware` for token expiry.

### 9. **Cookie Security Insufficient**
   - **Location**: Lines 368-372 (register), 491-495 (refresh)
   - **Issue**: 
     ```typescript
     res.cookie("auth_token", token, {
       httpOnly: true,
       secure: process.env.NODE_ENV === "production", // Only HTTPS in prod
       sameSite: "lax", // Allows some cross-site cookie access
     });
     ```
   - **Impact**: 
     - `sameSite: "lax"` allows cookies on top-level navigation (some CSRF risk)
     - `secure` depends on NODE_ENV detection (fragile)
   - **Severity**: **MEDIUM** - Security hardening
   - **Recommendation**: Use `sameSite: "strict"`, enforce HTTPS via deployment config, not NODE_ENV.

### 10. **No Audit Logging for Auth Events**
   - **Location**: Entire auth.ts
   - **Issue**: No logging for registrations, logins, tier upgrades, or failed auth attempts.
   - **Impact**: Cannot detect abuse, privilege escalation, or compromised accounts.
   - **Severity**: **MEDIUM** - Compliance/observability
   - **Recommendation**: Add audit log entries for all auth events with user ID, IP, timestamp, action.

---

## 2. server/routes/extraction.ts

**Description**: Metadata extraction endpoints for single files, batch processing, and advanced forensic analysis (722 lines).

**Critical Functional Issues**:

### 1. **Trial Email Not Required in Query Parameter**
   - **Location**: Line 117
   - **Issue**: 
     ```typescript
     trialEmail = normalizeEmail(req.body?.trial_email);
     ```
   - **Impact**: Trial email comes from request body, not validated or rate-limited. Users can claim trial multiple times by changing email slightly.
   - **Severity**: **HIGH** - Business model broken
   - **Recommendation**: Require trial email to be cryptographically tied to session/IP, add validation for real emails.

### 2. **Default Tier is Enterprise (Not Enforced at Route Level)**
   - **Location**: Line 111
   - **Issue**: 
     ```typescript
     const requestedTier = (req.query.tier as string) || 'enterprise';
     ```
   - **Impact**: If `tier` query param is missing, defaults to `'enterprise'`. Frontend never sends tier, so all uploads get enterprise behavior.
   - **Severity**: **CRITICAL** - Business model breaking
   - **Recommendation**: 
     - Remove default; derive tier from `req.user` (authenticated) or deny (unauthenticated)
     - Never accept tier from query params; only from server-side subscription status

### 3. **Bypass Credits Flag in Development**
   - **Location**: Line 76-87
   - **Issue**: 
     ```typescript
     function shouldBypassCredits(req: AuthRequest): boolean {
       if (process.env.NODE_ENV === 'development') return true; // ALWAYS BYPASS IN DEV
       if (process.env.NODE_ENV !== 'test') return false;
       const value = String(req.headers['x-test-bypass-credits'] ?? '').toLowerCase();
       return value === '1' || value === 'true';
     }
     ```
   - **Impact**: Development environment completely bypasses all credit checks. If NODE_ENV is misconfigured, billing is disabled.
   - **Severity**: **HIGH** - Accidental production deployment risk
   - **Recommendation**: Remove blanket dev bypass; use feature flags or specific test headers only.

### 4. **Credit Charging Happens After Extraction (Fire-and-Forget)**
   - **Location**: Line 210-219
   - **Issue**: 
     ```typescript
     if (chargeCredits && creditBalanceId) {
       storage.useCredits(...).catch((err) => console.error(...));
     }
     ```
   - **Impact**: Credits are deducted in a non-blocking promise. If storage fails, user doesn't get charged (loss of revenue).
   - **Severity**: **CRITICAL** - Billing/revenue risk
   - **Recommendation**: Make credit deduction synchronous and required, or implement retry with message queue.

### 5. **Trial Usage Recording Fails Silently**
   - **Location**: Line 221-233
   - **Issue**: 
     ```typescript
     try {
       await storage.recordTrialUsage({...});
     } catch (err) {
       console.error('Failed to record trial usage:', err); // Just log
     }
     ```
   - **Impact**: If trial recording fails, user can claim trial unlimited times (no enforcement).
   - **Severity**: **CRITICAL** - Abuse vector
   - **Recommendation**: Make trial recording synchronous/required before responding to user.

### 6. **Metadata Saved to DB After Response (Can Fail)**
   - **Location**: Line 236-249
   - **Issue**: 
     ```typescript
     try {
       const savedRecord = await storage.saveMetadata({...});
       metadata.id = savedRecord.id;
     } catch (dbError) {
       console.error('[Extraction] Failed to save metadata to DB:', dbError);
       // Continue anyway - frontend will use memory fallback
     }
     ```
   - **Impact**: Database save is async/non-blocking after response. Data loss if DB is down; frontend can't access results.
   - **Severity**: **MEDIUM** - Data durability
   - **Recommendation**: Save to DB before responding, use transaction for credits+save.

### 7. **Batch Processing Has No Validation**
   - **Location**: Line 251+ (batch endpoint, not shown in excerpt)
   - **Issue**: Batch endpoint accepts file arrays but no:
     - Max batch size limit
     - Concurrent processing cap (DoS risk)
     - Per-file error recovery
   - **Impact**: Attacker can upload 1000 files in one batch, crash server.
   - **Severity**: **HIGH** - DoS vulnerability
   - **Recommendation**: Cap batch to 10-50 files, limit concurrent processing to 2-3 per user.

### 8. **Advanced Analysis Hardcoded for Forensic+ Tier**
   - **Location**: Line 463-477
   - **Issue**: 
     ```typescript
     if (!['forensic', 'enterprise'].includes(normalizedTier)) {
       return res.status(403).json({
         error: 'Advanced analysis unavailable',
       });
     }
     ```
   - **Impact**: Hardcoded tier check; if tier list changes, endpoint breaks. No way to offer advanced analysis to other tiers.
   - **Severity**: **LOW** - Maintainability
   - **Recommendation**: Use `getTierConfig().features.advancedAnalysis` instead of hardcoded list.

### 9. **Python Extraction Timeout Not Enforced Properly**
   - **Location**: Line 68-72
   - **Issue**: 
     ```typescript
     const EXTRACTION_HEALTH_TIMEOUT_MS = Number(
       process.env.EXTRACTION_HEALTH_TIMEOUT_MS ?? 
       (process.env.NODE_ENV === 'test' ? 500 : 10000)
     );
     ```
   - **Impact**: Timeout only applies to health check, not actual extraction. Main extraction could hang forever.
   - **Severity**: **HIGH** - Resource leak / DoS
   - **Recommendation**: Apply timeout to all Python spawns, use `child_process.timeout` or kill processes after N seconds.

### 10. **No Request Validation for Query Parameters**
   - **Location**: Line 111, 171
   - **Issue**: 
     ```typescript
     const requestedTier = (req.query.tier as string) || 'enterprise';
     req.query.store === 'true' // String comparison
     ```
   - **Impact**: Tier parameter is unvalidated; `store` flag uses string comparison (fragile).
   - **Severity**: **MEDIUM** - Type safety
   - **Recommendation**: Use Zod/schema validation for all query/body params.

---

## 3. server/db.ts

**Description**: Database connection setup using Drizzle ORM and PostgreSQL (31 lines).

**Critical Functional Issues**:

### 1. **Database Connection Error Silently Swallows Failure**
   - **Location**: Line 11-22
   - **Issue**: 
     ```typescript
     let db: ReturnType<typeof drizzle> | null = null;
     
     if (isDatabaseConfigured) {
       try {
         const pool = new Pool({...});
         db = drizzle(pool, { schema });
       } catch (error) {
         console.error("Failed to initialize database:", error);
         // db remains null, no throw
       }
     }
     ```
   - **Impact**: If database connection fails, `db` is null silently. Subsequent queries will fail with unclear errors.
   - **Severity**: **CRITICAL** - Unreliable initialization
   - **Recommendation**: Throw error on startup failure, or implement retry logic with exponential backoff.

### 2. **DATABASE_URL Configuration Check is Incomplete**
   - **Location**: Line 6-7
   - **Issue**: 
     ```typescript
     const isDatabaseConfigured = process.env.DATABASE_URL && 
       !process.env.DATABASE_URL.includes("user:password@host");
     ```
   - **Impact**: Only checks for placeholder string; doesn't validate connection string format, reachability, or credentials.
   - **Severity**: **MEDIUM** - Unclear errors later
   - **Recommendation**: Add actual connection test, validate URL format, provide clear error messages.

### 3. **Pool Cleanup Function Not Called**
   - **Location**: Line 27-31
   - **Issue**: 
     ```typescript
     export async function closeDatabase() {
       if (db && (db as any).$pool) {
         await (db as any).$pool.end();
       }
     }
     ```
   - **Impact**: `closeDatabase()` is exported but never called. On server shutdown, connections leak.
   - **Severity**: **MEDIUM** - Resource leak
   - **Recommendation**: Call `closeDatabase()` in server shutdown handlers (SIGTERM, graceful shutdown).

### 4. **Type Assertions Bypass Type Safety**
   - **Location**: Line 19, 28
   - **Issue**: 
     ```typescript
     (db as any).$pool = pool; // Unsafe type assertion
     if (db && (db as any).$pool) { // Unsafe access
     ```
   - **Impact**: Bypasses TypeScript, breaks if Drizzle's internal structure changes.
   - **Severity**: **MEDIUM** - Fragility
   - **Recommendation**: Extend Drizzle types properly, or create wrapper class.

### 5. **No Connection Pool Configuration**
   - **Location**: Line 13-14
   - **Issue**: 
     ```typescript
     const pool = new Pool({
       connectionString: process.env.DATABASE_URL,
     });
     ```
   - **Impact**: No pool size limits, connection timeouts, or idle timeout. Under load, pool can exhaust.
   - **Severity**: **HIGH** - Production reliability
   - **Recommendation**: Add pool config:
     ```typescript
     const pool = new Pool({
       connectionString: process.env.DATABASE_URL,
       max: 20, // Max connections
       idleTimeoutMillis: 30000,
       connectionTimeoutMillis: 5000,
     });
     ```

### 6. **No Health Check / Verification**
   - **Location**: Entire file
   - **Issue**: Database connection is never tested after initialization.
   - **Impact**: Server starts successfully but can't query database; errors appear later.
   - **Severity**: **MEDIUM** - Reliability
   - **Recommendation**: Add startup health check:
     ```typescript
     if (db) {
       await db.select().from(users).limit(1); // Test query
     }
     ```

---

## Summary by Severity

### CRITICAL (Business-Breaking / Security)
- Auth: Enterprise default tier for unauthenticated users
- Auth: Tier override vulnerability in login
- Auth: Unprotected `/api/auth/update-tier` endpoint
- Auth: Hard-coded JWT secret
- Extraction: Enterprise default tier
- Extraction: Credit charging happens asynchronously (revenue loss)
- Extraction: Trial enforcement fails silently
- DB: Connection errors swallowed silently

### HIGH (Abuse / DoS / Revenue Risk)
- Auth: No rate limiting on auth endpoints
- Extraction: Trial email not enforced, bypass credits in dev mode
- Extraction: Batch processing has no limits (DoS)
- Extraction: Python timeout not enforced on main extraction
- DB: No connection pool configuration

### MEDIUM (Reliability / Security Hardening)
- Auth: Cookie security (sameSite, secure)
- Auth: No audit logging
- Auth: Subscription refresh failures not handled
- Extraction: Metadata save fails silently
- Extraction: Unvalidated query parameters
- DB: DATABASE_URL validation incomplete
- DB: Pool cleanup never called
- DB: Type assertions bypass safety

### LOW (Maintainability)
- Auth: Minor token expiry edge case
- Extraction: Advanced analysis tier check hardcoded

---

## Recommended Fix Priority

1. **Immediate** (blocks launch):
   - Fix default tiers (enterprise → free/trial)
   - Remove tier override in login
   - Secure `/api/auth/update-tier` endpoint
   - Require JWT_SECRET env var
   - Make credit charging synchronous
   - Make trial recording synchronous
   - Add rate limiting to auth endpoints

2. **Before Production**:
   - Fix database error handling
   - Add connection pool config
   - Implement audit logging
   - Validate all query/body parameters
   - Fix cookie security settings
   - Add batch processing limits

3. **Post-Launch**:
   - Better timeout enforcement
   - Healthcheck endpoints
   - Subscription sync improvements
