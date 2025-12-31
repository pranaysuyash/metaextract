# Ultimate Metadata Universe - All Domains

**Date**: 2025-12-30 (Updated with comprehensive research)
**Scope**: All possible metadata fields across media, documents, scientific data, forensic/security, and web/social domains
**Purpose**: Capture the full technical universe (tens of thousands of fields) beyond media-only coverage

---

## Summary

- **All-domain universe**: comprehensive set of possible metadata fields across standards and formats.
- **Media-only universe**: ~7,870 fields (see `METADATA_COMPLETE_UNIVERSE.md`).
- **All-domain expansion** adds document, scientific, forensic/security, and web/social metadata.

This document is a complete inventory reference, not an immediate implementation target.

---

## Domain Breakdown (Updated with Research)

### 1) Image Metadata (15,000+ fields)

- **EXIF Standard (Core)**: 1,200+ fields (basic EXIF, GPS subsystem, interoperability IFD, thumbnail data)
- **MakerNotes (Vendor-Specific)**: 7,000+ fields (Canon 1,200+, Nikon 950+, Sony 850+, Fuji 750+, Olympus 650+, Panasonic 550+, Pentax 450+, Leica 350+, Sigma 250+, Hasselblad 400+, Phase One 350+, Minolta/Konica 300+, Ricoh 250+, DJI 200+, GoPro 150+)
- **IPTC Standards**: 150+ fields (IPTC Core 50+, IPTC Extension 100+)
- **XMP Standards**: 500+ fields (Dublin Core 15+, XMP Basic 30+, XMP Media Management 25+, XMP Rights Management 20+, Adobe Specific 100+, PLUS License 50+, Custom Namespaces 250+)
- **Color Management**: 200+ fields (ICC Profiles 150+, Color Appearance Models 50+)
- **Smartphone/Computational Photography**: 300+ fields (iOS/iPhone 150+, Android/Google 100+, Samsung 50+, Huawei/Xiaomi 30+)

### 2) Video Metadata (8,000+ fields)

- **Container Formats**: 2,000+ fields (MP4/MOV 800+, MKV 600+, AVI 200+, WebM 150+, MXF 250+)
- **Codec-Specific**: 3,000+ fields (H.264/AVC 400+, H.265/HEVC 500+, VP9/AV1 300+, ProRes 250+, DNxHD/HR 200+, FFV1 150+, MPEG-2/4 300+)
- **Professional Video**: 3,000+ fields (Broadcast Standards 200+, Timecode & Synchronization 150+, Closed Captioning 100+, Audio Tracks 500+, Chapter Markers 50+, 3D/VR Video 300+, HDR Metadata 200+, Camera Raw Video 1,000+)

### 3) Audio Metadata (3,500+ fields)

- **ID3 Standards**: 1,200+ fields (ID3v1/v1.1 5 fields, ID3v2.2/v2.3/v2.4 1,195+ frames)
- **Other Audio Formats**: 2,300+ fields (Vorbis Comments 300+, APEv2 150+, MP4/iTunes 400+, WAV/RIFF 200+, AIFF/AIFC 150+, AAC/HE-AAC 300+, Opus 100+, DSD/DSF 50+, Professional Audio 650+)

### 4) Document Metadata (4,000+ fields)

- **PDF Standards**: 2,000+ fields (Basic PDF 50+, XMP in PDF 300+, AcroForms 200+, Annotations 150+, Bookmarks/Outlines 100+, Digital Signatures 50+, 3D Models 100+, Multimedia 150+, Accessibility 200+, Prepress/Printing 300+)
- **Office Documents**: 1,000+ fields (Microsoft Office OOXML 500+, OpenDocument Format 300+, Apple iWork 150+, LibreOffice 50+)
- **Text/Markup**: 1,000+ fields (HTML Metadata 200+, XML Namespaces 300+, Markdown Frontmatter 50+, Email Headers 150+, EPUB E-books 300+)

### 5) Scientific/Technical Metadata (15,000+ fields)

- **Medical Imaging (DICOM)**: 8,000+ fields (complete data dictionary with 7,999+ standard fields)
- **Astronomical Imaging (FITS)**: 3,000+ fields (FITS Standard 1,200+, World Coordinate System 200+, Telescope/Observatory 150+, Astronomy Visualization Metadata 100+, Spectral Data 300+, Time Series 200+, Mosaics/Multi-extension 150+, Calibration Frames 300+)
- **Geospatial/GIS**: 2,000+ fields (GeoTIFF 500+, Shapefile Metadata 200+, KML/KMZ 300+, EXIF GPS 50+, EXIF Geotagging 100+, Astronomical Position 200+)
- **Scientific Data Formats**: 2,000+ fields (HDF5/NetCDF 800+, Microscopy 400+, Spectroscopy 300+, Telemetry/Logging 200+, Chemical Data 150+, 3D/Point Cloud 350+)

### 6) Forensic/Security Metadata (2,500+ fields)

- **File System & OS**: 500+ fields (Windows NTFS 200+, macOS APFS/HFS+ 150+, Linux ext4/XFS 100+, File Timestamps 12 fields, File Permissions 50+)
- **Digital Signatures & Authentication**: 800+ fields (Code Signing 200+, Document Signatures 150+, Image Authentication 100+, Blockchain Provenance 200+, Watermarking 50+, Steganography 100+)
- **Network/Communication**: 700+ fields (Email Headers 150+, Web Headers 100+, TCP/IP Metadata 200+, DNS Records 150+, TLS/SSL 100+)
- **Device & Hardware**: 500+ fields (Device Identifiers 100+, Hardware Signatures 150+, Firmware Versions 100+, Peripheral Devices 150+)

### 7) Social/Mobile/Web Metadata (2,000+ fields)

- **Social Media Platforms**: 800+ fields (Instagram 200+, Facebook 150+, Twitter/X 100+, TikTok 150+, YouTube 200+)
- **Mobile Device Metadata**: 700+ fields (iOS/iPhone 300+, Android 250+, Windows Mobile 150+)
- **Web Standards**: 500+ fields (Open Graph Protocol 50+, Twitter Cards 30+, Schema.org 300+, Web Manifest 50+, Service Workers 30+, Progressive Web Apps 40+)

---

## Implementation Implications

- **Multiple specialized engines** required (DICOM, FITS, GIS, HDF5, OCR).
- **Performance/storage**: full extraction can be orders of magnitude larger than media-only.
- **Compliance**: medical and personal data requires strict handling (PHI/PII).
- **Operational cost**: high compute/memory demands for large scientific formats.

---

## Coverage Strategy (High-Level)

- **Media-first** (Phases 1-6): image/video/audio depth with IPTC/XMP/codec and MakerNotes.
- **Documents**: PDF + Office + HTML metadata.
- **Scientific/Medical**: DICOM + FITS + GIS + HDF5.
- **Forensic/Security**: signatures, C2PA/JUMBF, filesystem provenance.
- **Web/Social**: platform-specific metadata ingestion.

This strategy is reflected in the expanded roadmap phases.

---

## Research Validation

**External Research Findings** (2025 comprehensive analysis):

- **Total Universe**: a comprehensive inventory (tens of thousands of fields) across all domains and standards
- **Technical Reality**: No single tool can extract all fields due to performance, complexity, and legal constraints
- **Practical Maximum**: 10,000-15,000 fields (ExifTool with all plugins)
- **Consumer Tools**: 50-500 fields (Adobe Lightroom, Google Photos)
- **Professional Tools**: 500-1,500 fields (PhotoMechanic, Capture One)
- **Forensic Tools**: 1,000-3,000 fields (Amped FIVE, Cellebrite)
- **Scientific Tools**: 2,000-5,000 fields (FITS Liberator, OsiriX DICOM)

**Competitive Advantage Focus**:

- Quality of extraction (accuracy, completeness)
- Contextual analysis (relationships between fields)
- Forensic reliability (court-admissible results)
- User experience (making complex data understandable)
- Performance (fast analysis of critical fields)
