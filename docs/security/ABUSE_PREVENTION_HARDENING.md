# Security Hardening: Abuse Prevention System

## Overview

This update implements a 4-priority security hardening system for the images_mvp free tier, addressing the abuse vectors identified in the security audit.

## Files Added/Modified

| File | Action | Purpose |
|------|--------|---------|
| `server/utils/device-token.ts` | NEW | Server-issued device tokens |
| `server/utils/cost-calculator.ts` | NEW | File type cost matrix |
| `server/utils/circuit-breaker.ts` | NEW | Load shedding system |
| `server/rateLimitRedis.ts` | MODIFIED | Fixed fail-open vulnerability |
| `server/utils/free-quota-enforcement.ts` | MODIFIED | Integration |
| `server/routes/images-mvp.ts` | MODIFIED | Extraction flow updates |

## Abuse Vectors Addressed

### 1. Rate Limit Bypass via Redis Errors (CRITICAL)
- **Before**: Rate limiting failed open when Redis unavailable
- **After**: Uses in-memory fallback at 50% normal limits

### 2. Cookie-Clearing Quota Reset
- **Before**: Client could clear cookies to reset free quota
- **After**: Server-issued device tokens with HMAC signatures

### 3. Cost Extraction Attacks
- **Before**: All file types cost the same
- **After**: Cost matrix assigns higher costs to expensive formats (HEIC, RAW)

### 4. Load-Based Resource Exhaustion
- **Before**: No protection during high load
- **After**: Circuit breaker delays free tier, prioritizes paid users

## How It Works

### Device Token Flow
```
1. Request arrives without device token
2. Server generates HMAC-signed token: deviceId.issuedAt.expiry.signature
3. Token set as httpOnly cookie (not accessible via JS)
4. Subsequent requests use same device identity
5. Clearing cookies doesn't help - new token gets fresh quota but tracked separately
```

### Circuit Breaker States
```
CLOSED (normal) → Queue depth > 500 → OPEN (free tier delayed)
                                          ↓
                                    60 sec timeout
                                          ↓
                                    HALF_OPEN (testing)
                                          ↓
                             5 successful requests → CLOSED
```

## Configuration

### Environment Variables
```bash
# Required (already set)
TOKEN_SECRET=<your-existing-secret>

# Optional (recommended for production)
DEVICE_TOKEN_SECRET=<separate-32-byte-hex-secret>
```

### Thresholds (defaults in circuit-breaker.ts)
```typescript
queueDepthThreshold: 500,
cpuThreshold: 80,
memoryThreshold: 85,
resetTimeout: 60000,
successThreshold: 5,
```

## Testing

### Verify Fail-Closed Behavior
1. Stop Redis
2. Make request to `/api/images_mvp/extract`
3. Should get 429 (not 200)

### Verify Device Token
1. Upload file (observe `metaextract_device` cookie)
2. Clear all cookies
3. Upload again (new device token, separate quota)

## Future Enhancements

1. **CAPTCHA escalation** - Require verification for suspicious devices
2. **Paid tier queue bypass** - Skip load shedding entirely for paid users
3. **Fingerprint aggregation** - Combine device tokens with browser fingerprints
4. **Redis revocation list** - Ability to revoke device tokens
