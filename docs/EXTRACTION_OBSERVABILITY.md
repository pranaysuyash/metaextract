# Extraction Observability: Provenance, Sensitive Fields, and Shadow Mode

**Status**: Implemented (PR #1)  
**Risk Level**: Low  
**Reversible**: Yes (all changes confined to `extraction_info`)

---

## Overview

This PR adds observability infrastructure to the metadata extraction pipeline without changing any client-facing metadata. All new data is added to `extraction_info` only.

### Components

| Component | Purpose | Location in Response |
|-----------|---------|---------------------|
| **Provenance Tracking** | Records which module produced each top-level key | `extraction_info.provenance` |
| **Sensitive Field Detection** | Identifies likely PII fields (GPS, device IDs, etc.) | `extraction_info.sensitive_fields` |
| **Shadow Mode** | Runs `image_master` in parallel, diffs results | `extraction_info.shadow.image_master` |

---

## 1. Provenance Tracking

### What It Tracks

- **Top-level result keys only** (e.g., `exif`, `gps`, `mobile_metadata`)
- **Conflicts** when multiple modules write to the same key

### Response Format

```json
{
  "extraction_info": {
    "provenance": {
      "module_provenance": {
        "file": "base_metadata_engine",
        "exif": "base_metadata_engine",
        "gps": "base_metadata_engine",
        "mobile_metadata": "mobile_metadata",
        "forensic_security": "forensic_metadata"
      },
      "provenance_conflicts": [],
      "conflict_count": 0
    }
  }
}
```

### Conflict Example

```json
{
  "provenance_conflicts": [
    {
      "key": "makernote",
      "first_module": "base_engine",
      "second_module": "mobile_metadata"
    }
  ],
  "conflict_count": 1
}
```

---

## 2. Sensitive Field Detection

### What It Detects

| Kind | Patterns Matched |
|------|------------------|
| `gps` | GPS, latitude, longitude, coord, geotag, location |
| `device_id` | serial, bodyserial, lensserial, cameraid, uuid, imei |
| `person` | owner, author, artist, creator, copyright, username |
| `network` | mac, ip, ssid, bluetooth, wifi |
| `contact` | email, phone, address |

### Response Format

```json
{
  "extraction_info": {
    "sensitive_fields": {
      "sensitive_fields_detected": [
        {"path": "exif.GPSLatitude", "kind": "gps"},
        {"path": "exif.GPSLongitude", "kind": "gps"},
        {"path": "exif.SerialNumber", "kind": "device_id"},
        {"path": "exif.Artist", "kind": "person"}
      ],
      "sensitive_fields_count": 4,
      "sensitive_fields_by_kind": {
        "gps": 2,
        "device_id": 1,
        "person": 1
      },
      "truncated": false
    }
  }
}
```

### Limits

- Maximum 200 sensitive fields reported (prevents huge payloads)
- Maximum recursion depth of 10 (prevents stack overflow)

---

## 3. Shadow Mode for `image_master`

### Purpose

Run the dormant `image_master.py` extraction system in parallel to measure:
- How many additional fields it extracts
- Where it conflicts with the main extraction
- Performance overhead

### Controls

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `IMAGE_MVP_SHADOW_IMAGE_MASTER` | Enable shadow mode | `0` (off) |
| `IMAGE_MVP_SHADOW_SAMPLE_PCT` | Percentage of requests to shadow | `100` |
| `IMAGE_MVP_SHADOW_TIMEOUT` | Maximum seconds for shadow extraction | `2.0` |
| `IMAGE_MVP_SHADOW_LOG_DIFF` | Log detailed diffs to stderr | `0` (off) |

### Response Format

**Shadow disabled:**
```json
{
  "extraction_info": {
    "shadow": {
      "image_master": {
        "enabled": false,
        "reason": "not_enabled"
      }
    }
  }
}
```

**Shadow enabled (success):**
```json
{
  "extraction_info": {
    "shadow": {
      "image_master": {
        "enabled": true,
        "duration_seconds": 0.45,
        "error": null,
        "diff": {
          "added_keys_count": 127,
          "removed_keys_count": 0,
          "changed_keys_count": 3,
          "main_total_keys": 245,
          "shadow_total_keys": 372,
          "added_keys_sample": ["modules.perceptual_hashes", "modules.colors.dominant", "..."],
          "changed_keys_sample": ["exif.ImageWidth", "..."]
        }
      }
    }
  }
}
```

**Shadow enabled (error):**
```json
{
  "extraction_info": {
    "shadow": {
      "image_master": {
        "enabled": true,
        "duration_seconds": 2.0,
        "error": "Shadow extraction timed out after 2.0s"
      }
    }
  }
}
```

---

## Safety Invariants

### ✅ No Client-Facing Changes

All observability data is added to `extraction_info` only. Fields like `exif`, `gps`, `image`, etc. are unchanged.

### ✅ Shadow Mode Never Fails Main Path

- Shadow errors are caught and recorded in `extraction_info.shadow.image_master.error`
- Timeout enforced (default 2s)
- All exceptions caught with try/except

### ✅ Provenance is Deterministic

- First module to write a key wins
- Conflicts are logged but don't change behavior

### ✅ Observability Errors Are Non-Fatal

If observability data generation fails, the main result is returned with an `extraction_info.observability_error` field.

### ✅ No PII in Logs (Security Critical)

- Diff logs contain **paths and counts only**, never raw values
- `IMAGE_MVP_SHADOW_LOG_DIFF=1` logs: `Shadow diff: added=127, removed=0, changed=3`
- Sensitive field detection reports **paths only**, not actual GPS coordinates, serials, etc.

### ✅ Payload Bloat Prevention

All lists are capped to prevent unbounded growth:

| Field | Maximum |
|-------|---------|
| `provenance_conflicts` | 50 |
| `sensitive_fields_detected` | 200 |
| `diff.added_keys` | 100 |
| `diff.added_keys_sample` | 20 |

### ✅ Schema Evolution

`extraction_info.observability_version` is included for forward compatibility:

```json
{
  "extraction_info": {
    "observability_version": 1,
    "provenance": {...},
    "sensitive_fields": {...},
    "shadow": {...}
  }
}
```

### ✅ Per-Request Randomness

Shadow sampling uses `random.SystemRandom()` for true per-request randomness (not seeded once at module import).

---

## Files Modified

1. **server/extractor/extraction_observability.py** (NEW)
   - Provenance tracking functions
   - Sensitive field detection
   - Shadow mode infrastructure

2. **server/extractor/comprehensive_metadata_engine.py**
   - Import observability module
   - Initialize provenance tracking at extraction start
   - Run shadow mode for images
   - Add observability data at extraction end

3. **server/extractor/test_extraction_observability.py** (NEW)
   - 17 unit tests for all observability functions

---

## Testing

```bash
# Run unit tests
python -m pytest server/extractor/test_extraction_observability.py -v

# Test with shadow mode enabled
IMAGE_MVP_SHADOW_IMAGE_MASTER=1 python -c "
from server.extractor.comprehensive_metadata_engine import extract_comprehensive_metadata
result = extract_comprehensive_metadata('path/to/image.jpg', tier='super')
print(result['extraction_info']['shadow'])
"
```

---

## Next Steps (PR #2)

After collecting shadow mode data from production:

1. **Analyze diff results** to see which `image_master` fields add value
2. **Decide on exposure strategy**:
   - Add to existing sections (merge)
   - Add as `metadata.extended` (opt-in)
   - Keep shadow-only (not ready)
3. **Update pricing** if extraction complexity increases significantly

---

## Verification Checklist

- [x] Shadow off: extraction output matches previous behavior (except `extraction_info.*`)
- [x] Shadow on: metadata outside `extraction_info` is identical
- [x] Shadow failure: main extraction still succeeds
- [x] Perf: shadow off has no overhead; shadow on bounded by timeout
- [x] All 17 unit tests pass
