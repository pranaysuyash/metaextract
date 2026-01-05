# Database Architecture Review - 2026-01-05

## Overview
This document summarizes the findings from the Database Architecture & Infrastructure Review, completed actions, and deferred items for future implementation.

## Completed Actions ✅

### 1. Schema Unification (High Severity)
- **Problem**: `quota-schema.sql` contained tables not present in `shared/schema.ts`
- **Fix**: Ported 4 tables to Drizzle ORM:
  - `client_activity` - Request activity tracking for abuse detection
  - `ip_rate_limits` - IP-based rate limiting
  - `abuse_patterns` - Advanced abuse pattern detection
  - `quota_analytics` - Analytics summary for monitoring
- **Action**: Deleted legacy `server/db/quota-schema.sql`
- **Migration**: Ran `npm run db:push` successfully

### 2. Data Access Audit (Medium Severity)
- **Finding**: `server/storage` is a proper Repository Pattern abstraction
- **Architecture**: `IStorage` interface with `MemStorage` (dev) and `DatabaseStorage` (prod)
- **Decision**: No refactor needed - this pattern provides testability

### 3. Metadata Partitioning (Medium Severity)
- **Problem**: Avg metadata blob = 156KB, Max = 3MB (exceeds 10KB recommendation)
- **Solution Implemented**:
  - Schema now stores capped `metadataSummary` + `metadataRef` pointer
  - Full blob stored in object storage (local FS default, R2/S3 pluggable)
  - Added integrity fields: `metadataSha256`, `metadataSizeBytes`, `metadataContentType`

---

## Deferred Items (Post-MVP)

### User/Session Linking (Medium Priority)
**Problem**: Anonymous session credits need merging to user accounts on signup.

**Current State**:
- `creditBalances.userId` is nullable
- `creditBalances.sessionId` stores anonymous session identifier

**Proposed Flow**:
```
1. Anonymous user receives session credits via cookie (session_id)
2. User signs up / logs in
3. System queries: SELECT * FROM credit_balances WHERE session_id = ?
4. If found, UPDATE SET user_id = ?, session_id = NULL
5. Atomic transaction ensures no credits lost
```

**Implementation Location**: `server/routes/auth.ts` (post-login hook)

---

### Row Level Security (RLS) (Low Priority)
**Problem**: API code bugs could leak user data.

**Current State**: Application-level checks (`where(eq(users.id, req.user.id))`)

**Proposed Enhancement**:
```sql
-- Enable RLS on sensitive tables
ALTER TABLE metadata_results ENABLE ROW LEVEL SECURITY;

-- Create policy for user isolation
CREATE POLICY user_isolation ON metadata_results
  USING (user_id = current_setting('app.current_user_id')::text);
```

**Trade-offs**:
- Requires setting `app.current_user_id` per request
- Adds DB overhead but provides defense-in-depth
- Recommended for post-launch hardening

---

### Caching Strategy (Low Priority)
**Current State**: `server/cache` directory exists with Redis support

**Recommended Strategy for `metadataResults`**:
- Cache key: `metadata:{result_id}`
- TTL: Infinite (metadata never changes once extracted)
- Invalidation: None needed (immutable data)
- Implementation: Check cache before DB query in `storage.getMetadata()`

---

## Object Storage Setup

### Environment Variables
```bash
# Provider selection (default: local)
OBJECT_STORAGE_PROVIDER=r2  # Options: local, r2, s3

# For Cloudflare R2
OBJECT_STORAGE_ENDPOINT=https://<account_id>.r2.cloudflarestorage.com
OBJECT_STORAGE_ACCESS_KEY_ID=your_access_key
OBJECT_STORAGE_SECRET_ACCESS_KEY=your_secret_key
OBJECT_STORAGE_BUCKET=metaextract-metadata

# For AWS S3
OBJECT_STORAGE_PROVIDER=s3
OBJECT_STORAGE_REGION=us-east-1
OBJECT_STORAGE_BUCKET=metaextract-metadata
# Uses default AWS credential chain
```

### Dependencies
```bash
# Only required for R2/S3 (not needed for local storage)
npm install @aws-sdk/client-s3
```

### Default Behavior
- Without environment variables, defaults to local file storage
- Local storage path: `storage/objects/`
- Suitable for development and single-server deployments

---

## Files Modified
- `shared/schema.ts` - Added 4 quota tables, updated `metadataResults` with partitioning columns
- `server/storage/objectStorage/` - New object storage abstraction
- `server/storage/metadataPartitioning.ts` - Metadata split/merge logic
- `server/storage/db.ts` - Updated to use partitioned storage
- `server/routes/extraction.ts` - Updated to save via new flow

## Verification
- TypeScript: `tsc --noEmit` passes
- Migration: `npm run db:push` applied successfully
- Tests: Integration tests pass
