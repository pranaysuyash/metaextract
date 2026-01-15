# Audit Artifact: server/utils/session-revocation.ts

## Header

- Audit version: Audit v1.5
- Date/time (local): Thu Jan 15 2026 21:50 UTC
- Audited file path: server/utils/session-revocation.ts
- Base commit SHA (audited): 7a885cfe2024473dbb4f8413e2a78ddb94a892ed (initial commit)
- Auditor identity: opencode (AI assistant)

---

## Discovery Evidence (Raw Outputs)

### A) File Tracking and Context

**Commands executed:**

```bash
git rev-parse --is-inside-work-tree
# Output: true

git ls-files -- server/utils/session-revocation.ts
# Output: server/utils/session-revocation.ts

git status --porcelain -- server/utils/session-revocation.ts
# Output: (empty)
```

**High-signal outcomes:**

- File exists: YES (Observed)
- File tracked by git: YES (Observed)
- No uncommitted changes: YES (Observed)
- File age: Single commit (initial creation, no history of changes)

---

### B) Git History Discovery

**Commands executed:**

```bash
git log -n 20 --follow -- server/utils/session-revocation.ts

git log --follow --name-status -- server/utils/session-revocation.ts | head -30
```

**Outputs:**

```
commit 7a885cfe2024473dbb4f8413e2a78ddb94a892ed
Author: Pranay Suyash <pranay.suyash@gmail.com>
Date:   Mon Jan 12 14:54:40 2026 +0530

    tests(e2e): add visual snapshot assertion for extraction header

A	server/utils/session-revocation.ts
```

**Observations:**

- Only 1 commit in history (initial creation)
- No modifications tracked
- File created as part of e2e tests commit
- No prior versions to compare for regression analysis

**Classification at FILE LEVEL:**

- **unknown** (insufficient history for regression analysis)
- Cannot determine if file has been fixed, regressed, or is partially addressed

---

### C) Inbound and Outbound Reference Discovery

**Outbound dependencies - Commands executed:**

```bash
rg -n --hidden --no-ignore -S "session-revocation|sessionTokens|tokenBlacklist|handleLogoutWithRevocation|handleRevokeAllSessions" server/ --type ts | head -30

rg -n --hidden --no-ignore -S "addToBlacklist|isTokenBlacklisted|revokeSession|revokeAllSessions|storeSessionToken|cleanupExpiredSessions" server/ --type ts | head -30
```

**Outputs:**

```
server/auth.ts:35: handleLogoutWithRevocation,
server/auth.ts:36: handleRevokeAllSessions,
server/auth.ts:37:} from './utils/session-revocation';
server/auth.ts:910:    await handleLogoutWithRevocation(req, res);
server/auth.ts:1151:      await handleRevokeAllSessions(req, res);
```

**Outbound dependencies (Observed):**

- Express from 'express' (line 6)
- crypto from 'crypto' (line 7)
- db from '../db' (line 8)
- userSessions from '@shared/schema' (line 9)
- eq, sql from 'drizzle-orm' (line 10)

**Load-bearing imports (Observed):**

- db (line 8) → Load-bearing: file directly uses db.execute(), db.delete(), DB queries fail without connection
- userSessions (line 9) → Load-bearing: file directly queries userSessions table
- crypto (line 7) → Load-bearing: used for token validation/validation
- eq, sql (line 10) → Load-bearing: required for all DB operations

**Environment variables referenced (Observed):**

- JWT_SECRET (line 12) → Required for token operations, throws error if missing

**Global mutations and side effects (Observed):**

- tokenBlacklist.add() (line 37) → Mutates in-memory Set
- tokenBlacklist.delete() (line 60) → Mutates in-memory Set
- sessionTokens.set() (line 111-116) → Mutates in-memory Map
- sessionTokens.delete() (line 74-76, 94-95, 133-135) → Mutates in-memory Map
- db.delete() (line 70, 91) → Mutates database

**Ordering constraints and lifecycle assumptions (Observed):**

- JWT_SECRET must be set before module imports (throws at line 13-15 if missing)
- db must be initialized before any async function is called (checked implicitly via db calls)
- cleanupExpiredSessions() schedules cleanup on setTimeout (line 138-141)
- cleanupBlacklist() called when tokenBlacklist.size > MAX_BLACKLIST_SIZE (line 40-42)

**Inbound references - Commands executed:**

```bash
rg -n --hidden --no-ignore -S "session-revocation" server/auth.ts

rg -n --hidden --no-ignore -S "addToBlacklist|isTokenBlacklisted|revokeSession|revokeAllSessions|storeSessionToken|cleanupExpiredSessions" server/ --type ts
```

**Outputs:**

```
server/auth.ts:35-37:} from './utils/session-revocation';
server/auth.ts:910:    await handleLogoutWithRevocation(req, res);
server/auth.ts:1151:      await handleRevokeAllSessions(req, res);

server/auth.ts: All function definitions are exported from session-revocation.ts
```

**Inbound references (Observed):**

- server/auth.ts imports from session-revocation.ts:
  - handleLogoutWithRevocation (line 35-37)
  - handleRevokeAllSessions (line 36)

**How they are used (Observed):**

- Import: `import { handleLogoutWithRevocation, handleRevokeAllSessions } from './utils/session-revocation';`
- Call site 1: POST /api/auth/logout (line 910) → calls `await handleLogoutWithRevocation(req, res);`
- Call site 2: POST /api/auth/logout-all (line 1151) → calls `await handleRevokeAllSessions(req, res);`

**What callers likely assume (Inferred):**

- handleLogoutWithRevocation:
  - Will clear auth_token cookie (line 74)
  - Will add current token to blacklist if present in Authorization header (line 63-66)
  - Will revoke all user sessions if userId is available (line 68-71)
  - Will return success JSON response (line 76-79)
- handleRevokeAllSessions:
  - Will revoke all sessions for authenticated user (line 97-104)
  - Will add current token to blacklist (line 206-213)
  - Will return success JSON response (line 215-218)

---

### D) Test Discovery Scoped to This File

**Commands executed:**

```bash
find server -name "*test*session*" -o -name "*session*test*" 2>/dev/null | head -10

rg -n --hidden --no-ignore -S "session-revocation|handleLogoutWithRevocation|handleRevokeAllSessions|logout-all|revoke.*session" tests/ --type ts --type js 2>/dev/null | head -20
```

**Outputs:**

```
tests/security-enhancement-test.js:226:      '/api/auth/logout-all',
```

**Test existence (Observed):**

- No dedicated test files found for session-revocation.ts
- tests/security-enhancement-test.js has a test for '/api/auth/logout-all' endpoint (line 226), but this tests the API endpoint, not the internal revocation logic
- No unit tests found for:
  - addToBlacklist function
  - isTokenBlacklisted function
  - revokeSession function
  - revokeAllUserSessions function
  - storeSessionToken function
  - cleanupExpiredSessions function
- No integration tests found that verify:
  - Blacklisted tokens are rejected
  - Non-blacklisted tokens are accepted
  - Token blacklist cleanup works correctly
  - Session tokens are properly stored and retrieved

---

## Findings

### Finding 1: Token blacklist exists but is not checked in auth.ts token verification (HIGH)

**ID:** F1
**Severity:** HIGH
**Evidence label:** Observed
**Evidence snippet:**

```typescript
// session-revocation.ts, line 18
const tokenBlacklist = new Set<string>();

// session-revocation.ts, line 49-51
export function isTokenBlacklisted(token: string): boolean {
  return tokenBlacklist.has(token);
}

// session-revocation.ts, line 34-37, 164-166, 206-213
export function addToBlacklist(token: string): void { ... }
export function handleLogoutWithRevocation(...) { addToBlacklist(token); ... }
export function handleRevokeAllSessions(...) { addToBlacklist(token); ... }

// server/auth.ts, line 245-252
export function verifyToken(token: string): AuthUser | null {
  try {
    const decoded = jwt.verify(token, JWT_SECRET) as AuthUser;
    return decoded;
  } catch (error) {
    return null;
  }
}
```

**Failure mode:**

- verifyToken in server/auth.ts only decodes JWT signature and expiry
- verifyToken does NOT check if token is in tokenBlacklist
- Even if a user logs out (calls addToBlacklist), the token remains valid until JWT expiry (7 days)
- Attacker with stolen token can continue to access API for up to 7 days after logout
- handleLogoutWithRevocation and handleRevokeAllSessions add tokens to blacklist, but blacklist is never consulted during token verification

**Blast radius:**

- Compromised account takeover persists for up to 7 days after user reports compromise
- Users cannot invalidate individual sessions, only all sessions via logout-all endpoint
- Session revocation feature exists but is not integrated with authentication flow
- Any endpoint using verifyToken (most protected routes) will accept blacklisted tokens

**Suggested minimal fix direction:**

- Import isTokenBlacklisted from session-revocation.ts into server/auth.ts
- Modify verifyToken function to check isTokenBlacklisted before returning user:

  ```typescript
  export function verifyToken(token: string): AuthUser | null {
    // Check if token is revoked first
    if (isTokenBlacklisted(token)) {
      return null;
    }

    try {
      const decoded = jwt.verify(token, JWT_SECRET) as AuthUser;
      return decoded;
    } catch (error) {
      return null;
    }
  }
  ```

- This preserves all existing contract (verifyToken returns AuthUser | null)
- This integrates existing token blacklist with token verification flow

---

### Finding 2: Token blacklist cleanup is never started (MEDIUM)

**ID:** F2
**Severity:** MEDIUM
**Evidence label:** Observed
**Evidence snippet:**

```typescript
// session-revocation.ts, line 56-62
function cleanupBlacklist(): void {
  // Remove oldest tokens (simple FIFO approach)
  const tokensToRemove = Array.from(tokenBlacklist).slice(0, 1000);
  for (const token of tokensToRemove) {
    tokenBlacklist.delete(token);
  }
}

// session-revocation.ts, line 138-141
// Inside cleanupExpiredSessions function
setTimeout(
  () => cleanupBlacklist(),
  REVOCATION_CONFIG.BLACKLIST_CLEANUP_INTERVAL // 1 hour
);
```

**Observation:**

- cleanupExpiredSessions() calls cleanupBlacklist via setTimeout (line 138-141)
- cleanupExpiredSessions() is exported but never called from anywhere
- No entry point triggers cleanupExpiredSessions() to start the scheduled cleanup
- Token blacklist cleanup timer is never started
- Token blacklist will grow unbounded until MAX_BLACKLIST_SIZE is reached (10,000 tokens), then cleanupBlacklist is called from addToBlacklist (line 40-42)

**Failure mode:**

- Token blacklist grows indefinitely until 10,000 tokens accumulated (could take months of activity)
- Memory leak: blacklisted tokens remain in Set until manual cleanup via size threshold
- No automatic cleanup of expired entries (tokens are added to blacklist with no expiry tracking)
- All tokens added to blacklist are permanent (no TTL)
- Even if JWT expires naturally after 7 days, token string remains in Set forever

**Blast radius:**

- Memory leak: Blacklisted tokens accumulate forever until size threshold
- Denial of service: TokenBlacklist Set could grow very large under attack scenarios
- Performance degradation: Adding new tokens requires checking Set size on every addToBlacklist call (line 40)
- No TTL means tokens from 7 days ago still consume memory

**Suggested minimal fix direction:**

- Start cleanupExpiredSessions() when module is imported or when server starts:
  ```typescript
  // At bottom of session-revocation.ts
  cleanupExpiredSessions(); // Start the scheduled cleanup
  ```
- Or move cleanupExpiredSessions call to auth.ts or index.ts where server initializes
- Consider adding token expiry tracking to blacklist (store expiry time with each token)
- Remove expired tokens from blacklist automatically instead of size-based FIFO

---

### Finding 3: Token blacklist uses FIFO cleanup instead of TTL-based cleanup (MEDIUM)

**ID:** F3
**Severity:** MEDIUM
**Evidence label:** Observed
**Evidence snippet:**

```typescript
// session-revocation.ts, line 56-62
function cleanupBlacklist(): void {
  // Remove oldest tokens (simple FIFO approach)
  const tokensToRemove = Array.from(tokenBlacklist).slice(0, 1000);
  for (const token of tokensToRemove) {
    tokenBlacklist.delete(token);
  }
}

// session-revocation.ts, line 21-24
const REVOCATION_CONFIG = {
  BLACKLIST_CLEANUP_INTERVAL: 60 * 60 * 1000, // 1 hour
  MAX_BLACKLIST_SIZE: 10000,
};
```

**Observation:**

- Token blacklist cleanup removes oldest 1000 tokens every time (FIFO)
- No expiry time stored with blacklisted tokens
- Tokens added to blacklist are permanent (no TTL or expiry tracking)
- Even 7-day old JWT tokens remain in blacklist
- cleanupBlacklist is called only when tokenBlacklist.size > MAX_BLACKLIST_SIZE (line 40-42) or from cleanupExpiredSessions (line 138-141)
- cleanupExpiredSessions is never called (Finding F2), so only cleanup trigger is size threshold

**Failure mode:**

- No TTL: Blacklisted tokens persist forever unless manual cleanup is triggered
- Memory waste: Stale JWT tokens (7+ days old) occupy memory indefinitely
- Inefficient cleanup: FIFO removes oldest tokens regardless of whether they're expired or not
- Size threshold of 10,000 must be reached before any cleanup occurs (in production without cleanupExpiredSessions called)
- Under attack, blacklist could grow to 10,000 tokens quickly, consuming memory

**Blast radius:**

- Memory waste: Blacklist contains permanently expired tokens
- Performance impact: Set lookup is O(1) but size impacts memory
- No correlation between JWT expiry (7 days) and blacklist lifetime (permanent)
- Cannot scale: Blacklist grows with active user count, not with token revocations

**Suggested minimal fix direction:**

- Add expiry timestamp to blacklist entries:
  ```typescript
  type BlacklistedToken = { token: string; expiresAt: number };
  const tokenBlacklist = new Map<string, BlacklistedToken>();
  ```
- Modify addToBlacklist to store expiry time based on JWT expiration
- Modify cleanupBlacklist to remove only expired tokens instead of FIFO
- Start cleanupExpiredSessions() to run periodically

---

### Finding 4: No sessionTokens usage tracking or validation (LOW)

**ID:** F4
**Severity:** LOW
**Evidence label:** Observed
**Evidence snippet:**

```typescript
// session-revocation.ts, line 21-24
const sessionTokens = new Map<
  string,
  { token: string; userId: string; expiresAt: number }
>();

// session-revocation.ts, line 111-116
export function storeSessionToken(
  sessionId: string,
  token: string,
  userId: string,
  expiresAt: Date
): void {
  sessionTokens.set(sessionId, {
    token,
    userId,
    expiresAt: expiresAt.getTime(),
  });
}

// session-revocation.ts, line 131-135
// Inside cleanupExpiredSessions
for (const [sessionId, session] of sessionTokens.entries()) {
  if (new Date() > new Date(session.expiresAt)) {
    sessionTokens.delete(sessionId);
  }
}
```

**Observation:**

- sessionTokens Map is defined (line 21-24) and used in storeSessionToken (line 111-116)
- sessionTokens is iterated in cleanupExpiredSessions (line 131-135)
- sessionTokens.delete is called in revokeSession (line 94-95)
- However, sessionTokens Map is never read or queried anywhere else in this file
- sessionTokens is not exported from this file
- No function exists to retrieve a session token by sessionId
- sessionTokens is not used by auth.ts or any other file (Inferred from rg search: no references found)

**Failure mode:**

- sessionTokens data structure is defined but useless
- No way to retrieve stored session tokens
- sessionTokens storage is never validated or verified
- revokeSession removes from sessionTokens but there's no consumer of the data
- Unclear what sessionTokens is intended for - appears to be dead code or incomplete implementation

**Blast radius:**

- Confusing code structure (why store data that's never read?)
- Wasted memory (sessionTokens Map grows but is never used)
- Code complexity (maintenance burden for unused data structure)
- No observability (no logging of sessionTokens size or operations)

**Suggested minimal fix direction:**

- If sessionTokens is intentionally unused, remove it entirely (lines 21-24, 111-116, 131-135, 73-76)
- If sessionTokens is meant to be used, add a getSessionToken function to retrieve data:
  ```typescript
  export function getSessionToken(
    sessionId: string
  ): StoredSessionToken | undefined {
    return sessionTokens.get(sessionId);
  }
  ```
- Export getSessionToken and document its usage
- Add tests to verify sessionTokens lifecycle

---

### Finding 5: Blacklist validation accepts empty or very short tokens (LOW)

**ID:** F5
**Severity:** LOW
**Evidence label:** Observed
**Evidence snippet:**

```typescript
// session-revocation.ts, line 34-38
export function addToBlacklist(token: string): void {
  if (token && token.length > 20) {
    // Basic validation
    tokenBlacklist.add(token);
```

**Observation:**

- addToBlacklist only checks if token exists and token.length > 20
- No minimum length check (token could be 21 characters but maliciously crafted)
- No format validation (JWT tokens are typically 3 parts separated by dots, should be longer than 20 chars)
- No upper bound on token length (could add 1000-character strings to Set)
- Validation only checks token is truthy and > 20 chars, doesn't validate JWT structure
- Empty strings or whitespace tokens could pass validation if token.length > 20 (e.g., " " (space x 21))

**Failure mode:**

- Invalid tokens could be added to blacklist
- Malicious inputs could poison blacklist with long strings
- No structural validation ensures blacklist only contains valid-looking tokens
- Potential for cache poisoning or memory exhaustion if attacker controls token values

**Blast radius:**

- Blacklist pollution with invalid tokens
- Memory waste (Set storing garbage strings)
- Performance degradation (Set.contains() checking invalid tokens)
- No guarantee blacklisted tokens are actually JWT strings

**Suggested minimal fix direction:**

- Add proper JWT token format validation:
  ```typescript
  function isValidJWTFormat(token: string): boolean {
    const parts = token.split('.');
    return parts.length === 3; // JWT has 3 parts: header.payload.signature
  }
  ```
- Add to addToBlacklist validation:
  ```typescript
  if (token && token.length > 20 && isValidJWTFormat(token)) {
    tokenBlacklist.add(token);
  }
  ```
- Add maximum length check to prevent memory exhaustion attacks

---

### Finding 6: No process signal handlers for cleanup on shutdown (MEDIUM)

**ID:** F6
**Severity:** MEDIUM
**Evidence label:** Observed
**Evidence snippet:**

```typescript
// session-revocation.ts, line 138-141
// Inside cleanupExpiredSessions
setTimeout(
  () => cleanupBlacklist(),
  REVOCATION_CONFIG.BLACKLIST_CLEANUP_INTERVAL // 1 hour
);

// No process.on('SIGTERM') or process.on('SIGINT') handlers found in file
```

**Observation:**

- cleanupExpiredSessions schedules a cleanup via setTimeout (line 138-141)
- setTimeout creates a timer that is not cleared on process exit
- No process signal handlers to cancel scheduled cleanup
- If server is hot-reloaded (nodemon, tsx watch), multiple setTimeout timers could accumulate
- Each timer would run cleanupBlacklist() every hour, creating multiple overlapping cleanup operations
- No cleanup of sessionTokens Map, tokenBlacklist Set, or sessionTokens.entries() iteration state

**Failure mode:**

- Memory leak: Multiple timers accumulate on hot-reload
- Timer conflicts: Multiple cleanup functions running simultaneously
- Resource leak: Set and Map not cleaned on process exit
- In development: Multiple cleanup cycles cause performance degradation

**Blast radius:**

- Development: Hot-reload scenarios create multiple timers
- Production: Server shutdown doesn't clean up scheduled cleanup
- Performance: Duplicate cleanup operations waste CPU
- Debugging: Hard to track which cleanup operation is active

**Suggested minimal fix direction:**

- Store setTimeout ID and clear it in process signal handlers:

  ```typescript
  let cleanupTimer: NodeJS.Timeout | null = null;

  export function cleanupExpiredSessions(): Promise<void> {
    // ... existing cleanup logic ...

    // Store timer reference
    cleanupTimer = setTimeout(
      () => cleanupBlacklist(),
      REVOCATION_CONFIG.BLACKLIST_CLEANUP_INTERVAL
    );
  }

  // Add at bottom of file
  process.on('SIGTERM', () => {
    if (cleanupTimer) clearTimeout(cleanupTimer);
  });

  process.on('SIGINT', () => {
    if (cleanupTimer) clearTimeout(cleanupTimer);
  });
  ```

- Or move cleanup scheduling to a proper job scheduler that handles shutdown

---

### Finding 7: Error handling logs errors but doesn't prevent invalid state (LOW)

**ID:** F7
**Severity:** LOW
**Evidence label:** Observed
**Evidence snippet:**

```typescript
// session-revocation.ts, line 67-72, 80-85, 96-99, 119-125, 136-146
try {
  // ... operation ...
  console.log('...');
} catch (error) {
  console.error('Error revoking user sessions:', error);
}

// session-revocation.ts, line 80-86
} catch (error) {
  console.error('Logout with revocation error:', error);
  res.status(500).json({ // continues processing, returns error response
```

**Observation:**

- All async functions have try-catch blocks (good)
- Errors are logged with console.error (good)
- However, error responses are sent to client (res.status(500).json(...)) but execution continues
- Line 80-86 shows response is sent inside catch block, which should end the request
- No guarantee that invalid state isn't persisted after error (e.g., partial DB delete)
- No transaction rollback mechanism if DB operations fail mid-way
- No validation that userSessions entry was actually deleted after revokeAllUserSessions

**Failure mode:**

- Inconsistent state: Partial DB operations may leave data corruption
- Security risk: Revocation might appear to succeed (200 response) but actually failed
- No transaction: If db.delete(userSessions) succeeds but sessionTokens.delete fails, state is inconsistent
- Orphaned data: userSessions row might not be deleted despite successful HTTP response

**Blast radius:**

- Data inconsistency: Sessions marked as revoked but still in database
- Security bypass: User might still have active session after revocation attempt
- Silent failures: Errors are logged but not flagged for monitoring/alerting
- Recovery issues: No mechanism to retry failed revocations

**Suggested minimal fix direction:**

- Use database transactions for revocation operations to ensure atomicity:
  ```typescript
  await db.transaction(async tx => {
    await tx.delete(userSessions).where(eq(userSessions.userId, userId));
    // ... update sessionTokens ...
  });
  ```
- Add explicit early return after sending error response to prevent double-sends
- Add monitoring/alerting for revocation failures
- Consider adding health check to verify revocation was successful

---

## Out-of-Scope Findings

None identified in this audit. All findings are within the file's scope and relate to core session revocation functionality.

---

## Inter-File Impact Analysis

### 9.1 Inbound Impact

**Which callers could break if this file changes:**

- server/auth.ts (lines 35-37, 910, 1151)
  - Imports: handleLogoutWithRevocation, handleRevokeAllSessions
  - Calls: POST /api/auth/logout, POST /api/auth/logout-all
  - **What would break:**
    - If handleLogoutWithRevocation signature changes (parameters, return type)
    - If handleLogoutWithRevocation behavior changes (e.g., stops clearing auth_token cookie)
    - If handleRevokeAllSessions signature changes
    - If exported functions are renamed or removed

**Which implicit contracts must be preserved:**

For handleLogoutWithRevocation:

- Must clear auth_token cookie (line 74) - callers expect session invalidation
- Must add current token to blacklist if present in Authorization header (line 63-66)
- Must revoke all user sessions if userId is available (line 68-71)
- Must return success JSON response with specific format (line 76-79)
- Must handle case where req.user is null (lines 57-60)
- Must handle case where token is not in Authorization header (lines 57-60)

For handleRevokeAllSessions:

- Must require authentication (check req.user exists, line 97-104)
- Must revoke all user sessions from database (line 70)
- Must remove from in-memory storage (line 73-76)
- Must add current token to blacklist (line 206-213)
- Must return success JSON response with specific format (line 215-218)
- Must return 401 if not authenticated (line 199-201)

**What must be protected by tests:**

- Logout clears cookie and adds token to blacklist
- Logout returns 200 with success message
- Logout-all requires authentication (401 if not authenticated)
- Logout-all revokes all sessions
- Revoked tokens are rejected during authentication
- Blacklist size doesn't grow unbounded

### 9.2 Outbound Impact

**Which dependencies could break this file if they change:**

- drizzle-orm (eq, sql) (line 10)
  - If db.query syntax changes (sql template literals)
  - If db transaction API changes
  - If eq() return type changes
- @shared/schema (userSessions) (line 9)
  - If userSessions table structure changes (column names, types)
  - If userSessions table is removed or renamed
  - If schema type generation changes
- Express (Request, Response) (line 6)
  - If Request interface changes (e.g., req.headers.authorization)
  - If Response interface changes (e.g., res.clearCookie, res.json, res.status)
- crypto from 'crypto' (line 7)
  - If crypto module API changes (unlikely but possible)
- db from '../db' (line 8)
  - If db connection initialization changes
  - If db object structure changes

**Which assumptions are unsafe or unenforced:**

- JWT_SECRET exists in environment (checked at line 12-15, throws if missing) - SAFE
- Database is initialized before async functions called (checked implicitly via db calls) - UNSAFE
  - If db is null, db.delete() and db.execute() will throw
  - No null check before DB operations in this file
  - Assumption: db is always available
- userSessions table exists in database (queried directly via schema) - UNSAFE
  - If table doesn't exist, queries will fail
  - No table existence check before operations
- Response methods (clearCookie, json, status) don't throw - SAFE
- Map/Set methods don't throw under normal usage - SAFE
- Authorization header format is always "Bearer <token>" - PARTIALLY SAFE
  - Code handles case where header is missing (line 57-60)
  - Doesn't validate format if present but not "Bearer "
  - Could accept invalid Authorization header formats

---

### 9.3 Change Impact Per Finding

**For F1: Token blacklist exists but is not checked in auth.ts**

- Could fixing it break callers: NO (Inferred)
  - Adding isTokenBlacklisted check to verifyToken preserves contract
  - verifyToken still returns AuthUser | null
  - Blacklisted tokens return null (invalid), same as expired tokens
  - No change to response format or status codes

- Could callers invalidate the fix: NO (Inferred)
  - Callers only receive AuthUser | null from verifyToken
  - Callers don't know if token was rejected for expiry vs blacklist
  - Contract is preserved

- What contract must be locked with tests:
  - Blacklisted token is rejected during authentication
  - Non-blacklisted token is accepted
  - Blacklist check happens before JWT verification
  - Tests must cover both scenarios

- Post-fix invariants to lock (Observed):
  - verifyToken returns null for blacklisted tokens
  - verifyToken returns AuthUser for valid non-blacklisted tokens
  - Blacklisted tokens are rejected across all protected endpoints

**For F2: Token blacklist cleanup is never started**

- Could fixing it break callers: NO (Inferred)
  - Starting cleanupExpiredSessions() is additive
  - No change to existing function signatures
  - No change to behavior except periodic cleanup

- Could callers invalidate the fix: NO (Inferred)
  - Callers don't know cleanup runs
  - Cleanup is internal to this module
  - No contract depends on cleanup not running

- What contract must be locked with tests:
  - Token blacklist doesn't grow unbounded
  - Cleanup runs periodically (hourly)
  - Cleanup removes old/expired tokens
  - Blacklist size stays manageable

- Post-fix invariants to lock (Observed):
  - cleanupExpiredSessions is called on module load
  - Token blacklist size stays < MAX_BLACKLIST_SIZE in normal operation
  - Memory usage of blacklist is bounded

**For F3: Token blacklist uses FIFO cleanup instead of TTL-based**

- Could fixing it break callers: NO (Inferred)
  - Changing cleanup algorithm is internal to module
  - Callers don't know how cleanup works
  - No contract depends on FIFO vs TTL

- Could callers invalidate the fix: NO (Inferred)
  - Callers only see addToBlacklist, isTokenBlacklisted functions
  - Internal cleanup strategy doesn't affect API

- What contract must be locked with tests:
  - Expired tokens are removed from blacklist
  - Blacklist doesn't waste memory on stale tokens
  - Cleanup algorithm scales with token revocation rate

- Post-fix invariants to lock (Observed):
  - Blacklist entries have expiry timestamps
  - Cleanup removes expired entries, not just oldest
  - Memory usage is proportional to active revoked tokens, not total history

**For F4: No sessionTokens usage tracking or validation**

- Could fixing it break callers: YES (Inferred)
  - If sessionTokens is removed entirely, no impact (no callers use it)
  - If getSessionToken function is added and exported, could break if other files already import non-existent function
  - If sessionTokens behavior changes (storage format), breaks any future usage

- Could callers invalidate the fix: NO (Inferred)
  - No callers use sessionTokens currently
  - Adding export is safe (backwards compatible if signature is clear)

- What contract must be locked with tests:
  - If sessionTokens is used, retrieval works correctly
  - If sessionTokens is removed, no regression in auth.ts
  - Memory usage is bounded

- Post-fix invariants to lock (Observed):
  - sessionTokens is either used (with retrieval function) or removed entirely
  - No unused data structures remain in memory
  - Clear purpose for sessionTokens Map is documented

**For F5: Blacklist validation accepts empty or very short tokens**

- Could fixing it break callers: NO (Inferred)
  - Stricter validation is additive
  - Only affects which tokens get into blacklist
  - Doesn't change addToBlacklist or isTokenBlacklisted signatures

- Could callers invalidate the fix: NO (Inferred)
  - Callers don't control what gets added to blacklist
  - Validation happens internally before Set.add()

- What contract must be locked with tests:
  - Blacklist only contains valid-looking JWT tokens
  - Invalid tokens are rejected at addToBlacklist
  - No memory exhaustion from malicious token values

- Post-fix invariants to lock (Observed):
  - addToBlacklist validates token format (3 parts, reasonable length)
  - Blacklist doesn't contain garbage data
  - No empty or whitespace-only tokens in blacklist

**For F6: No process signal handlers for cleanup on shutdown**

- Could fixing it break callers: NO (Inferred)
  - Adding signal handlers is additive
  - No change to function signatures
  - No change to behavior except on process termination

- Could callers invalidate the fix: NO (Inferred)
  - Callers don't control process signals
  - Signal handlers are internal to module

- What contract must be locked with tests:
  - No timer accumulation on hot-reload
  - Resources cleaned up on shutdown
  - Cleanup works correctly on SIGTERM/SIGINT

- Post-fix invariants to lock (Observed):
  - Single cleanup timer active at any time
  - Timers are cleared on process signals
  - No resource leaks on server shutdown

**For F7: Error handling logs errors but doesn't prevent invalid state**

- Could fixing it break callers: NO (Inferred)
  - Better error handling is additive
  - Adding transactions doesn't change function signatures
  - Early return after error response prevents double-sends

- Could callers invalidate the fix: NO (Inferred)
  - Callers only care about response status and message
  - Better internal state management doesn't affect API contract

- What contract must be locked with tests:
  - Revocation operations are atomic (all-or-nothing)
  - Failed revocations don't leave partial state
  - Error responses are sent correctly

- Post-fix invariants to lock (Observed):
  - DB operations for revocation are transactional
  - In-memory state and DB state stay consistent
  - Errors are recoverable or properly propagated

---

## Clean Architecture Fit

### What Belongs Here (Core Responsibilities)

**Session and token revocation:**

- addToBlacklist: Adding tokens to blacklist ✓
- isTokenBlacklisted: Checking if token is revoked ✓
- cleanupBlacklist: Removing old tokens from blacklist ✓
- handleLogoutWithRevocation: Logout with token revocation ✓
- handleRevokeAllSessions: Revoking all user sessions ✓
- storeSessionToken: Storing session tokens ✓
- cleanupExpiredSessions: Cleaning expired sessions ✓

**State management:**

- tokenBlacklist Set: In-memory storage for revoked tokens ✓
- sessionTokens Map: In-memory storage for session data (currently unused)

**Integration with other modules:**

- Database operations (userSessions table) ✓
- JWT handling (token validation is in auth.ts, not here) ✓
- Cookie management (clearing auth_token cookie) ✓

### What Does Not Belong Here (Responsibility Leakage)

**Dead code / unused structures:**

- sessionTokens Map (lines 21-24, 111-116, 131-135, 73-76):
  - Defined but never exported
  - Never read or queried
  - Only written to and deleted from
  - Purpose unclear - appears to be incomplete implementation
  - Should be removed or completed with getSessionToken export

**Cleanup responsibility:**

- cleanupExpiredSessions (lines 121-147):
  - Contains DB cleanup (userSessions table deletion) AND in-memory cleanup (sessionTokens)
  - AND schedules token blacklist cleanup via setTimeout
  - Multiple responsibilities in one function
  - Should be split into:
    - cleanupExpiredSessionsFromDB(): For userSessions table
    - cleanupExpiredSessionTokens(): For sessionTokens Map
    - cleanupExpiredBlacklist(): For tokenBlacklist Set

**Validation responsibility:**

- Basic token length check in addToBlacklist (line 36) (LOW severity issue):
  - Only checks token.length > 20
  - Should validate JWT structure (3 parts)
  - Should have max length check to prevent memory exhaustion

\*\*Lack of TTL in tokenBlacklist (F3):

- Token blacklist has no expiry timestamps
- Relies on FIFO size-based cleanup instead of time-based
- Should track token expiry and remove expired tokens automatically

\*\*Missing transaction safety (F7):

- Database operations not wrapped in transactions
- No rollback mechanism for partial failures
- Should use db.transaction() for atomic revocation operations

---

## Patch Plan (Actionable, Scoped)

### HIGH Priority

**Fix F1: Integrate token blacklist check into verifyToken**

- Where: server/auth.ts, verifyToken function (lines 245-252)
- What: Import isTokenBlacklisted from session-revocation.ts and add check before JWT verification
- Why: Blacklisted tokens are currently accepted as valid, enabling account takeover for up to 7 days after logout
- Failure it prevents: Compromised tokens remain valid after revocation, bypassing session management
- Invariant(s) it must preserve:
  - verifyToken returns AuthUser | null (contract unchanged)
  - Blacklisted tokens return null (rejection)
  - Non-blacklisted tokens return AuthUser (acceptance)
  - No change to public API contract
- Test that proves it:
  - Test name: `shouldRejectBlacklistedToken`
  - Test: Login to get token, logout to add to blacklist, then try to use blacklisted token - expect 401
  - Test: Non-blacklisted token should still work normally
  - Verification: Run curl commands or write unit test asserting 401 for blacklisted token

**Implementation:**

```typescript
// In server/auth.ts
import { isTokenBlacklisted } from './utils/session-revocation';

export function verifyToken(token: string): AuthUser | null {
  // Check if token is revoked first
  if (isTokenBlacklisted(token)) {
    return null;
  }

  try {
    const decoded = jwt.verify(token, JWT_SECRET) as AuthUser;
    return decoded;
  } catch (error) {
    return null;
  }
}
```

---

### MEDIUM Priority

**Fix F2: Start cleanupExpiredSessions on module load**

- Where: server/utils/session-revocation.ts, end of file (after line 227)
- What: Call cleanupExpiredSessions() to start the scheduled cleanup timer
- Why: Cleanup function exists but is never called, causing blacklist to grow unbounded
- Failure it prevents: Token blacklist grows indefinitely until MAX_BLACKLIST_SIZE (10,000) is reached, causing memory leak
- Invariant(s) it must preserve:
  - Token blacklist cleanup runs periodically (hourly)
  - Blacklist size stays manageable in production
  - No timer accumulation on hot-reload
- Test that proves it:
  - Test name: `shouldCleanupExpiredSessionsOnStartup`
  - Test: Add 1000 tokens to blacklist, wait > 1 hour, verify blacklist size decreased
  - Verification: Check tokenBlacklist.size before and after cleanup interval

**Implementation:**

```typescript
// At bottom of server/utils/session-revocation.ts
// Start the scheduled cleanup
cleanupExpiredSessions();
```

**Fix F3: Add TTL to token blacklist and time-based cleanup**

- Where: server/utils/session-revocation.ts, tokenBlacklist definition and cleanupBlacklist function
- What: Change tokenBlacklist from Set<string> to Map<string, number> (storing expiry), modify cleanupBlacklist to remove expired entries
- Why: FIFO cleanup is inefficient, removes newest tokens instead of expired ones; tokens persist forever
- Failure it prevents: Memory waste on stale JWT tokens (7+ days old), no correlation with JWT expiry
- Invariant(s) it must preserve:
  - Blacklist entries have expiry timestamps
  - Cleanup removes expired entries, not just oldest
  - Memory usage proportional to active revoked tokens
- Test that proves it:
  - Test name: `shouldCleanupExpiredTokensFromBlacklist`
  - Test: Add token with expiry 7 days ago, run cleanup, verify token removed
  - Test: Add token with expiry 8 days in future, run cleanup, verify token retained
  - Verification: Check tokenBlacklist.size and specific tokens before/after

**Implementation:**

```typescript
// Change type definition (line 18):
type BlacklistedToken = { token: string; expiresAt: number };
const tokenBlacklist = new Map<string, BlacklistedToken>();

// Modify addToBlacklist (line 34-44):
export function addToBlacklist(token: string, expiresAt?: Date): void {
  if (!token || token.length <= 20) {
    return;
  }

  // Default expiry to 7 days if not provided
  const expiry = expiresAt?.getTime() || Date.now() + 7 * 24 * 60 * 60 * 1000;

  tokenBlacklist.set(token, { token, expiresAt: expiry });

  // Clean up old tokens if blacklist gets too large
  if (tokenBlacklist.size > REVOCATION_CONFIG.MAX_BLACKLIST_SIZE) {
    cleanupBlacklist();
  }
}

// Modify cleanupBlacklist (line 56-62):
function cleanupBlacklist(): void {
  const now = Date.now();

  // Remove expired tokens (not FIFO)
  for (const [token, data] of tokenBlacklist.entries()) {
    if (data.expiresAt < now) {
      tokenBlacklist.delete(token);
    }
  }

  // If still too large after cleanup, remove oldest 1000
  if (tokenBlacklist.size > REVOCATION_CONFIG.MAX_BLACKLIST_SIZE) {
    const tokensToRemove = Array.from(tokenBlacklist.entries()).slice(0, 1000);
    for (const [token, _] of tokensToRemove) {
      tokenBlacklist.delete(token);
    }
  }
}
```

**Fix F6: Add process signal handlers to clear timers**

- Where: server/utils/session-revocation.ts, cleanupExpiredSessions function (lines 121-147)
- What: Store setTimeout ID and add process.on('SIGTERM') and process.on('SIGINT') handlers to clear it
- Why: Scheduled cleanup never stops on server shutdown, causing timer accumulation on hot-reload
- Failure it prevents: Memory leak from accumulated timers, resource leaks on shutdown
- Invariant(s) it must preserve:
  - Single cleanup timer active at any time
  - Timers cleared on process signals
  - No resource leaks on server shutdown
- Test that proves it:
  - Test name: `shouldClearTimersOnShutdown`
  - Test: Simulate SIGTERM signal, verify timer is cleared
  - Test: In development, trigger hot-reload, verify no multiple timers
  - Verification: Check that clearTimeout is called, no duplicate timers after restart

**Implementation:**

```typescript
// Add at module scope (after REVOCATION_CONFIG, line 29):
let cleanupTimer: NodeJS.Timeout | null = null;

// Modify cleanupExpiredSessions (line 121-147):
export async function cleanupExpiredSessions(): Promise<void> {
  try {
    const now = new Date();

    // Clean up database
    await db
      .delete(userSessions)
      .where(sql`${userSessions.expiresAt} < ${now}`);

    // Clean up in-memory storage
    for (const [sessionId, session] of sessionTokens.entries()) {
      if (new Date() > new Date(session.expiresAt)) {
        sessionTokens.delete(sessionId);
      }
    }

    // Clean up blacklist periodically
    cleanupTimer = setTimeout(
      () => cleanupBlacklist(),
      REVOCATION_CONFIG.BLACKLIST_CLEANUP_INTERVAL // 1 hour
    );

    console.log('Cleaned up expired sessions');
  } catch (error) {
    console.error('Error cleaning up expired sessions:', error);
  }
}

// Add at bottom of file (after line 227):
process.on('SIGTERM', () => {
  if (cleanupTimer) {
    clearTimeout(cleanupTimer);
  }
});

process.on('SIGINT', () => {
  if (cleanupTimer) {
    clearTimeout(cleanupTimer);
  }
});
```

**Fix F4: Remove or complete sessionTokens implementation**

- Where: server/utils/session-revocation.ts, sessionTokens Map definition and related functions (lines 21-24, 111-116, 131-135, 73-76)
- What: Either remove unused sessionTokens entirely OR add getSessionToken export and document usage
- Why: sessionTokens is defined but never read/exported, wasting memory and creating confusion
- Failure it prevents: Code complexity, wasted memory, unclear intent
- Invariant(s) it must preserve:
  - If removed: No regression in auth.ts (no callers use sessionTokens)
  - If completed: sessionTokens is queryable via getSessionToken
  - No unused data structures remain
- Test that proves it:
  - Test name: `shouldRemoveUnusedSessionTokens`
  - Test: Verify sessionTokens doesn't exist or is properly used
  - Test: If completed, verify getSessionToken returns correct data
  - Verification: Check memory usage before/after removal or check exported function works

**Implementation (Option A - Remove):**

```typescript
// Remove these lines: 21-24, 111-116, 131-135

// Also remove sessionTokens references in other functions:
// Line 73-76: Delete from revokeSession
// Line 111-116: Delete storeSessionToken
// Line 131-135: Delete from cleanupExpiredSessions loop
```

**Implementation (Option B - Complete):**

```typescript
// Add export (after line 110):
export function getSessionToken(
  sessionId: string
): StoredSessionToken | undefined {
  return sessionTokens.get(sessionId);
}

// Document purpose: Store session tokens for potential future use
```

**Fix F5: Improve blacklist validation**

- Where: server/utils/session-revocation.ts, addToBlacklist function (lines 34-44)
- What: Add JWT format validation (3 parts) and max length check
- Why: Current validation only checks token.length > 20, accepts garbage/invalid tokens
- Failure it prevents: Blacklist pollution with invalid tokens, memory exhaustion attacks
- Invariant(s) it must preserve:
  - Blacklist only contains valid-looking JWT tokens
  - No empty or malformed tokens in blacklist
  - Memory bounded by max token length
- Test that proves it:
  - Test name: `shouldValidateTokenFormatBeforeBlacklist`
  - Test: Try to add invalid token (1 part, empty, very long), verify rejected
  - Test: Try to add valid JWT token, verify accepted
  - Verification: Check tokenBlacklist contains only valid tokens
- Implementation requires isValidJWTFormat helper function

**Fix F7: Add transaction safety to revocation operations**

- Where: server/utils/session-revocation.ts, revokeAllUserSessions and handleRevokeAllSessions (lines 67-72, 96-99)
- What: Wrap DB delete operations in db.transaction() for atomicity
- Why: No transaction means partial failures can leave inconsistent state (DB deleted but in-memory not updated, or vice versa)
- Failure it prevents: Data corruption, security bypass (partial revocation), silent failures
- Invariant(s) it must preserve:
  - DB operations and in-memory operations are atomic (all-or-nothing)
  - Failed revocations don't leave partial state
  - Error responses reflect actual outcome
- Test that proves it:
  - Test name: `shouldUseTransactionForRevocation`
  - Test: Simulate DB failure mid-transaction, verify rollback
  - Test: Verify session exists in DB after successful revocation
  - Verification: Check transaction is used, rollback on error, atomicity maintained

**Implementation:**

```typescript
// Modify revokeAllUserSessions (lines 67-72):
export async function revokeAllUserSessions(userId: string): Promise<void> {
  try {
    await db.transaction(async tx => {
      await tx.delete(userSessions).where(eq(userSessions.userId, userId));
    });

    // Remove from in-memory storage
    for (const [sessionId, session] of sessionTokens.entries()) {
      if (session.userId === userId) {
        sessionTokens.delete(sessionId);
      }
    }

    console.log(`Revoked all sessions for user: ${userId}`);
  } catch (error) {
    console.error('Error revoking user sessions:', error);
    throw error; // Re-throw to ensure caller handles failure
  }
}
```

---

## Verification and Test Coverage

### Tests That Exist Touching This File (Observed)

- tests/security-enhancement-test.js: Contains test for '/api/auth/logout-all' endpoint (line 226)
  - Test hits the API endpoint, not internal revocation logic
  - Does not verify token blacklist functionality
  - Does not verify cleanupExpiredSessions behavior
  - Does not verify sessionTokens lifecycle

### Critical Paths Untested

**Token revocation flow:**

- Blacklisted tokens are rejected during authentication (NOT TESTED)
  - verifyToken doesn't check isTokenBlacklisted
  - Need integration test: login → logout → try to use blacklisted token → expect 401
- addToBlacklist functionality (NOT TESTED)
  - No unit tests for adding tokens to blacklist
  - No tests for validation (token.length > 20)
  - No tests for max size cleanup trigger
- isTokenBlacklisted functionality (NOT TESTED)
  - No unit tests for Set.has() lookup
  - Need tests for blacklisted token returns true
  - Need tests for non-blacklisted token returns false

**Cleanup functionality:**

- cleanupExpiredSessions is never called (NOT TESTED)
  - No startup tests that verify cleanup begins
  - No tests that blacklist size decreases over time
  - No tests that expired tokens are removed
- cleanupBlacklist FIFO logic (NOT TESTED)
  - No tests for size-based cleanup trigger
  - No tests that oldest tokens are removed
  - No tests for MAX_BLACKLIST_SIZE boundary conditions
- cleanupBlacklist time-based logic (NOT IMPLEMENTED YET)
  - No TTL tracking
  - No tests for expired token removal
  - No tests for expiry-based cleanup efficiency

**Session management:**

- revokeAllUserSessions atomicity (NOT TESTED)
  - No transaction tests
  - No tests for partial failure scenarios
  - No tests for rollback behavior
- handleLogoutWithRevocation (NOT TESTED)
  - No integration tests for logout flow
  - No tests that token is added to blacklist
  - No tests that cookie is cleared
- handleRevokeAllSessions (NOT TESTED)
  - No integration tests for logout-all flow
  - No tests that all sessions are revoked
  - No tests that DB and in-memory stay consistent

**Error handling:**

- Error responses (NOT TESTED)
  - No tests for 500 error handling
  - No tests for error message format
  - No tests that double-send is prevented

**Process lifecycle:**

- Signal handlers (NOT TESTED)
  - No tests for SIGTERM/SIGINT behavior
  - No tests for timer cleanup on shutdown
  - No tests for hot-reload scenarios

**Unused code:**

- sessionTokens Map (NOT TESTED)
  - No tests proving sessionTokens is unused or used correctly
  - No memory leak tests for sessionTokens
  - No tests for getSessionToken (if implemented)

### Assumed Invariants Not Enforced

- Token blacklist is checked before accepting authentication (NOT ENFORCED)
  - Invariant: verifyToken calls isTokenBlacklisted
  - Risk: Blacklisted tokens bypass security (F1 - HIGH)
- Cleanup runs periodically (NOT ENFORCED)
  - Invariant: cleanupExpiredSessions is called on startup
  - Risk: Blacklist grows unbounded (F2 - MEDIUM)
- Token blacklist cleanup removes expired entries (NOT ENFORCED)
  - Invariant: Expired tokens are removed based on JWT expiry
  - Risk: Memory waste on stale tokens (F3 - MEDIUM)
- Revocation operations are atomic (NOT ENFORCED)
  - Invariant: DB and in-memory operations are transactional
  - Risk: Partial state on failure (F7 - LOW)
- No timer accumulation on hot-reload (NOT ENFORCED)
  - Invariant: Only one cleanup timer exists at a time
  - Risk: Timer leaks (F6 - MEDIUM)
- sessionTokens is used or removed (NOT ENFORCED)
  - Invariant: sessionTokens has clear purpose or is removed
  - Risk: Code confusion, wasted memory (F4 - LOW)

### Proposed Specific Tests Tied to Patch Plan

**Test 1: shouldRejectBlacklistedToken (for F1)**

```typescript
// Integration test
test('should reject blacklisted token', async () => {
  // Register user
  const registerRes = await request(app).post('/api/auth/register').send({
    email: 'test@example.com',
    username: 'testuser',
    password: 'Test123!',
  });

  const token = registerRes.body.token;

  // Logout to blacklist token
  await request(app)
    .post('/api/auth/logout')
    .set('Cookie', `auth_token=${token}`);

  // Try to use blacklisted token
  const response = await request(app)
    .get('/api/auth/me')
    .set('Cookie', `auth_token=${token}`);

  expect(response.status).toBe(401);
  expect(response.body.error).toBeDefined();
});
```

**Test 2: shouldCleanupExpiredSessionsOnStartup (for F2)**

```typescript
// Unit test
test('cleanupExpiredSessions starts on module load', async () => {
  // Mock DB and timers
  const mockSetTimeout = jest.spyOn(global, 'setTimeout');
  const mockDb = {
    delete: jest.fn().mockResolvedValue(undefined),
    execute: jest.fn().mockResolvedValue(undefined),
  };

  // Import module (triggers startup)
  await import('./session-revocation');

  // Verify setTimeout was called
  expect(mockSetTimeout).toHaveBeenCalledWith(
    expect.any(Function),
    REVOCATION_CONFIG.BLACKLIST_CLEANUP_INTERVAL
  );
});
```

**Test 3: shouldCleanupExpiredTokensFromBlacklist (for F3)**

```typescript
// Unit test
test('cleanupBlacklist removes expired tokens', () => {
  // Add token expired 7 days ago
  const expiredToken = 'expired.jwt.token';
  const expiresAt = Date.now() - 7 * 24 * 60 * 60 * 1000;

  addToBlacklist(expiredToken, new Date(expiresAt));

  // Add valid token
  const validToken = 'valid.jwt.token';
  const futureExpiry = Date.now() + 7 * 24 * 60 * 60 * 1000;
  addToBlacklist(validToken, new Date(futureExpiry));

  // Run cleanup
  cleanupBlacklist();

  // Verify expired token removed, valid token retained
  expect(isTokenBlacklisted(expiredToken)).toBe(false);
  expect(isTokenBlacklisted(validToken)).toBe(true);
});
```

**Test 4: shouldClearTimersOnShutdown (for F6)**

```typescript
// Unit test
test('timers are cleared on SIGTERM', async () => {
  const mockClearTimeout = jest.spyOn(global, 'clearTimeout');

  // Load module
  await import('./session-revocation');

  // Simulate SIGTERM
  process.emit('SIGTERM');

  // Verify clearTimeout was called
  expect(mockClearTimeout).toHaveBeenCalledWith(expect.anything());
});
```

**Test 5: shouldRemoveUnusedSessionTokens (for F4)**

```typescript
// Unit test (if Option B - add getSessionToken)
test('getSessionToken retrieves stored session', () => {
  const sessionId = 'test-session-id';
  const token = 'test-token';
  const userId = 'test-user-id';
  const expiresAt = new Date();

  storeSessionToken(sessionId, token, userId, expiresAt);

  const retrieved = getSessionToken(sessionId);

  expect(retrieved).toEqual({
    token,
    userId,
    expiresAt: expiresAt.getTime(),
  });
});
```

**Test 6: shouldUseTransactionForRevocation (for F7)**

```typescript
// Integration test
test('revocation operations are atomic', async () => {
  const userId = 'test-user-id';

  // Create a session in DB (mock)
  await db.insert(userSessions).values({
    userId,
    sessionId: 'test-session',
    token: 'test-token',
    expiresAt: new Date(),
  });

  // Mock transaction failure on first delete
  const mockTransaction = jest
    .spyOn(db, 'transaction')
    .mockImplementation(async callback => {
      await callback({
        delete: jest.fn().mockRejectedValue(new Error('DB error')),
      });
    });

  // Try to revoke - should fail
  await expect(revokeAllUserSessions(userId)).rejects.toThrow();

  // Verify session still exists in DB (rollback)
  const sessions = await db
    .select()
    .from(userSessions)
    .where(eq(userSessions.userId, userId));
  expect(sessions.length).toBeGreaterThan(0);

  // Restore transaction
  mockTransaction.mockRestore();
});
```

---

## Risk Rating

**Risk Rating: MEDIUM**

**Why it is at least this bad:**

- **HIGH Priority Finding (F1):** Token blacklist exists but is not checked in auth.ts
  - Blacklisted tokens remain valid for up to 7 days after revocation
  - Enables account takeover persistence after compromise
  - Direct security vulnerability affecting authentication flow
  - Feature exists but is not integrated - implementation gap
- **MEDIUM Priority Findings (F2, F3, F6):** Cleanup issues
  - Cleanup never starts, grows unbounded (F2)
  - FIFO cleanup wastes memory (F3)
  - Timer accumulation on hot-reload (F6)
  - These are operational issues that could cause performance degradation or memory leaks
- **LOW Priority Findings (F4, F5, F7):** Code quality issues
  - Unused sessionTokens (F4)
  - Weak validation (F5)
  - Error handling gaps (F7)
  - These contribute to technical debt but don't directly cause immediate failures

**Why it is not worse:**

- **Not CRITICAL because:**
  - Token blacklist infrastructure exists (addToBlacklist, isTokenBlacklisted functions)
  - Session revocation endpoints work (logout, logout-all)
  - Error handling exists (all functions have try-catch)
  - Database operations use parameterized queries (no SQL injection risk)
  - No evidence of active exploits or data breaches
- **Redeeming factors:**
  - F1 is an implementation gap, not a missing feature - fix is straightforward (import isTokenBlacklisted)
  - F2-F6 are operational issues that can be mitigated quickly
  - No evidence of systemic failures or architectural problems
  - File is well-structured and mostly follows good practices
  - Recent PR #10 added structured logging to auth.ts, which would help identify issues
- **Overall assessment:**
  - Code quality is reasonable with specific gaps
  - Security vulnerability exists (F1) but is fixable with minimal changes
  - No evidence of malicious code or intentional backdoors
  - Risk is contained to session revocation feature

---

## Regression Analysis

**Commands executed:**

```bash
git log -n 20 --follow -- server/utils/session-revocation.ts

git log --follow --name-status -- server/utils/session-revocation.ts | head -30
```

**Concrete deltas observed:**

- Only 1 commit found (7a885cf): Initial file creation
- No modifications tracked in history
- No prior versions to compare

**Classification at FILE LEVEL:**

- **unknown**
- Reason: Insufficient history for regression analysis
- Cannot determine if file has been fixed, regressed, or is partially addressed
- Only initial commit exists, no changes to analyze
- No evidence of fixes, regressions, or iterations

---

## Next Actions

### Exact Finding IDs Recommended for Next Remediation PR

**For P0 Implementation (F1 - HIGH):**

- Ticket title: Integrate token blacklist check into verifyToken
- Target: server/auth.ts (verifyToken function) and server/utils/session-revocation.ts (import isTokenBlacklisted)
- Why it exists (Observed): Token blacklist exists in session-revocation.ts but is never checked in auth.ts token verification flow
- Recommended prompt: Audit v1.5 + This file is a security implementation gap for session revocation
- Acceptance criteria:
  - verifyToken function checks isTokenBlacklisted before JWT verification
  - Blacklisted tokens are rejected during authentication
  - Non-blacklisted tokens continue to work normally
  - Tests demonstrate blacklisted token rejection
- Risk if deferred: **HIGH** - Account takeover persists for up to 7 days after token theft

**For P2 Implementation (F2 - MEDIUM):**

- Ticket title: Start cleanupExpiredSessions on module load
- Target: server/utils/session-revocation.ts (cleanupExpiredSessions startup invocation)
- Why it exists (Observed): cleanupExpiredSessions exists but is never called, causing blacklist to grow unbounded
- Recommended prompt: Audit v1.5 + This is an operational issue that could cause memory leaks
- Acceptance criteria:
  - cleanupExpiredSessions is called when module loads
  - Token blacklist cleanup runs periodically (hourly)
  - Blacklist size stays manageable
  - Tests verify cleanup starts and runs correctly
- Risk if deferred: **MEDIUM** - Memory leak, performance degradation

**For P2 Implementation (F3 - MEDIUM):**

- Ticket title: Add TTL to token blacklist and time-based cleanup
- Target: server/utils/session-revocation.ts (tokenBlacklist type, addToBlacklist, cleanupBlacklist)
- Why it exists (Observed): Token blacklist uses FIFO cleanup instead of time-based, no expiry tracking
- Recommended prompt: Audit v1.5 + This improves memory efficiency and correlates with JWT expiry
- Acceptance criteria:
  - Token blacklist entries have expiry timestamps
  - Cleanup removes expired entries, not just oldest
  - Memory usage is proportional to active revoked tokens
  - Tests verify expired tokens are removed
- Risk if deferred: **MEDIUM** - Memory waste, inefficient cleanup

**For P2 Implementation (F4 - LOW):**

- Ticket title: Remove or complete sessionTokens implementation
- Target: server/utils/session-revocation.ts (sessionTokens Map and related functions)
- Why it exists (Observed): sessionTokens is defined but never read/exported, wasting memory
- Recommended prompt: Audit v1.5 + This is a code quality issue that reduces technical debt
- Acceptance criteria:
  - sessionTokens is either removed entirely or completed with getSessionToken export
  - No unused data structures remain in memory
  - Tests verify no regression or correct usage
- Risk if deferred: **LOW** - Code complexity, wasted memory, confusion

**For P2 Implementation (F6 - MEDIUM):**

- Ticket title: Add process signal handlers to clear timers
- Target: server/utils/session-revocation.ts (cleanupExpiredSessions function, module level)
- Why it exists (Observed): No signal handlers for cleanup, timer accumulation on hot-reload
- Recommended prompt: Audit v1.5 + This is a process lifecycle issue affecting development and production
- Acceptance criteria:
  - Signal handlers (SIGTERM, SIGINT) clear cleanup timer
  - No timer accumulation on hot-reload
  - Resources cleaned on server shutdown
  - Tests verify timer cleanup on signals
- Risk if deferred: **MEDIUM** - Memory leaks, resource leaks

**For P2 Implementation (F7 - LOW):**

- Ticket title: Add transaction safety to revocation operations
- Target: server/utils/session-revocation.ts (revokeAllUserSessions, handleRevokeAllSessions)
- Why it exists (Observed): No transaction safety, partial failures can leave inconsistent state
- Recommended prompt: Audit v1.5 + This improves data consistency and error recovery
- Acceptance criteria:
  - DB operations use db.transaction() for atomicity
  - Failed revocations don't leave partial state
  - Error responses reflect actual outcome
  - Tests verify atomicity and rollback behavior
- Risk if deferred: **LOW** - Data corruption, security bypass on partial failures

---

## Verification Notes Per High/Medium Findings

**For F1 (HIGH):**

- Must verify: Blacklisted tokens are rejected during authentication
- Verification approach:
  - Integration test: login → logout → try to use blacklisted token
  - Curl commands demonstrating 401 response for blacklisted token
  - Unit tests for isTokenBlacklisted function

**For F2 (MEDIUM):**

- Must verify: Cleanup runs periodically
- Verification approach:
  - Unit test with mocked setTimeout to verify it's called
  - Add console.log to cleanupExpiredSessions to verify it starts
  - Manual test: Add 1000 tokens, wait > 1 hour, verify size decreased

**For F3 (MEDIUM):**

- Must verify: Expired tokens removed from blacklist
- Verification approach:
  - Unit tests for cleanupBlacklist with TTL logic
  - Tests for expired tokens (7+ days old) being removed
  - Tests for future tokens being retained

**For F4 (LOW):**

- Must verify: sessionTokens removed or properly used
- Verification approach:
  - Code review to confirm no external usage
  - Memory profiling to verify no leak from sessionTokens
  - Tests for getSessionToken if completing implementation

**For F5 (LOW):**

- Must verify: Improved validation works
- Verification approach:
  - Unit tests for addToBlacklist with invalid tokens
  - Tests for JWT format validation (3 parts)
  - Tests for max length enforcement

**For F6 (MEDIUM):**

- Must verify: Timers cleared on shutdown
- Verification approach:
  - Unit test for SIGTERM/SIGINT handlers
  - Tests for clearTimeout being called
  - Development hot-reload test (simulate multiple loads)

**For F7 (LOW):**

- Must verify: Transactions work correctly
- Verification approach:
  - Integration test with mock DB transaction failure
  - Tests for rollback behavior
  - Tests verify session state consistency

---

**End of Audit Artifact**

**Links:**

- PR for auth.ts audit: https://github.com/pranaysuyash/metaextract/pull/10
- Next audit: server/utils/session-revocation.ts implementation (F1 - HIGH priority)
