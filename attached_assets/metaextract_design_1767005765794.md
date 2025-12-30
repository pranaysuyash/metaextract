# MetaExtract: Standalone Metadata Extraction App
## Product Design Document

**Version:** 1.0  
**Date:** December 29, 2024  
**Status:** Design Phase  
**Relationship:** Standalone product, later "by PhotoSearch"

---

## 📋 Executive Summary

**MetaExtract** is a lightweight, standalone web application that extracts comprehensive metadata from digital files. It leverages PhotoSearch's world-class `metadata_extractor.py` backend (320+ fields across images, videos, audio, PDFs, SVGs) to provide forensic-grade metadata extraction as a freemium service.

### Why This Product

1. **Existing Backend** - `metadata_extractor.py` is already standalone-ready
2. **Validated Market** - Digital forensics, OSINT, photography, legal, journalism
3. **Low Effort** - 1-2 week MVP, no new ML models required
4. **Revenue Validation** - If people pay for extraction, PhotoSearch has market
5. **Lead Generation** - Funnel to full PhotoSearch for power users

---

## 🎯 Target Audiences (Priority Order)

### 1. **Digital Forensics & Legal** ⭐ PRIMARY
- Lawyers needing evidence verification
- Private investigators tracing photo origins
- Insurance fraud analysts
- eDiscovery professionals
- Law enforcement (OSINT)

**What they need:**
- File hashes (MD5, SHA256) for chain of custody
- GPS coordinates to place photos at locations
- Timestamps to establish timelines
- Device identification (camera make/model/serial)
- Modification detection (created vs modified dates)
- Exportable reports for legal proceedings

### 2. **Journalists & Fact-Checkers** 
- Verification of photo authenticity
- Tracing image origins
- Checking for manipulation signals
- Confirming claimed locations/times

### 3. **Security Researchers & OSINT**
- Bug bounty hunters checking for data leaks
- Privacy auditors
- Penetration testers
- Intelligence analysts

### 4. **Photographers & Content Creators**
- Checking camera settings from old photos
- Verifying export settings before delivery
- Comparing compression across platforms
- Learning from settings of good shots

### 5. **Privacy-Conscious Users**
- Checking what data their photos expose
- Verifying metadata was stripped before sharing
- Understanding what apps can see about them

---

## 💰 Pricing Strategy

### Tier Structure

| Tier | Files/Day | Max Size/File | Fields | Price |
|------|-----------|---------------|--------|-------|
| **Free** (no signup) | 5 | 5 MB | ~20 basic | $0 |
| **Free + Account** | 10 | 10 MB | ~50 standard | $0 |
| **Pro** | 100 | 100 MB | 320+ all fields | $7/mo or 70 credits |
| **Business** | 500 | 500 MB | 320+ + API + batch | $19/mo or 200 credits |
| **Enterprise** | Unlimited | 2 GB | Custom | Contact |

### Credit System (Pay-as-you-go)
- **$1 = 10 credits**
- Standard image extraction = 1 credit
- Large file (>50MB) = 2-3 credits
- Video file = 2 credits
- Batch (10+ files) = 0.8 credits each (20% discount)
- API call = 1 credit

### Field Gating Strategy

#### **Free Tier (~20 fields)**
```
Filesystem:
  ✓ file_name, extension, size_human, mime_type
  ✓ created, modified

Basic EXIF:
  ✓ camera.make, camera.model
  ✓ width, height, format
  ✓ date_taken

GPS (basic):
  ✓ latitude, longitude (if present)
  ✓ "GPS data found" indicator

Hashes:
  ✗ Locked (show "MD5: ●●●●●●... [Upgrade to see]")
```

#### **Standard Tier (~50 fields)** - Free with Account
```
Everything in Free, plus:

EXIF Extended:
  ✓ iso, aperture, shutter_speed, focal_length
  ✓ flash, exposure_mode, metering_mode
  ✓ white_balance, color_space

GPS Full:
  ✓ altitude, speed, direction
  ✓ timestamp, datestamp

Timestamps:
  ✓ digitized, original, subsec times

Filesystem Extended:
  ✓ accessed, permissions, owner
```

#### **Pro Tier (320+ fields)** - Paid
```
Everything in Standard, plus:

Complete EXIF:
  ✓ ALL MakerNote data (manufacturer-specific)
  ✓ lens_make, lens_model, serial_number
  ✓ ALL GPS fields (satellites, DOP, processing method)
  ✓ scene_type, subject_distance, digital_zoom_ratio

File Integrity:
  ✓ MD5 hash
  ✓ SHA256 hash
  ✓ Hash verification tool

Calculated Metadata:
  ✓ aspect_ratio (16:9, 3:2, etc.)
  ✓ megapixels
  ✓ orientation (portrait/landscape/square)
  ✓ file_age (human readable)

Extended Attributes:
  ✓ macOS Finder tags, comments
  ✓ Spotlight metadata (kMDItem*)
  ✓ Custom xattr

Image Quality Analysis:
  ✓ bits_per_pixel
  ✓ compression type
  ✓ ICC profile details
  ✓ color palette (for indexed images)

Video (if enabled):
  ✓ ALL streams (video, audio, subtitles)
  ✓ codecs, bitrates, frame rates
  ✓ chapters, tags
  ✓ HDR metadata

Audio (if enabled):
  ✓ ID3/Vorbis/iTunes tags
  ✓ album art detection
  ✓ duration, bitrate, sample_rate

PDF (if enabled):
  ✓ page_count, author, title
  ✓ creation/modification dates
  ✓ encryption status, producer

SVG (if enabled):
  ✓ viewBox, element_count
  ✓ has_scripts, has_links
  ✓ Dublin Core metadata
```

#### **Business Tier** - Paid
```
Everything in Pro, plus:

API Access:
  ✓ REST API endpoints
  ✓ Webhook notifications
  ✓ SDK (Python, JavaScript)

Batch Processing:
  ✓ Upload up to 100 files
  ✓ Bulk export (JSON, CSV)
  ✓ ZIP download

Team Features:
  ✓ Team workspace
  ✓ Shared extraction history
  ✓ Usage analytics

Advanced Export:
  ✓ PDF forensic report
  ✓ Court-ready documentation
  ✓ Custom branding
  ✓ Comparison reports
```

---

## 🏗️ Architecture

### MVP Stack (Recommended)

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                          │
│  Hosting: Vercel (free tier initially)                       │
│                                                              │
│  Components:                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  DropZone    │  │  Results     │  │  Pricing     │       │
│  │  (upload)    │  │  Display     │  │  Page        │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Field       │  │  Export      │  │  Usage       │       │
│  │  Toggles     │  │  Options     │  │  Dashboard   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
│  Hosting: Railway / Fly.io / Render ($5-10/mo)              │
│                                                              │
│  Endpoints:                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ POST         │  │ GET          │  │ GET          │       │
│  │ /extract     │  │ /usage       │  │ /fields      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ POST         │  │ POST         │  │ GET          │       │
│  │ /batch       │  │ /export      │  │ /credits     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │     metadata_extractor.py (from PhotoSearch)           │ │
│  │     - extract_all_metadata()                           │ │
│  │     - Already handles images, video, audio, PDF, SVG   │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    SERVICES                                  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Clerk      │  │   Stripe     │  │  PostHog     │       │
│  │   (Auth)     │  │  (Payments)  │  │ (Analytics)  │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │  Upstash     │  │   R2/S3      │                         │
│  │  (Rate Limit)│  │ (Temp Store) │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

### File Processing Flow

```
1. User drops file → Frontend validates (size, type)
                          │
2. Upload to backend → Stored in memory (never disk for free tier)
                          │
3. Check rate limits → Upstash Redis (IP + user_id based)
                          │
4. Extract metadata → metadata_extractor.extract_all_metadata()
                          │
5. Filter by tier → Remove locked fields for free users
                          │
6. Return JSON → Frontend displays with locked field indicators
                          │
7. Delete file → Immediate deletion (privacy guarantee)
```

### Privacy Architecture

**CRITICAL: Files are NEVER stored permanently**

```python
@app.post("/extract")
async def extract_metadata(file: UploadFile, user: Optional[User]):
    try:
        # 1. Read file into memory
        content = await file.read()
        
        # 2. Create temp file (deleted after processing)
        with tempfile.NamedTemporaryFile(delete=True) as tmp:
            tmp.write(content)
            tmp.flush()
            
            # 3. Extract metadata
            metadata = extract_all_metadata(tmp.name)
        
        # 4. File automatically deleted when context exits
        
        # 5. Filter metadata based on user tier
        filtered = filter_by_tier(metadata, user.tier if user else "free")
        
        # 6. Return (original file content is garbage collected)
        return {"metadata": filtered, "tier": user.tier if user else "free"}
        
    except Exception as e:
        # Even on error, temp file is cleaned up
        raise HTTPException(500, "Extraction failed")
```

---

## 📱 UI/UX Design

### Landing Page Structure

```
┌─────────────────────────────────────────────────────────────┐
│  🔍 MetaExtract                              [Sign In]       │
│     The most comprehensive metadata extraction on the web    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                                                     │    │
│  │     📁 Drop your file here                          │    │
│  │         or click to browse                          │    │
│  │                                                     │    │
│  │     Supports: JPG, PNG, HEIC, MP4, MP3, PDF, SVG   │    │
│  │     Max 5MB per file • 5 files per day (free)      │    │
│  │                                                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  🔒 Your files are processed in memory and never stored     │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Trusted by forensics professionals, journalists,           │
│  photographers, and security researchers worldwide.         │
│                                                              │
│  [320+ fields] [Zero storage] [Instant results]            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Results Display (After Upload)

```
┌─────────────────────────────────────────────────────────────┐
│  📄 IMG_2847.jpg                    [JSON] [CSV] [PDF ⭐]   │
│  2.3 MB • JPEG • 4032 × 3024                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📁 File Information                              [▼ open]   │
│  ├─ Name: IMG_2847.jpg                                      │
│  ├─ Size: 2.3 MB (2,413,568 bytes)                         │
│  ├─ Type: image/jpeg                                        │
│  ├─ Created: Dec 15, 2024 3:42:18 PM                       │
│  └─ Modified: Dec 15, 2024 3:42:18 PM                      │
│                                                              │
│  📷 Camera & Lens                                 [▼ open]   │
│  ├─ Make: Apple                                             │
│  ├─ Model: iPhone 15 Pro Max                               │
│  ├─ Lens: iPhone 15 Pro Max back triple camera             │
│  ├─ Serial: ●●●●●●●●●●●● [🔒 Upgrade to Pro]               │
│  └─ Firmware: 17.2                                          │
│                                                              │
│  ⚙️ Capture Settings                              [▼ open]   │
│  ├─ ISO: 50                                                 │
│  ├─ Aperture: f/2.8                                        │
│  ├─ Shutter: 1/120                                         │
│  ├─ Focal Length: 24mm                                     │
│  └─ Flash: Off                                              │
│                                                              │
│  📍 Location                                      [▼ open]   │
│  ├─ Latitude: 37.7749° N                                   │
│  ├─ Longitude: 122.4194° W                                 │
│  ├─ Altitude: 12m above sea level                          │
│  └─ [🗺️ View on Map]                                        │
│                                                              │
│  🔐 File Integrity                    [🔒 Upgrade to Pro]   │
│  ├─ MD5: ●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●                  │
│  └─ SHA256: ●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●● │
│                                                              │
│  📊 Calculated                        [🔒 Upgrade to Pro]   │
│  ├─ Aspect Ratio: ●●●●● [🔒]                               │
│  ├─ Megapixels: ●●●●● [🔒]                                 │
│  └─ Orientation: ●●●●● [🔒]                                │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  ⚡ Want all 320+ fields? Upgrade to Pro for $7/month       │
│  [Upgrade Now]                [View Pricing]                 │
└─────────────────────────────────────────────────────────────┘
```

### Locked Field UI Pattern

For locked fields, show tantalizing hints:

```tsx
// Instead of hiding, show locked preview
{!isPro ? (
  <div className="flex items-center gap-2 text-muted-foreground">
    <Lock className="h-4 w-4" />
    <span>SHA256: {metadata.hashes.sha256.slice(0, 8)}●●●●●●●●</span>
    <Badge variant="outline" className="text-xs">Pro</Badge>
  </div>
) : (
  <div>{metadata.hashes.sha256}</div>
)}
```

---

## 🔧 API Design

### Endpoints

```yaml
# Public Endpoints
POST /api/extract
  - Upload file, get metadata
  - Rate limited by IP (free) or user_id (authenticated)
  - Returns filtered metadata based on tier

GET /api/fields
  - List all available fields by tier
  - Used for documentation and UI

GET /api/usage
  - Current usage stats for authenticated user
  - Daily count, credits remaining, tier info

# Authenticated Endpoints  
POST /api/batch
  - Upload multiple files (Business tier)
  - Returns array of metadata

POST /api/export
  - Generate export (JSON, CSV, PDF report)
  - PDF requires Pro tier

GET /api/history
  - Get extraction history (Pro tier)
  - Last 30 days

# Webhook (Business tier)
POST /api/webhook/register
  - Register webhook URL for async processing

# Admin
GET /api/admin/stats
  - Usage statistics, revenue, etc.
```

### Request/Response Examples

```python
# POST /api/extract
# Request
Content-Type: multipart/form-data
file: <binary>

# Response (Free tier)
{
  "success": true,
  "tier": "free",
  "fields_returned": 20,
  "fields_available": 320,
  "metadata": {
    "file": {
      "name": "IMG_2847.jpg",
      "size_bytes": 2413568,
      "size_human": "2.3 MB",
      "extension": ".jpg",
      "mime_type": "image/jpeg"
    },
    "filesystem": {
      "created": "2024-12-15T15:42:18Z",
      "modified": "2024-12-15T15:42:18Z"
    },
    "image": {
      "width": 4032,
      "height": 3024,
      "format": "JPEG"
    },
    "exif": {
      "image": {
        "Make": "Apple",
        "Model": "iPhone 15 Pro Max"
      }
    },
    "gps": {
      "latitude": 37.7749,
      "longitude": -122.4194
    }
  },
  "locked_fields": [
    "hashes.md5",
    "hashes.sha256",
    "exif.image.SerialNumber",
    "calculated.aspect_ratio",
    "calculated.megapixels",
    "extended_attributes.*"
  ],
  "usage": {
    "daily_used": 3,
    "daily_limit": 5,
    "remaining": 2
  },
  "upgrade_cta": {
    "message": "Unlock 300+ more fields with Pro",
    "url": "/pricing"
  }
}
```

---

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clerk_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    tier VARCHAR(50) DEFAULT 'free',
    credits INTEGER DEFAULT 0,
    stripe_customer_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Usage Table
```sql
CREATE TABLE usage (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    ip_address INET,
    extraction_date DATE NOT NULL,
    file_type VARCHAR(50),
    file_size_bytes BIGINT,
    fields_returned INTEGER,
    tier_at_time VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for rate limiting
CREATE INDEX idx_usage_user_date ON usage(user_id, extraction_date);
CREATE INDEX idx_usage_ip_date ON usage(ip_address, extraction_date);
```

### Credits History
```sql
CREATE TABLE credit_transactions (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    amount INTEGER NOT NULL,  -- positive for purchases, negative for usage
    type VARCHAR(50) NOT NULL,  -- 'purchase', 'subscription', 'extraction', 'refund'
    description TEXT,
    stripe_payment_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🚀 Implementation Roadmap

### Phase 1: MVP (Week 1-2)

**Goal:** Working extraction with free tier limits

**Backend:**
- [ ] Create new FastAPI project: `metaextract-api/`
- [ ] Copy `metadata_extractor.py` from PhotoSearch
- [ ] Implement `/extract` endpoint
- [ ] Implement tier-based field filtering
- [ ] Add IP-based rate limiting (Upstash Redis)
- [ ] Deploy to Railway

**Frontend:**
- [ ] Create React app with Vite
- [ ] Build DropZone component
- [ ] Build MetadataDisplay component
- [ ] Build locked field indicators
- [ ] Deploy to Vercel

**No auth, no payments - just working extraction**

### Phase 2: Auth & Limits (Week 2-3)

**Goal:** User accounts with proper rate limiting

- [ ] Integrate Clerk for authentication
- [ ] Create users table in Supabase/Postgres
- [ ] Implement user-based rate limiting
- [ ] Add extraction history for logged-in users
- [ ] Free tier: 10 files/day (vs 5 for anon)

### Phase 3: Payments (Week 3-4)

**Goal:** Revenue!

- [ ] Integrate Stripe
- [ ] Implement Pro tier ($7/mo)
- [ ] Implement credit purchases
- [ ] Build pricing page
- [ ] Build usage dashboard

### Phase 4: Polish (Week 4-5)

**Goal:** Production-ready

- [ ] Add PDF forensic report export
- [ ] Implement batch upload (Business)
- [ ] Build API documentation
- [ ] Add PostHog analytics
- [ ] SEO optimization
- [ ] Landing page content

### Phase 5: Growth (Ongoing)

- [ ] Chrome extension
- [ ] CLI tool
- [ ] Public API launch
- [ ] "by PhotoSearch" branding addition

---

## 📈 Success Metrics

### Week 1 (MVP)
- [ ] 100+ extractions
- [ ] <3s average extraction time
- [ ] Zero file storage (verified)

### Month 1
- [ ] 1,000+ unique users
- [ ] 10+ Pro conversions ($70 MRR)
- [ ] <1% error rate

### Month 3
- [ ] 10,000+ unique users
- [ ] 100+ paying users ($700+ MRR)
- [ ] API adoption begins

### Month 6
- [ ] 50,000+ unique users
- [ ] $2,000+ MRR
- [ ] "by PhotoSearch" integration live

---

## 🔗 Relationship to PhotoSearch

### Phase 1: Standalone
- MetaExtract launches independently
- No mention of PhotoSearch
- Focus on extraction utility

### Phase 2: Soft Connection
- "Built with technology from PhotoSearch"
- Footer link to PhotoSearch
- Optional: "Want to search 50,000 photos by metadata? Try PhotoSearch"

### Phase 3: Integration
- "MetaExtract by PhotoSearch"
- Unified account system
- PhotoSearch Pro includes MetaExtract Pro

---

## 💡 Competitive Advantages

| Feature | MetaExtract | exiftool.org | Jeffrey's Exif | metapicz |
|---------|-------------|--------------|----------------|----------|
| Fields extracted | 320+ | 300+ | 100+ | 50+ |
| Video support | ✓ | ✓ | ✗ | ✗ |
| Audio support | ✓ | Limited | ✗ | ✗ |
| PDF support | ✓ | ✗ | ✗ | ✗ |
| SVG support | ✓ | ✗ | ✗ | ✗ |
| Beautiful UI | ✓ | ✗ | ✗ | ✓ |
| File hashes | ✓ | ✗ | ✗ | ✗ |
| Calculated fields | ✓ | ✗ | ✗ | ✗ |
| API access | ✓ | ✗ | ✗ | ✗ |
| Batch processing | ✓ | CLI | ✗ | ✗ |
| PDF reports | ✓ | ✗ | ✗ | ✗ |
| Zero storage | ✓ | ✓ | ✓ | ? |

### Key Differentiators

1. **"320+ fields across 5 file types"** - More comprehensive than any online tool
2. **"Zero storage, processed in memory"** - Privacy-first, forensics-friendly
3. **"File hashes for chain of custody"** - Unique for online tools
4. **"Calculated metadata"** - Aspect ratio, megapixels, file age
5. **"Beautiful, organized display"** - Not raw JSON dump

---

## 📝 Marketing Copy Drafts

### Tagline Options
- "The most comprehensive metadata extraction on the web"
- "320+ fields. Zero storage. Instant results."
- "Forensic-grade metadata extraction, free to start"
- "See what your files really contain"

### Landing Page Hero
> **Unlock the hidden data in your files**
> 
> MetaExtract reveals 320+ metadata fields from images, videos, audio, and documents. 
> Trusted by forensics professionals, journalists, and security researchers.
> 
> [Try Free - No Signup Required]

### For Forensics Audience
> **Chain of custody starts here**
> 
> MD5 and SHA256 hashes. GPS coordinates with precision. 
> Timestamps to the millisecond. Export court-ready PDF reports.
> 
> MetaExtract gives you the evidence you need.

---

## ❓ Open Questions for Pranay

1. **Domain:** metaextract.io? metaextract.app? extractmeta.com?

2. **Images Only for MVP?** Or include all file types from day 1? (Backend supports all, just gating question)

3. **Branding:** 
   - Minimal (clean, professional, forensics-focused)?
   - Friendly (accessible, colorful, broad appeal)?
   
4. **Video processing** - Enable from start? Videos are larger, more compute.

5. **Pricing confirmation:**
   - Pro: $7/mo or $5/mo?
   - Business: $19/mo or $15/mo?
   - Credits: $1 = 10 or $1 = 15?

6. **History storage** - Should we store extraction history for Pro users? (Requires actual DB storage of metadata, not files)

---

*Document created: December 29, 2024*
*Next step: Review with Pranay, then begin Phase 1 implementation*
