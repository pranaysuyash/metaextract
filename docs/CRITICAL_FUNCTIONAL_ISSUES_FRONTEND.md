# Critical Functional Issues - Frontend & Shared Schema

Analysis of critical issues in frontend authentication, context providers, and shared database schemas.

---

## 1. client/src/lib/auth.tsx

**Description**: Core authentication context provider and hooks for managing user sessions, login/register, and tier-based access control (228 lines).

**Critical Functional Issues**:

### 1. **Tier Override Via localStorage (CRITICAL SECURITY)**
   - **Location**: Lines 72-81
   - **Issue**: 
     ```typescript
     const tierOverride = localStorage.getItem("metaextract_tier_override");
     const response = await fetch("/api/auth/login", {
       body: JSON.stringify({
         email,
         password,
         ...(tierOverride ? { tier: tierOverride } : {}),  // User-controlled tier!
       }),
     });
     ```
   - **Impact**: User can set localStorage key to upgrade themselves. Combined with backend's `ALLOW_TIER_OVERRIDE`, this is a privilege escalation vulnerability.
   - **Severity**: **CRITICAL** - Privilege escalation
   - **Recommendation**: Remove tier override from frontend; never send tier from client.

### 2. **useEffectiveTier Returns "enterprise" for Unauthenticated (Same Bypass)**
   - **Location**: Lines 202-215
   - **Issue**: 
     ```typescript
     export function useEffectiveTier(): string {
       const { user, isAuthenticated } = useAuth();
       
       if (!isAuthenticated || !user) {
         return "enterprise";  // Unauthenticated = enterprise!
       }
       
       if (user.subscriptionStatus === "active") {
         return user.tier;
       }
       
       return "enterprise";  // Inactive subscription = enterprise!
     }
     ```
   - **Impact**: Feature gating on frontend defaults to enterprise for all unauthenticated/inactive users. All premium features enabled.
   - **Severity**: **CRITICAL** - Business model broken
   - **Recommendation**: Return "free" or "trial" for unauthenticated; "free" for inactive subscriptions.

### 3. **Token Stored in localStorage (XSS Vulnerability)**
   - **Location**: Lines 99, 143, 166
   - **Issue**: 
     ```typescript
     localStorage.setItem("auth_token", (data as any).token);
     ```
   - **Impact**: JWT token stored in localStorage is vulnerable to XSS attacks. Attacker can read token and impersonate user.
   - **Severity**: **HIGH** - Security
   - **Recommendation**: 
     - Store token in httpOnly cookie (already done server-side)
     - Don't store in localStorage
     - Use cookie via `credentials: "include"` (already done)

### 4. **No Token Refresh Logic**
   - **Location**: Entire file
   - **Issue**: Token is obtained once at login/register. No refresh mechanism if token expires.
   - **Impact**: After token expires (7 days), API calls fail silently. User appears logged in but can't use features.
   - **Severity**: **MEDIUM** - UX/reliability
   - **Recommendation**: 
     - Implement token refresh endpoint
     - Call refresh when API returns 401
     - Add refresh-before-expiry logic

### 5. **Auth Check Doesn't Handle Network Errors Gracefully**
   - **Location**: Lines 50-68
   - **Issue**: 
     ```typescript
     const checkAuth = async () => {
       try {
         const response = await fetch("/api/auth/me", {...});
         const data = await parseJsonSafe(response);
         if (data && (data as any).authenticated && (data as any).user) {
           setUser((data as any).user);
         } else {
           setUser(null);
         }
       } catch (error) {
         console.error("Auth check failed:", error);
         setUser(null);  // Treats network error same as unauthenticated
       }
     };
     ```
   - **Impact**: Network error during auth check logs user out. Should retry or use cached state.
   - **Severity**: **MEDIUM** - Reliability
   - **Recommendation**: Distinguish network errors from auth failures; cache last known state.

### 6. **parseJsonSafe Doesn't Log Errors (Observability)**
   - **Location**: Lines 29-39
   - **Issue**: 
     ```typescript
     const parseJsonSafe = async (response: Response) => {
       const contentType = response.headers.get("content-type") || "";
       if (!contentType.includes("application/json")) {
         return null;  // Silent failure
       }
       try {
         return await response.json();
       } catch {
         return null;  // Silent failure
       }
     };
     ```
   - **Impact**: If server returns non-JSON, response is silently ignored. Debugging is difficult.
   - **Severity**: **MEDIUM** - Observability
   - **Recommendation**: Log non-JSON responses; include status code in error logging.

### 7. **No Validation of User Object from Server**
   - **Location**: Lines 57-58, 93-94, 138-139
   - **Issue**: 
     ```typescript
     if (data && (data as any).authenticated && (data as any).user) {
       setUser((data as any).user);  // No validation of shape
     }
     ```
   - **Impact**: If server returns invalid user object, state becomes corrupted. No type safety.
   - **Severity**: **MEDIUM** - Data integrity
   - **Recommendation**: Use Zod schema to validate user object before setting state.

### 8. **useAuth Hook Can Throw During Render (Error Boundary Needed)**
   - **Location**: Lines 193-196
   - **Issue**: 
     ```typescript
     export function useAuth() {
       const context = useContext(AuthContext);
       if (!context) {
         throw new Error("useAuth must be used within an AuthProvider");
       }
       return context;
     }
     ```
   - **Impact**: If useAuth is called outside provider, throws error during render (hard to debug).
   - **Severity**: **MEDIUM** - Error handling
   - **Recommendation**: Wrap in error boundary; provide clearer error message.

### 9. **Tier Order Array Hardcoded (Not Maintainable)**
   - **Location**: Line 223
   - **Issue**: 
     ```typescript
     const tierOrder = ["free", "professional", "forensic", "enterprise"];
     ```
   - **Impact**: If tier list changes, must update here and 10 other places. Easy to get out of sync.
   - **Severity**: **LOW** - Maintainability
   - **Recommendation**: Move to centralized tierConfig.

---

## 2. shared/schema.ts

**Description**: Drizzle ORM and Zod schemas for database tables and validation (182 lines).

**Critical Functional Issues**:

### 1. **Users Table Defaults Tier to "enterprise" (CRITICAL)**
   - **Location**: Line 11
   - **Issue**: 
     ```typescript
     tier: text("tier").notNull().default("enterprise"),
     ```
   - **Impact**: Every new user is created with enterprise tier by default. No free tier exists in database.
   - **Severity**: **CRITICAL** - Business model broken
   - **Recommendation**: Change default to "free".

### 2. **extractionAnalytics Defaults Tier to "enterprise" (Cascading Issue)**
   - **Location**: Line 51
   - **Issue**: 
     ```typescript
     tier: text("tier").notNull().default("enterprise"),
     ```
   - **Impact**: All analytics entries default to enterprise. Can't track free tier usage.
   - **Severity**: **HIGH** - Analytics/billing
   - **Recommendation**: Change default to "free"; require explicit tier on insert.

### 3. **trialUsages Email Column Unique (Blocks Multiple Trials)**
   - **Location**: Line 169
   - **Issue**: 
     ```typescript
     email: text("email").notNull().unique(),
     ```
   - **Impact**: Email is unique, so can only claim trial once. Good for enforcement, but:
     - If user deletes record, can claim again
     - No IP/user agent tracking to prevent abuse (stored but not indexed)
   - **Severity**: **MEDIUM** - Abuse risk
   - **Recommendation**: Add unique constraint on (email, ipAddress) or add abuse tracking logic.

### 4. **creditBalances Allows Orphaned Balances (Data Consistency)**
   - **Location**: Lines 79-80
   - **Issue**: 
     ```typescript
     userId: varchar("user_id").references(() => users.id),  // Optional reference
     sessionId: text("session_id"),  // Both optional, no constraint
     ```
   - **Impact**: Can have credit balance with neither userId nor sessionId. Orphaned record that can't be cleaned up.
   - **Severity**: **MEDIUM** - Data integrity
   - **Recommendation**: Add constraint: `userId OR sessionId must be not null`.

### 5. **creditTransactions Type Not Enumerated (No Validation)**
   - **Location**: Line 89
   - **Issue**: 
     ```typescript
     type: text("type").notNull(), // 'purchase', 'usage', 'refund'
     ```
   - **Impact**: Database allows any string as type. No constraint on valid values.
   - **Severity**: **MEDIUM** - Data quality
   - **Recommendation**: Use PostgreSQL enum or add CHECK constraint.

### 6. **No Foreign Key Constraint on Trial Usage (Cascades)**
   - **Location**: Lines 167-174
   - **Issue**: 
     ```typescript
     export const trialUsages = pgTable("trial_usages", {
       // No reference to users or sessions
       email: text("email").notNull().unique(),
       // ...
     });
     ```
   - **Impact**: Trial usage is orphaned from users table. Hard to correlate.
   - **Severity**: **LOW** - Query complexity
   - **Recommendation**: Add reference to userId if applicable.

### 7. **Metadata jsonb Column Stores Full Extraction (Storage Inefficiency)**
   - **Location**: Line 123
   - **Issue**: 
     ```typescript
     metadata: jsonb("metadata").notNull(), // Stores the full extraction result
     ```
   - **Impact**: Stores entire metadata response (potentially MB per file). No cleanup policy. Table will grow unbounded.
   - **Severity**: **HIGH** - Operational/cost
   - **Recommendation**: 
     - Add retention policy (delete after 30 days)
     - Or store only summary + reference to S3
     - Add index on userId for queries

### 8. **No Cascade Delete on User Deletion**
   - **Location**: Throughout schema
   - **Issue**: Deleting a user doesn't cascade to their:
     - subscriptions
     - credit balances
     - metadata results
     - onboarding sessions
   - **Impact**: Orphaned records accumulate. Foreign key constraints may prevent deletion.
   - **Severity**: **MEDIUM** - Operational
   - **Recommendation**: Add `onDelete: "cascade"` to all user references.

### 9. **Subscription Status Not Enumerated**
   - **Location**: Line 30
   - **Issue**: 
     ```typescript
     status: text("status").notNull().default("pending"),
     ```
   - **Impact**: Can be any string. Examples in code: "active", "on_hold", "failed", "cancelled". What else?
   - **Severity**: **MEDIUM** - Data quality
   - **Recommendation**: Use PostgreSQL enum with valid values.

### 10. **No Indexes on Query Columns**
   - **Location**: Entire schema
   - **Issue**: No indexes on:
     - `extractionAnalytics.requestedAt` (time-range queries)
     - `creditTransactions.balanceId` (frequent lookups)
     - `metadataResults.userId` (query user's files)
     - `subscriptions.userId` (lookup subscription)
   - **Impact**: Analytics queries are slow; N+1 problems possible.
   - **Severity**: **MEDIUM** - Performance
   - **Recommendation**: Add indexes on frequently queried columns.

---

## Summary by Severity

### CRITICAL (Business Model / Security)
- Frontend: **Tier override via localStorage** (privilege escalation)
- Frontend: **useEffectiveTier defaults to enterprise** (all users get premium)
- Schema: **Users default tier to "enterprise"** (new users have full access)

### HIGH (Abuse / Data / Performance)
- Frontend: **Token stored in localStorage** (XSS vulnerability)
- Frontend: **No token refresh logic** (users logged out after expiry)
- Schema: **extractionAnalytics defaults to enterprise** (analytics broken)
- Schema: **Metadata jsonb stores full extraction** (unbounded storage growth)

### MEDIUM (Reliability / Consistency / Abuse)
- Frontend: **Auth check treats network errors as logout** (reliability)
- Frontend: **No validation of user object from server** (data integrity)
- Frontend: **useAuth throws during render** (poor error handling)
- Frontend: **Tier order hardcoded** (maintainability)
- Schema: **creditBalances allows orphaned records** (data consistency)
- Schema: **creditTransactions type not enumerated** (data quality)
- Schema: **Subscription status not enumerated** (data quality)
- Schema: **No cascade delete on user** (operational)
- Schema: **trialUsages email unique but IP not indexed** (abuse tracking weak)

### LOW (Maintainability)
- Frontend: **parseJsonSafe doesn't log errors** (observability)
- Schema: **Trial usage not linked to users** (query complexity)
- Schema: **No indexes on frequently queried columns** (performance)

---

## Recommended Fixes (Priority Order)

1. **IMMEDIATE**:
   - ✅ Remove tier override from frontend localStorage
   - ✅ Change useEffectiveTier to return "free" for unauthenticated
   - ✅ Change schema defaults from "enterprise" to "free"
   - ✅ Remove auth_token from localStorage

2. **BEFORE LAUNCH**:
   - Implement token refresh logic
   - Validate user object from server (Zod)
   - Add cascade delete on user
   - Enumerate subscription status and transaction types
   - Add metadata retention policy
   - Add indexes on query columns

3. **AFTER LAUNCH**:
   - Implement error boundary for useAuth
   - Add network error recovery in auth check
   - Log non-JSON responses
   - Add abuse tracking on trial usage
   - Centralize tier ordering
