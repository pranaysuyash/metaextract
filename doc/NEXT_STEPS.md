# MetaExtract - Next Improvement Tasks

**Session Status:** ✅ First task complete (8 bare exception handlers fixed)  
**Date:** January 1, 2026

## Recommended Workflow

### ✅ Task 1: Fix Bare Exception Handlers (COMPLETED)
- **File:** server/extractor/metadata_engine.py
- **Scope:** 8 bare `except: pass` blocks
- **Status:** ✅ DONE - Tested & verified
- **Documentation:** TASK_FIX_BARE_EXCEPTION_HANDLERS_COMPLETED.md

---

## 🎯 Task 2: Clean Orphaned TODO Logging Comments (READY TO START)
- **Files:** 10 modules, 30 locations
- **Scope:** Replace "pass  # TODO: Consider logging" with actual logging
- **Effort:** 45-60 minutes
- **Impact:** Medium (removes misleading TODOs, improves debuggability)
- **Status:** ⏳ Ready to start

### Key Files (by priority):
1. **scientific_medical.py** - 8 locations (FITS/DICOM extraction)
2. **dicom_medical.py** - 11 locations (Medical imaging)
3. **audio_codec_details.py** - 3 locations (Audio extraction)
4. **Other modules** - 8 locations (icc_profile, geocoding, etc.)

### Example Fix:
```python
# Before:
except ValueError as e:
    pass  # TODO: Consider logging: logger.debug(f'Handled exception: {e}')

# After:
except ValueError as e:
    logger.debug(f"Failed to parse audio frame: {e}")
```

**Documentation:** TASK_CLEAN_ORPHANED_TODO_LOGGING.md

---

## 📋 Task 3: Implement Stub Modules (HIGH IMPACT - FUTURE)
- **Scope:** Multiple scientific DICOM/FITS modules with TODO stubs
- **Examples:** scientific_dicom_fits_ultimate_advanced_extension_clii.py, etc.
- **Status:** 15+ modules identified
- **Effort:** High (each needs real extraction logic)
- **Impact:** HIGH (completes metadata field coverage)

**Note:** These have placeholder functions that don't extract real data. Implementing would significantly increase metadata extraction capability.

---

## 🎨 Task 4: Complete Theme Toggle Feature (LOW PRIORITY)
- **File:** docs/THEME_TOGGLE_IMPLEMENTATION.md
- **Status:** Needs manual testing
- **Effort:** Low
- **Impact:** Low (frontend feature, not core extraction)
- **Next Steps:**
  1. Test theme switching in browser
  2. Verify light mode styles
  3. Test accessibility with screen readers

---

## 🔍 Task 5: Watchdog Module Fallback (MEDIUM PRIORITY)
- **File:** server/extractor/module_discovery.py
- **Status:** Has fallback when watchdog not installed
- **Effort:** Low-Medium
- **Impact:** Medium (file watching capability)
- **Next Steps:** Verify file watching works properly without watchdog

---

## Priority Matrix

```
           Low Effort     High Effort
High Impact   Task 2        Task 3
              (45-60min)    (2-4 hours)

Low Impact    Task 4, 5     (none)
              (1-2 hours)
```

## Recommendation

**Do Task 2 next** because:
- ✅ Same pattern as Task 1 (builds momentum)
- ✅ Medium effort (reasonable time commitment)
- ✅ Medium-high impact (removes 30 misleading TODOs)
- ✅ Completes exception handling cleanup across codebase
- ✅ Improves code maintainability
- ✅ Clear success criteria

---

## Quick Reference

### To Get Started on Task 2:

1. **Read the task definition:**
   ```
   /Users/pranay/Projects/metaextract/TASK_CLEAN_ORPHANED_TODO_LOGGING.md
   ```

2. **Key locations (30 total):**
   - scientific_medical.py: 8 locations
   - dicom_medical.py: 11 locations  
   - audio_codec_details.py: 3 locations
   - Others: 8 locations

3. **General pattern:**
   - Find: `pass  # TODO: Consider logging`
   - Replace with: `logger.debug(f"Failed to [operation]: {e}")`
   - Context determines exact message

4. **Test after:**
   ```bash
   python3 -m py_compile server/extractor/modules/*.py
   pytest tests/ -v
   ```

---

## Session Progress

| Task | Status | When | Duration | Impact |
|------|--------|------|----------|--------|
| 1. Fix bare exceptions | ✅ DONE | Just now | ~45 min | HIGH |
| 2. Clean TODO logging | ⏳ READY | Next | ~45-60 min | MEDIUM |
| 3. Implement stubs | 📋 PLANNED | Later | 2-4 hours | HIGH |
| 4. Theme toggle | 📋 PLANNED | Future | ~30 min | LOW |
| 5. Watchdog module | 📋 PLANNED | Future | ~30 min | MEDIUM |

---

## Key Documents

- **AGENTS.md** - Development guidelines (daily reference)
- **SESSION_IMPROVEMENTS_SUMMARY.md** - Session overview
- **TASK_CLEAN_ORPHANED_TODO_LOGGING.md** - Next task (detailed)
- **COMPLETED_IMPROVEMENTS.md** - Session results summary

---

## Quality Assurance

Each task maintains:
- ✅ Zero breaking changes
- ✅ 100% backward compatibility
- ✅ All tests passing
- ✅ Full documentation
- ✅ Clear success criteria
- ✅ Low deployment risk

---

**Ready to continue? Start with Task 2 above.**
