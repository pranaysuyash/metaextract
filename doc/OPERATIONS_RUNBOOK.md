# MetaExtract Operations Runbook

## Overview

MetaExtract is an image metadata extraction service with credit-based access control.

## Architecture

- **Backend**: Node.js/Express on port 3000
- **Frontend**: Vite dev server on port 5173 (proxies to 3000)
- **Database**: PostgreSQL (via `storage` module)
- **Cache/Rate Limit**: Redis
- **Python Extraction**: Virtual environment at `.venv/bin/python3`

## Key Endpoints

| Endpoint                              | Description                           |
| ------------------------------------- | ------------------------------------- |
| `GET /api/health`                     | Health check                          |
| `POST /api/auth/login`                | User authentication                   |
| `POST /api/images_mvp/quote`          | Get extraction quote (credits needed) |
| `POST /api/images_mvp/extract`        | Extract metadata from image           |
| `GET /api/images_mvp/credits/balance` | Check credit balance                  |

## Common Operations

### Starting the Service

```bash
cd /Users/pranay/Projects/metaextract

# Development (frontend + backend)
npm run dev

# Backend only (port 3000)
npm run dev:server

# Frontend only (port 5173)
npm run dev:client
```

### Checking Service Status

```bash
# Check if server is running
curl http://localhost:3000/api/health

# Check port usage
lsof -i :3000

# Check running processes
ps aux | grep node
```

### Testing Extraction

```bash
# Get auth token
TOKEN=$(curl -s -X POST http://localhost:3000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@metaextract.com","password":"TestPassword123!"}' | \
  grep -o '"token":"[^"]*"' | cut -d'"' -f4)

# Get quote
QUOTE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"files":[{"id":"test-1","name":"test.jpg","mime":"image/jpeg","sizeBytes":100000}],"ops":{"embedding":true}}' \
  http://localhost:3000/api/images_mvp/quote)
QUOTE_ID=$(echo $QUOTE | grep -o '"quoteId":"[^"]*"' | cut -d'"' -f4)

# Extract
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -F "file=@test-data/embedding_test.jpg" \
  -F "quoteId=$QUOTE_ID" \
  -F "ops={\"embedding\":true}" \
  http://localhost:3000/api/images_mvp/extract
```

## Monitoring

### Logs

- Server logs: `/tmp/server.log` (when started with `npm run dev:server > /tmp/server.log`)
- Python extraction logs: Displayed in server console

### Health Metrics

- `GET /api/health` returns service status, version, timestamp

### Security Alerts

The system monitors:

- Rate limit violations
- Failed uploads
- Suspicious IP patterns
- Resource usage (memory, disk)

Alerts are logged to console and can be sent via email (requires `ENABLE_EMAIL_ALERTS=true`).

## Rate Limits

| Endpoint                | Limit | Window     |
| ----------------------- | ----- | ---------- |
| Quote creation          | 30    | per minute |
| Extraction (auth)       | 50    | per 15 min |
| Extraction (anon)       | 10    | per minute |
| Burst protection (anon) | 10    | per minute |

## Troubleshooting

### Extraction Fails with 500 Error

1. Check if Python venv exists: `.venv/bin/python3`
2. Check temp directory permissions: `/tmp/metaextract-uploads`
3. Verify disk space: `df -h /tmp`
4. Check server logs for specific error

### Database Connection Issues

1. Verify PostgreSQL is running
2. Check connection string in `.env`
3. Run: `npm run db:push` to sync schema

### Rate Limiting Issues

1. Check Redis connection: `redis-cli ping`
2. Verify rate limit headers in response
3. Review `/api/admin/rate-limits` endpoint

### Performance Issues

- Extraction typically takes 7-10 seconds (Python startup overhead)
- Monitor `/api/admin/metrics` for performance data
- Check for temp file buildup: `ls -la /tmp/metaextract-uploads/`

## Security Considerations

### Implemented Security

- CSRF protection (httpOnly cookies)
- Rate limiting (Redis-backed)
- Input validation and sanitization
- Path traversal prevention
- Credit hold atomicity (prevents double-charging)

### Environment Variables Required

```
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
JWT_SECRET=your-secret
PYTHON_EXECUTABLE=/path/to/python3
DODO_PAYMENTS_API_KEY=...
```

## Testing

```bash
# Run all tests
npm test

# Run extraction tests only
npm test -- server/routes/extraction.test.ts

# Run with coverage
npm test -- --coverage
```

## Credit System

### Credit Consumption Formula

```
Total = Base (1) + MP Bucket (0/1/3/7) + Features (OCR=5, Embedding=3, Forensics=4)
```

### Credit Packs

- Starter: 50 credits
- Pro: 200 credits

### Free Tier

- 2 extractions per device (cookie-based)
- Full metadata extraction with redaction applied
