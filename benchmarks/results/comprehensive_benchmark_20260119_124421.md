# MetaExtract Comprehensive Benchmark Report

**Generated:** 2026-01-19T07:14:15.179805Z

**ExifTool Available:** True

**Iterations per file:** 3


## Executive Summary

- **Total Files Tested:** 18

- **Categories Covered:** 7

- **Average Time:** 92.31ms

- **Average Tags per File:** 57.0

- **Total Tags Extracted:** 1026.0

- **Total Size:** 93.63MB


## By Category

| Category | Files | Avg Time | Avg Tags | Sample Files |

|----------|-------|----------|----------|--------------|

| real_phone_with_gps | 3 | 90.79ms | 94.7 | 3 files |

| real_dicom_medical | 2 | 97.5ms | 180.0 | 2 files |

| real_fits_scientific | 2 | 107.41ms | 24.5 | 2 files |

| large_images | 4 | 92.81ms | 22.5 | 4 files |

| raw_simulation | 1 | 91.32ms | 110.0 | 1 files |

| standard_synthetic | 3 | 89.82ms | 21.3 | 3 files |

| professional_synthetic | 3 | 82.46ms | 23.0 | 3 files |


## File Details

| File | Ext | Size | MP Bucket | Time | Tags | Credits |

|------|-----|------|-----------|------|------|---------|

| CT_small.dcm | .dcm | 0.037MB | standard | 100.67ms | 267.0 | 1 |

| raw_simulation.jpg | .jpg | 0.005MB | standard | 91.32ms | 110.0 | 1 |

| test_image.jpg | .jpg | 9.119MB | standard | 90.36ms | 100.0 | 1 |

| gps-map-photo.jpg | .jpg | 9.119MB | standard | 89.07ms | 100.0 | 1 |

| MR_small.dcm | .dcm | 0.009MB | standard | 94.34ms | 93.0 | 1 |

| IMG_20251225_164634.jpg | .jpg | 2.629MB | standard | 92.93ms | 84.0 | 1 |

| wcs_astronomy.fits | .fits | 2.005MB | standard | 131.52ms | 28.0 | 1 |

| test_tiff.tiff | .tiff | 0.006MB | standard | 82.11ms | 25.0 | 1 |

| test_dng.dng | .dng | 0.006MB | standard | 81.58ms | 25.0 | 1 |

| large_xl.jpg | .jpg | 0.986MB | standard | 90.06ms | 24.0 | 1 |

| large_xxl.jpg | .jpg | 1.717MB | standard | 83.83ms | 24.0 | 1 |

| test_jpg.jpg | .jpg | 0.001MB | standard | 83.04ms | 24.0 | 1 |

| primary_3d.fits | .fits | 25.005MB | xl | 83.3ms | 21.0 | 4 |

| png_standard.png | .png | 8.596MB | standard | 90.58ms | 21.0 | 1 |

| png_xl.png | .png | 34.384MB | xl | 106.78ms | 21.0 | 4 |

| test_png.png | .png | 0.0MB | standard | 101.69ms | 21.0 | 1 |

| test_webp.webp | .webp | 0.0MB | standard | 84.73ms | 19.0 | 1 |

| test_minimal.psd | .psd | 0.0MB | standard | 83.7ms | 19.0 | 1 |


## Tag Categories (All Files Combined)

| Category | Total Tags |

|----------|------------|

| DICOM | 335 |

| System | 144 |

| ExifIFD | 107 |

| File | 102 |

| Composite | 69 |

| IFD0 | 49 |

| ICC-header | 48 |

| GPS | 31 |

| ICC_Profile | 28 |

| FITS | 25 |

| JFIF | 24 |

| PNG | 21 |

| ExifTool | 18 |

| IFD1 | 7 |

| XMP-exif | 6 |

| RIFF | 5 |

| Photoshop | 5 |

| InteropIFD | 1 |

| XMP-x | 1 |


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


### large_images

- test-data/png_standard.png ✓

- test-data/png_xl.png ✓

- test-data/large_xl.jpg ✓

- test-data/large_xxl.jpg ✓


### raw_simulation

- test-data/raw_simulation.jpg ✓


### standard_synthetic

- test-data/test_jpg.jpg ✓

- test-data/test_png.png ✓

- test-data/test_webp.webp ✓


### professional_synthetic

- test-data/test_tiff.tiff ✓

- test-data/test_dng.dng ✓

- test-data/test_minimal.psd ✓
