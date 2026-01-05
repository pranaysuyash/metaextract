# Images MVP Infrastructure Readiness Guide

This guide details the operational steps required to complete the infrastructure-dependent items from the Subsystem Audit.

## 1. Storage Lifecycle & Security
*Code complete. Configuration required.*

### Encryption at Rest (Item #81)
**Action**: Enable blocking public access and default encryption on the S3 bucket.
```bash
# Example AWS CLI command
aws s3api put-bucket-encryption \
    --bucket metaextract-images-mvp \
    --server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'
```

### Lifecycle Policies (Item #82)
**Action**: Configure lifecycle rule to transition original uploads to Glacier/Deep Archive after 30 days.
- **Rule Name**: `ArchiveOriginals`
- **Prefix**: `original/`
- **Transition**: Standard-IA after 30 days, Glacier after 90 days.
- **Expiration**: Optional (e.g., 1 year).

### Presigned Uploads (Item #83)
**Action**: Configure CORS on the bucket to allow PUT requests from client domain.
```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["PUT", "POST"],
        "AllowedOrigins": ["https://metaextract.com"],
        "ExposeHeaders": ["ETag"]
    }
]
```

## 2. Observability & SLOs
*Code complete (Correlation IDs). Monitoring setup required.*

### Dashboards (Item #85) & SLOs (Item #86)
**Action**: Set up Grafana/Datadog dashboard tracking:
1.  **Latency**: `rateLimitExtraction` duration (node_exporter/custom metric).
2.  **Queue Depth**: Redis list size (if using Redis queue).
3.  **Error Rate**: 5xx responses on `/api/images_mvp/extract`.

**Target SLOs**:
- **Availability**: 99.9% successful uploads.
- **Latency**: P90 extraction time < 5s.
- **Freshness**: Queue age < 10s.

## 3. Advanced Features
*Future Roadmap*

### Resumable Uploads (Item #87)
**Recommendation**: Use **Tus** protocol.
- **Client**: `tus-js-client`.
- **Server**: `@tus/server` middleware.
- **Note**: Requires separate endpoint `/api/upload/resumable`.

### Load Testing (Item #88)
**Plan**: Use k6 for concurrency testing.
- **Scenario**: 50 concurrent uploads of 5MB images.
- **Success Criteria**: 0 errors, P95 latency < 8s.
