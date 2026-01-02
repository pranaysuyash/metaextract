# Critical Functional Issues - Part 3
## Forensic Routes and Payment Processing

Analysis of critical issues in forensic batch processing, metadata comparison, and payment webhook handling.

---

## 1. server/routes/forensic.ts

**Description**: Forensic analysis endpoints for batch comparison, timeline reconstruction, and forensic reports (762 lines).

**Critical Functional Issues**:

### 1. **Hardcoded Enterprise Default Tier (Same Pattern as Extraction)**
   - **Location**: Lines 61, 169, 675
   - **Issue**: 
     ```typescript
     const requestedTier = (req.query.tier as string) || 'enterprise';
     ```
   - **Impact**: Unauthenticated requests default to enterprise, bypassing tier restrictions.
   - **Severity**: **CRITICAL** - Business model broken
   - **Recommendation**: Remove default; require authentication to determine tier.

### 2. **Development Mode Disables All Tier Restrictions**
   - **Location**: Lines 67, 70, 84, 98, 110, 123, 131, 144-145, 149, 174, 681
   - **Issue**: 
     ```typescript
     const advanced_analysis_available: process.env.NODE_ENV === 'development' || normalizedTier !== 'free',
     steganography_detection: {
       available: process.env.NODE_ENV === 'development' || normalizedTier === 'professional' || ...
     ```
   - **Impact**: In dev mode, all forensic features are enabled for all tiers. If NODE_ENV is misconfigured in production, billing is bypassed.
   - **Severity**: **HIGH** - Accidental production bypass risk
   - **Recommendation**: Use explicit feature flags; never rely on NODE_ENV for access control.

### 3. **Batch Processing Has No Concurrent Limit (DoS Vulnerability)**
   - **Location**: Line 158
   - **Issue**: 
     ```typescript
     app.post('/api/compare/batch', upload.array('files', 50), async (req, res) => {
       // Uploads max 50 files but no limit on concurrent processing
       for (const fileInfo of fileInfos) {
         const rawMetadata = await extractMetadataWithPython(...); // Sequential, no parallelism
       }
     ```
   - **Impact**: Processing is sequential but no timeout per file. Attacker can upload 50 large files causing 50 * 180s = 15,000 seconds of server time.
   - **Severity**: **HIGH** - Resource exhaustion / DoS
   - **Recommendation**: 
     - Add timeout per file (e.g., 10s)
     - Limit concurrent batches per user
     - Return error if total processing time would exceed threshold

### 4. **Metadata Comparison Has No Validation on Extracted Data**
   - **Location**: Lines 235-249
   - **Issue**: 
     ```typescript
     const allKeys = new Set([
       ...Object.keys(meta1.exif || {}),
       ...Object.keys(meta2.exif || {}),
     ]);
     // Assumes exif exists and is object, no type checking
     ```
   - **Impact**: If `meta1.exif` is not an object (e.g., string, null, or circular reference), this crashes or produces wrong results.
   - **Severity**: **MEDIUM** - Robustness
   - **Recommendation**: Add prop validation and type guards before accessing nested properties.

### 5. **Forensic Report Generation Has Hardcoded Thresholds (Not Configurable)**
   - **Location**: Lines 549-573
   - **Issue**: 
     ```typescript
     if (rawMetadata.steganography_analysis?.suspicious_score && 
         rawMetadata.steganography_analysis.suspicious_score > 0.3) { // Hardcoded 0.3
       forensicFindings.push('Potential steganography detected');
       authenticityScore -= 30; // Hardcoded 30
     }
     ```
   - **Impact**: Thresholds are frozen in code; cannot adjust sensitivity without code changes.
   - **Severity**: **MEDIUM** - Inflexibility
   - **Recommendation**: Move thresholds to config or database, make them adjustable per tier.

### 6. **Forensic Score Calculation Can Go Negative**
   - **Location**: Line 580
   - **Issue**: 
     ```typescript
     authenticityScore -= 30; // Could go below 0
     ...
     authenticity_score: Math.max(0, authenticityScore) // Bounded to 0
     ```
   - **Impact**: Score starts at 100, can be reduced multiple times. If all indicators hit, negative score is clamped to 0, losing nuance.
   - **Severity**: **LOW** - Logic issue
   - **Recommendation**: Cap score reduction per indicator, use normalized probabilities.

### 7. **Temp Files May Leak on Error Path**
   - **Location**: Line 660 (finally block)
   - **Issue**: 
     ```typescript
     finally {
       await cleanupTempFiles(tempPaths);
     }
     ```
   - **Impact**: If `cleanupTempFiles` fails, error is swallowed. Temp files may accumulate.
   - **Severity**: **MEDIUM** - Resource leak
   - **Recommendation**: Log cleanup errors, add periodic cleanup task.

### 8. **Advanced Extraction Endpoint Has No Session/User Tracking**
   - **Location**: Line 666
   - **Issue**: 
     ```typescript
     app.post('/api/extract/advanced', upload.single('file'), async (req, res) => {
       // No logging of who performed analysis, no credit deduction
     ```
   - **Impact**: Advanced forensic analysis is free and untracked. No accountability.
   - **Severity**: **HIGH** - Billing/compliance
   - **Recommendation**: Add user tracking, credit deduction, audit logging.

### 9. **Forensic Report ID Uses Crypto.randomUUID (Timing Leak)**
   - **Location**: Line 620
   - **Issue**: 
     ```typescript
     report_id: crypto.randomUUID(),
     ```
   - **Impact**: UUIDs are cryptographically random but not time-constant. Sequential requests may leak timing info.
   - **Severity**: **LOW** - Theoretical attack
   - **Recommendation**: Use `crypto.randomBytes()` instead; timing is less critical for UUIDs.

### 10. **No Rate Limiting on Forensic Endpoints**
   - **Location**: Entire forensic.ts
   - **Issue**: `/api/compare/batch`, `/api/forensic/report`, `/api/extract/advanced` have no rate limiting.
   - **Impact**: User can spam 50-file batches repeatedly, exhausting server resources.
   - **Severity**: **HIGH** - DoS vulnerability
   - **Recommendation**: Add rate limiting middleware per endpoint (e.g., 1 batch per minute).

---

## 2. server/payments.ts

**Description**: Stripe/DodoPayments integration for subscriptions and credit purchases (715 lines).

**Critical Functional Issues**:

### 1. **Webhook Signature Validation Missing (Critical Security)**
   - **Location**: Lines 452-465
   - **Issue**: 
     ```typescript
     app.post('/api/webhooks/dodo', async (req: Request, res: Response) => {
       try {
         const event = req.body;
         
         switch (event.type) {
           case 'subscription.active': {
             // Processes webhook WITHOUT validating signature
           }
     ```
   - **Impact**: Anyone can POST to `/api/webhooks/dodo` with fake events to grant subscriptions, upgrade tiers, add credits.
   - **Severity**: **CRITICAL** - Fraud vulnerability
   - **Recommendation**: 
     ```typescript
     const signature = req.headers['x-dodo-signature'] as string;
     if (!verifyDodoSignature(signature, req.body, DODO_WEBHOOK_SECRET)) {
       return res.status(401).json({ error: 'Invalid signature' });
     }
     ```

### 2. **Failed Subscription Downgrades User to Enterprise (WRONG DIRECTION)**
   - **Location**: Lines 635-636
   - **Issue**: 
     ```typescript
     await db.update(users).set({
       subscriptionStatus: 'failed',
       tier: 'enterprise', // Should downgrade to 'free', not 'enterprise'!
     })
     ```
   - **Impact**: When subscription payment fails, user is upgraded to enterprise access instead of downgraded. Complete opposite of intended behavior.
   - **Severity**: **CRITICAL** - Revenue loss
   - **Recommendation**: Change to `tier: 'free'`.

### 3. **Cancelled Subscription Also Upgrades to Enterprise**
   - **Location**: Lines 687-688
   - **Issue**: 
     ```typescript
     await db.update(users).set({
       subscriptionStatus: 'cancelled',
       tier: 'enterprise', // Should be 'free'
     })
     ```
   - **Impact**: When user cancels subscription, they keep enterprise access. No revenue recapture.
   - **Severity**: **CRITICAL** - Revenue loss
   - **Recommendation**: Change to `tier: 'free'`.

### 4. **Subscription Active Event Defaults Tier to Enterprise**
   - **Location**: Line 544
   - **Issue**: 
     ```typescript
     const tier = normalizeTier(metadata?.tier || 'enterprise');
     ```
   - **Impact**: If webhook doesn't include tier in metadata, user defaults to enterprise.
   - **Severity**: **HIGH** - Upgrade bypass
   - **Recommendation**: Only update tier if explicitly set in metadata; error otherwise.

### 5. **No Idempotency Check (Replay Attack Risk)**
   - **Location**: Entire webhook handler
   - **Issue**: Webhook events (e.g., `subscription.active`) are processed without checking if already processed.
   - **Impact**: Attacker (or payment provider glitch) can replay webhook, charging credits/subscriptions multiple times.
   - **Severity**: **HIGH** - Fraud/duplicate charges
   - **Recommendation**: Track webhook IDs in database, reject duplicates:
     ```typescript
     const existingWebhook = await db.select().from(webhookLog)
       .where(eq(webhookLog.eventId, event.id)).limit(1);
     if (existingWebhook.length > 0) return res.json({ received: true });
     ```

### 6. **No Error Handling in Webhook Handlers (Silent Failures)**
   - **Location**: Lines 537-715
   - **Issue**: 
     ```typescript
     await db.update(users).set({...});
     // No try-catch, no error logging if update fails
     ```
   - **Impact**: If database update fails, subscription status is not updated in-database but webhook returns 200. User's billing state becomes inconsistent.
   - **Severity**: **HIGH** - Billing consistency
   - **Recommendation**: Add try-catch around all DB operations, log failures, consider retry queue.

### 7. **Anonymous Users Get Free Credits on Payment Success**
   - **Location**: Lines 700-713
   - **Issue**: 
     ```typescript
     if (metadata?.type === 'credit_purchase') {
       const credits = parseInt(metadata.credits || '0');
       const balanceId = metadata.balance_id;
       if (credits > 0 && balanceId) {
         await storage.addCredits(balanceId, credits, ...);
       }
     }
     ```
   - **Impact**: If `balanceId` is undefined or forged, credits still added. No userId validation.
   - **Severity**: **MEDIUM** - Fraud risk
   - **Recommendation**: Validate balanceId against user in database before adding credits.

### 8. **Checkout Session Metadata Not Validated (Injection Risk)**
   - **Location**: Lines 174-178, 237-242
   - **Issue**: 
     ```typescript
     metadata: {
       tier: normalizedTier,
       user_id: userId || 'anonymous', // No validation on userId format
       type: 'subscription',
     },
     ```
   - **Impact**: userId can be any string; if webhook handler trusts it without validation, privilege escalation possible.
   - **Severity**: **MEDIUM** - Injection risk
   - **Recommendation**: Validate userId format; only accept UUIDs in expected format.

### 9. **No Logging of Payment Events (Audit Trail Missing)**
   - **Location**: Entire payments.ts
   - **Issue**: Payment success/failure logged only to console (`console.log`).
   - **Impact**: No durable audit trail for compliance, debugging, or fraud investigation.
   - **Severity**: **MEDIUM** - Compliance
   - **Recommendation**: Log to database with timestamps, user IDs, amounts.

### 10. **Credit Pack Prices Hardcoded (Not Dynamic)**
   - **Location**: Lines 60-85
   - **Issue**: 
     ```typescript
     single: { credits: 10, price: 0, priceDisplay: '$0.00', ... },
     batch: { credits: 50, price: 600, priceDisplay: '$6.00', ... },
     ```
   - **Impact**: Prices must be changed in code; cannot adjust per region, season, or A/B test.
   - **Severity**: **LOW** - Inflexibility
   - **Recommendation**: Move to database or config.

### 11. **Subscription Failed Handler Missing Logic**
   - **Location**: Lines 611-640
   - **Issue**: 
     ```typescript
     async function handleSubscriptionFailed(subscription: any) {
       const { subscription_id } = subscription;
       await db.update(subscriptions).set({ status: 'failed', ... });
       // No email notification, no retry logic, just logs
     }
     ```
   - **Impact**: User's payment failed but they're not notified. No attempt to retry with saved payment method.
   - **Severity**: **MEDIUM** - UX/retention
   - **Recommendation**: Send email notification, trigger retry logic, offer alternative payment methods.

---

## Summary by Severity

### CRITICAL (Fraud / Revenue Loss / Security)
- Forensic: Default tier enterprise for unauthenticated requests
- Payments: **Webhook signature NOT validated** (unauthenticated webhook processing)
- Payments: **Failed subscription upgrades to enterprise** (should be free)
- Payments: **Cancelled subscription upgrades to enterprise** (should be free)

### HIGH (DoS / Billing / Abuse)
- Forensic: Development mode disables all tier restrictions
- Forensic: Batch processing no concurrent/timeout limits (DoS)
- Forensic: Advanced extraction not tracked or charged
- Forensic: No rate limiting on forensic endpoints
- Payments: No idempotency check on webhooks (replay attacks)
- Payments: Silent failure in webhook handlers (billing inconsistency)
- Payments: Subscription active defaults tier to enterprise if missing

### MEDIUM (Robustness / Compliance / Risk)
- Forensic: Metadata comparison doesn't validate extracted data
- Forensic: Hardcoded forensic thresholds (not configurable)
- Forensic: Temp file cleanup fails silently
- Payments: No validation on credits recipient (balanceId)
- Payments: userId injection risk in checkout metadata
- Payments: No audit logging of payments
- Payments: No notification on payment failure

### LOW (Maintainability)
- Forensic: Forensic score calculation logic (clamping)
- Forensic: Timing leak with crypto.randomUUID
- Payments: Credit pack prices hardcoded

---

## Recommended Fix Priority (Payments First)

1. **IMMEDIATE** (blocks launch):
   - ✅ Add webhook signature validation
   - ✅ Fix failed/cancelled subscription tier (enterprise → free)
   - ✅ Add idempotency check for webhook events
   - ✅ Add try-catch + logging to webhook handlers

2. **BEFORE PRODUCTION**:
   - Remove hardcoded enterprise defaults (forensic + payments)
   - Remove NODE_ENV-based tier bypass
   - Add rate limiting to forensic endpoints
   - Add credit tracking to advanced extraction
   - Validate userId/balanceId formats
   - Add audit logging

3. **SOON AFTER**:
   - Add batch processing limits (timeout per file, concurrent cap)
   - Move thresholds/prices to config/database
   - Add payment retry logic
   - Send email notifications on payment failure
