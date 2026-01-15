# Audit: server/auth.ts

## Header

| Field | Value |
|-------|-------|
| Audit version | v1.5.1 |
| Date/time | 2026-01-15 |
| Audited file path | `server/auth.ts` |
| Base commit SHA | `da52d67c431f35d7e902dce8fa5034760102788a` |
| Auditor identity | Amp Agent |

---

## Discovery Evidence (Raw Outputs)

### A) File Tracking & Context

```bash
$ git rev-parse --is-inside-work-tree
true

$ git ls-files -- server/auth.ts
server/auth.ts

$ git status --porcelain -- server/auth.ts
(empty - file is tracked, no pending changes)
```

**Observed**: File is tracked by git with no uncommitted changes.

### B) Git History Discovery

```bash
$ git log -n 10 --oneline --follow -- server/auth.ts
7a23026 fix(session-revocation): integrate token blacklist check into verifyToken (#11)
337aff3 fix(auth): implement audit findings - security, logging, and validation (#10)
716658a Add password max length validation and apiLimiter import
89d1676 fix(auth): implement audit findings - deprecate tiering and fix critical issues
708956a fix(images-mvp): neutralize tier/trial copy; add LimitedAccessModal; stabilize tests
13e1fe2 Add function aliases to renamed modules + E2E smoke test pass
7a885cf tests(e2e): add visual snapshot assertion for extraction header
d7f4e7c Add evidence pack verification scripts and security hardening
bc9c57d Stabilize server performance tests
e2c9124 Auto-sync after agent response
```

**Observed**: File has been actively audited and remediated recently (commits `337aff3`, `7a23026`).

### C) Inbound/Outbound Dependencies

**Outbound (imports from this file):**
- `express` (Request, Response, NextFunction, Express)
- `bcryptjs` - password hashing
- `jsonwebtoken` - JWT operations
- `zod` - validation schemas
- `crypto` - token generation
- `./db` - database connection
- `@shared/schema` - users, subscriptions, creditBalances
- `drizzle-orm` - eq, sql
- `@shared/tierConfig` - normalizeTier (deprecated)
- `./security-utils` - isLockedOut, recordFailedAttempt, clearFailedAttempts, generateUserCSRFToken, validateUserCSRFToken
- `./utils/email-verification` - handleEmailVerification, handleResendVerification
- `./utils/session-revocation` - handleLogoutWithRevocation, handleRevokeAllSessions, isTokenBlacklisted
- `./auth-enhanced` - apiLimiter

**Inbound (files importing this file):**
```bash
$ rg -n "authMiddleware|requireAuth|verifyToken|setupAuthRoutes" --type ts
server/index.ts:8:import { registerAuthRoutes, authMiddleware } from './auth';
server/index.ts:56:  app.use(authMiddleware);
server/routes/metadata.ts:15:import { requireAuth } from '../auth';
server/routes/batch.ts:14:import { requireAuth } from '../auth';
server/routes/images-mvp.ts:30:import { requireAuth } from '../auth';
server/routes/forensic.ts:13:import { requireAuth } from '../auth';
server/routes/extraction.ts:39:import { requireAuth } from '../auth';
server/middleware/admin-auth.ts:7:import { verifyToken } from '../auth';
```

**Observed**: This file is load-bearing - central auth module used by index.ts and all major route files.

### D) Test Discovery

```bash
$ rg -n "auth" tests/ server/__tests__ server/tests --type ts | head -30
tests/auth-enhanced.test.ts - comprehensive tests for enhanced auth
tests/security/security.test.ts - security tests for login endpoints
tests/integration/fullstack.test.ts - integration tests including auth
```

**Observed**: Tests exist in `tests/auth-enhanced.test.ts` and `tests/security/security.test.ts`.

---

## Findings

### AUTH-001: CSRF Token Cookie httpOnly=false (MEDIUM)

| Field | Value |
|-------|-------|
| Severity | MEDIUM |
| Evidence label | Observed |
| Location | Lines 934-942 |

**Evidence snippet:**
```typescript
res.cookie('csrf_token', token, {
  httpOnly: false, // Allow client-side JavaScript to read for AJAX requests
  // SECURITY NOTE: httpOnly: false allows CSRF token to be read via XSS attacks.
```

**Failure mode**: If XSS vulnerability exists anywhere in the application, attacker can steal CSRF tokens and perform CSRF attacks.

**Blast radius**: All authenticated user actions protected by CSRF middleware.

**Suggested fix direction**: Consider double-submit cookie pattern or keep CSRF token in response body only (not cookie). The current approach is documented and acknowledged, but represents a trade-off.

**Invariant**: CSRF token must remain unpredictable and tied to user session.

---

### AUTH-002: In-Memory Password Reset Tokens (LOW)

| Field | Value |
|-------|-------|
| Severity | LOW |
| Evidence label | Observed |
| Location | Lines 180-197, 484-489 |

**Evidence snippet:**
```typescript
const inMemoryResetTokens = new Map<string, ResetTokenRecord>();
// ...
if (e?.code === '42P01') {
  inMemoryResetTokens.set(tokenHash, { userId: user.id, tokenHash, expiresAt });
}
```

**Failure mode**: In-memory tokens lost on server restart. Multi-instance deployments won't share reset tokens.

**Blast radius**: Password reset functionality in environments without DB table `password_reset_tokens`.

**Suggested fix direction**: This is a fallback for dev/test. Ensure production always has the DB table. Add startup check or migration.

**Invariant**: Password reset tokens must persist across reasonable server lifecycle events in production.

---

### AUTH-003: Token in Response Body (LOW)

| Field | Value |
|-------|-------|
| Severity | LOW |
| Evidence label | Observed |
| Location | Lines 701-711, 878-889, 1051-1061 |

**Evidence snippet:**
```typescript
res.status(201).json({
  success: true,
  user: { ... },
  token,  // Token returned in response body
});
```

**Failure mode**: Token exposed in response body could be logged by proxies, stored in browser history, or captured by browser extensions.

**Blast radius**: Session tokens for all authenticated users.

**Suggested fix direction**: Token is also set in httpOnly cookie. Consider removing token from response body if client can rely solely on cookies. Current approach supports both cookie-based and header-based auth.

**Invariant**: Primary auth token must be transmitted via httpOnly cookie for browser clients.

---

### AUTH-004: Console.log with User Data (LOW)

| Field | Value |
|-------|-------|
| Severity | LOW |
| Evidence label | Observed |
| Location | Lines 591-594, 694-699, 891-896, 912-915 |

**Evidence snippet:**
```typescript
console.log('Password reset completed:', { userId, ip: req.ip });
console.log('User registered:', { userId, email, username, ip: req.ip });
console.log('User logged in:', { userId, email, username, ip: req.ip });
```

**Failure mode**: Sensitive data (email, username, IP) written to stdout. May be captured in logs.

**Blast radius**: User privacy; potential PII exposure in log aggregation systems.

**Suggested fix direction**: Use structured logging with log levels. Sanitize or redact email in production logs. Consider removing email from standard log output.

**Invariant**: Production logs must not contain full email addresses.

---

### AUTH-005: Password Reset Token Dev Exposure (LOW)

| Field | Value |
|-------|-------|
| Severity | LOW |
| Evidence label | Observed |
| Location | Lines 498-500 |

**Evidence snippet:**
```typescript
if (process.env.NODE_ENV === 'development') {
  response.token = token;
}
```

**Failure mode**: If `NODE_ENV` is incorrectly set in production, password reset tokens would be exposed in API response.

**Blast radius**: Account takeover for any user requesting password reset.

**Suggested fix direction**: Current guard is appropriate. Ensure deployment pipeline explicitly sets `NODE_ENV=production`. Add startup validation.

**Invariant**: `NODE_ENV` must be `production` in production deployments.

---

## Out-of-Scope Findings

### OOS-001: auth-enhanced.ts Rate Limiting Implementation

**Observed**: `apiLimiter` is imported from `./auth-enhanced` (line 39). Rate limiting behavior and configuration are in that file.

**Recommendation**: Audit `server/auth-enhanced.ts` separately.

---

### OOS-002: Session Revocation Implementation

**Observed**: `isTokenBlacklisted`, `handleLogoutWithRevocation`, `handleRevokeAllSessions` imported from `./utils/session-revocation` (lines 35-38).

**Recommendation**: Audit `server/utils/session-revocation.ts` separately.

---

### OOS-003: Security Utils (Lockout, CSRF)

**Observed**: `isLockedOut`, `recordFailedAttempt`, `clearFailedAttempts`, `generateUserCSRFToken`, `validateUserCSRFToken` imported from `./security-utils` (lines 24-29).

**Recommendation**: Audit `server/security-utils.ts` separately.

---

## Next Actions

| Finding ID | Recommended Action | Verification |
|------------|-------------------|--------------|
| AUTH-001 | Document risk acceptance or implement alternative CSRF pattern | Review XSS protections; confirm CSP headers |
| AUTH-002 | Add DB migration check at startup for password_reset_tokens table | Test password reset in multi-instance deployment |
| AUTH-003 | Evaluate removing token from response body for browser clients | Confirm client uses httpOnly cookie exclusively |
| AUTH-004 | Switch to structured logger with PII redaction | Verify production logs don't contain email |
| AUTH-005 | Add startup assertion that NODE_ENV=production in prod | Review deployment configuration |

**Priority for next remediation PR**: AUTH-004 (logging), AUTH-002 (DB migration check)

**Next audit queue**:
1. `server/auth-enhanced.ts` (rate limiting, token management)
2. `server/security-utils.ts` (lockout, CSRF generation)
3. `server/utils/session-revocation.ts` (token blacklist)
