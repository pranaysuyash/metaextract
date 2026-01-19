# MetaExtract Benchmark Coverage - Blocking Issues

**Date:** January 19, 2026  
**Status:** 🚫 BLOCKER - MVP NOT READY  
**Purpose:** Document all gaps preventing launch

---

## Executive Summary

**The current benchmark system does NOT provide confidence for launch.**

Critical gaps:

- No real RAW camera files (18 formats claimed, 0 tested)
- No DICOM medical files (claimed)
- No comprehensive FITS files (1,500+ fields claimed, 16 tested)
- No files with full XMP/IPTC metadata
- Credit consumption not verified against actual extraction work

---

## Format Coverage Analysis

### Claimed vs Tested

| Format Group    | Claimed Support | Tested          | Coverage |
| --------------- | --------------- | --------------- | -------- |
| Standard Images | 8 formats       | 3               | 37%      |
| RAW Camera      | 18 formats      | 1 (header only) | 0%       |
| Professional    | 7 formats       | 2               | 28%      |
| Scientific      | 3 formats       | 2               | 66%      |
| Vector/Icon     | 3 formats       | 0               | 0%       |
| **Total**       | **39+ formats** | **10**          | **26%**  |

### Field Coverage Gap

| Format | Claimed Fields | Tested Fields | Gap |
| ------ | -------------- | ------------- | --- |
| JPEG   | 95-320         | 100 (best)    | 31% |
| RAW    | 800-2,400      | 15            | <1% |
| TIFF   | 150-500        | 25            | 5%  |
| FITS   | 1,500-3,000    | 16            | <1% |
| DICOM  | 2,500-4,500    | 0             | 0%  |

---

## Missing Test Files

### Critical (Blocking Launch)

1. **RAW Camera Files** - 18 formats claimed
   - Canon CR2/CR3 with full EXIF, MakerNotes
   - Nikon NEF with focus data, AF points
   - Sony ARW with proprietary data
   - Adobe DNG with linearization data

2. **Medical DICOM** - Claims 2,500-4,500 fields
   - Patient demographics
   - Study/series metadata
   - Image pixel data
   - Equipment info

3. **Scientific FITS** - Claims 1,500+ fields
   - WCS coordinates
   - Observation metadata
   - Telescope parameters

### High Priority

4. **Professional TIFF/PSD** - Claims 150-500 fields
   - Layer info
   - Color profiles
   - Resolution data

5. **Files with Full XMP/IPTC**
   - Caption, keywords, byline
   - Copyright, credit, source
   - Location data

---

## Credit System Verification

### What We Verified

| Feature             | Status | Notes          |
| ------------------- | ------ | -------------- |
| Base credit (1)     | ✅     | Always charged |
| MP bucket (0/1/3/7) | ✅     | Size-based     |
| OCR (+5)            | ❌     | Not tested     |
| Embedding (+3)      | ❌     | Not tested     |
| Forensics (+4)      | ❌     | Not tested     |

### Critical Missing Verification

1. **Does OCR actually add 5 credits worth of work?**
   - Need to measure Tesseract processing time
   - Verify field extraction from OCR

2. **Does embedding actually add 3 credits worth of work?**
   - Need to measure vector generation
   - Verify embedding quality

3. **Does forensics actually add 4 credits worth of work?**
   - Need to measure manipulation detection
   - Verify detection accuracy

---

## Action Plan to Remove Blocker

### Phase 1: Acquire Real Test Files (Day 1)

| Format    | Source        | Action                         |
| --------- | ------------- | ------------------------------ |
| RAW (CR3) | Canon samples | Download official test files   |
| RAW (NEF) | Nikon samples | Download official test files   |
| RAW (ARW) | Sony samples  | Download official test files   |
| DICOM     | NIH NCI       | Download sample datasets       |
| FITS      | ESO HST       | Download public astronomy data |

### Phase 2: Create Comprehensive Synthetic Files (Day 2)

For formats where real files unavailable:

- Create files with EXIFTool using `-exiftool -all= ` to embed known tags
- Include GPS, camera, IPTC, XMP data
- Include ICC profiles
- Include MakerNotes data

### Phase 3: Verify Credit Consumption (Day 3)

| Feature         | Test Method                | Pass Criteria                  |
| --------------- | -------------------------- | ------------------------------ |
| Base extraction | Time extraction            | < 100ms for standard           |
| OCR             | Add text to image, extract | Text detected                  |
| Embedding       | Generate vector            | Vector exists, valid dimension |
| Forensics       | Add manipulation, detect   | Manipulation flagged           |

### Phase 4: Re-run Full Benchmark (Day 4)

Run comprehensive benchmark suite:

- All 39+ formats
- All credit combinations
- Field count verification
- Performance baselines

---

## Files to Create

```
benchmarks/
├── sample-files/
│   ├── standard/
│   │   ├── jpeg/ (10 files with varying metadata)
│   │   ├── png/
│   │   └── webp/
│   ├── raw/
│   │   ├── canon/
│   │   ├── nikon/
│   │   ├── sony/
│   │   └── adobe/
│   ├── professional/
│   │   ├── tiff/
│   │   ├── psd/
│   │   └── exr/
│   ├── scientific/
│   │   ├── fits/
│   │   └── dicom/
│   └── medical/
│       └── dicom/
├── run_benchmark.py (enhanced)
├── verify_credits.py (new)
└── expected_fields.json (new - expected fields per format)
```

---

## CTO Decision Required

**Current Status:** 🚫 NOT READY FOR LAUNCH

**To Remove Blocker:**

1. ☐ Acquire real RAW camera files (Canon, Nikon, Sony)
2. ☐ Acquire medical DICOM samples
3. ☐ Acquire scientific FITS samples
4. ☐ Create comprehensive synthetic files where needed
5. ☐ Verify credit consumption for all features
6. ☐ Re-run benchmarks with full coverage
7. ☐ Document all field extractions
8. ☐ Verify 39+ formats actually work
9. ☐ Confirm field counts match claims

**Estimated Time:** 4-5 days

---

## Conclusion

The current benchmark system is **insufficient for launch**. We cannot claim:

- "45,000+ metadata fields" when we only test 32 per file on average
- "531 Python modules" when we don't verify they all work
- "39+ formats" when we only test 10
- Correct credit consumption when features aren't tested

**Recommendation:** Pause MVP launch until benchmark coverage is complete.
