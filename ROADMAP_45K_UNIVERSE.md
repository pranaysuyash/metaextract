# MetaExtract: 45k Universe Roadmap (Phase-Based Strategy)

## Overview

The technical universe of metadata contains **45,000+ possible fields** across all standards, formats, and domains. This roadmap provides a **phased, practical strategy** to scale MetaExtract toward a competitive 10,000-15,000 field extraction engine while maintaining:

- **Performance**: Sub-second analysis of critical fields
- **Safety**: Allowlisting, PII/PHI redaction, no sensitive data retention
- **Reliability**: Court-admissible forensic results
- **Usability**: Clear, actionable output for analysts

---

## Current State (Dec 30, 2025)

| Component              | Count | Target        | Progress              |
| ---------------------- | ----- | ------------- | --------------------- |
| **Implemented**        | 2,899 | 7,000         | 41.4%                 |
| **Phase 1 (Done)**     | +632  | —             | ✅ C2PA + ExifTool    |
| **Phase 2-3 (Next)**   | TBD   | +2,000-3,000  | 🔄 Media + Docs       |
| **Phase 4 (Optional)** | TBD   | +1,000-2,000  | ⏳ Scientific (gated) |
| **Competitive Target** | —     | 10,000-15,000 | —                     |

---

## Phased Roadmap

### ✅ Image Metadata Deep Dive (Active)

See `docs/IMAGE_METADATA_ROADMAP.md` for the detailed plan and status on EXIF/IFD, MakerNotes, IPTC/XMP, ICC, and mobile/computational metadata.

### ✅ Phase 1: Forensic Foundation (COMPLETE - Dec 30)

**Objective**: Deep forensic capabilities + content authenticity

**Delivered**:

- Forensic metadata expansion: Filesystem, device, network, email, signatures
- C2PA/JUMBF box parsing for content authenticity
- ExifTool-based MakerNote allowlist (Canon, Nikon, Sony, Fuji, Olympus, etc.)
- Field count: 2,267 → **2,899** (+632 fields)

**Modules**:

```
✅ forensic_metadata.py (253 fields)
   - Filesystem: timestamps, permissions, hashes, entropy
   - Device: identifiers, firmware, serial numbers
   - Network: IP, DNS, WiFi, VPN, firewall status
   - Email: headers, authentication, attachments
   - Digital signatures: C2PA, Adobe CC, code signing, blockchain

✅ c2pa_adobe_cc.py (30 fields)
   - JUMBF box detection
   - C2PA manifest parsing
   - Adobe Content Credentials extraction
   - Allowlisted fields (manifest_version, claim_generator, signature_valid, etc.)

✅ makernote_exiftool.py (111 fields)
   - ExifTool integration with allowlist
   - 8+ camera manufacturers supported
   - Safe field filtering (excludes firmware, secrets, passwords)
   - Per-camera field estimation
```

**Key Achievement**: **Expanded forensic from 35 → 253 fields** (7x improvement)

---

### 🔄 Phase 2: Media Depth (Next Sprint - Est. +1,200-1,800 fields)

**Objective**: Comprehensive video, audio, and codec-specific metadata

**Planned Modules**:

#### 2.1 Video Codec Extraction (~400-600 fields)

```python
# server/extractor/modules/video_codec_details.py
- H.264/AVC: SPS/PPS parameters, profile, level, entropy coding, ref frames
- H.265/HEVC: VPS/SPS/PPS, CTU size, transform hierarchy, SAO, RDOQ
- VP9/AV1: Frame headers, transform blocks, prediction modes
- Codec profiles, levels, tiers, frame types, motion vectors
- Estimated: 400-600 fields
```

**Implementation**:

- Parse ffprobe codec_long_name into structured fields
- Extract SPS/PPS/VPS payloads (binary parsing)
- HDR10/Dolby Vision detection (transfer characteristics)
- VR/360 video metadata (equirectangular, cubemap, projection)

#### 2.2 Container Metadata (~300-400 fields)

```python
# server/extractor/modules/container_metadata.py
- MP4/MOV: atom enumeration (ftyp, mvhd, stsd, stts, stsc, stco, stss)
- MKV: EBML segment info, track properties, tags, chapters
- AVI: RIFF chunks, stream headers, index tables
- WebM: EBML elements (duration, muxing app, writing app)
- Estimated: 300-400 fields
```

**Implementation**:

- Atom/box parsing via binary offset walking
- ffprobe JSON enrichment (already partially done)
- Track count, duration, bitrate per stream
- Chapter/cue point enumeration

#### 2.3 Audio Codec Deep Dive (~200-300 fields)

```python
# server/extractor/modules/audio_codec_details.py
- MP3: LAME version, VBR method, quality, encoder delay, gain
- AAC: Profile (AAC-LC, HE-AAC, HE-AACv2), SBR, PS, frame length
- FLAC: Frame info, MD5, block sizes, sample rates
- Opus: Header data, channel mapping, pre-skip, gain
- Vorbis: Channel count, sample rate, bitrate, vendor string
- Estimated: 200-300 fields
```

**Implementation**:

- Parse bitstream headers (binary format)
- Mutagen library enhancements
- ID3 v2.4 frame parsing (already 75 fields, expand to 150+)

#### 2.4 RAW Format Metadata (~150-250 fields)

```python
# server/extractor/modules/raw_formats.py
- DNG: 40+ fields (color matrix, baseline exposure, CFA, white level)
- Canon CR2/CR3: 20+ fields (make/model specific)
- Nikon NEF: 20+ fields (lens, focus info)
- Sony ARW: 15+ fields (camera settings)
- Fujifilm RAF: 15+ fields (film simulation, dynamic range)
- Estimated: 150-250 fields
```

**Implementation**:

- ExifTool passthrough for RAW headers
- TIFF/BigTIFF parsing for DNG tags
- Selective allowlist (avoid proprietary compression keys)

#### 2.5 HDR & Advanced Video (~100-200 fields)

```python
# server/extractor/modules/hdr_metadata.py
- HDR10: MaxCLL, MaxFALL, mastering display primaries
- Dolby Vision: Profile, level, version, dynamic metadata
- HLG: Nominal peak luminance
- VR/360: Spherical metadata, projection type, initial view orientation
- Timecode: SMPTE timecode, drop-frame, user bits
- Closed captions: CEA-608/708 detection
- Estimated: 100-200 fields
```

**Phase 2 Total**: **+1,200-1,800 fields** → **4,100-4,700 cumulative**

---

### 📋 Phase 3: Documents & Web (Est. +800-1,200 fields)

**Objective**: PDF, Office documents, and web metadata standards

#### 3.1 PDF Deep Dive (~400-500 fields)

```python
# server/extractor/modules/pdf_metadata_complete.py
- Basic metadata: Author, Title, Subject, Keywords, Creator, Producer
- XMP packets: Full XMP namespace extraction
- Annotations: Highlight, underline, comment counts and types
- Forms: AcroForm field enumeration, validation rules
- Bookmarks: Outline hierarchy, destination counts
- Encryption: Type, strength, permissions flags
- Digital signatures: Signature count, validity, algorithm, timestamp
- 3D/multimedia: Embedded objects count
- Accessibility: Tagged PDF validation, reading order, alt text
- Estimated: 400-500 fields
```

#### 3.2 Office Documents (~250-350 fields)

```python
# server/extractor/modules/office_documents.py
- OOXML (Word/Excel/PowerPoint): Core properties, custom properties, comments, revisions
- ODF (LibreOffice): Manifest, metadata, custom properties
- Apple iWork: Presets, themes, version info
- Estimated: 250-350 fields
```

#### 3.3 Web & Social Standards (~250-350 fields)

```python
# server/extractor/modules/web_social_metadata.py
- Open Graph: og:title, og:image, og:video, og:audio (14 fields, expand to 50+)
- Twitter Cards: card type, player, app data, dimensions (30+ fields)
- Schema.org: Type, property enumeration, rich snippet fields (100+ fields)
- Web Manifest: Icons, display mode, theme colors, screenshots (40+ fields)
- Microdata: Item types, properties
- Estimated: 250-350 fields
```

#### 3.4 Email & Communication (~100-150 fields)

```python
# server/extractor/modules/email_metadata.py
- MIME headers: From, To, CC, BCC, Subject, Date, Message-ID
- Authentication: SPF, DKIM, DMARC results, authentication-results
- Routing: Received headers, return-path
- Attachments: MIME types, sizes, hashes
- Estimated: 100-150 fields
```

**Phase 3 Total**: **+800-1,200 fields** → **4,900-5,900 cumulative**

---

### ⏳ Phase 4: Scientific & Specialized (Optional, Gated - Est. +1,000-2,000 fields)

**Objective**: Medical imaging, astronomy, GIS, with strict PII/PHI protection

**Note**: These formats are large, require specialized knowledge, and have legal implications. Recommended as **optional install** with explicit consent/compliance review.

#### 4.1 DICOM Medical Imaging (~800+ fields)

```python
# server/extractor/modules/dicom_medical_complete.py
# ONLY extracted when explicitly enabled + compliance verified
- Patient/Study/Series/Instance: ~200 fields
- Equipment/Modality: ~100 fields (CT, MRI, PET, Ultrasound, etc.)
- Image Properties: ~150 fields (pixel spacing, orientation, window/level)
- Waveforms: ~100 fields (ECG, EEG, physiological)
- Structured Reporting: ~300 fields (SR templates, measurements, findings)
- Radiation Dose: ~50 fields
- Workflow: ~50 fields
# REDACTION REQUIRED: Patient name, ID, dates shifted, accession numbers masked
```

#### 4.2 FITS Astronomical (~500+ fields)

```python
# server/extractor/modules/fits_metadata.py
- FITS Standard: ~200 keyword fields
- WCS (World Coordinate System): ~100 fields
- Telescope/Observatory: ~75 fields
- Spectral data: ~100 fields
- Time series: ~50 fields
- Calibration: ~75 fields
```

#### 4.3 GIS & Geospatial (~300+ fields)

```python
# server/extractor/modules/gis_metadata.py
- GeoTIFF: Projection, datum, scale, bounds
- Shapefile: Attribute definitions, spatial references, geometry types
- KML/KMZ: Placemarks, regions, camera views, styling
- LAS/LAZ (Point Cloud): Point record format, classification, intensity
```

**Phase 4 Total (Optional)**: **+1,000-2,000 fields** (gated, requires compliance review)

- **If enabled**: 5,900-7,900 cumulative
- **If disabled**: Phase 3 endpoint (4,900-5,900) is production-ready

---

### 🎯 Phase 5: Optimization & UX (Concurrent with Phases 2-3)

**Objective**: Performance, safety, usability, and reliability

#### 5.1 Performance Optimization

- **Field extraction capping**: Max 500 fields per module tier (avoid bloat)
- **Sampling**: For large metadata (e.g., DICOM), sample/summarize instead of full dump
- **Lazy loading**: Extract only requested field groups (EXIF vs. MakerNotes vs. forensic)
- **Timeout guards**: Per-module timeouts (2s for video, 5s for forensic, 10s for scientific)
- **Streaming results**: Incremental field reporting for large files

#### 5.2 Safety & Compliance

- **PII/PHI Redaction**: Automatic masking of personal data
  - Patient names → `[REDACTED_NAME]`
  - Medical record numbers → `[REDACTED_MRN]`
  - Dates (DICOM) → `[SHIFTED_DATE]`
  - Email addresses → `[REDACTED_EMAIL]`
- **Allowlist expansion**: Per-module safe field lists
- **Audit logging**: Track what was extracted, when, by whom
- **Data retention**: Zero storage of metadata post-analysis

#### 5.3 Forensic Reliability

- **Version tracking**: Log MetaExtract version, module versions
- **Hash certification**: MD5/SHA256 of source file + metadata output
- **Timestamp validation**: Verify EXIF datetime vs. filesystem mtime
- **Chain of custody**: Optional JSON signature of results
- **Report format**: JSON + human-readable forensic report

#### 5.4 User Experience

- **Grouped output**: Organize by forensic type (authenticity, provenance, device, etc.)
- **Confidence scores**: Flag uncertain/ambiguous extractions
- **Warnings**: Highlight suspicious metadata (timestamp anomalies, stripped EXIF, etc.)
- **Normalization**: Map vendor-specific fields to standard names
- **Visualization**: Timeline of events, GPS map for location data, device timeline

---

## Implementation Timeline

| Phase       | Duration  | Target Completion | Field Count                      | Difficulty |
| ----------- | --------- | ----------------- | -------------------------------- | ---------- |
| **Phase 1** | 2 days    | ✅ Dec 30         | +632 → 2,899                     | Medium     |
| **Phase 2** | 2-3 weeks | Jan 20            | +1,200-1,800 → 4,100-4,700       | High       |
| **Phase 3** | 1-2 weeks | Feb 3             | +800-1,200 → 4,900-5,900         | Medium     |
| **Phase 4** | 1-2 weeks | Feb 17            | +1,000-2,000 → 5,900-7,900 (opt) | Very High  |
| **Phase 5** | 1 week    | Feb 24            | 0 new fields                     | Medium     |

**Total realistic implementation**: 6-8 weeks to reach **5,000-6,000 fields** (71-86% of 7k target)
**With Phase 4**: 7-9 weeks to reach **7,000+ fields** (100%+ of target)

---

## Success Metrics

### Coverage

- ✅ **Media dominance**: 60%+ of fields from image/video/audio
- ✅ **Forensic strength**: 20%+ of fields for authenticity/provenance/integrity
- ✅ **Document support**: 10%+ for PDFs and office documents
- ✅ **Scientific (optional)**: 10%+ for specialized formats

### Quality

- ✅ **Accuracy**: 98%+ of extracted fields validated (vs. reference tools)
- ✅ **Completeness**: Capture 80%+ of fields present in real-world files
- ✅ **Safety**: Zero PII/PHI leakage; all sensitive fields redacted
- ✅ **Performance**: <1 second for typical file analysis; <5s for large video

### Forensic Reliability

- ✅ **Court-admissible**: Reproducible, documented, timestamped
- ✅ **Chain of custody**: Full audit trail of extraction
- ✅ **Tamper detection**: Identify metadata discrepancies and anomalies
- ✅ **Expert-friendly**: Output matches industry tools (ExifTool, Amped FIVE)

---

## Competitive Positioning

### Current Tools Benchmark

| Tool                     | Field Count   | Focus          | Forensic Grade  |
| ------------------------ | ------------- | -------------- | --------------- |
| **Adobe Lightroom**      | 50-500        | Photography    | Consumer        |
| **PhotoMechanic**        | 500-800       | Professional   | Professional    |
| **ExifTool**             | 10,000-18,000 | Comprehensive  | Expert          |
| **Amped FIVE**           | 1,000-3,000   | Forensic       | Court-certified |
| **MetaExtract (Target)** | 7,000-15,000  | Forensic-first | Court-ready     |

### MetaExtract Advantage

- **Forensic-first design**: Not photography-first like Lightroom
- **Deep MakerNote support**: Comparable to ExifTool but with safety guardrails
- **Content authenticity**: Native C2PA/JUMBF support (rare in tools)
- **Accessibility**: Open-source, free, extensible
- **Speed**: Optimized extraction vs. ExifTool's comprehensiveness trade-off

---

## Risk Mitigation

| Risk                          | Impact | Mitigation                                  |
| ----------------------------- | ------ | ------------------------------------------- |
| **DICOM PHI exposure**        | High   | Strict allowlisting, redaction, gating      |
| **ExifTool unavailable**      | Medium | Graceful fallback, built-in parsers         |
| **Performance degradation**   | Medium | Field capping, lazy loading, timeouts       |
| **Binary format instability** | Low    | Version pinning, regression tests           |
| **Legal compliance**          | High   | Audit trail, encryption at rest, consent UI |

---

## Getting Started: Phase 2 Sprint

To begin Phase 2 immediately:

1. **Setup**:

   ```bash
   cd /Users/pranay/Projects/metaextract
   git checkout -b phase-2-media-depth
   ```

2. **Video Codec Module** (first priority):

   ```bash
   touch server/extractor/modules/video_codec_details.py
   # Implement H.264/HEVC/AV1 parser
   # Target: 400+ fields
   ```

3. **Testing**:

   ```bash
   python test_phase2_video_codecs.py
   # Validate against ffprobe output
   ```

4. **Integration**:

   ```python
   # Add to metadata_engine.py
   if tier_config.video_codec_details:
       result["video_codec"] = extract_video_codec_metadata(filepath)
   ```

5. **Track Progress**:
   ```bash
   python field_count.py
   # Target: 2,899 → 3,300+ fields
   ```

---

## Conclusion

MetaExtract's path to 45,000 fields is not a single engineering effort but a **strategic, phased roadmap** balancing:

- **Practical field coverage** (10,000-15,000 vs. theoretical 45,000)
- **Performance and safety** (allowlists, redaction, timeouts)
- **Forensic reliability** (court-admissible, reproducible)
- **User experience** (clear output, confidence scores, warnings)

The **Phase 1-3 roadmap delivers 5,000-6,000 high-value forensic fields in 6-8 weeks**, positioning MetaExtract as a competitive forensic analysis tool with media depth, document support, and content authenticity capabilities unmatched in the open-source space.
