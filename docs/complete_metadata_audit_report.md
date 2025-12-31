# MetaExtract Field Inventory – Extended Audit (Draft)

Last updated: 2025‑12‑30

**Target:** From a comprehensive field universe to roughly **65,000+ fields** when fully expanded across image, video, audio, document, scientific, forensic, and web metadata.

## 0. Overview

Current inventory (~12,586 fields in reality vs simulated 70k) needs alignment with real standards.
Real Standards Universe:

- Full EXIF + MakerNotes for major vendors.
- DICOM standard tags plus key private tags.
- Complete ID3v2 + other audio tag families.
- PDF/Office/EPUB document structures.
- Scientific formats (FITS, GeoTIFF, HDF5, NetCDF, LAS).
- Forensic/network/email headers (HTTP, TCP/IP, DNS, MIME).

## 1. Image Metadata

### 1.1 EXIF & MakerNotes

**Gap:** MakerNotes are the biggest missing piece.
**Targets:**

- **Canon MakerNotes:** 1,400+ (Mostly done)
- **Nikon:** ~2,000 tags
- **Sony/Fujifilm/Olympus/Panasonic/Pentax:** ~1,000+ each
- **Missing Vendors (High Priority):**
  - Leica
  - Hasselblad
  - Phase One
  - Sigma
  - Ricoh
  - DJI
  - GoPro

### 1.2 IPTC & XMP

**Targets:**

- IPTC: Raise to ~250–300 fields.
- XMP: Raise to 800–1,200+ (including Photoshop, Camera Raw, Rights namespaces).

### 1.3 Color & Computational

**Targets:**

- ICC Profiles: Hundreds of parameters.
- Smartphone Computational (Night mode, HDR, ProRAW): 600-800 fields.

## 2. Video Metadata

### 2.1 Containers & Codecs

**Targets:**

- **Containers (MP4, MKV, MXF):** 3,000–3,500 fields.
- **Codecs (H.264/5, AV1, ProRes):** 5,000+ fields (SPS/PPS, SEI, HDR).

### 2.2 Professional, HDR, VR

**Targets:**

- **Broadcast/Pro:** 6,000+ fields (MXF, HDR10, Dolby Vision, RAW Video, UAV).

## 3. Audio Metadata

### 3.1 ID3 & Tags

**Targets:**

- **ID3v2:** 2,000–2,500 fields (full frame set, chapters, private).
- **Pro Audio:** 1,000+ fields (BWF, RF64, Vorbis, APEv2).

## 4. Document & Text

### 4.1 PDF & Office

**Targets:**

- **PDF:** 3,000–4,000 fields (Annotations, AcroForms, Signatures).
- **Office/EPUB:** Rich OOXML properties.
- **Email/MIME:** 300+ fields (RFC registries).

## 5. Scientific & Technical

### 5.1 DICOM

**Targets:**

- **DICOM:** Real standard dictionary (thousands of tags) + Private tags.

### 5.2 FITS & Geospatial

**Targets:**

- **FITS/Astronomy:** 4,000+ fields.
- **Geospatial:** 3,000+ fields (GeoTIFF keys, Shapefile, CRS).

## 6. Forensic, Security, Network

**Targets:**

- **Network/Forensic:** High count via full Protocol headers (HTTP, DNS, TLS).
- **C2PA:** 400–600+ fields (Manifests, Assertions).

## 7. Social / Mobile / Web

**Targets:**

- **Social:** 1,500–2,000+ distinct fields across platforms.
- **Web:** 1,000–1,200+ fields (Schema.org, OpenGraph).

## Priority Implementation Order

**Immediate (Week 1-2) - High ROI**

- Fujifilm MakerNotes (+669 fields)
- Olympus MakerNotes (+595 fields)
- Panasonic MakerNotes (+509 fields)
- ID3v2 Complete
- **New Vendors:** Leica, Hasselblad, Phase One, Sigma, Ricoh.
