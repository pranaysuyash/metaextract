# Task: Clean Up Orphaned TODO Logging Comments

**Status:** Ready to start  
**Effort:** Medium (45-60 minutes)  
**Impact:** Medium (improves code quality, removes misleading TODOs)  
**Priority:** HIGH (completes exception handling cleanup)

## Summary

Remove 30 orphaned "pass  # TODO: Consider logging" comments from exception handlers across multiple modules. These are stubs from an automated tooling pass that were never implemented.

## The Problem

Various modules contain this pattern:
```python
try:
    some_operation()
except SomeError as e:
    pass  # TODO: Consider logging: logger.debug(f'Handled exception: {e}')
```

**Issues:**
- Misleading TODO comments suggest future work
- `pass` statement silently swallows exceptions
- No error visibility in logs
- Inconsistent with our new exception handling pattern
- Creates maintenance burden (unclear intent)

## The Solution

**Option A: Remove pass + add logging** (Recommended)
```python
try:
    some_operation()
except SomeError as e:
    logger.debug(f"Failed to [operation description]: {e}")
```

**Option B: Just remove the TODO if operation is optional**
```python
try:
    some_operation()
except SomeError:
    pass  # Operation is optional
```

**Option C: Convert to warning if critical**
```python
try:
    some_operation()
except SomeError as e:
    logger.warning(f"Failed to [operation description]: {e}")
```

## Affected Files & Locations

### High Priority (Critical extraction functions)

| File | Line | Function | Recommended Action |
|------|------|----------|------------------|
| audio_codec_details.py | 2133 | Audio frame parsing | Add logging |
| audio_codec_details.py | 2278 | Audio codec extraction | Add logging |
| audio_codec_details.py | 2686 | Audio metadata | Add logging |
| scientific_medical.py | 424 | FITS data extraction | Add logging |
| scientific_medical.py | 455 | Medical DICOM parsing | Add logging |
| scientific_medical.py | 515 | Astronomical data | Add logging |
| scientific_medical.py | 570 | Sensor data extraction | Add logging |
| scientific_medical.py | 611 | Instrument parsing | Add logging |
| scientific_medical.py | 628 | Data validation | Add logging |
| scientific_medical.py | 655 | Quality metrics | Add logging |
| scientific_medical.py | 865 | Metadata analysis | Add logging |
| scientific_medical.py | 1047 | Data interpretation | Add logging |

### Medium Priority (Utility/Quality functions)

| File | Line | Function | Recommended Action |
|------|------|----------|------------------|
| icc_profile.py | 274 | Color profile parsing | Add logging |
| print_publishing.py | 49 | Print metadata | Add logging |
| iptc_xmp_fallback.py | 141 | Fallback metadata | Add logging |
| geocoding.py | 45 | Location lookup | Add logging |
| perceptual_hashes.py | 322 | Image hash calculation | Add logging |
| perceptual_comparison.py | 230 | Hash comparison | Add logging |

### Lower Priority (File system functions)

| File | Line | Function | Recommended Action |
|------|------|----------|------------------|
| filesystem.py | 110 | File stat reading | Add logging |
| temporal_astronomical.py | 124 | Time calculation | Add logging |

### High Impact (Medical imaging)

| File | Line | Function | Recommended Action |
|------|------|----------|------------------|
| dicom_medical.py | 858-932 | DICOM parsing (11 locations) | Add logging |

## Implementation Approach

### Step 1: Inspect Each Location
Read the surrounding code to understand what operation is being performed.

### Step 2: Determine Appropriate Exception Type
```python
# Review the actual except clause to identify exception types
except (ValueError, TypeError) as e:
```

### Step 3: Add Meaningful Log Message
```python
except ValueError as e:
    logger.debug(f"Failed to parse audio frame data: {e}")
```

### Step 4: Preserve Fallback Behavior
Ensure that graceful degradation still happens (extraction continues with partial results).

## Logging Strategy

### Use DEBUG level for:
- Optional features that have fallbacks
- Expected failures (missing optional data)
- File format variations

### Use WARNING level for:
- Unexpected failures during core extraction
- Failures that affect data quality
- Errors in required functions

## File-by-File Guidance

### audio_codec_details.py (3 locations)
- Line 2133: Frame parsing - DEBUG level
- Line 2278: Codec detection - DEBUG level
- Line 2686: Metadata extraction - DEBUG level
```python
# Add context about what codec/format was being parsed
logger.debug(f"Failed to extract audio [property]: {e}")
```

### scientific_medical.py (8 locations + 1 critical)
- Lines 424, 455, 515, 570, 611, 628, 655, 865, 1047
- These are FITS/DICOM extraction - HIGH IMPACT
```python
# Add context about file type and what field
logger.debug(f"Failed to extract [FITS/DICOM] [field_name]: {e}")
```

### dicom_medical.py (11 locations - lines 858-932)
- These are medical imaging functions
- High impact on medical file extraction
```python
# Add context about DICOM tag/element
logger.debug(f"Failed to parse DICOM [tag/element]: {e}")
```

### Other modules (8 locations)
- Generally utility functions with optional features
- DEBUG level appropriate
```python
logger.debug(f"Failed to [operation]: {e}")
```

## Testing Strategy

1. **Syntax check** - Verify no Python syntax errors
2. **Import test** - Ensure modules can be imported
3. **Unit tests** - Run existing tests for affected modules
4. **Logging test** - Verify debug output appears when errors occur

```bash
# Syntax check
python3 -m py_compile server/extractor/modules/*.py

# Unit tests for affected modules
pytest tests/ -k "audio or medical or dicom or geocoding" -v

# Integration test
python -c "from server.extractor.metadata_engine import extract_metadata; extract_metadata('test.jpg')"
```

## Success Criteria

- [ ] All 30 orphaned TODO comments removed
- [ ] Each has appropriate logging (DEBUG or WARNING)
- [ ] No orphaned `pass` statements remain
- [ ] All files have valid Python syntax
- [ ] Module imports work
- [ ] Unit tests pass
- [ ] No functional behavior changes
- [ ] Debug messages are clear and contextual

## Related to Previous Work

This task **completes the exception handling cleanup** started with the bare `except: pass` fix in metadata_engine.py. Those were isolated cases; this task handles distributed occurrences across modules.

Both tasks follow the AGENTS.md principle: "Implement proper error handling instead of removing code."

## Rollback Plan

- Git history preserves original code
- Changes are isolated to exception handlers
- No functional behavior changes (only visibility/logging improvements)

## Documentation Needed

After completing:
1. Create TASK_CLEAN_ORPHANED_TODO_LOGGING_COMPLETED.md
2. Update session summary with completion
3. List all files modified

## Priority Notes

**HIGH:** This task should be done soon because:
1. Continues momentum from previous fix
2. Uses same pattern and approach
3. Removes misleading TODO comments
4. Improves code maintainability
5. Only 45-60 minutes effort
6. High quality/effort ratio

---

**Recommendation:** Start with scientific_medical.py and dicom_medical.py (highest impact), then work through audio_codec_details.py and utility modules.
