# MetaExtract Comprehensive Benchmark Report

**Generated:** 2026-01-19T06:09:09.258976Z

**ExifTool Available:** True

**Iterations per file:** 3


## Executive Summary

- **Total Files Tested:** 13

- **Categories Covered:** 5

- **Average Time:** 87.5ms

- **Average Tags per File:** 63.5

- **Total Tags Extracted:** 826.0

- **Total Size:** 47.94MB


## By Category

| Category | Files | Avg Time | Avg Tags | Sample Files |

|----------|-------|----------|----------|--------------|

| real_phone_with_gps | 3 | 90.86ms | 94.7 | 3 files |

| real_dicom_medical | 2 | 97.21ms | 180.0 | 2 files |

| real_fits_scientific | 2 | 85.19ms | 24.5 | 2 files |

| standard_synthetic | 3 | 83.69ms | 21.3 | 3 files |

| professional_synthetic | 3 | 83.01ms | 23.0 | 3 files |


## File Details

| File | Ext | Size | MP Bucket | Time | Tags | Credits |

|------|-----|------|-----------|------|------|---------|

| CT_small.dcm | .dcm | 0.037MB | standard | 99.12ms | 267.0 | 1 |

| test_image.jpg | .jpg | 9.119MB | standard | 92.07ms | 100.0 | 1 |

| gps-map-photo.jpg | .jpg | 9.119MB | standard | 90.95ms | 100.0 | 1 |

| MR_small.dcm | .dcm | 0.009MB | standard | 95.29ms | 93.0 | 1 |

| IMG_20251225_164634.jpg | .jpg | 2.629MB | standard | 89.56ms | 84.0 | 1 |

| wcs_astronomy.fits | .fits | 2.005MB | standard | 87.45ms | 28.0 | 1 |

| test_tiff.tiff | .tiff | 0.006MB | standard | 82.5ms | 25.0 | 1 |

| test_dng.dng | .dng | 0.006MB | standard | 83.04ms | 25.0 | 1 |

| test_jpg.jpg | .jpg | 0.001MB | standard | 81.53ms | 24.0 | 1 |

| primary_3d.fits | .fits | 25.005MB | xl | 82.93ms | 21.0 | 4 |

| test_png.png | .png | 0.0MB | standard | 84.05ms | 21.0 | 1 |

| test_webp.webp | .webp | 0.0MB | standard | 85.49ms | 19.0 | 1 |

| test_minimal.psd | .psd | 0.0MB | standard | 83.48ms | 19.0 | 1 |


## Tag Categories (All Files Combined)

| Category | Total Tags |

|----------|------------|

| DICOM | 335 |

| System | 104 |

| ExifIFD | 74 |

| File | 68 |

| ICC-header | 48 |

| Composite | 45 |

| IFD0 | 39 |

| ICC_Profile | 28 |

| FITS | 25 |

| ExifTool | 13 |

| JFIF | 12 |

| GPS | 10 |

| IFD1 | 7 |

| PNG | 7 |

| RIFF | 5 |

| Photoshop | 5 |

| InteropIFD | 1 |


## Credit Breakdown

| Feature | Credit Cost |

|---------|-------------|

| base | 1 |

| embedding | 3 |

| ocr | 5 |

| forensics | 4 |


## MP Bucket Pricing

| Bucket | Size Limit | Credits |

|--------|------------|---------|

| standard | 12 MP | 0 |

| large | 24 MP | 1 |

| xl | 48 MP | 3 |

| xxl | 96 MP | 7 |


## Files Used


### real_phone_with_gps

- tests/fixtures/test_image.jpg ✓

- tests/persona-files/sarah-phone-photos/IMG_20251225_164634.jpg ✓

- tests/persona-files/sarah-phone-photos/gps-map-photo.jpg ✓


### real_dicom_medical

- test-data/CT_small.dcm ✓

- test-data/MR_small.dcm ✓


### real_fits_scientific

- test-data/wcs_astronomy.fits ✓

- test-data/primary_3d.fits ✓


### standard_synthetic

- test-data/test_jpg.jpg ✓

- test-data/test_png.png ✓

- test-data/test_webp.webp ✓


### professional_synthetic

- test-data/test_tiff.tiff ✓

- test-data/test_dng.dng ✓

- test-data/test_minimal.psd ✓
