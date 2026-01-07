# Abuse/Misuse Consultant Report

**Date:** January 7, 2026
**Focus:** Images MVP Frontend + Full Backend
**Role:** Abuse/Misuse Consultant (thinking like a hostile but lazy attacker)

---

## Executive Summary

This report analyzes the MetaExtract images_mvp system for potential abuse vectors from the perspective of a "hostile but lazy attacker." The goal is to identify vulnerabilities that would allow attackers to bypass rate limits, drain compute resources, and extract costs from the free tier.

**Key Finding:** The system is reasonably hardened, but has a **critical weakness** - cookie-based device tracking that attackers can easily bypass by clearing cookies or rotating IPs.

---

## Analysis Philosophy

As a lazy attacker, I focus on:

- **Minimal effort** → Easy bypasses
- **Maximum ROI** → High extraction volume for low work
- **Common tools** → Proxies, automation, browser tricks

I don't want to:

- Reverse engineer complex systems
- Solve CAPTCHAs repeatedly
- Write custom exploits

---

## Abuse Vectors Identified

### 1. Rate-Limit Evasion (HIGH RISK)

**Attacker's thought process:** "How do I bypass their rate limits?"

#### Vulnerabilities

| Issue                                | Location                    | Exploitability | Attack Cost |
| ------------------------------------ | --------------------------- | -------------- | ----------- |
| Fail-open on Redis error             | `rateLimitRedis.ts:188-193` | Easy           | 1/10        |
| Separate IP and client tracking      | `middleware/rate-limit.ts`  | Easy           | 2/10        |
| Cookie-based token is only device ID | `free-quota-enforcement.ts` | Easy           | 1/10        |
| No browser fingerprint validation    | Client-side only            | Easy           | 2/10        |

#### Lazy Attacker's Preferred Method

```bash
# Rotate IPs, clear cookies, repeat
for i in {1..100}; do
  curl -H "User-Agent: Mozilla/5.0 (iPhone...)" \
       --cookie-jar cookies_$i.txt \
       http://target/api/images_mvp/extract \
       -F "file=@photo.jpg"
done
```

**Attack Cost:** 5 minutes to write script, free proxies online, run from cheap VPS ($5/month)

---

### 2. Session Reset Abuse (HIGH RISK)

**Attacker's thought process:** "Can I just reset my session to get free checks again?"

#### Vulnerabilities

| Issue                              | Location                            | Exploitability | Attack Cost |
| ---------------------------------- | ----------------------------------- | -------------- | ----------- |
| Session ID is client-generated     | `simple-upload.tsx:220-222`         | Trivial        | 1/10        |
| Cookie maxAge is only 7 days       | `free-quota-enforcement.ts:39`      | Moderate       | 2/10        |
| Token can be regenerated on demand | `free-quota-enforcement.ts:188-207` | Trivial        | 1/10        |

#### Lazy Attacker's Preferred Method

```bash
# No cookies = new token = 2 fresh free extractions
curl -X POST http://target/api/images_mvp/extract -F "file=@test.jpg"
```

---

### 3. IP Hopping (MEDIUM RISK)

**Attacker's thought process:** "Just use different IPs."

#### Current IP-Based Protections

- `IP_DAILY_LIMIT: 10` per IP
- `IP_MINUTE_LIMIT: 2` per IP
- `getClientIP()` trusts `X-Forwarded-For` from proxies

#### Bypass Vectors

1. **Proxy rotation** - Cheap residential proxies cost ~$5/GB
2. **X-Forwarded-For spoofing** - Easy to fake if not validating proxy
3. **No subnet-based limiting** - `/24` subnet could generate 256 unique IPs

---

### 4. Headless Browser Abuse (MEDIUM RISK)

**Attacker's thought process:** "Can I automate this with Puppeteer?"

#### Current Protections

- No automated request detection
- No JavaScript execution verification
- WebSocket connection optional (checked but not enforced)

#### Exploit

```javascript
const puppeteer = require('puppeteer');
const browser = await puppeteer.launch();
const page = await browser.newPage();
await page.goto('http://target/images_mvp');
// Upload, extract, repeat with fresh cookies each time
```

---

### 5. File Spam Uploads (MEDIUM-HIGH RISK)

**Attacker's thought process:** "Can I flood their storage/queue?"

#### Current Protections

- Multer `fileSize: 100MB` limit per file
- File type validation via MIME + extension
- Magic byte validation exists (`images-mvp.ts:117-129`)

#### Gaps

| Issue                                      | Impact                                     | Exploitability |
| ------------------------------------------ | ------------------------------------------ | -------------- |
| No file count per IP/user                  | Upload 100 tiny files rapidly              | Easy           |
| No upload frequency cooldown               | `upload.array('files', 100)` allows batch  | Easy           |
| No hash-based deduplication                | Same file uploaded twice = processed twice | Easy           |
| `/tmp/metaextract` temp directory writable | Could fill disk                            | Medium         |

---

### 6. Cost-Extraction Attacks (CRITICAL FOR FREE TIER)

**Attacker's thought process:** "How do I drain their compute/resources for free?"

#### Cost Vectors

| Resource                 | Current Protection         | Bypass                     |
| ------------------------ | -------------------------- | -------------------------- |
| Python extraction engine | Rate limits only           | IP hop + cookie clear      |
| Disk I/O                 | Temp file cleanup          | Small files, rapid uploads |
| Database storage         | No size limits on metadata | Tiny files, many requests  |
| WebSocket connections    | No per-session limits      | Connection flooding        |

#### Lazy Attacker's Optimal Exploit

```bash
# Script to drain resources - runs from cheap VPS
for ip in $(seq 1 254); do
  for port in 80 443; do
    curl -H "X-Forwarded-For: 192.168.1.$ip" \
         --cookie-jar /dev/null \
         http://target/api/images_mvp/extract \
         -F "file=@1kb.jpg" &
  done
done
```

---

## Summary: Attacker Effort vs Reward

| Attack Vector                     | Effort | Reward                    | Likelihood |
| --------------------------------- | ------ | ------------------------- | ---------- |
| Cookie clearing + IP rotation     | 1/10   | 2 free checks             | HIGH       |
| X-Forwarded-For spoofing          | 2/10   | Unlimited (if proxy list) | MEDIUM     |
| Headless browser automation       | 3/10   | Hundreds free checks      | MEDIUM     |
| Resource exhaustion (small files) | 2/10   | CPU/DISK cost             | MEDIUM     |
| Batch upload exploitation         | 4/10   | 100 files/minute          | LOW        |

---

## What the System Does Well

1. ✅ **File type validation** - MIME + extension + magic byte checks
2. ✅ **Magic byte verification** - Prevents file spoofing
3. ✅ **File size limits** - 100MB cap per file
4. ✅ **Multi-tier rate limiting** - IP + client limits
5. ✅ **WebSocket progress tracking** - Good UX, prevents duplicate processing
6. ✅ **Credit-based system** - Tracks usage accurately

---

## Critical Weakness

**Cookie-only device tracking is the primary vulnerability.**

A lazy attacker just clears cookies and rotates IPs to bypass all protections. The system needs:

1. **Server-issued device tokens** (httpOnly, signed)
2. **Browser fingerprinting** (canvas, WebGL, audio API)
3. **Multi-dimensional identity tracking** (IP + device + fingerprint + behavior)
4. **Progressive friction** (captcha → email → OAuth)
5. **Queue-based throttling** (not hard blocks)

---

## Recommended Fixes (Priority Order)

### CRITICAL (Fix Immediately)

1. **Move quota tracking to server-minted device token**
   - Client should not control the identity being counted
   - Server signs token with secret, stores in httpOnly cookie

2. **Add browser fingerprinting as risk signal**
   - Canvas fingerprint
   - WebGL renderer
   - Audio context
   - Timezone + language
   - Use as confidence score, not hard gate

### HIGH (Fix Within 1 Week)

3. **Implement file hash deduplication cache**
   - Don't process same file twice in 24h
   - Reduces compute waste

4. **Add upload frequency cooldown**
   - Max X uploads per minute regardless of size
   - Prevents rapid small-file flooding

5. **Add JS challenge token**
   - Required in request body
   - Generated by client-side JS
   - Validated server-side

### MEDIUM (Fix Within 1 Month)

6. **Implement identity ladder**
   - Anonymous (2 credits) → Challenge (+3) → Email (+10) → OAuth (+20)
   - Make signup easier than abuse

7. **Add queue with priority**
   - Paid = fast queue
   - Free = slow queue under load
   - Graceful degradation, not hard blocks

8. **Add IP reputation scoring**
   - Track ASN, subnet behavior
   - Block known datacenter IPs

### LOW (Nice to Have)

9. **Add WebSocket connection rate limiting**
10. **Implement behavioral velocity detection**
11. **Add CAPTCHA for high-velocity users**

---

## Economic Analysis

### Attacker Economics (Current State)

| Attack                 | Cost     | Gain                      | ROI  |
| ---------------------- | -------- | ------------------------- | ---- |
| Cookie clearing script | Free     | Unlimited 2-check batches | ∞    |
| Proxy rotation ($5/mo) | $0.05/GB | Unlimited extractions     | High |
| Headless automation    | Free VPS | Hundreds/day              | High |

### Defender Economics (After Fixes)

| Protection           | Cost                  | Benefit                     |
| -------------------- | --------------------- | --------------------------- |
| Server device tokens | Dev time              | Stops cookie clearing       |
| Fingerprinting       | Dev time + CPU        | Complicates automation      |
| Identity ladder      | Dev time + OAuth cost | Converts abusers to signups |
| Queue throttling     | Dev time              | Binds compute to revenue    |

**Goal:** Make "sign up for free credits" (30 seconds) easier than "write abuse script" (10 minutes).

---

## Next Steps

See `FREE_TIER_IMPLEMENTATION.md` for detailed implementation plan including:

- Server-issued device token system
- Identity ladder implementation
- Cost-based credit calculation
- Queue with priority
- Challenge system

See `DEPRECATION_UPDATE_PLAN.md` for dependency updates and deprecation fixes.

---

## References

- Files analyzed:
  - `server/routes/images-mvp.ts` (1553 lines)
  - `server/utils/free-quota-enforcement.ts` (528 lines)
  - `server/middleware/rate-limit.ts` (235 lines)
  - `server/middleware/free-quota.ts` (44 lines)
  - `client/src/components/images-mvp/simple-upload.tsx` (564 lines)
  - `client/src/pages/images-mvp/index.tsx` (116 lines)
  - `shared/tierConfig.ts` (710 lines)

- Attacks simulated:
  - Cookie clearing
  - IP rotation
  - Session reset
  - File spam
  - Resource exhaustion
