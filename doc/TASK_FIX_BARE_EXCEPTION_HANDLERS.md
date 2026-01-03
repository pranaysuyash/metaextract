# Task: Replace Bare Exception Handlers with Proper Logging

## Summary
Fix 16 bare `except: pass` blocks in `server/extractor/metadata_engine.py` that silently swallow all exceptions without logging. This technical debt makes debugging impossible and violates the AGENTS.md guideline: "No tech debt - understand root cause before modifying code."

## What & Why

### The Problem
```python
def detect_mime_type(filepath: str) -> str:
    mime_type = None
    if MAGIC_AVAILABLE:
        try: mime_type = magic.from_file(filepath, mime=True)
        except: pass  # ❌ Silent failure - no logging, no error info
    if not mime_type: mime_type = mimetypes.guess_type(filepath)[0]
    return mime_type or "application/octet-stream"
```

When `magic.from_file()` fails:
- Error is completely hidden
- Debugging is impossible
- No monitoring/alerting possible
- Hard to diagnose extraction failures
- Violates Python best practices (PEP 8)

### The Solution
```python
def detect_mime_type(filepath: str) -> str:
    mime_type = None
    if MAGIC_AVAILABLE:
        try:
            mime_type = magic.from_file(filepath, mime=True)
        except OSError as e:  # ✅ Specific exception type
            logger.debug(f"Failed to detect MIME type with magic: {e}")
            # Gracefully fall back to mimetypes module
    if not mime_type: mime_type = mimetypes.guess_type(filepath)[0]
    return mime_type or "application/octet-stream"
```

Benefits:
- **Debuggability**: Know exactly what failed and why
- **Robustness**: Graceful degradation (fallback to mimetypes)
- **Observability**: Errors visible in logs for production monitoring
- **No functional change**: Still works exactly the same way

## Locations (16 instances)

Found in `server/extractor/metadata_engine.py`:

| Line | Context | Exception Type |
|------|---------|---|
| 402 | `detect_mime_type()` - magic.from_file() | `OSError` |
| 1093 | `get_file_metadata()` - pwd/grp lookup | `KeyError` |
| 1143 | Video codec extraction | TBD (inspect) |
| 1199 | Audio codec extraction | TBD (inspect) |
| 1289 | XMP metadata extraction | TBD (inspect) |
| 1400 | MakerNote parsing | TBD (inspect) |
| 1410 | IPTC extraction | TBD (inspect) |
| 1420 | Extended attributes | TBD (inspect) |

## Approach

1. **Inspect each block** at the specified lines
   - Understand what operation is being attempted
   - Identify specific exception types (OSError, KeyError, ImportError, etc.)
   - Check if there's already a fallback strategy

2. **Replace pattern**:
   ```python
   # Before:
   try:
       operation()
   except: pass
   
   # After:
   try:
       operation()
   except SpecificError as e:
       logger.debug(f"Context: failed to X: {e}")
       # Continue gracefully
   ```

3. **Logging strategy**:
   - Use `logger.debug()` for expected failures (e.g., optional dependencies)
   - Use `logger.warning()` for unexpected failures during critical extraction
   - Include context about what operation failed and why

4. **Keep extraction graceful**:
   - One failed operation shouldn't stop entire extraction
   - Return partial results (this is already the pattern)
   - Document expected failures in code comments

## Testing Strategy

Existing tests should still pass (no functional change):
```bash
pytest tests/ -v -k "test_metadata_engine" --log-cli-level=DEBUG
npm run test:ci
```

Manual verification:
```bash
python server/extractor/metadata_engine.py test_images/sample.jpg --log-level=DEBUG
```

## Impact

| Metric | Value |
|--------|-------|
| Lines to change | ~8-16 |
| Complexity | Low (straightforward pattern replacement) |
| Risk | Minimal (no functional change) |
| Time estimate | 30-45 minutes |
| Payoff | High (improves debuggability across entire system) |
| Tech debt reduction | Significant |

## Why This Matters

**From AGENTS.md:**
> "Code Quality: No tech debt. Before deleting code for issue resolution, implement missing or wrong code properly instead of removing functionality."

This task follows that principle - we're NOT removing code, we're IMPLEMENTING proper error handling that was missing. This will:
- Improve production debugging
- Enable better monitoring
- Follow Python best practices (PEP 8: "Bare except clauses should be avoided")
- Make future development easier
- Reduce time spent debugging extraction failures

## Current State

File: `/Users/pranay/Projects/metaextract/server/extractor/metadata_engine.py`
- Logger already configured (lines 59-61)
- Multiple extraction fallback patterns already in place
- Ready for error handling improvement

## Success Criteria

- [ ] All 16 `except: pass` blocks replaced with specific exception types
- [ ] Each has appropriate logging statement
- [ ] All existing tests pass
- [ ] No functional behavior changes
- [ ] Code follows AGENTS.md guidelines
