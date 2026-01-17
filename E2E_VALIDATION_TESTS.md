# End-to-End Production Validation Tests

**Date:** January 17, 2026
**Purpose:** Prove device_free quota enforcement, paid credit atomicity, and quote lifecycle correctness
**Status:** IN PROGRESS

---

## Test Suite Overview

This document tracks concrete, provable validations beyond unit tests (953 tests passing). Each test includes:

- Setup steps
- Expected behavior
- Actual results captured
- Evidence location (curl output, database queries, logs)

---

## Test 1: device_free Extraction Quota Enforcement (2-extraction limit)

### Objective

Prove that anonymous users can extract exactly 2 times per device, then receive 402 on 3rd attempt.

### Setup

- Start fresh browser session (no cookies)
- Generate device token via first request
- Track extraction count

### Test Steps

```bash
# Step 1: Create a small test image (1x1 pixel PNG)
python3 << 'EOF'
import struct
# Minimal valid PNG (1x1 transparent pixel)
png_data = bytes([
    0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,  # PNG signature
    0x00, 0x00, 0x00, 0x0d,  # IHDR chunk length
    0x49, 0x48, 0x44, 0x52,  # IHDR
    0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1
    0x08, 0x06, 0x00, 0x00, 0x00,  # 8-bit RGBA, interlaced
    0x1f, 0x15, 0xc4, 0x89,  # CRC
    0x00, 0x00, 0x00, 0x0a,  # IDAT chunk length
    0x49, 0x44, 0x41, 0x54,  # IDAT
    0x78, 0x9c, 0x63, 0xf8, 0xcf, 0xc0, 0x00, 0x00,  # compressed data
    0x03, 0x01, 0x01, 0x00,  #
    0x18, 0xdd, 0x8d, 0xb4,  # CRC
    0x00, 0x00, 0x00, 0x00,  # IEND chunk length
    0x49, 0x45, 0x4e, 0x44,  # IEND
    0xae, 0x42, 0x60, 0x82   # CRC
])
with open('/tmp/test.png', 'wb') as f:
    f.write(png_data)
print("Created /tmp/test.png (1x1 PNG)")
EOF

# Step 2: First extraction (should succeed with 200)
echo "=== EXTRACTION #1 ==="
curl -s -X POST http://localhost:3000/api/images_mvp/extract \
  -F "file=@/tmp/test.png" \
  -c /tmp/cookies1.txt \
  -b /tmp/cookies1.txt | jq -r '.access.mode, .access.free_used, .status // "200"'

# Check device_free mode
grep "metaextract_client" /tmp/cookies1.txt

# Step 3: Second extraction (should succeed with 200, free_used=2)
echo -e "\n=== EXTRACTION #2 ==="
curl -s -X POST http://localhost:3000/api/images_mvp/extract \
  -F "file=@/tmp/test.png" \
  -c /tmp/cookies2.txt \
  -b /tmp/cookies1.txt | jq -r '.access.mode, .access.free_used, .status // "200"'

# Step 4: Third extraction (should fail with 402 Payment Required)
echo -e "\n=== EXTRACTION #3 (should fail) ==="
curl -s -X POST http://localhost:3000/api/images_mvp/extract \
  -F "file=@/tmp/test.png" \
  -b /tmp/cookies1.txt -w "\nHTTP_STATUS: %{http_code}\n" | jq -r '.error // ., .status // .message'

# Step 5: Verify database records
echo -e "\n=== DATABASE VERIFICATION ==="
psql -U postgres -d metaextract -c "
  SELECT client_id, free_used, last_used_at FROM trial_usages
  ORDER BY last_used_at DESC LIMIT 1;"
```

### Expected Results

- Extraction 1: `"device_free"`, `free_used: 1`, HTTP 200
- Extraction 2: `"device_free"`, `free_used: 2`, HTTP 200
- Extraction 3: `"Quota exceeded"`, HTTP 402
- Database: trial_usages table shows 2 uses, quota enforced

### Actual Results

[TO BE EXECUTED]

---

## Test 2: Paid User Credit Consumption (Atomicity)

### Objective

Prove that credit deduction is atomic: 1 extraction = 1 credit deduction (no double-charging on replay).

### Setup

- Create test user with 100 credits
- Track credit balance before/after extraction
- Verify no double-charging on concurrent requests

### Test Steps

```bash
# Step 1: Create paid user and generate auth token
curl -s -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test_paid_'$(date +%s)'@test.com","password":"Test123!@#"}' | jq -r '.user.id, .token'

AUTH_TOKEN="<token_from_above>"
USER_ID="<user_id_from_above>"

# Grant user 100 credits directly
psql -U postgres -d metaextract -c "
  INSERT INTO credit_balances (user_id, balance, updated_at)
  VALUES ('$USER_ID', 100, NOW())
  ON CONFLICT (user_id) DO UPDATE SET balance = 100;"

# Step 2: Get initial credit balance
INITIAL_CREDITS=$(curl -s -X GET http://localhost:3000/api/auth/me \
  -H "Authorization: Bearer $AUTH_TOKEN" | jq '.user.credit_balance')
echo "Initial credits: $INITIAL_CREDITS"

# Step 3: Get quote for extraction (should show actual cost)
QUOTE=$(curl -s -X POST http://localhost:3000/api/images_mvp/quote \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d '{"files":[{"id":"test","name":"test.png","size":1024,"type":"image/png"}],"ops":{"ocr":true}}' | jq -r '.quoteId, .creditsTotal')

QUOTE_ID=$(echo "$QUOTE" | head -1)
CREDIT_COST=$(echo "$QUOTE" | tail -1)
echo "Quote ID: $QUOTE_ID, Cost: $CREDIT_COST credits"

# Step 4: Execute extraction with quoteId
curl -s -X POST http://localhost:3000/api/images_mvp/extract \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -F "file=@/tmp/test.png" \
  -F "quoteId=$QUOTE_ID" \
  -F "ops={\"ocr\":true}" | jq '.access.credits_charged'

# Step 5: Check balance after extraction
AFTER_CREDITS=$(curl -s -X GET http://localhost:3000/api/auth/me \
  -H "Authorization: Bearer $AUTH_TOKEN" | jq '.user.credit_balance')
echo "After extraction: $AFTER_CREDITS"
echo "Deducted: $((INITIAL_CREDITS - AFTER_CREDITS)) credits"

# Step 6: Verify database records (no double entry)
psql -U postgres -d metaextract -c "
  SELECT user_id, operation, credits, created_at FROM credit_transactions
  WHERE user_id = '$USER_ID'
  ORDER BY created_at DESC LIMIT 5;"
```

### Expected Results

- Initial balance: 100 credits
- Quote cost: Actual value (e.g., 12 credits for OCR + image size)
- After extraction: 100 - cost (e.g., 88)
- Credit transactions: Exactly 1 entry (no duplicates on replay)

### Actual Results

[TO BE EXECUTED]

---

## Test 3: Quote Lifecycle (Expiration & Replay Protection)

### Objective

Prove that:

- Quotes expire after 15 minutes
- Used quotes cannot be replayed
- Quote status transitions correctly (active → used)

### Test Steps

```bash
# Step 1: Generate quote
QUOTE_RESP=$(curl -s -X POST http://localhost:3000/api/images_mvp/quote \
  -H "Content-Type: application/json" \
  -d '{"files":[],"ops":{}}'
)
QUOTE_ID=$(echo "$QUOTE_RESP" | jq -r '.quoteId')
EXPIRES_AT=$(echo "$QUOTE_RESP" | jq -r '.expiresAt')
echo "Quote ID: $QUOTE_ID"
echo "Expires at: $EXPIRES_AT"

# Verify 15-minute expiration
CREATED_AT=$(date -u +%s)
EXPIRES_TS=$(date -d "$EXPIRES_AT" +%s)
EXPIRES_IN_SECONDS=$((EXPIRES_TS - CREATED_AT))
echo "Expires in: $EXPIRES_IN_SECONDS seconds (should be ~900 for 15 minutes)"

# Step 2: Check database status (should be 'active')
psql -U postgres -d metaextract -c "
  SELECT id, status, created_at, expires_at, used_at
  FROM images_mvp_quotes
  WHERE id = '$QUOTE_ID';"

# Step 3: Use quote for extraction
curl -s -X POST http://localhost:3000/api/images_mvp/extract \
  -F "file=@/tmp/test.png" \
  -F "quoteId=$QUOTE_ID" | jq '.status'

# Step 4: Check database status (should be 'used')
psql -U postgres -d metaextract -c "
  SELECT id, status, created_at, expires_at, used_at
  FROM images_mvp_quotes
  WHERE id = '$QUOTE_ID';"

# Step 5: Try to replay same quoteId (should fail with 409 or 402)
echo -e "\n=== REPLAY TEST (should fail) ==="
curl -s -X POST http://localhost:3000/api/images_mvp/extract \
  -F "file=@/tmp/test.png" \
  -F "quoteId=$QUOTE_ID" \
  -w "\nHTTP_STATUS: %{http_code}\n" | jq '.error // .message // .'
```

### Expected Results

- Quote expires in ~900 seconds (15 minutes)
- Initial status: 'active'
- After use: status = 'used', used_at populated
- Replay attempt: HTTP 409 Conflict or 402 (cannot reuse)

### Actual Results

[TO BE EXECUTED]

---

## Test 4: GPS Redaction Validation (device_free)

### Objective

Prove that device_free users get rounded GPS (2 decimals), NOT removed completely.

### Test Steps

```bash
# Step 1: Create test image with known GPS EXIF
# For this test, we'll use a sample JPEG with GPS data embedded
# Expected format: latitude: 37.7749295, longitude: -122.4194155

# Step 2: Anonymous extraction (device_free)
echo "=== DEVICE_FREE EXTRACTION (Anonymous) ==="
curl -s -X POST http://localhost:3000/api/images_mvp/extract \
  -F "file=@/tmp/gps_test.jpg" \
  -c /tmp/anon_cookies.txt | jq '.gps'

# Expected: {"latitude": 37.77, "longitude": -122.42} (rounded to 2 decimals)

# Step 3: Paid user extraction (full GPS)
echo -e "\n=== PAID EXTRACTION (Full GPS) ==="
curl -s -X POST http://localhost:3000/api/images_mvp/extract \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -F "file=@/tmp/gps_test.jpg" | jq '.gps'

# Expected: {"latitude": 37.7749295, "longitude": -122.4194155} (full precision)

# Step 4: Trial user extraction (GPS removed)
echo -e "\n=== TRIAL EXTRACTION (GPS Removed) ==="
curl -s -X POST http://localhost:3000/api/images_mvp/extract \
  -H "Authorization: Bearer $TRIAL_TOKEN" \
  -F "file=@/tmp/gps_test.jpg" | jq '.gps'

# Expected: null or empty (fully removed for trial_limited)
```

### Expected Results

- device_free: GPS rounded to 2 decimals (37.77, -122.42)
- paid: Full GPS precision (37.7749295, -122.4194155)
- trial_limited: GPS = null

### Actual Results

[TO BE EXECUTED]

---

## Test 5: Production DB Migration Reality

### Objective

Verify that images_mvp_quotes table would be created in production when init.sql is applied.

### Test Steps

```bash
# Check if table exists in current DB
psql -U postgres -d metaextract -c "
  SELECT to_regclass('public.images_mvp_quotes');"

# Check schema
psql -U postgres -d metaextract -c "
  \d images_mvp_quotes"

# Verify indexes exist
psql -U postgres -d metaextract -c "
  SELECT indexname FROM pg_indexes
  WHERE tablename = 'images_mvp_quotes';"

# Check if deployed prod would get this (search for deploy process)
grep -r "init.sql" /Users/pranay/Projects/metaextract/railway* 2>/dev/null || echo "Check deployment config"
grep -r "psql" /Users/pranay/Projects/metaextract/docker* 2>/dev/null || echo "Check Docker setup"
```

### Expected Results

- Table exists: ✅ YES
- Columns: 14 fields present (id, session_id, user_id, files, ops, etc.)
- Indexes: 4 indexes created
- Production path: Identified and documented

### Actual Results

[TO BE EXECUTED]

---

## Summary Checklist

### Must-Prove (Critical for Production)

- [ ] Device_free quota enforcement (2-extraction limit works)
- [ ] Paid credit atomicity (no double-charging)
- [ ] Quote expiration (15-minute window enforced)
- [ ] Replay protection (used quotes cannot be reused)
- [ ] GPS redaction (rounded for device_free, full for paid)
- [ ] Production DB migration path identified

### Nice-to-Have (Confidence Builders)

- [ ] Concurrent request handling (no race conditions)
- [ ] Error message clarity (users understand 402 means upgrade)
- [ ] Audit trail (transactions logged correctly)
- [ ] Performance (extraction completes in <5s)

---

## Next Steps

1. Execute Test 1 (quota enforcement)
2. Execute Test 2 (credit atomicity)
3. Execute Test 3 (quote lifecycle)
4. Execute Test 4 (GPS redaction)
5. Execute Test 5 (DB migration)
6. Document all results with actual command output
7. Create acceptance checklist for production deployment
