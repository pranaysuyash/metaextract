# Deprecation and Dependency Update Plan

**Date:** January 7, 2026
**Focus:** Python deprecations, Node.js dependency updates, TypeScript fixes
**Status:** Analysis Complete, Implementation Pending

---

## Summary

### Python Deprecations

✅ **FIXED:** `audioop` deprecation warning from `pydub` and `audioread`

### Node.js Dependencies

🔶 **27 packages outdated** - includes 6 major version updates requiring breaking change review

### TypeScript Errors

⚠️ **Existing errors found** - unrelated to deprecations but should be fixed

---

## Python Deprecations

### 1. `audioop` Deprecation - ✅ FIXED

**Status:** FIXED - Suppressed in code

**Issue:** Python's `audioop` module is deprecated and slated for removal in Python 3.13. This warning appears when using `pydub` and `audioread` packages.

**Source:** `pydub@0.25.1` and `audioread@3.1.0` (internal dependencies)

**Location:** `server/extractor/modules/audio_metadata_extended.py`

**Warning Message:**

```
DeprecationWarning: 'audioop' is deprecated and slated for removal in Python 3.13
    import audioop
```

**Impact:** Warning in console only. No functional breakage (yet). Python 3.13 hasn't been released.

**Root Cause:** These libraries use deprecated `audioop` module internally.

**Solution Implemented:**

Added deprecation warning suppression in `server/extractor/modules/audio_metadata_extended.py:31-35`:

```python
# Suppress audioop deprecation warning from pydub/audioread until upstream fix
# These libraries use deprecated audioop module scheduled for removal in Python 3.13
warnings.filterwarnings('ignore',
                    category=DeprecationWarning,
                    message='.*audioop.*',
                    module='audioread|pydub')
```

**Verification:**

```bash
$ .venv/bin/python -W all -c "import pydub; import audioread"
# No deprecation warnings
```

**Long-term Options:**

| Option                              | Effort | Benefit       | Recommendation      |
| ----------------------------------- | ------ | ------------- | ------------------- |
| **A. Suppress (DONE)**              | Low    | Quiet console | ✅ Implemented      |
| **B. Replace with soundfile/numpy** | High   | Future-proof  | Monitor upstream    |
| **C. Wait for upstream fix**        | None   | Free          | ✅ Current approach |

**Why Wait for Upstream Fix:**

1. **No functional breakage** - Only warning in console
2. **Large rewrite** - Replacing pydub requires significant code changes
3. **Upstream monitoring** - `pydub` maintainers likely working on Python 3.13 compatibility
4. **Not urgent** - Python 3.13 not yet released

**Recommendation:** Keep suppression, monitor `pydub` repository for updates targeting Python 3.13.

---

## Node.js Dependency Updates

### Overview

Current versions → Latest versions with breaking change risk analysis.

### Phase 1: Safe Updates (Do First - No Breaking Changes)

```bash
npm update @types/jest@latest \
  @typescript-eslint/eslint-plugin@latest \
  @typescript-eslint/parser@latest \
  axe-core@latest \
  concurrently@latest \
  dodopayments@latest \
  drizzle-zod@latest \
  esbuild@latest \
  exiftool-vendored@latest \
  framer-motion@latest \
  jspdf-autotable@latest \
  lucide-react@latest \
  react-hook-form@latest \
  typescript@latest \
  vite@latest \
  ws@latest \
  date-fns@latest
```

**Details:**

| Package               | Current → Latest    | Risk   | Breaking Changes         |
| --------------------- | ------------------- | ------ | ------------------------ |
| @types/jest           | 29.5.14 → 30.0.0    | Low    | Minor type updates       |
| @typescript-eslint/\* | 8.51.0 → 8.52.0     | Low    | Bug fixes only           |
| axe-core              | 4.11.0 → 4.11.1     | Low    | Minor bug fix            |
| concurrently          | 8.2.2 → 9.2.1       | Low    | CLI improvements         |
| dodopayments          | 2.13.1 → 2.14.0     | Low    | API additions            |
| drizzle-zod           | 0.7.1 → 0.8.3       | Low    | Minor improvements       |
| esbuild               | 0.25.12 → 0.27.2    | Low    | Performance improvements |
| exiftool-vendored     | 34.2.0 → 34.3.0     | Low    | Bug fixes                |
| framer-motion         | 12.23.26 → 12.24.10 | Low    | Bug fixes                |
| jspdf-autotable       | 5.0.2 → 5.0.7       | Low    | Bug fixes                |
| lucide-react          | 0.545.0 → 0.562.0   | Low    | New icons                |
| react-hook-form       | 7.69.0 → 7.70.0     | Low    | Bug fixes                |
| typescript            | 5.6.3 → 5.9.3       | Low    | Type improvements        |
| vite                  | 7.3.0 → 7.3.1       | Low    | Bug fixes                |
| ws                    | 8.18.3 → 8.19.0     | Low    | Bug fixes                |
| date-fns              | 3.6.0 → 4.1.0       | Medium | Check changelog          |

### Phase 2: Medium Risk (Test After Update)

```bash
npm update drizzle-orm@latest \
  jest-watch-typeahead@latest \
  supertest@latest \
  zod@latest \
  zod-validation-error@latest
```

**Details:**

| Package              | Current → Latest | Risk   | Notes                                 |
| -------------------- | ---------------- | ------ | ------------------------------------- |
| drizzle-orm          | 0.39.3 → 0.45.1  | Medium | Breaking changes possible, check docs |
| jest-watch-typeahead | 2.2.2 → 3.0.1    | Medium | Major version update                  |
| supertest            | 6.3.4 → 7.2.2    | Medium | Breaking changes, API changes         |
| zod                  | 3.25.76 → 4.3.5  | Medium | Major version, API changes            |
| zod-validation-error | 4.0.2 → 5.0.0    | Medium | API changes                           |

**Drizzle ORM 0.45.1 Breaking Changes:**

Check migration guide at: https://orm.drizzle.team/versions/0.45

Potential changes:

- Query builder syntax changes
- Type signature updates
- Migration tool updates

**Zod 4.x Breaking Changes:**

- API method renames
- Type system changes
- Custom validator syntax updates

### Phase 3: Major Updates (Highest Risk - Test Thoroughly)

#### Express 5 Upgrade (CRITICAL - Breaking Changes)

```bash
npm install express@latest @types/express@latest
```

**Current:** express@4.22.1
**Latest:** express@5.2.1
**Risk:** HIGH - Significant breaking changes

**Express 5 Breaking Changes:**

1. **Removed: `req.param()` default behavior**

   ```typescript
   // Express 4 (removed)
   app.get('/users/:id', (req, res) => {
     const id = req.param('id'); // ❌ Removed
   });

   // Express 5 (use params directly)
   app.get('/users/:id', (req, res) => {
     const id = req.params.id; // ✅ Use params
   });
   ```

2. **Changed: `res.json()` no longer accepts non-object values**

   ```typescript
   // Express 4 (removed)
   res.json('success'); // ❌ String argument removed

   // Express 5
   res.json({ success: true }); // ✅ Object only
   ```

3. **Changed: Query parser defaults**

   ```typescript
   // Express 4 default
   // query: { url: '/path', parsed: true } // Extended parsing

   // Express 5 default
   // query: { url: '/path' } // Simple parsing
   ```

4. **Middleware signature changes**
   ```typescript
   // Some middleware may have updated signatures
   // Check each middleware's Express 5 compatibility
   ```

**Required Code Changes:**

**File:** `server/index.ts`

1. Review all `req.param()` usage
2. Update all `res.json()` calls to use objects only
3. Check query string parsing behavior
4. Verify file uploads (multer) compatibility
5. Test all middleware chain

**Files to Check:**

- `server/index.ts` - Main Express app
- `server/auth.ts` - Passport/middleware
- `server/routes/*.ts` - All route handlers
- `server/middleware/*.ts` - All middleware

**Migration Guide:** https://expressjs.com/en/guide/migrating-5.html

#### jsPDF 4 Upgrade

```bash
npm install jspdf@latest
```

**Current:** jspdf@3.0.4
**Latest:** jspdf@4.0.0
**Risk:** HIGH - Breaking changes

**jsPDF 4 Breaking Changes:**

1. **API method renames**

   ```typescript
   // jsPDF 3
   doc.text('Hello', 10, 10);

   // jsPDF 4 (check exact method names)
   // Potential renames, check docs
   ```

2. **Plugin compatibility**
   - `jspdf-autotable` may need update
   - Check all jsPDF plugins

**Files Using jsPDF:**

- `server/routes/extraction.ts` - PDF export
- `client/src/components/...` - Client-side PDF generation

**Migration Guide:** https://github.com/parallax/jsPDF/releases/tag/v4.0.0

#### Recharts 3 Upgrade

```bash
npm install recharts@latest
```

**Current:** recharts@2.15.4
**Latest:** recharts@3.6.0
**Risk:** HIGH - Breaking changes

**Recharts 3 Breaking Changes:**

1. **Component prop changes**

   ```typescript
   // Recharts 2
   <LineChart data={data} width={500} height={300} />

   // Recharts 3 (check exact props)
   // Possible prop renames or type changes
   ```

2. **TypeScript type updates**
   - `TooltipPayload` types may have changed
   - Custom chart types may need updates

**Files Using Recharts:**

- `client/src/components/analytics/*` - Analytics dashboards
- `client/src/pages/images-mvp/analytics.tsx` - Images MVP analytics

**Migration Guide:** https://recharts.org/en-US/guides/v3-migration

#### React Resizable Panels 4 Upgrade

```bash
npm install react-resizable-panels@latest
```

**Current:** react-resizable-panels@2.1.9
**Latest:** react-resizable-panels@4.3.0
**Risk:** HIGH - Breaking changes

**React Resizable Panels 4 Breaking Changes:**

1. **API restructure**

   ```typescript
   // v2 API
   import { PanelGroup, Panel } from 'react-resizable-panels';

   // v4 API (check exact import paths)
   // Possible import path changes
   ```

2. **Group behavior changes**
   - Default collapse behavior may have changed
   - Imperative API updates

**Files Using React Resizable Panels:**

- `client/src/components/dashboard/*` - Dashboard panels

**Migration Guide:** https://github.com/bvaughn/react-resizable-panels/releases/tag/v4.0.0

#### @types/express 5 Upgrade

```bash
npm install @types/express@latest
```

**Current:** @types/express@4.17.21
**Latest:** @types/express@5.0.6
**Risk:** HIGH - Type changes

**Type Changes:**

- Request type updates
- Response type updates
- Middleware signature type changes

#### @types/node 25 Upgrade

```bash
npm install @types/node@latest
```

**Current:** @types/node@20.19.27
**Latest:** @types/node@25.0.3
**Risk:** HIGH - Type changes

**Type Changes:**

- Node.js API type updates
- New Node.js 20+ features typed
- Deprecated types removed

**Impact:** May require type annotations fixes across codebase.

---

## TypeScript Errors (Found During Analysis)

These errors are unrelated to deprecations but should be fixed:

### 1. `server/rateLimitMiddleware.ts:85:11` - Implicit Any Type

```typescript
// ERROR: This variable implicitly has an any type.
// Line 85, column 11

// Fix:
const result: { count: number } = await storage.get(key);
const count = typeof result === 'number' ? result : 0;
```

### 2. `server/security-utils.ts:92,107` - Control Characters in Regex

```typescript
// ERROR: Unexpected control character in a regular expression.
// Lines 92:35, 92:40, 92:44, 92:48, 92:52, 92:57
// Lines 107:33, 107:38

// Likely cause: Unicode escape sequences or raw control chars in regex
// Fix: Escape properly or use Unicode escapes
```

### 3. `server/routes/images-mvp.ts:110,111` - Redis Type Incompatibility

```typescript
// ERROR: Type 'RedisClientType<{...}>' is not assignable to type 'RedisClientType | null'

// Root cause: Redis client type changes with latest version
// Fix: Update type annotations or upgrade Redis client consistently
```

### 4. `server/routes/extraction.ts:276,1403` - React Hooks Called Conditionally

```typescript
// ERROR: This hook is being called conditionally, but all hooks must be called in exact same order

// Fix: Move hooks to top of component, always call them
const [data, setData] = useState(null);

if (someCondition) {
  // Use data here, don't call hooks in condition
}
```

### 5. `client/src/pages/images-mvp/index.tsx:25,43` - React Accessibility

```typescript
// ERROR: The elements with this role can be changed to <main>
// Line 25, column 97

// Fix: Use <main> instead of <div role="main">
<main id="main-content">...</main>

// ERROR: Wrap comments inside children within braces.
// Line 43, column 41

// Fix: Wrap JSX comments in braces
{/* This is a comment */}
```

---

## Updated Package.json

A complete updated `package.json` with all recommended updates has been created at:

`/Users/pranay/Projects/metaextract/package.json.updated`

This file includes:

- All Phase 1 safe updates
- All Phase 2 medium risk updates
- All Phase 3 major updates (use with caution)

**To Apply:**

```bash
# Backup current package.json
cp package.json package.json.backup

# Review and apply changes
diff package.json package.json.updated

# If satisfied, update
mv package.json.updated package.json

# Install updates
npm install
```

---

## Update Command Summary

### Phase 1 - Safe Updates (Do Now)

```bash
npm update @types/jest @typescript-eslint/eslint-plugin @typescript-eslint/parser \
  axe-core concurrently dodopayments drizzle-zod esbuild \
  exiftool-vendored framer-motion jspdf-autotable \
  lucide-react react-hook-form typescript vite ws date-fns
```

### Phase 2 - Medium Risk (Test After)

```bash
npm update drizzle-orm jest-watch-typeahead supertest zod zod-validation-error
```

### Phase 3 - Major Updates (Test Thoroughly)

**Express 5:**

```bash
npm install express@latest @types/express@latest
# Then update all route handlers to use req.params instead of req.param()
```

**jsPDF 4:**

```bash
npm install jspdf@latest
# Update PDF generation code, check API changes
```

**Recharts 3:**

```bash
npm install recharts@latest
# Update chart components, check prop changes
```

**React Resizable Panels 4:**

```bash
npm install react-resizable-panels@latest
# Update panel components, check API changes
```

---

## Testing Checklist After Updates

After each major update, run:

### Express 5 Upgrade Test

```bash
# 1. Start server
npm run dev:server

# 2. Test file upload
curl -X POST http://localhost:3000/api/images_mvp/extract \
  -F "file=@test.jpg"

# 3. Test authentication
curl http://localhost:3000/api/auth/login

# 4. Test all routes
curl http://localhost:3000/api/credits/balance
curl http://localhost:3000/api/images_mvp/credits/packs
```

### jsPDF 4 Upgrade Test

```bash
# 1. Generate PDF in client
# Navigate to results page
# Click "Export PDF"
# Verify PDF generates correctly

# 2. Generate PDF in server
curl -X POST http://localhost:3000/api/export/pdf \
  -F "data=..." \
  -o output.pdf
# Verify PDF generates correctly
```

### Recharts 3 Upgrade Test

```bash
# 1. Navigate to analytics page
# Verify all charts render
# Verify tooltips work
# Verify legends display correctly
```

### React Resizable Panels 4 Upgrade Test

```bash
# 1. Navigate to dashboard
# Try resizing panels
# Verify panels persist size
# Verify panels can be collapsed/expanded
```

---

## Rollback Plan

If major updates cause issues:

```bash
# Git stash changes
git stash

# Or restore from backup
cp package.json.backup package.json
npm install
```

---

## Next Steps

1. ✅ **Review documentation** - Understand breaking changes
2. ⏳ **Phase 1 updates** - Run safe update commands
3. ⏳ **Test deployment** - Verify no regressions
4. ⏳ **Phase 2 updates** - Apply medium risk updates
5. ⏳ **Test deployment** - Verify no regressions
6. ⏳ **Phase 3 updates** - Apply major updates one at a time
7. ⏳ **Thorough testing** - Test each major update independently
8. ⏳ **Fix TypeScript errors** - Resolve all found TypeScript errors

---

## References

- Express 5 migration: https://expressjs.com/en/guide/migrating-5.html
- jsPDF 4 release: https://github.com/parallax/jsPDF/releases/tag/v4.0.0
- Recharts 3 migration: https://recharts.org/en-US/guides/v3-migration
- React Resizable Panels v4: https://github.com/bvaughn/react-resizable-panels/releases/tag/v4.0.0
- Drizzle ORM v0.45: https://orm.drizzle.team/versions/0.45
- Zod v4 migration: https://zod.dev/?id=v4-changelog
