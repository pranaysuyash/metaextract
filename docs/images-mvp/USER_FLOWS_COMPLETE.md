# Images MVP - Complete User Flows

**Version**: 1.0
**Last Updated**: January 6, 2026
**Focus**: Images MVP for casual users (BETA)

---

## Overview

**Target Audience**: Casual users who want to check photos for privacy issues before sharing
**Core Value**: Instant, private metadata extraction from images
**Supported Formats**: JPG, JPEG, PNG, HEIC, HEIF, WebP
**Payment Model**: Credit-based system (1 credit = 1 standard image)
**Free Trial**: 2 free extractions per email address

---

## API Endpoints

### Extraction

| Method | Endpoint                              | Purpose                     | Auth                        |
| ------ | ------------------------------------- | --------------------------- | --------------------------- |
| POST   | `/api/images_mvp/extract`             | Extract metadata from image | Optional (trial or credits) |
| GET    | `/api/images_mvp/jobs/:jobId/status`  | Check async job status      | Optional                    |
| GET    | `/api/images_mvp/thumbnail/:resultId` | Get stored thumbnail        | Optional                    |

### Credits

| Method | Endpoint                          | Purpose                    | Auth               |
| ------ | --------------------------------- | -------------------------- | ------------------ |
| GET    | `/api/images_mvp/credits/packs`   | Get available credit packs | None               |
| GET    | `/api/images_mvp/credits/balance` | Get user's credit balance  | Optional (cookies) |
| POST   | `/api/images_mvp/credits/claim`   | Claim purchased credits    | Required           |

### WebSocket

| Method | Endpoint                              | Purpose                    | Auth |
| ------ | ------------------------------------- | -------------------------- | ---- |
| WS     | `/api/images_mvp/progress/:sessionId` | Real-time progress updates | None |

### Analytics (Admin)

| Method | Endpoint                    | Purpose              | Auth     |
| ------ | --------------------------- | -------------------- | -------- |
| GET    | `/api/images_mvp/analytics` | Get analytics report | Required |

---

## User Flow 1: Landing Page → Upload → Results

### 1.1 Landing Page (`/images_mvp`)

**Entry Points**:

- Direct navigation: `/images_mvp`
- External link/QR code

**Components**:

- Hero section with value proposition
- Upload zone (drag & drop)
- Feature highlights (privacy check, instant analysis)

**User Actions**:

1. View landing page
2. Upload image via:
   - Drag & drop file into upload zone
   - Click to browse and select file
3. Wait for upload progress (WebSocket connection)

**Technical Flow**:

```
User lands on /images_mvp
  ↓
Track event: "images_landing_viewed"
  ↓
Upload component renders
  ↓
User uploads file
  ↓
Validate file:
  - Extension: .jpg, .jpeg, .png, .heic, .heif, .webp
  - MIME type: image/jpeg, image/png, image/heic, image/heif, image/webp
  - File size bucket check
  ↓
Check credits/trial:
  - If no trial email shown: Show trial email input
  - If trial email provided: Check 2 free uses limit
  - If trial exhausted: Show pricing modal
  - If authenticated: Check account credits
  ↓
If user has access:
  - Generate WebSocket session ID
  - Show progress tracker
  - Upload file to server
  - Track progress via WebSocket
  - Navigate to results page
```

**Analytics Events**:

- `images_landing_viewed` (location: "images_mvp")

---

### 1.2 Upload & Analysis

**States**:

1. `IDLE` - Waiting for file selection
2. `UPLOADING` - File is being uploaded (0-100%)
3. `ANALYZING` - Server is processing (WebSocket updates)
4. `COMPLETE` - Redirect to results
5. `ERROR` - Upload or extraction failed

**Upload Validation**:

**Client-Side**:

```typescript
SUPPORTED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.heic', '.heif', '.webp'];
```

**Server-Side**:

```typescript
SUPPORTED_MIMES = [
  'image/jpeg', 'image/png', 'image/heic',
  'image/heif', 'image/webp'
]

// Magic-byte validation
const detectedType = await fileTypeFromBuffer(req.file.buffer);
if (!SUPPORTED_MIMES.has(detectedType.mime)) {
  return 400: Invalid file content
}
```

**Trial/Quota Logic**:

**Scenario 1: No Email Provided (Free Trial)**

```
User doesn't provide email
  ↓
Show trial email input (optional)
  ↓
If email provided:
  - Check database for existing uses
  - If uses < 2: Allow extraction
  - If uses >= 2: Show pricing modal
  ↓
Record trial usage (IP + email + user-agent)
```

**Scenario 2: Authenticated User**

```
User is logged in
  ↓
Check credit balance
  ↓
If credits >= 1:
  - Deduct 1 credit
  - Process extraction
  ↓
If credits < 1:
  - Show pricing modal
```

**WebSocket Progress**:

```typescript
// Connection: WS /api/images_mvp/progress/{sessionId}

// Progress stages:
{
  type: "progress",
  sessionId: string,
  progress: 0-100,      // Upload + processing combined
  message: string,        // "Uploading...", "Extracting...", etc.
  stage: "uploading" | "processing" | "complete",
  timestamp: number
}

// Error notification:
{
  type: "error",
  sessionId: string,
  error: string,
  timestamp: number
}
```

**Error Handling**:

| Error             | Status | Message                        | User Action              |
| ----------------- | ------ | ------------------------------ | ------------------------ |
| Invalid file type | 400    | "File type not supported"      | Upload JPG/PNG/HEIC/WebP |
| File too large    | 413    | "File exceeds size limit"      | Use smaller image        |
| No trial/credits  | 402    | "Purchase credits to continue" | Click pricing button     |
| Extraction failed | 500    | "Processing failed"            | Try different image      |

**Success Flow**:

```
Upload complete (100% progress)
  ↓
Server processes image:
  1. Validate magic bytes
  2. Extract metadata via Python engine
  3. Transform for frontend
  4. Send WebSocket completion
  ↓
Client receives complete event
  ↓
Save metadata to sessionStorage
  ↓
Navigate to /images_mvp/results
```

**Analytics Events**:

- `upload_selected` (filename, size_bucket, format)
- `upload_rejected` (reason, filename)
- `analysis_started` (session_id)
- `analysis_completed` (success, processing_ms, fields_extracted)
- `analysis_failed` (error_code, error_message)

---

### 1.3 Results Page (`/images_mvp/results`)

**Entry Points**:

- After successful upload from landing page
- Direct navigation (if metadata in sessionStorage)
- Refresh (metadata restored from sessionStorage)

**Components**:

- Summary cards (privacy, authenticity, photography)
- Tabbed detailed view (Privacy, Authenticity, Photography, Raw EXIF)
- Search/filter functionality
- Export options (JSON, summary text)
- Quality indicator

**States**:

1. `loading` - Loading from sessionStorage
2. `ready` - Metadata displayed
3. `empty` - No metadata found or expired session

**Tabs**:

**Tab 1: Privacy (Default)**

```
Purpose: Check for sensitive data before sharing

Display:
├─ GPS Location
│  ├─ If present: Map + coordinates + address
│  ├─ Click to view on Google Maps
│  └─ Warning: "This photo contains location data"
│
├─ Device Information
│  ├─ Camera make/model
│  ├─ Serial number (MakerNotes)
│  └─ Warning: "Links to your specific device"
│
└─ Personal Data
   ├─ Camera settings
   ├─ Timestamp
   └─ Warning: "May reveal when/where taken"
```

**Tab 2: Authenticity**

```
Purpose: Check if photo has been modified

Display:
├─ Authenticity Score (0-100)
├─ Confidence indicators
├─ Warnings:
│  ├─ "EXIF data incomplete"
│  ├─ "Timestamps don't match"
│  └─ "Signs of modification"
└─ Recommendations
```

**Tab 3: Photography**

```
Purpose: Technical photography data

Display:
├─ Camera Settings
│  ├─ ISO
│  ├─ Shutter speed
│  ├─ Aperture
│  └─ Focal length
├─ Image Quality
│  ├─ Dimensions
│  ├─ DPI
│  └─ Format (JPEG/PNG/etc)
└─ Perceptual Hashes
   ├─ Used for duplicate detection
   └─ Privacy warning
```

**Tab 4: Raw EXIF**

```
Purpose: All extracted metadata fields

Display:
├─ Search bar (filter fields)
├─ All EXIF fields (key-value pairs)
├─ Advanced density toggle:
│  ├─ Normal: Important fields only
│  └─ Advanced: All 134+ fields
└─ Copy individual field values
```

**Search & Filtering**:

```typescript
// Real-time search across all metadata
const search = (query: string) => {
  return metadata.filter(
    field =>
      field.key.toLowerCase().includes(query) ||
      field.value.toLowerCase().includes(query)
  );
};

// Purpose-based filtering
const purposes = {
  privacy: ['gps', 'device', 'camera_make', 'serial_number'],
  authenticity: ['exif_integrity', 'modification_signs'],
  photography: ['iso', 'shutter_speed', 'aperture', 'focal_length'],
};
```

**Quality Indicator**:

```
Visual feedback:
├─ Green (High): All metadata extracted successfully
├─ Yellow (Medium): Some metadata missing
└─ Red (Low): Significant data missing
```

**Export Options**:

**Option 1: Copy Summary**

```
Button: "Copy to Clipboard"
Action: Copy formatted text summary to clipboard
Analytics: export_summary_copied
```

**Option 2: Download JSON**

```
Button: "Download JSON"
Action: Download full metadata as JSON file
Analytics: export_json_downloaded
```

**Option 3: Download Text**

```
Button: "Download Full Report"
Action: Download complete text report
Analytics: export_full_txt_downloaded
```

**Purpose Selection**:

```
User is prompted: "Why are you checking this photo?"

Options:
├─ Privacy: "Checking before sharing online"
├─ Authenticity: "Verifying photo authenticity"
├─ Photography: "Reviewing camera settings"
└─ Explore: "Just curious"

Analytics: purpose_selected (value)
Storage: localStorage
Usage: Customize tab order, recommendations
```

**Analytics Events**:

- `results_viewed` (filename, total_fields, has_gps, has_device_info)
- `purpose_selected` (value: 'privacy' | 'authenticity' | 'photography' | 'explore')
- `tab_viewed` (tab_name, duration)
- `search_used` (query, results_count)
- `export_summary_downloaded`
- `export_json_downloaded`
- `export_full_txt_downloaded`

---

## User Flow 2: Purchase Credits

### 2.1 Pricing Modal Trigger

**Trigger Points**:

1. Trial exhausted (after 2 free uses)
2. Insufficient credits (< 1)
3. User clicks "Get Credits" button

**Pricing Modal Display**:

```
Show available credit packs:
├─ Starter (10 credits) - $4.90
├─ Standard (50 credits) - $19.90
├─ Professional (100 credits) - $34.90
└─ Custom (200 credits) - $59.90

Analytics:
├─ paywall_viewed (location, credit_balance)
└─ paywall_previewed (pack_shown)
```

**User Actions**:

1. View pricing options
2. Select pack
3. Click purchase
4. Redirect to payment provider
5. Complete payment
6. Return to success page

**Payment Flow**:

```
User clicks purchase
  ↓
Generate payment link (Dodo Payments)
  ↓
Redirect to payment page
  ↓
User completes payment
  ↓
Webhook: POST /api/payments/webhook
  ↓
Confirm payment: POST /api/payments/confirm
  ↓
Add credits to user account
  ↓
Redirect to: /images_mvp/credits-success?pack={pack}&payment_id={id}
```

**Analytics Events**:

- `paywall_viewed` (location, credits_balance)
- `paywall_previewed` (pack_id)
- `paywall_clicked` (pack_id, amount)
- `purchase_started` (pack_id)
- `purchase_completed` (pack_id, credits_amount, payment_id)

---

### 2.2 Credits Success Page (`/images_mvp/credits-success`)

**Entry**:

- After payment completion
- URL: `/images_mvp/credits-success?pack={name}&payment_id={id}&status=succeeded`

**Display**:

```
Success message:
├─ "Credits Added"
├─ "{pack} pack purchase is complete"
├─ "{credits} credits have been added"
│
Information:
├─ 1 credit = 1 standard image
├─ Credits do not expire
└─ Refund policy: 7 days for unused packs
│
Actions:
├─ If authenticated: "Credits saved to account"
├─ If not authenticated:
│  ├─ "Save credits to your account"
│  ├─ "Sign In" button
│  └─ "Create Account" button
└─ "Analyze More Photos" button
```

**Credit Claiming**:

```
If user is authenticated:
  ↓
Auto-claim credits to account
  ↓
POST /api/images_mvp/credits/claim
  ↓
Credits added to user balance
  ↓
Show current balance
```

**Analytics Events**:

- `purchase_completed` (pack, credits)
- `credits_claimed` (amount)

---

## User Flow 3: Authentication (Optional)

### 3.1 Sign In / Create Account

**Trigger Points**:

1. From credits success page (to save credits)
2. From navigation menu
3. Before purchase (to save purchase history)

**Auth Modal**:

```
Tabs:
├─ Sign In
│  ├─ Email
│  ├─ Password
│  └─ "Sign In" button
│
└─ Create Account
   ├─ Email
   ├─ Password
   ├─ Confirm Password
   └─ "Create Account" button
```

**Benefits of Account**:

- Credits sync across browsers/devices
- Purchase history
- Persistent credits (no expiration)
- Export analysis history

**Analytics Events**:

- `auth_viewed` (source, intent)
- `auth_completed` (method: 'login' | 'signup')
- `auth_failed` (error_code)

---

## User Flow 4: Error Scenarios

### 4.1 Invalid File Type

**Scenario**:

- User uploads unsupported file (e.g., .mp4, .pdf, .xyz)

**Display**:

```
Toast notification:
├─ Error icon
├─ "File type not supported"
├─ "Please upload a JPG, PNG, HEIC, or WebP image"
└─ Dismiss button

Analytics:
└─ upload_rejected (reason: 'file_type')
```

**User Action**:

- Select valid image file
- Re-attempt upload

---

### 4.2 File Too Large

**Scenario**:

- User uploads very large image (> 50MB)

**Display**:

```
Toast notification:
├─ Error icon
├─ "File too large"
├─ "Maximum file size is 50MB"
└─ Dismiss button

Analytics:
└─ upload_rejected (reason: 'size_limit')
```

**User Action**:

- Compress image
- Use smaller image
- Re-attempt upload

---

### 4.3 Trial Exhausted

**Scenario**:

- User provided email, already used 2 free extractions

**Display**:

```
Toast + Pricing Modal:
├─ "Your free trial is complete"
├─ "Purchase credits to continue"
├─ Pricing packs shown
└─ "Get Credits" button

Analytics:
├─ trial_exhausted (email, uses)
└─ paywall_viewed (reason: 'trial_limit')
```

**User Action**:

- Purchase credits
- Or close modal (no action)

---

### 4.4 Insufficient Credits

**Scenario**:

- Authenticated user with < 1 credit

**Display**:

```
Toast + Pricing Modal:
├─ "Insufficient credits"
├─ "You have X credits. 1 credit required."
├─ Pricing packs shown
└─ "Get Credits" button

Analytics:
├─ quota_exceeded (current_credits, required)
└─ paywall_viewed (reason: 'credits')
```

**User Action**:

- Purchase credits
- Or close modal (no action)

---

### 4.5 Extraction Failed

**Scenario**:

- Server fails to extract metadata

**Display**:

```
Toast notification:
├─ Error icon
├─ "Processing failed"
├─ "We couldn't extract metadata from this image"
└─ "Please try a different image"

Analytics:
└─ analysis_failed (error_code, error_message)
```

**WebSocket Error Message**:

```typescript
{
  type: "error",
  sessionId: string,
  error: "Extraction failed: [details]",
  timestamp: number
}
```

**User Action**:

- Try different image
- Check image file integrity
- Contact support

---

### 4.6 Network Error

**Scenario**:

- Upload interrupted or server unreachable

**Display**:

```
Toast notification:
├─ Warning icon
├─ "Connection lost"
├─ "Please check your internet connection"
└─ Retry button

Analytics:
└─ network_error (phase: 'upload' | 'processing')
```

**User Action**:

- Check internet connection
- Click retry button
- Re-attempt upload

---

### 4.7 WebSocket Disconnected

**Scenario**:

- Progress tracking lost mid-upload

**Display**:

```
Toast notification:
├─ Warning icon
├─ "Progress update disconnected"
├─ "Your upload is still processing in the background"
└─ Refresh button

Fallback:
└─ HTTP polling for job status (if available)
```

**User Action**:

- Wait for completion (continue processing)
- Refresh page to check status
- Re-upload if needed

---

## User Flow 5: Advanced Features

### 5.1 Multiple File Uploads (Future)

**Not Implemented Yet**

**Planned**:

- Batch upload (up to 10 files)
- Progress per file
- Summary report across all files
- Export combined results

---

### 5.2 Export Formats (Future)

**Current**: JSON, text summary

**Planned**:

- CSV export
- PDF report
- Safe export (stripped metadata)

---

### 5.3 Account Dashboard (Future)

**Not Implemented Yet**

**Planned**:

- Analysis history
- Download saved results
- Manage credit packs
- Billing history

---

## Data Flow Diagrams

### Upload Flow

```
┌─────────┐
│  User   │
└────┬────┘
     │ Selects file
     ↓
┌──────────────────────┐
│  Client Browser      │
│  Validate:          │
│  - Extension       │
│  - Size           │
└────┬───────────────┘
     │ Upload (FormData)
     ↓
┌──────────────────────┐
│  Server API         │
│  /api/images_mvp/  │
│  extract           │
│                    │
│  1. Magic bytes    │
│  2. Trial quota    │
│  3. Credit check   │
│  4. Extract (PY)   │
│  5. Transform      │
└────┬───────────────┘
     │ Metadata + WebSocket
     ↓
┌──────────────────────┐
│  WebSocket          │
│  Real-time:         │
│  - 0% upload       │
│  - 25% uploading   │
│  - 50% processing  │
│  - 100% complete   │
└────┬───────────────┘
     │ Navigate
     ↓
┌──────────────────────┐
│  Results Page       │
│  Display:           │
│  - Privacy tab      │
│  - Authenticity     │
│  - Photography     │
│  - Raw EXIF        │
└──────────────────────┘
```

### Purchase Flow

```
┌─────────┐
│  User   │
└────┬────┘
     │ Click pricing
     ↓
┌──────────────────────┐
│  Pricing Modal       │
│  Show packs:        │
│  - Starter (10)    │
│  - Standard (50)    │
│  - Pro (100)       │
│  - Custom (200)     │
└────┬───────────────┘
     │ Select & purchase
     ↓
┌──────────────────────┐
│  Payment Provider   │
│  (Dodo Payments)   │
│  1. Payment flow   │
│  2. Webhook        │
└────┬───────────────┘
     │ Confirm
     ↓
┌──────────────────────┐
│  Server API         │
│  /api/payments/     │
│  confirm            │
│  - Verify payment   │
│  - Add credits     │
└────┬───────────────┘
     │ Redirect
     ↓
┌──────────────────────┐
│  Success Page      │
│  - Show credits    │
│  - Claim to acct   │
└──────────────────────┘
```

---

## Edge Cases

### Edge Case 1: Session Expired

**Scenario**: User refreshes results page after 1 hour

**Behavior**:

- Check sessionStorage for `currentMetadata`
- If missing/null: Redirect to landing page
- Show toast: "Session expired. Please upload again."

---

### Edge Case 2: Duplicate Upload

**Scenario**: User uploads same file twice

**Behavior**:

- Process normally (cache not implemented yet)
- Generate new session ID
- New results page
- Future: Detect and show "previously analyzed"

---

### Edge Case 3: Browser Navigation During Upload

**Scenario**: User closes tab mid-upload

**Behavior**:

- WebSocket connection closes
- Server continues processing (orphan job)
- Future: User can resume via job ID

---

### Edge Case 4: Payment Abandoned

**Scenario**: User starts purchase but doesn't complete

**Behavior**:

- No credits added
- No webhook received
- User can re-try purchase
- No error shown (silent)

---

### Edge Case 5: Credit Race Condition

**Scenario**: User has 1 credit, clicks purchase + upload simultaneously

**Behavior**:

- Credit check happens at upload time
- If purchase completes before upload: Uses new credit
- If upload completes before purchase: Shows pricing modal
- Future: Implement optimistic UI updates

---

## Analytics Tracking

### Events Tracked

| Event                        | Parameters                               | Frequency          |
| ---------------------------- | ---------------------------------------- | ------------------ |
| `images_landing_viewed`      | location                                 | Per session        |
| `upload_selected`            | filename, size_bucket, format            | Per upload         |
| `upload_rejected`            | reason, filename                         | On rejection       |
| `analysis_started`           | session_id                               | Per upload         |
| `analysis_completed`         | success, processing_ms, fields_extracted | Per upload         |
| `analysis_failed`            | error_code, error_message                | On failure         |
| `results_viewed`             | filename, total_fields, has_gps          | Per view           |
| `purpose_selected`           | value                                    | Per session        |
| `tab_viewed`                 | tab_name, duration                       | Per tab switch     |
| `search_used`                | query, results_count                     | Per search         |
| `export_summary_downloaded`  | -                                        | Per export         |
| `export_json_downloaded`     | -                                        | Per export         |
| `export_full_txt_downloaded` | -                                        | Per export         |
| `paywall_viewed`             | location, credits_balance                | Per view           |
| `paywall_previewed`          | pack_shown                               | Per view           |
| `paywall_clicked`            | pack_id, amount                          | Per click          |
| `purchase_started`           | pack_id                                  | Per purchase start |
| `purchase_completed`         | pack_id, credits, payment_id             | On completion      |
| `credits_claimed`            | amount                                   | On claim           |
| `auth_viewed`                | source, intent                           | Per view           |
| `auth_completed`             | method                                   | On completion      |
| `auth_failed`                | error_code                               | On failure         |

### Storage Keys

```typescript
// Session storage (ephemeral)
sessionStorage.setItem('currentMetadata', JSON.stringify(metadata));
sessionStorage.setItem('sessionId', sessionId);

// Local storage (persistent)
localStorage.setItem('images_mvp_purpose', 'privacy');
localStorage.setItem('images_mvp_density', 'normal');
localStorage.setItem('metaextract_images_mvp_purchase_completed', JSON.stringify({...}));

// Cookies (credits)
// Set via HttpOnly cookie by server
```

---

## Technical Implementation Notes

### File Validation

**Client-side**:

```typescript
// simple-upload.tsx
const SUPPORTED_EXTENSIONS = [
  '.jpg',
  '.jpeg',
  '.png',
  '.heic',
  '.heif',
  '.webp',
];

const getExtension = (name: string): string | null => {
  const index = name.lastIndexOf('.');
  if (index <= 0) return null;
  return name.slice(index).toLowerCase();
};
```

**Server-side**:

```typescript
// images-mvp.ts
const SUPPORTED_IMAGE_MIMES = new Set([
  'image/jpeg', 'image/png', 'image/heic',
  'image/heif', 'image/webp'
]);

// Magic-byte validation
const detectedType = await fileTypeFromBuffer(req.file.buffer);
if (detectedType && !SUPPORTED_IMAGE_MIMES.has(detectedType.mime)) {
  return 400: Invalid file content
}
```

### WebSocket Progress

**Connection**:

```typescript
// Client
const ws = new WebSocket(
  `ws://localhost:3000/api/images_mvp/progress/${sessionId}`
);

ws.onmessage = event => {
  const data = JSON.parse(event.data);

  if (data.type === 'progress') {
    updateProgressBar(data.progress);
    updateStatusMessage(data.message);
  }

  if (data.type === 'error') {
    showError(data.error);
  }
};
```

**Broadcast**:

```typescript
// Server
function broadcastProgress(
  sessionId: string,
  progress: number,
  message: string,
  stage?: string
) {
  const connections = activeConnections.get(sessionId);
  if (!connections || connections.length === 0) return;

  const progressData = {
    type: 'progress',
    sessionId,
    progress: Math.min(100, Math.max(0, progress)),
    message,
    stage: stage || 'processing',
    timestamp: Date.now(),
  };

  connections.forEach(conn => {
    if (conn.ws.readyState === 1) {
      // WebSocket.OPEN
      conn.ws.send(JSON.stringify(progressData));
    }
  });
}
```

### Trial/Quota Enforcement

**Trial Logic**:

```typescript
// Check trial usage
let trialUses = 0;
if (isDatabaseConnected()) {
  const result = await dbClient
    .select({ uses: trialUsages.uses })
    .from(trialUsages)
    .where(eq(trialUsages.email, trialEmail))
    .limit(1);
  trialUses = result[0]?.uses || 0;
} else {
  const usage = await storage.getTrialUsageByEmail(trialEmail);
  trialUses = usage?.uses || 0;
}

const hasTrialAvailable = !!trialEmail && trialUses < 2;
```

**Credit Logic**:

```typescript
// Check account credits
const data = await res.json();
const credits = typeof data?.credits === 'number' ? data.credits : 0;

if (credits >= 1) {
  // Allow extraction
  await incrementUsage(userId);
} else {
  // Show pricing modal
  setShowPricingModal(true);
}
```

---

## Accessibility Considerations

### Keyboard Navigation

- All buttons accessible via Tab
- Skip to content link
- Focus management in modals

### Screen Readers

- ARIA labels on upload zone
- Status announcements for progress
- Tab names descriptive
- Error messages in toasts

### Reduced Motion

- Respects `prefers-reduced-motion`
- Animated transitions optional

### Color Contrast

- Dark mode design (high contrast)
- Error/warning colors: red/yellow/green
- Text-to-background ratio > 4.5:1

---

## Performance Considerations

### Client-Side

- File validation: < 50ms
- WebSocket connection: < 200ms
- Progress updates: ~50ms interval
- Results page render: < 300ms

### Server-Side

- File upload: Depends on file size/network
- Extraction: 1-5 seconds (typical image)
- Response size: 50-200KB (JSON metadata)

### WebSocket

- Latency: < 100ms (local), < 500ms (remote)
- Connection timeout: 5 seconds
- Cleanup delay: 5 seconds (after completion)

---

## Security Considerations

### Client-Side

- No sensitive data in localStorage
- Credit balance server-verified
- Trial usage server-enforced

### Server-Side

- Magic-byte validation (prevents extension spoofing)
- Rate limiting on uploads
- IP logging for trial abuse prevention
- HttpOnly cookies for credits

### Payment

- Webhook signature verification
- Payment ID confirmation required
- Credits only added after verified payment

---

## Future Enhancements

### Phase 2 (Planned)

1. **Batch Upload** - Up to 10 files at once
2. **Safe Export** - Strip metadata from images
3. **Account Dashboard** - Analysis history
4. **Comparison** - Compare two images
5. **Duplicate Detection** - Find similar images

### Phase 3 (Future)

1. **Mobile App** - Native iOS/Android apps
2. **Browser Extension** - Right-click analyze
3. **Desktop App** - Electron app
4. **API Access** - Public API for developers

---

## References

### Frontend Components

- `/client/src/pages/images-mvp/index.tsx` - Landing page
- `/client/src/pages/images-mvp/results.tsx` - Results page
- `/client/src/pages/images-mvp/credits-success.tsx` - Credits success
- `/client/src/pages/images-mvp/analytics.tsx` - Analytics (admin)
- `/client/src/components/images-mvp/simple-upload.tsx` - Upload component
- `/client/src/components/images-mvp/pricing-modal.tsx` - Pricing modal
- `/client/src/components/images-mvp/progress-tracker.tsx` - Progress indicator
- `/client/src/components/images-mvp/quality-indicator.tsx` - Quality score

### Backend Routes

- `/server/routes/images-mvp.ts` - All API endpoints
- `/server/utils/free-quota-enforcement.ts` - Trial/credit logic
- `/server/payments.ts` - Credit pack definitions
- `/server/storage/index.ts` - Metadata storage

### Documentation

- `IMAGES_MVP_QUICK_REFERENCE.md` - Quick reference guide
- `IMAGES_MVP_LAUNCH_CHECKLIST.md` - Launch checklist
- `IMAGES_MVP_USER_FLOW_SCENARIOS.md` - User flow examples

---

## Summary

**Current State**: BETA - Images only, casual users

**Core Flows**:

1. ✅ Upload & Analysis (complete)
2. ✅ Results Display (complete)
3. ✅ Credit Purchase (complete)
4. ✅ Authentication (complete)
5. ✅ Analytics (admin only)

**Supported**: 6 image formats, trial, credits, WebSocket progress
**Unsupported**: Batch upload, safe export, account dashboard
**Known Issues**: Database connection, file type validation

**Next Steps**:

- Fix database issues
- Add file type validation middleware
- Implement batch upload (Phase 2)
- Add safe export (Phase 2)

---

**Document Version**: 1.0
**Last Updated**: January 6, 2026
**Author**: AI Assistant (OpenCode)
