# MetaExtract v4.0.0

**The world's most comprehensive metadata extraction system** - extracting 45,000+ metadata fields from any file type across digital domains with forensic-grade precision and privacy-first access control.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Setup Python environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Development (concurrent frontend + backend)
npm run dev

# Production build
npm run build
npm start
```

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Access Control System](#access-control-system)
- [Hybrid Device-Free Mode](#hybrid-device-free-mode)
- [Payment & Credit System](#payment--credit-system)
- [Security Implementation](#security-implementation)
- [API Documentation](#api-documentation)
- [Development Guide](#development-guide)
- [Testing](#testing)
- [Deployment](#deployment)

---

## 🏗️ Architecture Overview

MetaExtract uses a **hybrid Node.js/Python architecture** designed for performance, extensibility, and security:

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                   │
│  - TypeScript + React 19                                     │
│  - TanStack Query for data management                        │
│  - Radix UI components with Tailwind CSS                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/WebSocket
┌──────────────────────▼──────────────────────────────────────┐
│              Backend (Express + Node.js)                     │
│  - TypeScript API routes                                     │
│  - Credit enforcement & access control                      │
│  - Payment webhook handling                                  │
│  - File upload & session management                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ Python Bridge
┌──────────────────────▼──────────────────────────────────────┐
│         Python Metadata Extraction Engine                    │
│  - Comprehensive module system (240+ modules)                │
│  - ExifTool, scientific formats, forensic analysis           │
│  - 45,000+ field extraction capabilities                     │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend**:
- React 19 + TypeScript
- Vite 7 for fast development
- TanStack React Query for state management
- Radix UI + Tailwind CSS for components
- React Router v7 for navigation

**Backend**:
- Node.js + Express
- TypeScript for type safety
- Drizzle ORM with PostgreSQL
- JWT authentication
- WebSocket support for real-time progress

**Extraction Engine**:
- Python 3 with comprehensive module system
- ExifTool for EXIF/IPTC/XMP data
- Specialized scientific/forensic parsers
- 240+ extraction modules covering all file types

---

## 🎯 Access Control System

### **CRITICAL: Pack-Based System (NOT Tier-Based)**

MetaExtract uses a **credit pack system** without subscription tiers for access control. This is a **deliberate architectural choice** that eliminates tier-bypass complexity.

### Access Modes

There are **three distinct access modes** that control what data users can see:

```typescript
type AccessMode = 'device_free' | 'trial_limited' | 'paid';

interface AccessInfo {
  mode: AccessMode;
  free_used?: number;      // Device-free usage counter (0-2)
  free_limit?: number;     // Always 2 for device-free
  credits_required?: number; // Credits needed for paid extraction
  credits_charged?: number; // Credits actually charged
  trial_granted?: boolean;  // Email trial flag
}
```

### Access Decision Logic

**File**: `server/routes/images-mvp.ts:1640-1750`

```typescript
// Priority order for access mode determination:

1. Email Trial (trial_limited)
   - User provides trial_email
   - Has < 2 previous uses
   - Heavy redaction, "free" engine tier
   - No credits charged

2. Device-Free (device_free)
   - First 2 extractions per device
   - Server-issued device token (resistant to cookie clearing)
   - High-value data shown, PII redacted
   - No credits charged
   - Uses "super" engine tier for quality

3. Credit-Based (paid)
   - Requires sufficient credit balance
   - Full data access, no redaction
   - 1 credit charged per standard image
   - Uses "super" engine tier
```

### Why Packs Instead of Tiers?

**Architectural Advantages**:
1. **No tier enforcement complexity**: Eliminates bypass vulnerabilities
2. **Simpler security model**: Credits are binary (have enough vs. don't)
3. **Better user experience**: Pay-per-use vs. subscription commitment
4. **Reduced attack surface**: No tier upgrade/downgrade logic to exploit

**Database Schema Difference**:
```typescript
// users table HAS tier field (for future use)
users.tier: 'free' | 'professional' | 'forensic' | 'enterprise'

// BUT: Extraction routes DON'T check user tier
// They ONLY check credit balance + device-free quota
```

### Engine Tiers vs User Tiers

**Important Distinction**:

```typescript
// Engine tier controls extraction depth (internal Python parameter)
const engineTier = accessMode === 'trial_limited' ? 'free' : 'super';

// User tier exists in database but is NOT used for access control
// It's reserved for future subscription-based features
```

---

## 🔓 Hybrid Device-Free Mode

### Design Philosophy

**"Show value, protect privacy"** - First 2 extractions demonstrate product capability while redacting only sensitive identifiers.

### What Device-Free Shows

**High-value fields** (shown to demonstrate product capability):
```typescript
interface DeviceFreeShown {
  exif: Record<string, any>;        // Raw EXIF tags (camera settings, etc.)
  calculated: {                      // Computed metadata
    aspect_ratio: number;
    megapixels: number;
    orientation: string;
  };
  file_integrity: {                  // Cryptographic hashes
    md5: string;
    sha1: string;
    sha256: string;
    crc32: string;
  };
  thumbnail: {                       // Presence + dimensions
    has_embedded: boolean;
    width: number;
    height: number;
  };
  perceptual_hashes: {               // Image similarity detection
    phash: string;
    dhash: string;
    ahash: string;
    whash: string;
  };
  metadata_comparison: {             // Cross-format analysis
    formats_consistent: boolean;
    field_count_delta: number;
  };
}
```

### What Device-Free Redacts

**Sensitive identifiers** (protected for privacy):
```typescript
interface DeviceFreeRedacted {
  gps: null | {                      // Location data
    _locked: true;                   // Completely locked, not just rounded
    // latitude, longitude, google_maps_url removed
  };
  burned_metadata: {
    extracted_text: null;            // OCR text removed (may contain addresses)
    parsed_data: {
      gps: null;                     // Burned-in GPS coordinates
      plus_code: null;              // Google Plus Codes
      location: {                    // Coarsened address
        city?: string;              // City/state/country kept
        state?: string;
        country?: string;
        // street, address lines removed
      };
    };
  };
  extended_attributes: {
    attributes: Record<string, null>; // Values redacted, count shown
  };
  filesystem: {                       // Server internals removed
    owner: null;
    owner_uid: null;
    group: null;
    group_gid: null;
    inode: null;
    device: null;
    permissions_octal: null;
    // size, timestamps kept
  };
}
```

### Enterprise Module Redaction

**Heavy computational modules** (hidden in device-free to avoid abuse):
```typescript
const ENTERPRISE_MODULES = [
  'drone_telemetry',      // Flight data, sensor readings
  'emerging_technology',  // AI/ML analysis, synthetic media detection
  'blockchain_provenance', // NFT/crypto metadata
  'synthetic_media_analysis' // Deepfake detection
];
```

### Implementation

**Backend**: `server/utils/extraction-helpers.ts:558-694`
```typescript
export function applyAccessModeRedaction(
  metadata: FrontendMetadataResponse,
  mode: 'device_free' | 'trial_limited' | 'paid'
) {
  if (mode === 'device_free') {
    // Redact GPS completely
    if (metadata.gps) {
      metadata.gps = { _locked: true };
    }

    // Remove burned text
    if (metadata.burned_metadata?.extracted_text) {
      metadata.burned_metadata.extracted_text = null;
    }

    // Hide enterprise modules
    ENTERPRISE_MODULES.forEach(mod => {
      if ((metadata as any)[mod]) {
        (metadata as any)[mod] = null;
      }
    });
  }
}
```

**Frontend**: `client/src/pages/results.tsx:291-293`
```typescript
// UI gating based on access.mode (NOT credits!)
const unlocked = access.mode
  ? access.mode === 'paid' || access.mode === 'device_free'
  : false;

// Show banner for device-free users
{access.mode === 'device_free' && (
  <Banner>
    Free check used ({access.free_used}/{access.free_limit}).
    Sensitive identifiers hidden: exact GPS, device IDs, owner fields,
    and OCR-extracted address text.
  </Banner>
)}
```

---

## 💳 Payment & Credit System

### Credit Pack Model

**DodoPayments Integration** for one-time credit purchases:

```typescript
const CREDIT_PACKS = {
  single: {
    credits: 10,
    price: 0,
    priceDisplay: '$0.00',
    name: 'Test Pack',
    description: '10 credits for testing'
  },
  batch: {
    credits: 50,
    price: 600,  // $6.00 in cents
    priceDisplay: '$6.00',
    name: 'Batch Pack',
    description: '50 credits - best for occasional use'
  },
  bulk: {
    credits: 200,
    price: 2800, // $28.00 in cents
    priceDisplay: '$28.00',
    name: 'Bulk Pack',
    description: '200 credits - best value'
  }
};
```

### Credit Costs

```typescript
const CREDIT_COSTS = {
  standard_image: 1,   // JPG, PNG, GIF, etc.
  raw_image: 2,        // RAW formats (CR2, NEF, etc.)
  video: 3,           // MP4, MOV, etc.
  audio: 2,           // MP3, WAV, etc.
  pdf: 1              // PDF documents
};
```

### Payment Security

**File**: `server/payments.ts:703-821`

**Webhook Signature Validation**:
```typescript
app.post('/api/webhooks/dodo', async (req, res) => {
  // 1. Extract webhook signature headers
  const webhookId = req.headers['webhook-id'];
  const webhookSignature = req.headers['webhook-signature'];
  const webhookTimestamp = req.headers['webhook-timestamp'];

  // 2. Verify timestamp freshness (5-minute window)
  const timestamp = parseInt(webhookTimestamp);
  const now = Math.floor(Date.now() / 1000);
  if (Math.abs(now - timestamp) > 300) {
    return res.status(400).json({ error: 'Webhook timestamp expired' });
  }

  // 3. Verify HMAC-SHA256 signature
  const signedPayload = `${webhookId}.${webhookTimestamp}.${JSON.stringify(req.body)}`;
  const expectedSignature = crypto
    .createHmac('sha256', DODO_WEBHOOK_SECRET)
    .update(signedPayload, 'utf8')
    .digest('base64');

  // 4. Timing-safe comparison
  const signature = webhookSignature.split(',').find(p => p.startsWith('v1,'))?.replace('v1,', '');
  if (!crypto.timingSafeEqual(
    Buffer.from(signature, 'base64'),
    Buffer.from(expectedSignature, 'base64')
  )) {
    return res.status(400).json({ error: 'Invalid webhook signature' });
  }

  // 5. Idempotency check
  if (processedWebhooks.has(webhookId)) {
    return res.json({ received: true, duplicate: true });
  }
  processedWebhooks.set(webhookId, Date.now());

  // 6. Process payment event
  await handlePaymentSucceeded(event.data);
});
```

**Security Features**:
- ✅ **HMAC-SHA256 signature verification** prevents spoofing
- ✅ **Timestamp validation** prevents replay attacks
- ✅ **Idempotency tracking** prevents duplicate credit grants
- ✅ **Timing-safe comparison** prevents timing attacks
- ✅ **Automatic cleanup** of old webhook IDs (hourly)

### Credit Enforcement

**File**: `server/routes/images-mvp.ts:1661-1668`

```typescript
// Check credit balance before extraction
const balance = await storage.getOrCreateCreditBalance(balanceKey, userId);

if (!balance || balance.credits < creditCost) {
  return sendQuotaExceededError(res,
    `Insufficient credits (required: ${creditCost}, available: ${balance?.credits ?? 0})`
  );
}

// Atomic credit deduction
await storage.useCredits(balance.id, creditCost, `Extraction: ${fileType}`);
```

---

## 🔒 Security Implementation

### Architecture Principles

1. **Defense in Depth**: Multiple security layers
2. **Fail Securely**: Default to restrictive permissions
3. **Zero Trust**: Verify everything, trust nothing
4. **Privacy First**: Redact sensitive data by default

### Critical Security Fixes

**File**: `doc/SECURITY_FIXES_JAN5_2026.md`

#### 1. Legacy Route Memory Exhaustion ✅ FIXED
**Vulnerability**: `/api/extract` route allowed unlimited file uploads
**Fix**: Route registration commented out in `server/routes_legacy.ts`
**Verification**: `test_legacy_route_disabled.js` (needs ES module fix)

#### 2. Webhook Signature Validation ✅ IMPLEMENTED
**Vulnerability**: Payment webhooks not verified, allowing credit spoofing
**Fix**: HMAC-SHA256 signature validation with timestamp checking
**Impact**: Critical - prevents fake payment events

#### 3. Credit Deduction Race Condition ✅ FIXED
**Vulnerability**: Credits charged asynchronously, could fail silently
**Fix**: Changed to `await storage.useCredits()` with proper error handling
**Impact**: High - prevents revenue loss

#### 4. Default Tier Bypass ✅ FIXED
**Vulnerability**: `useEffectiveTier()` returned `'enterprise'` for unauthenticated users
**Fix**: Changed default return to `'free'`
**Impact**: Critical - prevents unauthorized premium access

### Rate Limiting

```typescript
// Multi-layer rate limiting
app.use('/api', rateLimitAPI());              // Global API limit
app.use(rateLimitExtraction());                // Extraction-specific limit
app.use(uploadLimiter);                        // Upload endpoint limit
```

### File Upload Security

```typescript
// Multer configuration
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 100 * 1024 * 1024,  // 100MB max
    files: 1                       // Single file only
  },
  fileFilter: (req, file, cb) => {
    // MIME type validation
    const allowedMimes = new Set(['image/jpeg', 'image/png', ...]);
    if (!allowedMimes.has(file.mimetype)) {
      return cb(new Error('File type not permitted'));
    }
    cb(null, true);
  }
});
```

### Authentication Security

**File**: `server/auth.ts`

- **CSRF Protection**: User-specific tokens for state-changing operations
- **Session Management**: Secure cookie handling with httpOnly + sameSite
- **Password Hashing**: bcrypt with salt rounds
- **JWT Validation**: Proper token verification and expiration
- **Account Lockout**: Failed attempt tracking with exponential backoff

---

## 📡 API Documentation

### Core Endpoints

#### Metadata Extraction
```http
POST /api/images_mvp/extract
Content-Type: multipart/form-data

{
  file: <binary>,              // Image file (required)
  trial_email?: string,         // For email trial (optional)
  quote_id?: string,            // For quoted cost (optional)
  client_file_id?: string,      // Client-side file ID (optional)
  session_id?: string,          // WebSocket session ID (optional)
  store?: boolean               // Store extraction result (optional)
}

Response 200:
{
  access: {
    mode: 'device_free' | 'trial_limited' | 'paid',
    free_used: number,
    free_limit: number,
    credits_required: number,
    credits_charged: number
  },
  metadata: { /* Extraction results */ },
  extraction_info: {
    processing_ms: number,
    fields_extracted: number,
    tier: string
  }
}

Error 402: { error: "Insufficient credits", required: 1, available: 0 }
Error 403: { error: "File type not permitted" }
Error 429: { error: "Rate limit exceeded" }
```

#### Credit Balance
```http
GET /api/credits/balance

Response 200:
{
  credits: 50,
  balanceId: "uuid"
}
```

#### Credit Purchase
```http
POST /api/credits/purchase
Content-Type: application/json

{
  pack: 'single' | 'batch' | 'bulk',
  email?: string
}

Response 200:
{
  checkout_url: "https://checkout.dodopayments.com/...",
  session_id: "session_uuid"
}
```

#### Credit Packs Info
```http
GET /api/credits/packs

Response 200:
{
  packs: { /* CREDIT_PACKS */ },
  costs: { /* CREDIT_COSTS */ },
  description: "1 credit = 1 standard file extraction"
}
```

### WebSocket Progress Updates

```javascript
const ws = new WebSocket('ws://localhost:3000/progress');

// Client sends
ws.send(JSON.stringify({
  session_id: 'client_session_id',
  action: 'subscribe'
}));

// Server sends progress updates
{
  session_id: string,
  progress: number,        // 0-100
  message: string,
  stage: string,           // 'upload_complete', 'extraction_start', etc.
  timestamp: string
}
```

---

## 🛠️ Development Guide

### Environment Setup

```bash
# Clone repository
git clone https://github.com/metaextract/metaextract.git
cd metaextract

# Install Node dependencies
npm install

# Setup Python environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# Setup database
npm run db:push
npm run seed:test-users  # Optional: create test users

# Start development servers
npm run dev  # Runs both frontend (:5173) and backend (:3000)
```

### Environment Variables

```bash
# Required
DATABASE_URL=postgresql://user:password@localhost:5432/metaextract
JWT_SECRET=your-super-secure-random-jwt-secret-here-at-least-32-characters
PYTHON_EXECUTABLE=/path/to/.venv/bin/python3

# Optional (for payments)
DODO_PAYMENTS_API_KEY=pk_test_...
DODO_WEBHOOK_SECRET=whsec_...
DODO_ENV=test  # or 'live'

# Optional (for hosting)
RAILWAY_PUBLIC_DOMAIN=your-app.railway.app
BASE_URL=https://your-domain.com
```

### Project Structure

```
metaextract/
├── client/                    # React frontend
│   ├── src/
│   │   ├── components/       # Reusable components
│   │   ├── pages/           # Route pages
│   │   ├── lib/             # Utilities, API client
│   │   └── __tests__/       # Frontend tests
│   └── package.json
├── server/                   # Node.js backend
│   ├── auth.ts              # Authentication system
│   ├── routes/              # API routes
│   │   ├── images-mvp.ts    # Main extraction endpoint
│   │   └── index.ts         # Route registration
│   ├── utils/               # Helper functions
│   ├── storage/             # Data access layer
│   ├── payments.ts          # Payment system
│   └── extractor/           # Python extraction engine
│       └── modules/         # 240+ extraction modules
├── shared/                  # Shared TypeScript code
│   └── schema.ts           # Database schemas
├── tests/                  # Test files
│   ├── e2e/               # Playwright end-to-end tests
│   └── debug_outputs/     # Test fixtures
└── package.json           # Root package.json
```

### Code Quality

```bash
# Type checking
npm run type-check

# Linting
npm run lint
npm run lint:fix

# Formatting
npm run format
npm run format:check

# All validations
npm run validate  # Runs type-check + lint + test:ci
```

---

## 🧪 Testing

### Test Structure

```bash
# Unit tests (Jest)
npm run test                 # Run all tests
npm run test:watch          # Watch mode
npm run test:coverage       # Generate coverage report
npm run test:ci            # CI mode (non-interactive)

# Integration tests
npm run smoke-server        # Test server health

# E2E tests (Playwright)
npm run test:e2e:smoke     # Smoke tests
npm run test:e2e:visual    # Visual regression tests
npm run test:e2e:visual:ci # CI visual tests
```

### Test Coverage

- **Backend**: Unit tests for routes, utilities, payment system
- **Frontend**: Component tests, hook tests, integration tests
- **E2E**: Critical user flows (upload, extract, purchase)
- **Security**: Authentication bypass, payment spoofing tests

### Key Test Files

- `server/routes/images-mvp.test.ts` - Extraction endpoint tests
- `server/utils/extraction-helpers.test.ts` - Redaction logic tests
- `server/payments.test.ts` - Payment system tests
- `client/src/__tests__/images-mvp.device-free.test.tsx` - Device-free UI tests
- `tests/e2e/images-mvp.smoke.spec.ts` - E2E smoke tests

---

## 🚀 Deployment

### Production Build

```bash
# Build frontend and backend
npm run build

# Start production server
NODE_ENV=production npm start
```

### Deployment Platforms

**Railway** (recommended):
```bash
# Install Railway CLI
npm install -g @railway/cli

# Link project
railway link

# Deploy
railway up
```

**Docker**:
```dockerfile
# Dockerfile included
docker build -t metaextract .
docker run -p 3000:3000 metaextract
```

### Environment Variables for Production

```bash
# Required
NODE_ENV=production
DATABASE_URL=postgresql://...
JWT_SECRET=strong-random-secret-32-chars-min
PYTHON_EXECUTABLE=/usr/bin/python3

# Payments
DODO_PAYMENTS_API_KEY=pk_live_...
DODO_WEBHOOK_SECRET=whsec_live_...
DODO_ENV=live

# Hosting
RAILWAY_PUBLIC_DOMAIN=your-domain.railway.app
BASE_URL=https://your-domain.com

# Optional
REDIS_URL=redis://...  # For caching
LOG_LEVEL=info
```

### Health Checks

```bash
# Server health
curl https://your-domain.com/health

# Database connectivity
curl https://your-domain.com/api/health/db

# Extraction system smoke test
npm run smoke-server
```

---

## 📊 System Capabilities

### Supported File Types

**Images**: JPG, PNG, GIF, WebP, AVIF, TIFF, RAW (CR2, NEF, ARW, etc.), PSD, BMP, ICO
**Video**: MP4, MOV, AVI, MKV, WebM
**Audio**: MP3, WAV, FLAC, AAC, OGG
**Documents**: PDF, DOC, DOCX, XLS, PPT
**Scientific**: DICOM, FITS, HDF5
**Forensic**: EXE, DLL, SYS, EML (email)

### Metadata Categories

- **Basic**: File size, dimensions, format, MIME type
- **EXIF**: Camera settings, GPS, timestamps, orientation
- **IPTC**: Copyright, keywords, categories, author info
- **XMP**: Adobe metadata, ratings, labels
- **GPS**: Coordinates, altitude, speed, map links
- **Thumbnail**: Embedded previews, dimensions
- **Hashes**: MD5, SHA1, SHA256, CRC32, perceptual hashes
- **Forensic**: Manipulation detection, steganography analysis
- **Advanced**: Drone telemetry, blockchain NFT data, AI generation detection
- **Scientific**: Medical imaging, astronomical data, geospatial analysis

### Field Count

- **Total modules**: 240+
- **Total extractable fields**: 45,000+
- **Supported file formats**: 500+
- **Processing languages**: Python, Node.js

---

## 🐛 Troubleshooting

### Common Issues

**1. Python extraction fails**
```bash
# Check Python executable
echo $PYTHON_EXECUTABLE  # Should point to .venv/bin/python3

# Test extraction manually
.venv/bin/python3 server/extractor/comprehensive_metadata_engine.py test.jpg --tier super
```

**2. Database connection errors**
```bash
# Check DATABASE_URL
echo $DATABASE_URL

# Test connection
npm run check:db
```

**3. Payment webhook verification fails**
```bash
# Check DODO_WEBHOOK_SECRET
echo $DODO_WEBHOOK_SECRET

# Test webhook signature (see test scripts)
node scripts/test-webhook.js
```

**4. Rate limiting issues**
```bash
# Check rate limit status
curl http://localhost:3000/api/health/rate-limits
```

### Debug Mode

```bash
# Enable verbose logging
LOG_LEVEL=debug npm run dev:server

# Enable Python debug output
PYTHON_VERBOSE=1 npm run dev:server
```

---

## 📈 Performance

### Benchmarks

- **Standard image extraction**: 2-5 seconds
- **RAW image extraction**: 5-15 seconds
- **Video metadata**: 3-10 seconds
- **PDF analysis**: 1-5 seconds
- **Concurrent users**: 100+ (with rate limiting)
- **Files processed per day**: 10,000+ (production)

### Optimization

- **Redis caching**: Frequently accessed metadata
- **Async processing**: Non-blocking extraction
- **Rate limiting**: Prevents abuse
- **Circuit breakers**: Load shedding under high demand
- **WebSocket progress**: Real-time updates

---

## 🤝 Contributing

### Development Workflow

```bash
# 1. Fork and clone
git clone https://github.com/your-username/metaextract.git

# 2. Create feature branch
git checkout -b feature/your-feature

# 3. Make changes and test
npm run validate

# 4. Commit and push
git commit -m "Add your feature"
git push origin feature/your-feature

# 5. Create pull request
# Include description of changes and test results
```

### Code Standards

- **TypeScript**: Strict mode enabled
- **Python**: PEP 8 style guide
- **Testing**: 80%+ coverage required for new code
- **Documentation**: JSDoc for TypeScript, docstrings for Python

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **ExifTool** by Phil Harvey - Foundation of EXIF extraction
- **DodoPayments** - Payment processing
- **Radix UI** - Beautiful, accessible components
- **Vite** - Lightning-fast build tool
- **Playwright** - Reliable E2E testing

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/metaextract/metaextract/issues)
- **Documentation**: [docs/](./docs/) directory
- **API Reference**: See API Documentation section above

---

**Built with ❤️ by the MetaExtract Team**

*Version 4.0.0 - January 2026*