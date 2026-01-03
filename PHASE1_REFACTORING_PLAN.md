# Phase 1 Refactoring Plan - Critical Issues

## Branch Information
- **Branch**: `phase1-refactoring-critical-issues`
- **Base**: `main` (as of 2026-01-03)
- **Goal**: Fix critical architectural issues while maintaining functionality

## Critical Issues to Address

### 1. Massive Engine Files (Priority 1)
**Target Files:**
- `server/extractor/comprehensive_metadata_engine.py` (3,492 lines)
- `server/extractor/metadata_engine.py` (2,039 lines)
- `server/extractor/metadata_engine_enhanced.py` (1,234 lines)

**Refactoring Strategy:**
```
server/extractor/
├── core/
│   ├── __init__.py
│   ├── base_engine.py              # Abstract base class
│   ├── orchestrator.py             # Main orchestration (300-400 lines)
│   └── extraction_context.py       # Context management
├── extractors/
│   ├── __init__.py
│   ├── image_extractor.py          # Image-specific logic
│   ├── video_extractor.py          # Video-specific logic
│   ├── audio_extractor.py          # Audio-specific logic
│   ├── document_extractor.py       # Document-specific logic
│   └── scientific_extractor.py     # Scientific formats (DICOM, FITS, etc.)
└── utils/
    ├── __init__.py
    ├── file_handler.py             # File operations
    └── result_formatter.py         # Result formatting
```

### 2. Extreme Code Duplication (Priority 2)
**Target Files:**
- `server/extractor/modules/makernotes_complete.py` (6,206 lines)
- `server/extractor/modules/vendor_makernotes.py` (1,066 lines)
- Multiple modules with duplicate vendor settings

**Refactoring Strategy:**
```
server/extractor/
├── data/
│   ├── __init__.py
│   ├── vendor_settings.py          # Centralized vendor data
│   ├── canon_makernotes.py         # Canon-specific data
│   ├── nikon_makernotes.py         # Nikon-specific data
│   ├── sony_makernotes.py          # Sony-specific data
│   └── other_vendors.py            # Other vendor data
├── parsers/
│   ├── __init__.py
│   ├── makernote_parser.py         # Unified parsing logic
│   └── vendor_specific_parsers.py  # Vendor-specific parsing
```

### 3. Inconsistent Error Handling (Priority 3)
**Target:** All extraction modules

**Refactoring Strategy:**
```
server/extractor/
├── exceptions/
│   ├── __init__.py
│   ├── extraction_exceptions.py    # Custom exception hierarchy
│   └── validation_exceptions.py    # Validation exceptions
├── utils/
│   ├── __init__.py
│   └── error_handler.py            # Standardized error processing
```

## Implementation Steps

### Step 1: Create New Directory Structure
1. Create `server/extractor/core/`
2. Create `server/extractor/extractors/`
3. Create `server/extractor/data/`
4. Create `server/extractor/parsers/`
5. Create `server/extractor/exceptions/`

### Step 2: Extract and Reorganize Code
1. **From comprehensive_metadata_engine.py:**
   - Extract image extraction logic → `extractors/image_extractor.py`
   - Extract video extraction logic → `extractors/video_extractor.py`
   - Extract audio extraction logic → `extractors/audio_extractor.py`
   - Extract orchestration logic → `core/orchestrator.py`

2. **From makernotes modules:**
   - Extract vendor data → `data/vendor_settings.py`
   - Extract parsing logic → `parsers/makernote_parser.py`

### Step 3: Implement Base Classes
1. Create `core/base_engine.py` with abstract methods
2. Create standardized error handling in `exceptions/`
3. Implement result formatting utilities

### Step 4: Update Imports and References
1. Update all import statements
2. Ensure backward compatibility
3. Add deprecation warnings for old imports

### Step 5: Testing and Validation
1. Run existing tests to ensure no regressions
2. Add unit tests for new modules
3. Integration testing with sample files

## Safety Measures

### 1. Backup Strategy
- All original files will be kept during refactoring
- New files will be created alongside old ones initially
- Gradual migration with fallback options

### 2. Compatibility Layer
- Maintain existing API signatures
- Add deprecation warnings for old methods
- Gradual migration path for consumers

### 3. Testing Protocol
```bash
# Before each major change:
1. Run full test suite: npm run test:ci && pytest tests/
2. Test with sample files to ensure functionality
3. Document any behavioral changes
4. Commit with descriptive messages
```

## Success Criteria

### Quantitative Metrics
- [ ] Reduce max file size from 6,206 to <500 lines
- [ ] Eliminate 80%+ of code duplication in vendor modules
- [ ] Achieve 100% standardized error handling
- [ ] Maintain 100% backward compatibility during transition

### Qualitative Metrics
- [ ] Improved code readability and maintainability
- [ ] Clear separation of concerns
- [ ] Consistent error handling patterns
- [ ] Better testability of individual components

## Rollback Plan

If critical issues arise:
1. **Immediate**: Revert to previous commit
2. **Short-term**: Switch back to main branch
3. **Long-term**: Fix forward with targeted patches

## Documentation

### Required Updates
- [ ] Update `AGENTS.md` with new architecture
- [ ] Document new module structure
- [ ] Update API documentation
- [ ] Add migration guide for developers

### Code Documentation
- [ ] Add docstrings to all new modules
- [ ] Document class hierarchies
- [ ] Add usage examples
- [ ] Update type annotations

## Timeline

- **Week 1**: Directory structure + Base classes
- **Week 2**: Extract image/video/audio extractors
- **Week 3**: Consolidate vendor data + parsers
- **Week 4**: Error handling + Testing + Documentation

## Daily Checkpoints

Each day will include:
1. Progress assessment against plan
2. Test execution to ensure no regressions
3. Documentation updates
4. Commit with detailed description
5. Risk assessment for next steps

---

**Next Steps:**
1. Create the new directory structure
2. Begin with `comprehensive_metadata_engine.py` extraction
3. Test after each major change
4. Document progress and any issues encountered