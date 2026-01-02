# MetaExtract UI Analysis - Input for ChatGPT

## Test File Information
- **Filename**: `20251225_44810PMByGPSMapCamera_A27, Santhosapuram, Kudremukh Colony, Koramangala_Bengaluru_Karnataka_India_12_923974_77_6254197J4VWJFG+H5GMT_+05_30.jpg`
- **Size**: 9.12 MB (9,562,433 bytes)
- **Type**: JPEG image from Xiaomi phone with GPS Map Camera app
- **Resolution**: 3072 x 4096 (12.58 MP, portrait orientation)

## Burned-In Metadata (OCR Extracted from Image Overlay)
The image has visual text overlay containing:
```
Bengaluru, Karnataka, India
A27 Santhosapuram, Kudremukh Colony, Koramangala
Bengaluru, Karnataka 560034, India
Lat 12.923974° Long 77.625419°
Plus Code: 7J4VWJFG+H5
Thursday, 25/12/2025 04:48 PM GMT +05:30
231° SW (compass direction)
25.54° C (temperature)
297.42 km/h (speed - likely erroneous)
34% (humidity)
903 m (altitude)
```

## Current API Response Structure (Enterprise Tier)

```json
{
    "filename": "gps_test_image.jpg",
    "filesize": "9.12 MB",
    "filetype": "JPG",
    "mime_type": "image/jpeg",
    "tier": "enterprise",
    "fields_extracted": 232,
    "fields_available": 45000,
    "processing_ms": 8963,
    
    "file_integrity": {
        "md5": "dd32a8f4770a8ce5cb018679885284a0",
        "sha256": "8774745d7a887daa96ed3e96552a9cc5fcb4683552dbaeb0db29415258367412",
        "sha1": "e00bae45e607d74f05c87c31e790d20b0a0735f0",
        "crc32": "a12c2dc9"
    },
    
    "filesystem": {
        "size_bytes": 9562433,
        "size_human": "9.12 MB",
        "created": "2026-01-01T00:43:21.220987",
        "modified": "2026-01-01T00:43:21.241103",
        "accessed": "2026-01-01T00:43:27.347190",
        "permissions_octal": "0o644",
        "permissions_human": "-rw-r--r--",
        "owner": "pranay",
        "inode": 192777236,
        "hard_links": 1
    },
    
    "calculated": {
        "aspect_ratio": "3:4",
        "megapixels": 12.58,
        "orientation": "portrait",
        "file_age_human": "just now"
    },
    
    "gps": {},  // Empty - GPS data is burned into image, not in EXIF
    
    "summary": {
        "filename": "gps_test_image.jpg",
        "filesize": "9.12 MB",
        "filetype": "JPG",
        "width": 3072,
        "height": 4096
    },
    
    "forensic": {
        "forensic": {
            "digital_signatures": {},
            "blockchain_nft": {},
            "watermarking": {},
            "c2pa": {},
            "adobe_credentials": {},
            "filesystem": {
                "file_created": "...",
                "file_modified": "...",
                "file_extended_attributes": ["com.apple.provenance"]
            }
        },
        "authentication": {
            "is_authenticated": false,
            "confidence_score": 0,
            "issues": ["No authentication metadata found"],
            "security_flags": ["unauthenticated_content"]
        },
        "integrity": {
            "file_hash_md5": "...",
            "file_hash_sha256": "..."
        }
    },
    
    "exif": {
        "ImageWidth": 3072,
        "Model": "24053PY09I :: Captured by - GPS Map Camera",
        "ImageHeight": 4096,
        "Make": "Xiaomi",
        "ApertureValue": 1.62,
        "DateTimeOriginal": "2025:12:25 16:48:10",
        "WhiteBalance": 0,
        "ExposureTime": 0.01,
        "Flash": 16,
        "FNumber": 1.63,
        "ISO": 1011,
        "FocalLengthIn35mmFormat": 25,
        "FocalLength": 5.84,
        "MeteringMode": 1,
        "Orientation": 0,
        "ModifyDate": "2025:12:25 16:48:10"
    },
    
    "image": {
        "width": 3072,
        "height": 4096,
        "format": "JPEG",
        "mode": "RGB",
        "dpi": [72, 72],
        "bits_per_pixel": 24,
        "has_icc_profile": true
    },
    
    "normalized": {
        "camera_make": "Xiaomi",
        "camera_model": "24053PY09I :: Captured by - GPS Map Camera",
        "iso": 1011,
        "aperture": 1.63,
        "shutter_speed": "1/100",
        "focal_length": 5.84,
        "flash_used": false,
        "color_space": "sRGB",
        "exposure_triangle": "ISO 1011, f/1.63, 1/100"
    },
    
    "thumbnail": {
        "has_embedded": true,
        "width": 120,
        "height": 160
    },
    
    "perceptual_hashes": {
        "available": true,
        "phash": "f9d8c0e443c3e1d3",
        "dhash": "3133337b3f07c3d1",
        "ahash": "fcdd990080c3f101",
        "whash": "fcdf990881c3f311"
    },
    
    "burned_metadata": {
        "has_burned_metadata": false,  // OCR didn't detect it automatically
        "ocr_available": true,
        "extracted_text": null,
        "confidence": "none"
    },
    
    "metadata_comparison": {
        "has_both": false,
        "has_embedded_only": false,
        "has_burned_only": false,
        "summary": {
            "embedded_metadata_present": false,
            "burned_metadata_present": false,
            "gps_comparison": "no_gps",
            "overall_status": "no_metadata"
        }
    },
    
    "locked_fields": [],  // Enterprise tier has no locked fields
    
    "extraction_info": {
        "tier": "super",
        "exiftool_used": true,
        "fields_extracted": 232,
        "specialized_engines": {
            "medical_imaging": true,
            "astronomical_data": true,
            "geospatial_analysis": true,
            "drone_telemetry": true,
            "blockchain_provenance": true,
            "emerging_technology": true,
            // ... 21 specialized engines total
        }
    }
}
```

---

## Current Results Page Structure

### Main Layout
```
┌─────────────────────────────────────────────────────────────────────┐
│ HEADER: filename | SIZE: 9.12 MB | TYPE: JPG | SHA256: 8774745d...  │
│ [Context Indicator] [DOWNLOAD_REPORT / UNLOCK_FULL_DATA button]     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐  ┌─────────────────────────────────────────────┐  │
│  │ LEFT SIDEBAR │  │              MAIN CONTENT AREA              │  │
│  │              │  │                                             │  │
│  │ Analysis     │  │  TABS: ALL | EXPLORER | ADVANCED |          │  │
│  │ Summary      │  │        FORENSIC | TECHNICAL | RAW           │  │
│  │ ─────────    │  │                                             │  │
│  │ Total Fields │  │  [Search/Filter input]                      │  │
│  │ 232          │  │                                             │  │
│  │              │  │  ┌─────────────────────────────────────┐    │  │
│  │ File         │  │  │ SECTION: File Integrity             │    │  │
│  │ Integrity    │  │  │ MD5: dd32a8f4770a8ce5cb018679...    │    │  │
│  │ VERIFIED     │  │  │ SHA256: 8774745d7a887daa96ed...     │    │  │
│  │              │  │  └─────────────────────────────────────┘    │  │
│  │ Location     │  │                                             │  │
│  │ Data         │  │  ┌─────────────────────────────────────┐    │  │
│  │ Not Found    │  │  │ SECTION: Forensic Evidence          │    │  │
│  │              │  │  │ authentication.is_authenticated:    │    │  │
│  │ Dimensions   │  │  │   false                             │    │  │
│  │ 12.58 MP     │  │  │ authentication.confidence_score: 0  │    │  │
│  │              │  │  │ ...                                 │    │  │
│  │ Advanced     │  │  └─────────────────────────────────────┘    │  │
│  │ Analysis     │  │                                             │  │
│  │ Not Run      │  │  ┌─────────────────────────────────────┐    │  │
│  ├──────────────┤  │  │ SECTION: File Summary               │    │  │
│  │ GPS Location │  │  │ filename: gps_test_image.jpg        │    │  │
│  │ (if present) │  │  │ filesize: 9.12 MB                   │    │  │
│  │ LAT: ...     │  │  │ width: 3072                         │    │  │
│  │ LON: ...     │  │  │ height: 4096                        │    │  │
│  │ [View Maps]  │  │  └─────────────────────────────────────┘    │  │
│  ├──────────────┤  │                                             │  │
│  │ File Preview │  │  ┌─────────────────────────────────────┐    │  │
│  │ [placeholder]│  │  │ SECTION: Calculated Fields          │    │  │
│  │              │  │  │ aspect_ratio: 3:4                   │    │  │
│  │ ZERO_DATA_   │  │  │ megapixels: 12.58                   │    │  │
│  │ RETENTION    │  │  │ orientation: portrait               │    │  │
│  └──────────────┘  │  └─────────────────────────────────────┘    │  │
│                    │                                             │  │
│                    │  ┌─────────────────────────────────────┐    │  │
│                    │  │ SECTION: Camera & EXIF              │    │  │
│                    │  │ ImageWidth: 3072                    │    │  │
│                    │  │ Model: 24053PY09I :: Captured by... │    │  │
│                    │  │ Make: Xiaomi                        │    │  │
│                    │  │ DateTimeOriginal: 2025:12:25...     │    │  │
│                    │  │ ISO: 1011                           │    │  │
│                    │  │ FNumber: 1.63                       │    │  │
│                    │  │ ... (30+ fields)                    │    │  │
│                    │  └─────────────────────────────────────┘    │  │
│                    │                                             │  │
│                    │  ┌─────────────────────────────────────┐    │  │
│                    │  │ SECTION: GPS Location               │    │  │
│                    │  │ (empty - no EXIF GPS data)          │    │  │
│                    │  └─────────────────────────────────────┘    │  │
│                    │                                             │  │
│                    │  [LOCKED FIELDS NOTICE - if not unlocked]   │  │
│                    │  "X ADDITIONAL FIELDS AVAILABLE"            │  │
│                    │  [UNLOCK_ALL_FIELDS button]                 │  │
│                    └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Current Tab Structure

### Tab 1: ALL (Default)
Shows all metadata in sections:
- File Integrity (MD5, SHA256)
- Metadata Comparison (if burned metadata detected)
- Burned Metadata Display (if detected)
- Forensic Evidence
- File Summary
- Calculated Fields
- Camera & EXIF
- GPS Location (if present)
- [Locked fields notice for free tier]

### Tab 2: EXPLORER
- Interactive metadata tree explorer
- View modes: simple | advanced | raw
- Expandable/collapsible sections

### Tab 3: ADVANCED
- Advanced forensic analysis results
- Steganography detection
- Manipulation detection
- AI content detection
- Comparison results
- Timeline analysis
- Forensic report generation

### Tab 4: FORENSIC
- Metadata Comparison Display
- Burned Metadata Display
- File Integrity Hashes
- Chain of Custody
- Filesystem Metadata

### Tab 5: TECHNICAL
- Camera Settings (EXIF)
- Interoperability (IFD)
- MakerNote (Vendor-Specific) - LOCKED for free tier
- IPTC Metadata - LOCKED for free tier
- XMP Metadata - LOCKED for free tier
- XMP Namespaces - LOCKED for free tier
- ICC Profile
- Thumbnail Metadata
- Embedded Thumbnails - LOCKED for free tier
- Image Container
- Scientific Metadata - LOCKED for free tier
- Scientific Data (HDF5/NetCDF) - LOCKED for free tier
- Video Telemetry
- 360° / Panorama

### Tab 6: RAW
- Extended metadata fields (200+ fields)
- Full JSON export capability
- LOCKED for free tier with purchase prompt

---

## Current Section Headers (with icons)

| Section | Icon | Color | Description |
|---------|------|-------|-------------|
| File Integrity | Hash | amber-500 | MD5, SHA256 hashes |
| Forensic Evidence | ShieldCheck | emerald-500 | Authentication, provenance |
| File Summary | FileText | primary | Basic file info |
| Calculated Fields | Calculator | cyan-500 | Derived values |
| Camera & EXIF | Camera | purple-400 | Camera settings |
| GPS Location | MapPin | rose-500 | Coordinates |
| MakerNote | Tag | orange-400 | Vendor-specific |
| IPTC Metadata | Tag | indigo-400 | Press/publishing |
| XMP Metadata | Tag | pink-400 | Adobe extensible |
| XMP Namespaces | Tag | fuchsia-400 | XMP namespace details |
| ICC Profile | Tag | emerald-400 | Color profile |
| Thumbnail Metadata | Tag | amber-400 | Embedded thumbnail info |
| Embedded Thumbnails | Image | yellow-400 | Thumbnail images |
| Image Container | Tag | blue-400 | Container format |
| Scientific Metadata | Database | sky-400 | Scientific data |
| Scientific Data | FileText | emerald-400 | HDF5/NetCDF |
| Video Telemetry | Zap | rose-400 | Video sensor data |
| 360° / Panorama | Camera | teal-400 | Spherical images |

---

## Current "Locked" UI Patterns

### Pattern 1: Individual Field Lock
```tsx
<button onClick={() => setShowPayment(true)}>
  <span>Upgrade to view</span>
  <Lock className='w-3 h-3' />
</button>
```

### Pattern 2: Section Lock Block
```tsx
<div className='p-4 border border-dashed border-white/10 rounded bg-white/5 text-center'>
  <Lock className='w-6 h-6 text-slate-600 mx-auto mb-2' />
  <p className='text-xs text-slate-400 font-mono mb-2'>
    {count} VENDOR-SPECIFIC FIELDS LOCKED
  </p>
  <Button variant='link' onClick={() => setShowPayment(true)}>
    UNLOCK_MAKERNOTES
  </Button>
</div>
```

### Pattern 3: Full Tab Lock (RAW tab)
```tsx
<div className='flex flex-col items-center justify-center h-[400px] text-center'>
  <Database className='w-16 h-16 text-white/5 mb-4' />
  <h3 className='text-lg font-bold text-white font-mono mb-2'>
    RAW_DATA_LOCKED
  </h3>
  <p className='text-slate-500 max-w-sm mb-6 text-sm'>
    Access to {count} extended metadata fields including MakerNotes,
    IPTC, XMP, and proprietary tags requires a license.
  </p>
  <Button onClick={() => setShowPayment(true)}>
    PURCHASE_LICENSE ($5.00)
  </Button>
</div>
```

---

## Current Issues Identified (from ChatGPT's analysis)

1. **Volume without prioritization**: 232 fields displayed without hierarchy
2. **Jargon**: MakerNotes, IPTC, XMP, IFD visible to all users
3. **Ambiguous flags**: "Not Found", "Integrity", "Forensic" terminology
4. **Locked blocks**: Multiple "LOCKED" sections feel ominous
5. **No "what this means" layer**: No plain-language explanations
6. **Tab names**: FORENSIC / TECHNICAL / RAW are intimidating
7. **Missing highlights**: No summary of key findings at top
8. **No impact/confidence labels**: Users can't assess importance

---

## Requested Mapping

Please provide an exact mapping from the current components to a "calm report first" layout that:

1. Adds a **Highlights card** at the top with:
   - 3-7 bullet findings in plain language
   - Impact labels (Privacy, Authenticity, Workflow, None)
   - Confidence labels (High/Med/Low)
   - Limitations disclaimer

2. Renames tabs to **intent-based names**:
   - Current: ALL | EXPLORER | ADVANCED | FORENSIC | TECHNICAL | RAW
   - Proposed: Privacy | Authenticity | Photography | Evidence | Research | Raw (advanced)

3. Adds **Normal/Advanced toggle** for density control

4. Groups by **user meaning** instead of standards:
   - When and where
   - Device and software
   - Edit history
   - Ownership/author
   - Security/integrity
   - File structure

5. Makes **risk non-alarming** with actionable language

6. Fixes **missingness language**:
   - "Not Found" → "Not present in this file"
   - "LOCKED" → "Available on Pro" with example fields

7. Makes **paywall feel honest**:
   - Show real locked field examples
   - Tie to user's current intent
