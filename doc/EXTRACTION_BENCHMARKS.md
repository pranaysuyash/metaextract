# MetaExtract Extraction Benchmarks (Updated)

**Version:** 4.0.1  
**Date:** January 19, 2026  
**Test Environment:** MacBook Pro M3 Pro, 18GB RAM, Python 3.11

---

## Executive Summary

This document provides **verified benchmarks** for MetaExtract's image extraction capabilities, based on actual sample files in `test-data/`.

**Key Finding:** The previous benchmark values were estimates. This document updates with measured values from actual extraction runs.

---

## Benchmark System

### Running Benchmarks

```bash
# Run extraction benchmarks
python benchmarks/run_benchmark.py --iterations 5

# Results output:
# - JSON: benchmarks/results/benchmark_<timestamp>.json
# - Markdown: benchmarks/results/benchmark_<timestamp>.md
```

### Current Sample Files

| File                          | Size  | Format    | Status   |
| ----------------------------- | ----- | --------- | -------- |
| `test-data/test_jpg.jpg`      | 821 B | JPEG      | ✓ Tested |
| `test-data/test_png.png`      | 313 B | PNG       | ✓ Tested |
| `test-data/test_webp.webp`    | 82 B  | WebP      | ✓ Tested |
| `test-data/test_tiff.tiff`    | 6 KB  | TIFF      | ✓ Tested |
| `test-data/test_dng.dng`      | 6 KB  | DNG (RAW) | ✓ Tested |
| `test-data/test_minimal.psd`  | 43 B  | PSD       | ✓ Tested |
| `test-data/test_cr3.cr3`      | 24 B  | CR3 (RAW) | ✓ Tested |
| `test-data/test_fits.fits`    | 3 KB  | FITS      | ✓ Tested |
| `test-data/test_minimal.exr`  | 9 B   | OpenEXR   | ✓ Tested |
| `test-data/test_minimal.heic` | 24 B  | HEIC      | ✓ Tested |

---

## Measured Benchmarks (January 19, 2026)

### Standard Images (Measured)

| Format | Avg Time | Raw EXIF Tags | Credits | Notes                       |
| ------ | -------- | ------------- | ------- | --------------------------- |
| JPEG   | 83.65ms  | 24            | 1       | Minimal synthetic test file |
| PNG    | 80.82ms  | 21            | 1       | Minimal synthetic test file |
| WebP   | 82.15ms  | 19            | 1       | Minimal synthetic test file |

### Professional Formats (Measured)

| Format | Avg Time | Raw EXIF Tags | Credits | Notes             |
| ------ | -------- | ------------- | ------- | ----------------- |
| TIFF   | 79.47ms  | 25            | 1       | 64x32px synthetic |
| DNG    | 78.66ms  | 25            | 1       | 64x32px synthetic |
| PSD    | 80.94ms  | 19            | 1       | 1x1px minimal     |

### RAW Camera Formats (Measured)

| Format | Avg Time | Raw EXIF Tags | Credits | Notes               |
| ------ | -------- | ------------- | ------- | ------------------- |
| CR3    | 99.81ms  | 15            | 1       | Minimal header only |

### Scientific Formats (Measured)

| Format | Avg Time | Raw EXIF Tags | Credits | Notes             |
| ------ | -------- | ------------- | ------- | ----------------- |
| FITS   | 95.06ms  | 16            | 1       | Minimal synthetic |
| EXR    | 79.78ms  | 14            | 1       | Minimal synthetic |

### Modern Formats (Measured)

| Format | Avg Time | Raw EXIF Tags | Credits | Notes               |
| ------ | -------- | ------------- | ------- | ------------------- |
| HEIC   | 92.69ms  | 15            | 1       | Minimal header only |

---

## Summary Statistics

| Metric             | Value         |
| ------------------ | ------------- |
| Total Files Tested | 10            |
| Average Time       | 85.3ms        |
| Min Time           | 78.66ms (DNG) |
| Max Time           | 99.81ms (CR3) |
| Total Credits      | 10            |
| Average Credits    | 1.0           |

**Note:** Current test files are minimal/synthetic. Real-world files with full metadata will show higher field counts and potentially longer extraction times.

---

## Credit Consumption System

### Credit Schedule

```
Total Credits = Base (1) + MP Bucket (0/1/3/7) + Features
```

| Component | Credits | Description                  |
| --------- | ------- | ---------------------------- |
| Base      | 1       | Standard metadata extraction |
| Embedding | +3      | Vector generation            |
| OCR       | +5      | Text recognition             |
| Forensics | +4      | Manipulation detection       |

### MP Bucket Pricing

| Bucket   | Max MP | Credits |
| -------- | ------ | ------- |
| standard | ≤12    | 0       |
| large    | ≤24    | 1       |
| xl       | ≤48    | 3       |
| xxl      | >48    | 7       |

### Credit Examples

| File Type       | Size   | Features     | Credits |
| --------------- | ------ | ------------ | ------- |
| JPEG (standard) | 2 MB   | Base only    | 1       |
| JPEG (high-res) | 20 MB  | Base only    | 2       |
| HEIC + OCR      | 5 MB   | Base + OCR   | 6       |
| RAW + Forensics | 30 MB  | All features | 11      |
| DICOM (medical) | 50 MB  | Base only    | 4       |
| 100MP TIFF      | 200 MB | All features | 20      |

---

## Supported Image Types

### Standard Formats (Web/Consumer)

- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- WebP (`.webp`)
- GIF (`.gif`)
- BMP (`.bmp`)
- AVIF (`.avif`)
- JPEG XL (`.jxl`)
- JPEG 2000 (`.jp2`, `.j2k`)

### Professional Formats

- TIFF/IF (`.tiff`, `.tif`)
- PSD/PSB (`.psd`, `.psb`)
- OpenEXR (`.exr`)
- DDS (`.dds`)
- TGA (`.tga`)
- HDR/RGBE (`.hdr`)

### RAW Camera Formats

| Brand      | Extensions     |
| ---------- | -------------- |
| Canon      | `.cr2`, `.cr3` |
| Nikon      | `.nef`, `.nrw` |
| Sony       | `.arw`, `.sr2` |
| Adobe      | `.dng`         |
| Olympus    | `.orf`         |
| Fujifilm   | `.raf`         |
| Pentax     | `.pef`         |
| Sigma      | `.x3f`         |
| Samsung    | `.srw`         |
| Panasonic  | `.rw2`         |
| Leica      | `.rwl`         |
| Hasselblad | `.3fr`         |
| Phase One  | `.iiq`         |

### Scientific/Medical

- FITS (`.fits`, `.fit`, `.fts`)
- DICOM (`.dcm`, `.dicom`)
- NIfTI (`.nii`, `.nii.gz`)

### Vector/Icon

- SVG (`.svg`, `.svgz`)
- ICO (`.ico`)
- ICNS (`.icns`)

---

## Field Categories by Format

### Standard Images (95-320 fields)

- Basic properties (8 fields)
- EXIF standard (37 fields)
- IPTC standard (13 fields)
- XMP namespaces (10 fields)
- ICC profiles (8 fields)

### RAW Camera (800-2,400 fields)

All standard fields PLUS:

- Camera settings (focus, drive mode, AF area)
- Lens data (min/max aperture, extension)
- Color science (matrix, calibration)
- MakerNotes (proprietary data)
- Image quality (compression, color depth)

### Scientific/Medical (1,500-5,000 fields)

**DICOM Fields:**

- Patient info (name, ID, demographics)
- Study/series metadata (UID, dates)
- Image properties (pixel spacing, windowing)
- Equipment info (manufacturer, model)

**FITS Fields:**

- Header keywords (SIMPLE, BITPIX, NAXIS)
- WCS coordinates (CRPIX, CDELT, CTYPE)
- Observation data (telescope, observer)

---

## Known Limitations

1. **Test files are minimal/synthetic** - lack real-world metadata
2. **Small file sizes** (most < 10 KB) - not representative
3. **Missing full RAW samples** - CR3/NEF are header-only
4. **No real HEIC** - test file lacks image data

### Recommended Sample Additions

| Category       | Source         | Target Size |
| -------------- | -------------- | ----------- |
| JPEG (high-MP) | Camera export  | 15-25 MB    |
| RAW (Canon)    | CR3 from 5D/1D | 25-40 MB    |
| RAW (Nikon)    | NEF from D850  | 40-55 MB    |
| HEIC (iPhone)  | iPhone Pro Max | 3-8 MB      |
| DICOM (CT)     | Public dataset | 50-500 MB   |
| FITS (astro)   | ESO/HST        | 10-100 MB   |

---

## Benchmark Files

- **Runner:** `benchmarks/run_benchmark.py`
- **Results:** `benchmarks/results/benchmark_*.json`
- **Reports:** `benchmarks/results/benchmark_*.md`
- **Specification:** `doc/IMAGE_BENCHMARK_SPECIFICATION.md`

---

## CTO Summary

**Ready for MVP Deployment:** Yes

- ✓ Credit system properly mapped (base + features + size)
- ✓ 39+ image formats supported
- ✓ Benchmark runner implemented and tested
- ⚠️ Real-world performance may vary (test files are minimal)
- ⚠️ Recommend acquiring production sample files before launch

**Credit Consumption Verified:**

- Base extraction: 1 credit
- Size buckets: 0/1/3/7 credits
- Features: embedding (3), OCR (5), forensics (4)
- Maximum per image: 20 credits
