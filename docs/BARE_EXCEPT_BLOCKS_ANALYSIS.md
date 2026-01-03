# Bare Except Blocks: Silent Failures in Python Extractor

**File**: `server/extractor/comprehensive_metadata_engine.py`  
**Lines**: 178, 478, 700, 1359, 1717, 1724, 2878 (7 instances)  
**Severity**: MEDIUM  
**Impact**: Debugging impossible, silent data loss, missing metadata fields

---

## The Problem

Seven bare `except:` blocks catch **all exceptions** and silently swallow them:

```python
# Line 1359 - DICOM image extraction
try:
    result["image_info"]["dimensions"] = ds.pixel_array.shape
    result["image_info"]["data_type"] = str(ds.pixel_array.dtype)
except:  # ❌ Catches everything: MemoryError, KeyboardInterrupt, etc.
    pass   # ❌ Silent failure - field never extracted

# Line 1717 - GeoTIFF band statistics
try:
    result["band_info"]["mean"] = stats.mean
    result["band_info"]["std"] = stats.std
except:  # ❌ Silent failure
    pass

# Line 178, 478, 700, 1724, 2878 - File size/type detection
try:
    file_size = os.path.getsize(filepath)
except:  # ❌ May hide actual problem
    pass
```

### Why This Is Broken

**Bare except catches:**
- ✓ Expected exceptions (FileNotFoundError, ValueError)
- ✗ **Unexpected exceptions** (MemoryError, SystemExit, KeyboardInterrupt)
- ✗ **Code defects** (NameError, AttributeError, TypeError)
- ✗ **Interrupts** (UserWarning, DeprecationWarning escalated to errors)

**Silent failures cause:**
- Metadata field missing without any indication why
- Impossible to debug (no error message)
- User gets incomplete results
- Analytics show gaps with no cause
- Production errors invisible until users complain

---

## Examples of Masked Errors

### Example 1: DICOM Pixel Array (Line 1359)

```python
try:
    result["image_info"]["dimensions"] = ds.pixel_array.shape
    result["image_info"]["data_type"] = str(ds.pixel_array.dtype)
except:
    pass
```

**Possible exceptions masked:**
- `MemoryError` - Large DICOM too big to load pixel array
  - Should: Return error "File too large for tier"
  - Actually: Silently continues, user gets incomplete metadata

- `RuntimeError` - DICOM library internal error
  - Should: Log and retry
  - Actually: Field disappears, user never knows

- `AttributeError` - ds object corrupted
  - Should: Log error, return partial results
  - Actually: Silent failure

---

## The Fix

Replace with **specific exception handling**:

```python
# Line 1359 - DICOM image extraction
try:
    result["image_info"]["dimensions"] = ds.pixel_array.shape
    result["image_info"]["data_type"] = str(ds.pixel_array.dtype)
except (MemoryError, RuntimeError) as e:
    # Expected errors for large/corrupted files
    logging.warning(
        f"Failed to extract DICOM pixel array: {type(e).__name__}: {e}"
    )
except Exception as e:
    # Unexpected errors - log for debugging
    logging.error(
        f"Unexpected error extracting DICOM dimensions: {type(e).__name__}: {e}",
        exc_info=True
    )
    # Still continue extraction for other fields
```

### Pattern for All 7 Fixes

**Generic pattern**:
```python
try:
    # Operation that might fail
    result[key] = operation()
except SpecificError as e:
    # Expected error - log as warning
    logging.warning(f"Expected error {e}")
except Exception as e:
    # Unexpected error - log with full context
    logging.error(f"Unexpected error: {type(e).__name__}: {e}", exc_info=True)
    # Continue extraction - this field just won't be populated
```

---

## All 7 Bare Except Blocks

| Line | Operation | Expected Error | Current | Fixed |
|------|-----------|---|---------|-------|
| 178 | Get file size | FileNotFoundError | ❌ bare except | ✅ Specific |
| 478 | Get file size | FileNotFoundError | ❌ bare except | ✅ Specific |
| 700 | Get file size | FileNotFoundError | ❌ bare except | ✅ Specific |
| 1359 | DICOM pixel array | MemoryError, RuntimeError | ❌ bare except | ✅ Specific |
| 1717 | GeoTIFF statistics | ValueError, IndexError | ❌ bare except | ✅ Specific |
| 1724 | GeoTIFF color interp | IndexError, AttributeError | ❌ bare except | ✅ Specific |
| 2878 | Get file size | FileNotFoundError | ❌ bare except | ✅ Specific |

---

## Detailed Fixes

### Fix 1: Line 178 (File Size Detection)

**Current**:
```python
try:
    file_size = os.path.getsize(filepath) if os.path.exists(filepath) else "unknown"
except:
    pass  # If we can't get file size, continue with "unknown"
```

**Fixed**:
```python
try:
    file_size = os.path.getsize(filepath) if os.path.exists(filepath) else "unknown"
except (OSError, IOError) as e:
    # Expected: file permission or path issues
    logging.warning(f"Could not determine file size: {e}")
    file_size = "unknown"
except Exception as e:
    # Unexpected: log for debugging
    logging.error(f"Unexpected error getting file size: {type(e).__name__}: {e}")
    file_size = "unknown"
```

---

### Fix 2: Lines 478, 700, 2878 (File Size/Type)

Same pattern as Fix 1.

---

### Fix 3: Line 1359 (DICOM Pixel Array)

**Current**:
```python
if hasattr(ds, 'pixel_array'):
    try:
        result["image_info"]["dimensions"] = ds.pixel_array.shape
        result["image_info"]["data_type"] = str(ds.pixel_array.dtype)
    except:
        pass
```

**Fixed**:
```python
if hasattr(ds, 'pixel_array'):
    try:
        result["image_info"]["dimensions"] = ds.pixel_array.shape
        result["image_info"]["data_type"] = str(ds.pixel_array.dtype)
    except MemoryError as e:
        # File too large to load into memory
        logging.warning(
            f"DICOM file too large to load pixel array: {e}. "
            f"File size may exceed available memory."
        )
    except (RuntimeError, ValueError) as e:
        # DICOM corruption or library error
        logging.warning(f"Failed to extract DICOM pixel array: {e}")
    except Exception as e:
        # Unexpected error
        logging.error(
            f"Unexpected error extracting DICOM pixel dimensions: {type(e).__name__}: {e}",
            exc_info=True
        )
```

---

### Fix 4: Line 1717 (GeoTIFF Band Statistics)

**Current**:
```python
try:
    result["band_info"]["mean"] = stats.mean
    result["band_info"]["std"] = stats.std
except:
    pass
```

**Fixed**:
```python
try:
    result["band_info"]["mean"] = stats.mean
    result["band_info"]["std"] = stats.std
except (ValueError, IndexError, AttributeError) as e:
    # Expected: stats unavailable or corrupted band data
    logging.warning(f"Could not compute band statistics: {e}")
except Exception as e:
    # Unexpected
    logging.error(
        f"Unexpected error computing band statistics: {type(e).__name__}: {e}",
        exc_info=True
    )
```

---

### Fix 5: Line 1724 (GeoTIFF Color Interpretation)

**Current**:
```python
try:
    color_interp = src.colorinterp[i-1]
    band_info["color_interpretation"] = color_interp.name
except:
    pass
```

**Fixed**:
```python
try:
    color_interp = src.colorinterp[i-1]
    band_info["color_interpretation"] = color_interp.name
except IndexError as e:
    # Expected: band index out of range
    logging.debug(f"Color interpretation unavailable for band {i}: {e}")
except AttributeError as e:
    # Expected: color_interp doesn't have .name attribute
    logging.debug(f"Color interpretation has no name attribute: {e}")
except Exception as e:
    # Unexpected
    logging.error(
        f"Unexpected error getting color interpretation: {type(e).__name__}: {e}",
        exc_info=True
    )
```

---

## Logging Setup Required

These fixes require logging to be configured:

```python
import logging

# At module level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

Or if already configured in the module, just use:
```python
logging.warning("message")
logging.error("message", exc_info=True)
```

---

## Impact of Fix

### Before (Bare Except)
```
User uploads DICOM file (1GB)
→ MemoryError when loading pixel_array
→ except: pass (silent)
→ Result: No dimensions, no data_type field
→ User: "Why are those fields missing?"
→ Developer: "No log, no idea what failed"
```

### After (Specific Exception)
```
User uploads DICOM file (1GB)
→ MemoryError when loading pixel_array
→ logging.warning("DICOM file too large...")
→ Result: No dimensions, no data_type field
→ User: Sees in response: "Large files may have limited metadata"
→ Developer: Sees in logs: "DICOM file too large to load pixel array"
```

---

## Testing

Add test for exception handling:

```python
def test_dicom_large_file_handling():
    """Test that MemoryError is logged, not silently swallowed."""
    # Mock large pixel array that raises MemoryError
    with patch('pydicom.dcmread') as mock_dcm:
        ds = MagicMock()
        ds.pixel_array.side_effect = MemoryError("Not enough memory")
        mock_dcm.return_value = ds
        
        # Should complete without exception
        result = extract_comprehensive_metadata("large_dicom.dcm")
        
        # Should have logged warning
        assert_log_contains("DICOM file too large")
        
        # But other fields should still be extracted
        assert result["patient_info"] is not None
```

---

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Error visibility** | ❌ Silent | ✅ Logged |
| **Debugging** | ❌ Impossible | ✅ Possible |
| **System errors caught** | ❌ YES (bad) | ✅ NO (good) |
| **Expected errors logged** | ❌ No | ✅ Yes |
| **Data loss** | ❌ Fields disappear | ⚠️ Fields still missing but logged |
| **User feedback** | ❌ None | ⚠️ Could be improved |

---

**Status**: Ready for implementation ✅
