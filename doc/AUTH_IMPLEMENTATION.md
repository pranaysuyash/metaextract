# MetaExtract Authentication & Pricing Implementation

## Summary of Changes

### 1. Authentication System (`server/auth.ts`)

- **JWT-based authentication** with 7-day token expiry
- **Secure password hashing** using bcryptjs (12 salt rounds)
- **Cookie + Bearer token support** for flexibility

**Endpoints:**

- `POST /api/auth/register` - Create new account
- `POST /api/auth/login` - Sign in, receive JWT
- `POST /api/auth/logout` - Clear session
- `GET /api/auth/me` - Get current user (session validation)
- `POST /api/auth/refresh` - Refresh JWT token
- `POST /api/auth/update-tier` - Internal endpoint for webhook to update user tier

**Middleware:**

- `authMiddleware` - Attaches user to request if authenticated
- `requireAuth` - Blocks unauthenticated requests (401)
- `requireTier(...tiers)` - Blocks insufficient tier (403)
- `getEffectiveTier(req)` - Returns user's tier or "free"

### 2. Revised Pricing (`shared/tierConfig.ts`)

| Tier             | Price   | File Limit | Max Size | Key Features                           |
| ---------------- | ------- | ---------- | -------- | -------------------------------------- |
| **Free**         | $0      | 3/day      | 10MB     | Standard images, 200-300 fields        |
| **Professional** | $19/mo  | 500/mo     | 100MB    | RAW formats, 2,000+ fields, MakerNotes |
| **Forensic**     | $49/mo  | Unlimited  | 500MB    | All files, 7,000+ fields, API (5K/mo)  |
| **Enterprise**   | $149/mo | Unlimited  | 2GB      | Unlimited API, dedicated support       |

**Credit Packs (Pay-per-use):**

- Single: $2 (1 file)
- Investigation: $15 (10 files) - **Popular**
- Case: $50 (50 files)
- Agency: $150 (200 files)

### 3. Frontend Components

**Auth Context (`client/src/lib/auth.tsx`):**

- `AuthProvider` - Wraps app with auth state
- `useAuth()` - Hook for auth state and methods
- `useEffectiveTier()` - Get user's active tier
- `useCanAccessTier(tier)` - Check feature access

**Auth Modal (`client/src/components/auth-modal.tsx`):**

- Login/Register tabs
- Form validation
- Error/success states
- Auto-close on success

**Layout Update (`client/src/components/layout.tsx`):**

- User dropdown when authenticated
- Tier badge display
- Sign In / Get Started buttons when not authenticated
- Mobile responsive

### 4. Updated Mock Data (`client/src/lib/mockData.ts`)

- New PRICING_TIERS array with 4 tiers
- CREDIT_PACKS with new pricing
- FEATURE_COMPARISON table data
- FAQ_ITEMS updated
- VALUE_PROPS for landing page

## Files Changed

```
server/
├── auth.ts           # NEW - Auth system
├── index.ts          # Updated - Added cookieParser, authMiddleware
├── routes.ts         # Updated - Added auth imports

shared/
├── tierConfig.ts     # REWRITTEN - New pricing structure

client/src/
├── App.tsx                      # Updated - Added AuthProvider
├── lib/
│   ├── auth.tsx                 # NEW - Auth context & hooks
│   └── mockData.ts              # REWRITTEN - New pricing data
├── components/
│   ├── auth-modal.tsx           # NEW - Login/Register modal
│   └── layout.tsx               # Updated - Auth UI in header
```

## Dependencies Added

```bash
npm install bcryptjs jsonwebtoken cookie-parser
npm install -D @types/bcryptjs @types/jsonwebtoken @types/cookie-parser
```

## Next Steps

### Immediate (Required for Production):

1. **Database Setup** - Configure real PostgreSQL:

   ```env
   DATABASE_URL=postgresql://user:pass@host:5432/metaextract
   SESSION_SECRET=your-secure-random-secret
   ```

2. **Run Migrations** - Create users table:

   ```bash
   npm run db:push
   ```

3. **Update Payment Webhooks** - Wire DodoPayments to call `/api/auth/update-tier`

4. **Enforce Tier in Extract Route** - Currently extraction uses query param tier. Should use:
   ```typescript
   const tier = getEffectiveTier(req as AuthRequest);
   ```

### Recommended:

5. **Rate Limiting** - Use the `getRateLimits(tier)` config
6. **Password Reset Flow** - Add forgot password endpoint
7. **Email Verification** - Verify email before full access
8. **2FA** - Optional two-factor for enterprise

## Testing

```bash
# Register
curl -X POST http://localhost:3000/api/auth/register \\
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"password123"}'

# Login
curl -X POST http://localhost:3000/api/auth/login \\
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Get current user
curl http://localhost:3000/api/auth/me \\
  -H "Authorization: Bearer <token>"
```

## Backwards Compatibility

- Old tier names (`starter`, `premium`, `super`) are mapped to new tiers via `LEGACY_TIER_MAP`
- `normalizeTier()` function handles conversion
- Anonymous users still get "free" tier via `getEffectiveTier()`
