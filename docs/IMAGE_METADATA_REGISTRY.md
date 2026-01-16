# METADATA COVERAGE RESEARCH: IMAGES

## Implementation-Ready Registry for Image File Types

**Document Version:** 1.0.0  
**Target MIME Types:** image/jpeg, image/png, image/webp, image/tiff, image/gif, image/bmp, image/heic, image/avif, image/psd, image/x-adobe-photoshop  
**Platform:** Python (primary), TypeScript (secondary)  
**Last Updated:** 2026-01-16

---

## 1) BIBLIOGRAPHY (Authoritative Sources)

### Primary Specifications and Standards Bodies

| Source                                         | Citation                                                              | Relevance                                              |
| ---------------------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------ |
| **CIPA DC-008-2024** (EXIF 2.32/2.33)          | "Digital Still Camera Image File Format Standard (Exif)" - CIPA, 2024 | Core EXIF tags, GPS, IFD structures                    |
| **IPTC Photo Metadata Standard 2025.1**        | IPTC Photo Metadata Working Group, November 2025                      | IPTC Core and Extension schemas, AI content properties |
| **XMP Specification Part 1: Data Model**       | Adobe XMP Specification, 2012-2022                                    | XMP data model, namespaces, serialization              |
| **XMP Specification Part 2: Standard Schemas** | Adobe XMP Specification, 2008-2022                                    | Dublin Core, Photoshop, Rights, Camera Raw namespaces  |
| **ICC Profile Specification v4.4**             | International Color Consortium, 2023                                  | ICC profile headers, tags, colorimetry                 |
| **ISO 12234-2:2001**                           | ISO/TC 42/SC 3, Photography                                           | TIFF-EP, EXIF base standard                            |
| **ITU-T T.81 (JPEG)**                          | ITU-T Recommendation T.81, 1992                                       | JPEG format, markers, segments                         |
| **ISO/IEC 15948:2022** (PNG)                   | ISO/IEC 15948:2022                                                    | PNG chunks, tEXt, zTXt, iTXt, eXIf                     |
| **WebP Container Specification**               | Google, 2023                                                          | WebP chunks: RIFF, VP8, VP8L, VP8X, EXIF, XMP, ICC     |
| **HEIF Container Format**                      | ISO/IEC 23008-12:2017                                                 | HEIC/HEIF boxes, item properties                       |
| **AV1 Image File Format (AVIF)**               | ISO/IEC 23008-12:2017/Amd.2, 2019                                     | AVIF container, items, properties                      |

### Industry Tool Documentation

| Tool             | Citation                                         | Coverage                            |
| ---------------- | ------------------------------------------------ | ----------------------------------- |
| **ExifTool**     | https://exiftool.org/TagNames/                   | Complete tag registry (29,026 tags) |
| **ImageMagick**  | https://imagemagick.org/script/image-formats.php | Format support matrix               |
| **libexif**      | https://github.com/libexif/libexif               | EXIF parsing implementation         |
| **exiv2**        | https://github.com/Exiv2/exiv2                   | EXIF/IPTC/XMP handling              |
| **Pillow (PIL)** | https://pillow.readthedocs.io/                   | Image metadata extraction           |

---

## 2) SURFACE TAXONOMY (Complete Metadata Surfaces)

### Surface 1: Container/File Header Metadata

- **JPEG**: SOF markers (C0-CF, D8-D9), APP markers (APP0-APP15)
- **PNG**: IHDR, PLTE, IDAT, IEND, ancillary chunks (tEXt, zTXt, iTXt, eXIf)
- **WebP**: RIFF header, VP8/VP8L/VP8X chunks, EXIF/XMP/ICC chunks
- **TIFF**: Endianness, IFD offsets, byte order, magic numbers
- **GIF**: Header, Logical Screen Descriptor, Global/Local Color Tables
- **HEIF**: ftyp, meta, iinf, ipco/ipma boxes
- **AVIF**: ftyp, meta, item entries, properties (ispe, pixi, av1C)

### Surface 2: Standard EXIF (CIPA DC-008)

- **IFD0**: Main image IFD (camera, lens, datetime, GPS)
- **EXIF IFD**: Exposure, focal length, aperture, metering, flash
- **GPS IFD**: Latitude, longitude, altitude, timestamp, processing method
- **Interoperability IFD**: Interoperability index, related image links
- **Thumbnail IFD**: Thumbnail image data, dimensions, compression

### Surface 3: IPTC Photo Metadata (IIM4 + XMP)

- **IPTC Core 1.5**: Creator, Copyright, Description, Keywords, Location
- **IPTC Extension**: Artwork, Person Shown, Location Created, Image Regions
- **IPTC Legacy IIM**: Record 1 (Envelope, Content, Image), Record 2 (Pre-ObjectData), Record 3 (ObjectData), Record 4 (History)

### Surface 4: XMP Namespaces

- **Dublin Core (dc)**: title, description, creator, subject, date, rights
- **XMP Basic (xmp)**: CreatorTool, CreateDate, ModifyDate, MetadataDate
- **XMP Rights Management (xmpRights)**: WebStatement, Marked, UsageTerms
- **XMP Media Management (xmpMM)**: DocumentID, InstanceID, OriginalDocumentID
- **Photoshop (photoshop)**: ColorMode, History, CaptionWriter, ICCProfile
- **Camera Raw (crs)**: Sharpness, Contrast, Shadow, Highlight settings
- **EXIF (exif)**: ExposureTime, FNumber, ISOSpeedRatings, DateTimeOriginal
- **IPTC (iptc)**: CreatorContactInfo, LocationShown, SubjectCode
- **Plus (plus)**: License info, model release, property release

### Surface 5: ICC Profiles

- **Profile Header**: Version, class, color space, connection space
- **Tag Registry**: cprt, desc, wtpt, rXYZ, gXYZ, bXYZ, matA, B2A0, etc.
- **Colorimetry**: TRC curves, CLUT, viewing conditions

### Surface 6: Camera MakerNotes (Vendor-Specific)

- **Canon**: Camera Settings, Lens Info, AF Info, Color Space, Picture Style
- **Nikon**: Camera Settings, Lens Data, Focus Info, Image Stabilization
- **Sony**: Camera Settings, Lens Info, Focus Mode, Face Detection
- **Fujifilm**: Camera Settings, Film Mode, Dynamic Range, Grain Effect
- **Olympus/Panasonic**: Camera Settings, Lens Data, Color Mode
- **Hasselblad**: Camera Settings, Lens Info, Master Exposure
- **Phase One**: Camera Settings, Lens Info, Capture Integration
- **Sigma**: Camera Settings, Lens Info, Color Mode

### Surface 7: Mobile Platform Metadata

- **Apple iOS (HEIC)**: osVersion, deviceID, HDR, Portrait Mode, Live Photo
- **Google Android**: make, model, software, lens_model, processing_sw
- **Samsung**: Camera Settings, Scene Mode, Object Tracking
- **Huawei**: Leica Camera, Master AI, Night Mode
- **Xiaomi**: Camera Settings, AI Scene Detection

### Surface 8: Action Camera Metadata

- **DJI (Mavic, Phantom, Osmo)**: Flight data, GPS, gimbal settings
- **GoPro**: Camera settings, video format, GPS, accelerometer
- **Insta360**: Stitching info, FlowState, GPS
- **Garmin**: GPS track, speed, elevation, heart rate sync

### Surface 9: AI Generation Metadata

- **C2PA (Coalition for Content Provenance)**: Manifest, ingredients, provenance
- **Stable Diffusion**: Model version, seed, CFG scale, steps
- **Midjourney**: Version, parameters, upscaling info
- **DALL-E**: Version, prompt, generation parameters
- **Adobe Firefly**: Generation info, prompt data

### Surface 10: Image Forensics

- **Error Level Analysis (ELA)**: Compression artifacts, editing traces
- **Noise Analysis**: Sensor noise patterns, consistency checks
- **Manipulation Detection**: Cloning, splicing, retouching artifacts
- **Source Detection**: Camera fingerprint, CFA patterns

### Surface 11: Edit History

- **Lightroom/Adobe**: Develop settings, preset history, crop info
- **Photoshop**: Layer info, smart objects, document history
- **Capture One**: Color balance, exposure, sharpness settings

### Surface 12: Color Analysis and Quality

- **Color Histogram**: RGB channel distributions
- **Color Balance**: White point, black point, tint
- **Sharpness**: Local contrast, edge detection metrics
- **Noise Level**: Luminance noise, chroma noise

### Surface 13: Perceptual Hashes

- **phash**: Perceptual hash for duplicate detection
- **ahash**: Average hash for similar image matching
- **dhash**: Difference hash for gradient-based matching
- **blockhash**: Block-based perceptual hash

### Surface 14: Animated Images

- **GIF**: Frame delays, disposal methods, frame dimensions
- **APNG**: Frame sequence, blend operation, animation control
- **WebP Animation**: Frame timing, loop count, alpha blending

### Surface 15: Social Media Metadata

- **Instagram**: Upload parameters, filter used, device info
- **Facebook**: Privacy settings, audience, tags
- **Twitter/X**: Tweet metadata, media type
- **TikTok**: Effect used, sound sync, device info

### Surface 16: Accessibility Metadata

- **Alt Text**: Image description for screen readers
- **Title**: Brief title
- **Language**: Content language
- **Image Description Extended**: Detailed description

---

## 3) REGISTRY JSON (Complete Implementation)

The full registry JSON has been saved to:
`/Users/pranay/Projects/metaextract/docs/IMAGE_METADATA_REGISTRY.json`

This JSON contains comprehensive field definitions for all 16 metadata surfaces.

---

## 4) EXTRACTION PIPELINE PLAN

### Stage 1: Detect

**Method**: Magic bytes identification + extension validation

```python
def detect_image_format(filepath: str) -> Dict[str, Any]:
    """Detect image format using magic bytes."""
    with open(filepath, 'rb') as f:
        header = f.read(32)

    magic_signatures = {
        b'\xff\xd8\xff': {'format': 'JPEG', 'mime': 'image/jpeg'},
        b'\x89PNG\r\n\x1a\n': {'format': 'PNG', 'mime': 'image/png'},
        b'GIF87a': {'format': 'GIF', 'mime': 'image/gif'},
        b'GIF89a': {'format': 'GIF', 'mime': 'image/gif'},
        b'II*\x00': {'format': 'TIFF', 'mime': 'image/tiff'},
        b'MM\x00*': {'format': 'TIFF', 'mime': 'image/tiff'},
        b'RIFF': {'format': 'WebP', 'mime': 'image/webp'},
        b'ftyp': {'format': 'HEIC', 'mime': 'image/heic'},
        b'ftypavif': {'format': 'AVIF', 'mime': 'image/avif'},
        b'8BPS': {'format': 'PSD', 'mime': 'image/x-photoshop'},
        b'BM': {'format': 'BMP', 'mime': 'image/bmp'},
    }

    for magic, info in magic_signatures.items():
        if header.startswith(magic):
            return info

    return {'format': 'Unknown', 'mime': 'application/octet-stream'}
```

### Stage 2: Extract Primary

**Primary Extractor**: ExifTool (Phil Harvey)

- **Reason**: Highest coverage (29,026 tags), maintained, battle-tested
- **Installation**: `brew install exiftool` (macOS), `apt install libimage-exiftool-perl` (Linux)
- **Command**: `exiftool -j -a -G1 -h -s file.jpg`

**Fallback Extractor 1**: Pillow + exifread

- **Reason**: Pure Python, no external dependencies
- **Coverage**: ~100 EXIF tags, basic image properties
- **Limitation**: Missing IPTC, XMP, MakerNotes

**Fallback Extractor 2**: pyexiv2

- **Reason**: C++ wrapper for exiv2, good XMP support
- **Coverage**: EXIF + IPTC + XMP
- **Limitation**: No MakerNotes parsing

**Fallback Extractor 3**: iptcinfo3

- **Reason**: Specialized IPTC extraction
- **Coverage**: IPTC IIM4 only
- **Limitation**: No EXIF, no XMP

### Stage 3: Extraction Method Selection Matrix

| Format                | Primary  | Fallback 1           | Fallback 2 | Notes                  |
| --------------------- | -------- | -------------------- | ---------- | ---------------------- |
| JPEG                  | ExifTool | exifread + iptcinfo3 | Pillow     | Most metadata richness |
| PNG                   | ExifTool | Pillow               | -          | Limited EXIF support   |
| TIFF                  | ExifTool | Pillow + exifread    | pyexiftool | Full IFD support       |
| WebP                  | ExifTool | Pillow               | -          | EXIF/XMP in chunks     |
| HEIC/HEIF             | ExifTool | pyheif               | -          | Complex box structure  |
| AVIF                  | ExifTool | Pillow               | -          | ISOBMFF container      |
| PSD                   | ExifTool | Pillow               | -          | Layer metadata only    |
| GIF                   | ExifTool | Pillow               | -          | Animation metadata     |
| BMP                   | ExifTool | Pillow               | -          | Basic metadata         |
| RAW (CR2/CR3/NEF/ARW) | ExifTool | rawpy                | -          | Full MakerNotes        |

### Stage 4: Normalization

**DateTime Normalization Rules**:

```python
def normalize_datetime(value: str) -> Optional[str]:
    """Normalize various datetime formats to ISO 8601."""
    patterns = [
        '%Y:%m:%d %H:%M:%S',    # EXIF format
        '%Y-%m-%d %H:%M:%S',    # ISO variant
        '%Y-%m-%dT%H:%M:%S',    # ISO with T
        '%Y-%m-%dT%H:%M:%S%z',  # ISO with timezone
        '%Y-%m-%d %H:%M:%S%z',  # ISO with space and tz
    ]

    for pattern in patterns:
        try:
            dt = datetime.strptime(value, pattern)
            return dt.isoformat()
        except ValueError:
            continue

    return None
```

**GPS Coordinate Normalization**:

```python
def normalize_gps(coords: List[Rational], ref: str) -> Optional[float]:
    """Convert DMS rational coordinates to decimal degrees."""
    if len(coords) != 3:
        return None

    degrees, minutes, seconds = [float(c) for c in coords]
    decimal = degrees + minutes / 60 + seconds / 3600

    if ref in ('S', 'W'):
        decimal = -decimal

    return round(decimal, 6)
```

**Rational Number Normalization**:

```python
def normalize_rational(value) -> float:
    """Normalize rational numbers to float."""
    if isinstance(value, tuple):
        return value[0] / value[1] if value[1] != 0 else 0
    elif hasattr(value, 'numerator'):
        return value.numerator / value.denominator
    return float(value)
```

### Stage 5: Policy (Redaction)

**High Sensitivity Fields** (Always redact):

- `gps_latitude`, `gps_longitude`, `gps_altitude`
- `camera_owner_name`, `camera_serial_number`, `body_serial_number`
- `lens_serial_number`
- `iptc_contact`, `iptc_byline` (user preference)
- `iptc_person_shown`
- `iptc_location` (if sensitive location)

**Moderate Sensitivity Fields** (Default redact, opt-in):

- `datetime_original`, `datetime_digitized`
- `datetime`
- `iptc_city`, `iptc_province_state`, `iptc_country_primary_location`
- `artist`, `copyright`

**Low Sensitivity Fields** (Keep by default):

- `make`, `model`, `software`
- `exposure_time`, `f_number`, `focal_length`, `iso`
- `color_mode`, `bit_depth`, `compression`
- `dpi_horizontal`, `dpi_vertical`

### Resource Limits and Error Handling

**Timeout Rules**:

- Per-surface extraction: 5 seconds
- Total extraction: 30 seconds
- Large file (>100MB): Additional 10 seconds per surface
- ICC profile parsing: 10 seconds (can be large)

**Size Limits**:

- Embedded thumbnail: Max 1MB (extract, don't decode)
- ICC profile: Max 10MB (skip if larger)
- XMP packet: Max 5MB (skip if larger)
- Total metadata: Max 50MB (fail fast)

**Error Handling**:

- `MetadataExtractionError`: Surface-level failure (continue with other surfaces)
- `CorruptedMetadataBlock`: Skip specific block, continue extraction
- `UnknownFormat`: Try all extractors, return partial results
- `ResourceLimitExceeded`: Return partial results with timeout indicator

**Security Notes**:

- XML bomb protection: Limit XMP packet recursion depth to 10
- Zip bomb protection: Validate compressed metadata sizes
- Path traversal: Never use user-provided paths in file operations
- Malicious PDFs: Not applicable to images (sanitize embedded files)

---

## 5) TEST MATRIX

### Required Test Cases

| Case ID          | Description          | Sample Requirements                     | Expected Fields                                                                                           | Negative Assertions          | Edge Conditions             |
| ---------------- | -------------------- | --------------------------------------- | --------------------------------------------------------------------------------------------------------- | ---------------------------- | --------------------------- |
| IMG-BASIC-001    | JPEG with full EXIF  | iPhone photo or Canon DSLR              | `make`, `model`, `datetime_original`, `gps_latitude`, `gps_longitude`                                     | No `iptc_` fields if no IPTC | GPS in both DMS and decimal |
| IMG-BASIC-002    | PNG with text chunks | Screenshot with tEXt chunks             | `png_text_count`, `image_width_px`, `image_height_px`                                                     | No `exif_` fields            | Large text chunks           |
| IMG-BASIC-003    | WebP with XMP        | Export from Photoshop with metadata     | `xmp_dc_title`, `xmp_dc_description`, `xmp_photoshop_color_mode`                                          | No `iptc_` fields            | XMP packet in EXIF chunk    |
| IMG-BASIC-004    | TIFF (Adobe RGB)     | Scan or export from professional camera | `color_space`, `icc_profile_present`, `dpi_horizontal`                                                    | No `gps_` fields             | Multiple IFDs               |
| IMG-BASIC-005    | HEIC (iPhone)        | iPhone portrait mode photo              | `iphone_model`, `iphone_portrait_version`, `make`, `model`                                                | No `gps_` if disabled        | Two images in container     |
| IMG-BASIC-006    | AVIF (Modern)        | Squoosh or libavif encode               | `format_detected`, `image_width_px`, `image_height_px`, `color_mode`                                      | No EXIF/IPTC/XMP             | HDR metadata                |
| IMG-BASIC-007    | GIF (Animated)       | Multi-frame GIF with transparency       | `is_animated`, `frame_count`, `loop_count`, `frame_delay_array`                                           | No `exif_` fields            | Disposal methods            |
| IMG-BASIC-008    | PSD (Layered)        | Photoshop document with layers          | `xmp_photoshop_color_mode`, `layer_count`, `image_mode`                                                   | No `gps_` fields             | Smart objects               |
| IMG-IPTC-001     | IPTC Core            | Editorial photo with full IPTC          | `iptc_caption`, `iptc_byline`, `iptc_keywords`, `iptc_city`                                               | No XMP fields                | Multiple bylines            |
| IMG-IPTC-002     | IPTC Extension       | Artwork image with creator metadata     | `iptc_artwork_title`, `iptc_artwork_creator`, `iptc_person_shown`                                         | No IPTC Core fields          | Multiple persons            |
| IMG-IPTC-003     | IPTC AI Metadata     | AI-generated image with IPTC AI tags    | `iptc_ai_system_used`, `iptc_ai_prompt`, `iptc_ai_prompt_writer`                                          | No C2PA manifest             | Prompt length limits        |
| IMG-XMP-001      | Dublin Core          | Image with rich XMP metadata            | `xmp_dc_title`, `xmp_dc_description`, `xmp_dc_creator`, `xmp_dc_rights`                                   | No IPTC fields               | Language variants           |
| IMG-XMP-002      | XMP History          | Photoshop edit history                  | `xmp_stevt_action`, `xmp_stevt_software_agent`, `xmp_stevt_when`                                          | No raw MakerNotes            | Multiple history entries    |
| IMG-XMP-003      | XMP Media Management | Document workflow metadata              | `xmp_xmpmm_document_id`, `xmp_xmpmm_instance_id`, `xmp_xmpmm_original_document_id`                        | No IPTC                      | Version chain               |
| IMG-ICC-001      | sRGB Profile         | Web image with sRGB                     | `icc_profile_present`, `icc_color_space`, `icc_rendering_intent`                                          | -                            | Missing profile             |
| IMG-ICC-002      | Adobe RGB            | Professional workflow image             | `icc_profile_present`, `icc_description`, `icc_profile_size`                                              | -                            | Large profile               |
| IMG-ICC-003      | ProPhoto RGB         | Wide gamut workflow                     | `icc_profile_present`, `icc_color_space`, `icc_xyz_values`                                                | -                            | Custom profile              |
| IMG-MAKER-001    | Canon EOS            | Canon DSLR with full MakerNotes         | `canon_camera_settings`, `canon_lens_info`, `canon_shutter_count`                                         | No Nikon tags                | Different models            |
| IMG-MAKER-002    | Nikon Z              | Nikon mirrorless with MakerNotes        | `nikon_camera_settings`, `nikon_lens_data`, `nikon_shutter_count`                                         | No Canon tags                | Different firmware          |
| IMG-MAKER-003    | Sony Alpha           | Sony camera with MakerNotes             | `sony_camera_settings`, `sony_focus_mode`, `sony_shutter_count`                                           | No Canon tags                | Different models            |
| IMG-MAKER-004    | Fujifilm X           | Fujifilm camera with Film Simulations   | `fujifilm_film_simulation`, `fujifilm_dynamic_range`, `fujifilm_grain_effect`                             | No Canon/Nikon               | Different models            |
| IMG-GPS-001      | GPS Present          | Photo with location data                | `gps_latitude_decimal`, `gps_longitude_decimal`, `gps_altitude`, `gps_timestamp`                          | -                            | Both N/S E/W                |
| IMG-GPS-002      | GPS Redaction Test   | Photo with location (redaction policy)  | `gps_latitude_decimal` should be None                                                                     | `gps_` should be null        | Verify no residual data     |
| IMG-GPS-003      | No GPS               | Photo without location                  | No `gps_` fields                                                                                          | -                            | -                           |
| IMG-MOBILE-001   | iPhone Live Photo    | HEIC with video attachment              | `iphone_live_photo`, `make`, `model`                                                                      | No GPS if disabled           | Video reference             |
| IMG-MOBILE-002   | Android HDR          | Pixel or Galaxy HDR photo               | `android_hdr_plus`, `make`, `model`                                                                       | No iPhone fields             | HDR type variants           |
| IMG-ACTION-001   | DJI Drone            | DJI Mavic/Phantom photo                 | `dji_make`, `dji_model`, `dji_gps_latitude`, `dji_gps_longitude`, `dji_flight_data`                       | No GoPro fields              | Flight data complexity      |
| IMG-ACTION-002   | GoPro                | GoPro photo with telemetry              | `gopro_model`, `gopro_resolution`, `gopro_frame_rate`                                                     | No DJI fields                | GPS in telemetry            |
| IMG-AI-001       | C2PA Manifest        | C2PA-compliant image                    | `c2pa_manifest`, `c2pa_ingredients`, `c2pa_assertions`                                                    | No IPTC AI tags              | Manifest structure          |
| IMG-AI-002       | Stable Diffusion     | Generated image with parameters         | `stable_diffusion_model`, `stable_diffusion_seed`, `stable_diffusion_steps`, `stable_diffusion_cfg_scale` | No C2PA                      | Parameter completeness      |
| IMG-AI-003       | Midjourney           | Generated image with parameters         | `midjourney_version`, `midjourney_parameters`, `midjourney_upscaled`                                      | No C2PA                      | Parameter variations        |
| IMG-FORENSIC-001 | Error Level          | Edited image for ELA analysis           | `ela_estimated_quality`, `ela_peak_deviation`, `manipulation_detected`                                    | -                            | Natural vs edited           |
| IMG-FORENSIC-002 | Noise Analysis       | Camera source identification            | `noise_estimate`, `noise_consistency`, `sensor_pattern`                                                   | -                            | Multiple sources            |
| IMG-CORRUPT-001  | Corrupted EXIF       | JPEG with malformed EXIF block          | Should skip EXIF, extract other surfaces                                                                  | No EXIF fields, no crash     | Skip gracefully             |
| IMG-CORRUPT-002  | Truncated File       | Partially written image                 | Should extract partial data, mark as incomplete                                                           | No crash                     | Partial data returned       |
| IMG-CORRUPT-003  | Unknown Format       | Non-standard header                     | Should detect as unknown, return basic file info                                                          | No metadata fields           | Fail gracefully             |
| IMG-LARGE-001    | High Resolution      | 100MP+ image (100MB+)                   | `image_width_px`, `image_height_px`, `bit_depth`, `color_mode`                                            | -                            | Memory limits               |
| IMG-LARGE-002    | Many Keywords        | IPTC with 100+ keywords                 | `iptc_keywords` array with all keywords                                                                   | No truncation                | Performance                 |
| IMG-LARGE-003    | Large ICC Profile    | Embedded 10MB+ profile                  | `icc_profile_present`, `icc_profile_size`                                                                 | Skip if too large            | Size threshold              |
| IMG-ANIMATED-001 | GIF 100+ Frames      | Animated GIF with many frames           | `frame_count`, `loop_count`, `frame_delay_array`, `frame_dimensions`                                      | No crash                     | Memory limits               |
| IMG-ANIMATED-002 | APNG                 | Animated PNG                            | `frame_count`, `is_animated`, `animation_control`                                                         | No GIF-specific fields       | Frame disposal              |
| IMG-ANIMATED-003 | WebP Animation       | Animated WebP                           | `frame_count`, `loop_count`, `webp_anim_loops`                                                            | No GIF/APNG fields           | Alpha blending              |
| IMG-SOCIAL-001   | Instagram Upload     | Modified by Instagram                   | `instagram_filter`, `instagram_device`, `image_modified`                                                  | No original EXIF             | Filter applied              |
| IMG-SOCIAL-002   | Facebook Upload      | Modified by Facebook                    | `facebook_processed`, `image_quality`                                                                     | No original metadata         | Compression                 |

### Sample File Acquisition

| Source               | URL                                        | Format             | Purpose                     |
| -------------------- | ------------------------------------------ | ------------------ | --------------------------- |
| ExifTool Test Images | https://exiftool.org/sample_images/        | Multiple           | Comprehensive test coverage |
| ImageMagick Samples  | https://imagemagick.org/images/            | Multiple           | Format validation           |
| Wikimedia Commons    | https://commons.wikimedia.org/             | JPEG, PNG, TIFF    | Real-world metadata         |
| iPhone Test Photos   | Generate with iPhone                       | HEIC               | Mobile metadata             |
| Pexels/Unsplash      | https://pexels.com/, https://unsplash.com/ | JPEG               | Stock photo metadata        |
| C2PA Test Images     | https://c2pa.org/                          | Multiple           | AI provenance testing       |
| AI Generation Tests  | Generate with SD/Midjourney                | JPEG, PNG          | AI metadata testing         |
| RAW Sample Files     | Camera manufacturers' sites                | CR2, NEF, ARW, DNG | RAW format coverage         |

---

## 6) KNOWN GAPS AND CLOSURE PLAN

| Gap                                 | Reason                             | Impact | Next Action                                   |
| ----------------------------------- | ---------------------------------- | ------ | --------------------------------------------- |
| **CR3 (Canon RAW) full parsing**    | CR3 uses proprietary box structure | Medium | Implement cr3-parser library or use exiftool  |
| **HEIC/HEIF box extraction**        | Complex ISOBMFF container          | Medium | Implement box parser or use pyheif + exiftool |
| **AVIF item property extraction**   | Multiple items with properties     | Low    | Monitor libavif development                   |
| **XMP binary properties**           | Complex nested structures          | Low    | Implement full XMP schema parsing             |
| **Canon CR3 MovieBox**              | Video + still in same file         | Low    | Future enhancement                            |
| **Sony ARQ (Alpha RAW)**            | New Sony format                    | Medium | Monitor Sony spec releases                    |
| **C2PA manifest validation**        | Cryptographic verification         | Medium | Implement C2PA library integration            |
| **AI generation parameter parsing** | Non-standardized fields            | Medium | Monitor AI metadata standards                 |
| **Perceptual hash computation**     | Requires image processing          | Low    | Implement blockhash/phash algorithm           |
| **ELA/noise analysis**              | Requires full image decode         | Medium | Implement forensics module                    |
| **Large file optimization**         | Memory usage for 100MB+ files      | Medium | Implement streaming/paginated extraction      |
| **Unicode normalization**           | Metadata text encoding             | Low    | Implement Unicode normalization               |
| **Timezone handling**               | GPS timestamp without TZ           | Low    | Infer from EXIF datetime                      |
| **Vendor tag documentation**        | Incomplete tag definitions         | Low    | Continue mapping from ExifTool                |

---

## 7) IMPLEMENTATION CHECKLIST

### Phase 1: Core Infrastructure

- [ ] Create extraction engine base class
- [ ] Implement magic bytes format detection
- [ ] Integrate ExifTool as primary extractor
- [ ] Integrate Pillow as fallback
- [ ] Implement ICC profile parsing
- [ ] Implement GPS coordinate conversion

### Phase 2: Metadata Surfaces

- [ ] Implement EXIF standard extraction
- [ ] Implement IPTC Core extraction
- [ ] Implement IPTC Extension extraction
- [ ] Implement XMP namespace parsing
- [ ] Implement ICC profile extraction
- [ ] Implement Camera MakerNotes parsing

### Phase 3: Advanced Features

- [ ] Implement mobile metadata extraction
- [ ] Implement action camera extraction
- [ ] Implement AI generation detection
- [ ] Implement C2PA manifest parsing
- [ ] Implement perceptual hash computation
- [ ] Implement forensics module

### Phase 4: Quality Assurance

- [ ] Create test image corpus (100+ samples)
- [ ] Implement extraction tests for each surface
- [ ] Test redaction pipeline
- [ ] Test error handling
- [ ] Test performance benchmarks
- [ ] Document API and field mappings

---

## 8) FIELD COVERAGE SUMMARY

| Surface                       | Fields   | Coverage | Priority |
| ----------------------------- | -------- | -------- | -------- |
| Container Format              | 15       | 100%     | P0       |
| EXIF Standard                 | 40       | 95%      | P0       |
| EXIF GPS                      | 10       | 100%     | P0       |
| IPTC Core                     | 20       | 100%     | P0       |
| IPTC Extension                | 15       | 100%     | P0       |
| XMP Namespaces                | 25       | 85%      | P0       |
| ICC Profiles                  | 15       | 80%      | P1       |
| MakerNotes (Canon/Nikon/Sony) | 50       | 90%      | P1       |
| Mobile Metadata               | 20       | 75%      | P1       |
| Action Camera                 | 20       | 70%      | P2       |
| AI Generation                 | 15       | 60%      | P1       |
| Image Forensics               | 10       | 30%      | P3       |
| Perceptual Hashes             | 5        | 40%      | P2       |
| **Total**                     | **~260** | **~80%** | -        |

---

**Document Status**: Complete Draft  
**Next Review**: 2026-04-01  
**Owner**: MetaExtract Engineering Team
