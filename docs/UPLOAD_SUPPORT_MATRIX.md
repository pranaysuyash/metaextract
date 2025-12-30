# Upload Support Matrix (UI vs Backend vs Extractor)

This answers: “does upload support DICOM/FITS/HDF5/NetCDF etc?”

## Summary

- **Frontend**: accepts many extensions (including `.dcm`, `.fits`, `.h5`, `.nc`) but hard-caps size at **100MB**.
- **Backend**: supports extraction for scientific formats via Python engine, but tier/type enforcement is **MIME-based** and the default tier currently behaves like **enterprise**.
- **Extractor**: `server/extractor/comprehensive_metadata_engine.py` contains extractors for DICOM/FITS/HDF5/NetCDF (dependencies in `requirements.txt`).

## Current Effective Behavior

Because `/api/extract` defaults `tier=enterprise` when omitted, most uploads succeed regardless of file type *as long as the frontend lets them through*.

## Support Table

| Category | Example extensions | Frontend upload cap | Backend tier allowlist | Extractor support | Notes |
|---|---|---:|---|---|---|
| Standard images | `.jpg .png .webp .tif` | 100MB | Free+ | Yes | Good baseline. |
| RAW images / HEIC | `.cr2 .nef .arw .dng .heic` | 100MB | Pro+ | Yes | Tiering depends on correct MIME/validation. |
| Video | `.mp4 .mov .mkv .webm .avi` | 100MB | Forensic+ | Yes | Real-world videos often exceed 100MB → UI blocks today. |
| Audio | `.mp3 .wav .flac .m4a` | 100MB | Forensic+ | Yes | Broadcast/WAV edge cases may exceed 100MB. |
| PDF | `.pdf` | 100MB | Forensic+ | Yes | Deeper PDF features depend on what’s enabled in the extractor modules. |
| DICOM (single file) | `.dcm .dicom` | 100MB | **Enterprise today** (allowlist doesn’t include DICOM) | Yes | A “study” is usually many files → needs batch/zip for real workflows. |
| FITS | `.fits .fit .fts` | 100MB | **Enterprise today** (allowlist doesn’t include FITS) | Yes | FITS are often small; WCS coverage needs real samples. |
| HDF5 | `.h5 .hdf5` | 100MB | **Enterprise today** (allowlist doesn’t include HDF5) | Yes | HDF5 files commonly exceed 100MB; recursion can be heavy. |
| NetCDF | `.nc .nc4` | 100MB | **Enterprise today** (allowlist doesn’t include NetCDF) | Yes | Same as HDF5; CF conventions vary widely. |

## What To Fix Before Launch (If you want scientific uploads as “supported”)

1. Decide which tiers allow scientific files (probably Forensic+ or Enterprise).
2. Add explicit MIME/extension handling on the backend (don’t rely on browser MIME).
3. Align max upload size across frontend+backend (or show per-tier limits in UI).

