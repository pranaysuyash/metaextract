# Extended Metadata Gaps - Containers and Standards

**Date**: 2025-12-29
**Scope**: Container-level metadata and standards not covered in existing docs
**Purpose**: Capture missing container/standard fields for PNG/WebP/HEIF/AVIF/JXL, JUMBF/C2PA, XMP namespaces, and GPano photo sphere metadata.

---

## Summary

These gaps are not documented in `METADATA_GAPS_ANALYSIS.md`, `METADATA_COMPLETE_EXHAUSTIVE.md`, or the extended documents:

- PNG/APNG chunk metadata (text chunks, ICC, EXIF-in-PNG, APNG timing)
- WebP RIFF chunk metadata (VP8X/ANIM/ANMF/ALPH + embedded XMP/EXIF)
- HEIF/AVIF item properties and HDR/gain map metadata
- JPEG XL container metadata (Exif/XMP boxes)
- JUMBF/C2PA box-level structures
- XMP namespaces: xmpMM, xmpDM, xmpTPg, xmpBJ
- GPano photo sphere metadata

---

## 1) PNG/APNG Chunk Metadata (Not Implemented)

**Source**: PNG spec (W3C)

| Field | Chunk | Description |
|-------|-------|-------------|
| `png_text.keyword` | tEXt/zTXt/iTXt | Text keyword |
| `png_text.text` | tEXt/zTXt/iTXt | Text value |
| `png_text.language_tag` | iTXt | RFC 3066 language tag |
| `png_text.translated_keyword` | iTXt | Localized keyword |
| `png_text.compressed` | zTXt/iTXt | Compression flag |
| `png_icc.profile_name` | iCCP | ICC profile name |
| `png_icc.profile_data` | iCCP | ICC profile bytes |
| `png_exif_present` | eXIf | EXIF block present |
| `png_gamma` | gAMA | Image gamma |
| `png_chromaticities` | cHRM | White point and primaries |
| `png_srgb_intent` | sRGB | Rendering intent |
| `png_phys.x_ppu` | pHYs | Pixels per unit (X) |
| `png_phys.y_ppu` | pHYs | Pixels per unit (Y) |
| `png_phys.unit` | pHYs | Unit specifier |
| `png_time` | tIME | Image last-modified time |
| `apng.num_frames` | acTL | Total frames |
| `apng.num_plays` | acTL | Loop count |
| `apng.frame_width` | fcTL | Frame width |
| `apng.frame_height` | fcTL | Frame height |
| `apng.frame_x_offset` | fcTL | Frame X offset |
| `apng.frame_y_offset` | fcTL | Frame Y offset |
| `apng.frame_delay_num` | fcTL | Frame delay numerator |
| `apng.frame_delay_den` | fcTL | Frame delay denominator |
| `apng.frame_dispose_op` | fcTL | Dispose op |
| `apng.frame_blend_op` | fcTL | Blend op |
| `png_hdr.cicp` | cICP | CICP color info (if present) |
| `png_hdr.mdcv` | mDCV | Mastering display (if present) |
| `png_hdr.clli` | cLLI | Content light level (if present) |

**Extraction approach**: Parse PNG chunks directly (not exposed by Pillow).

---

## 2) WebP RIFF Chunk Metadata (Not Implemented)

**Source**: WebP RIFF container spec

| Field | Chunk | Description |
|-------|-------|-------------|
| `webp_vp8x.has_alpha` | VP8X | Alpha flag |
| `webp_vp8x.has_icc` | VP8X | ICC profile present |
| `webp_vp8x.has_exif` | VP8X | EXIF present |
| `webp_vp8x.has_xmp` | VP8X | XMP present |
| `webp_vp8x.has_animation` | VP8X | Animation flag |
| `webp_canvas_width` | VP8X | Canvas width |
| `webp_canvas_height` | VP8X | Canvas height |
| `webp_anim.loop_count` | ANIM | Loop count |
| `webp_anim.background_color` | ANIM | Background color |
| `webp_anim.frame_x` | ANMF | Frame X offset |
| `webp_anim.frame_y` | ANMF | Frame Y offset |
| `webp_anim.frame_width` | ANMF | Frame width |
| `webp_anim.frame_height` | ANMF | Frame height |
| `webp_anim.frame_duration` | ANMF | Frame duration (ms) |
| `webp_anim.blend_method` | ANMF | Blend method |
| `webp_anim.dispose_method` | ANMF | Dispose method |
| `webp_alpha.format` | ALPH | Alpha format |
| `webp_alpha.filter` | ALPH | Alpha filter |
| `webp_exif_present` | EXIF | EXIF chunk present |
| `webp_xmp_present` | XMP | XMP chunk present |
| `webp_icc_present` | ICCP | ICC chunk present |

**Extraction approach**: Parse RIFF chunks or use libwebp tools.

---

## 3) HEIF/AVIF Item Properties (Not Implemented)

**Source**: HEIF/AVIF (ISOBMFF) specs

| Field | Box/Property | Description |
|-------|--------------|-------------|
| `heif_ispe_width` | ispe | Image width |
| `heif_ispe_height` | ispe | Image height |
| `heif_pixi_bits_per_channel` | pixi | Bit depth per channel |
| `heif_clap_width` | clap | Clean aperture width |
| `heif_clap_height` | clap | Clean aperture height |
| `heif_clap_h_offset` | clap | Horizontal offset |
| `heif_clap_v_offset` | clap | Vertical offset |
| `heif_irot` | irot | Rotation |
| `heif_imir` | imir | Mirror flag |
| `heif_pasp_h_spacing` | pasp | Pixel aspect ratio (H) |
| `heif_pasp_v_spacing` | pasp | Pixel aspect ratio (V) |
| `heif_colr_primaries` | colr | Color primaries |
| `heif_colr_transfer` | colr | Transfer characteristics |
| `heif_colr_matrix` | colr | Matrix coefficients |
| `heif_aux_type` | auxC/auxi | Auxiliary type (alpha/depth) |
| `heif_iref_thmb` | iref | Thumbnail item reference |
| `heif_iref_auxl` | iref | Auxiliary item reference |
| `heif_hdr_clli` | clli | Content light level |
| `heif_hdr_mdcv` | mdcv | Mastering display |
| `heif_tmap_present` | tmap | Tone map / gain map item |

**Extraction approach**: Parse ISOBMFF item properties (libheif or avif tools).

---

## 4) JPEG XL Container Metadata (Not Implemented)

**Source**: JPEG XL file format (ISOBMFF container)

| Field | Box | Description |
|-------|-----|-------------|
| `jxl_container_type` | JXL | Codestream vs container |
| `jxl_box_count` | box list | Total boxes |
| `jxl_boxes` | box list | Types and sizes |
| `jxl_exif_present` | Exif | Exif box present |
| `jxl_xmp_present` | xml  | XMP box present |
| `jxl_jumbf_present` | jumb | JUMBF present |
| `jxl_codestream_present` | jxlc | Codestream box present |

**Extraction approach**: Parse ISOBMFF boxes (libjxl or exiftool).

---

## 5) JUMBF / C2PA Box Metadata (Not Implemented)

**Source**: JUMBF and C2PA specifications

| Field | Box | Description |
|-------|-----|-------------|
| `jumbf_box_count` | JUMBF | Number of JUMBF boxes |
| `jumbf_labels` | JUMBF | Labels per box |
| `jumbf_uuids` | JUMBF | UUIDs per box |
| `jumbf_content_types` | JUMBF | Content type boxes |
| `c2pa_manifest_present` | C2PA | C2PA manifest present |
| `c2pa_manifest_count` | C2PA | Manifest count |
| `c2pa_active_manifest_label` | C2PA | Active manifest label |
| `c2pa_claim_generator` | C2PA | Claim generator |
| `c2pa_signature_valid` | C2PA | Signature validity |
| `c2pa_assertion_count` | C2PA | Assertions count |
| `c2pa_actions` | C2PA | Actions list |
| `c2pa_ingredients_count` | C2PA | Ingredient count |

**Extraction approach**: Use c2patool or JUMBF parser; exiftool can surface some fields.

---

## 6) XMP Namespace Expansion (Not Implemented)

**Source**: Adobe XMP namespaces

### 6.1 xmpMM (Media Management)

| Field | Description |
|-------|-------------|
| `xmpMM:DocumentID` | Unique document ID |
| `xmpMM:InstanceID` | Instance ID |
| `xmpMM:OriginalDocumentID` | Original document ID |
| `xmpMM:DerivedFrom` | Derived-from structure |
| `xmpMM:History` | Edit history array |
| `xmpMM:ManagedFrom` | Managed-from structure |

### 6.2 xmpDM (Dynamic Media)

| Field | Description |
|-------|-------------|
| `xmpDM:duration` | Duration |
| `xmpDM:startTime` | Start time |
| `xmpDM:timeScale` | Time scale |
| `xmpDM:audioSampleRate` | Audio sample rate |
| `xmpDM:audioSampleType` | Audio sample type |
| `xmpDM:audioChannelType` | Audio channel type |
| `xmpDM:videoFrameRate` | Video frame rate |
| `xmpDM:videoPixelAspectRatio` | Pixel aspect ratio |

### 6.3 xmpTPg (Paged Text)

| Field | Description |
|-------|-------------|
| `xmpTPg:NPages` | Page count |
| `xmpTPg:Fonts` | Fonts list |
| `xmpTPg:MaxPageSize` | Max page size |
| `xmpTPg:Colorants` | Colorants list |
| `xmpTPg:PlateNames` | Plate names |

### 6.4 xmpBJ (Job Management)

| Field | Description |
|-------|-------------|
| `xmpBJ:JobRef` | Job reference |
| `xmpBJ:JobID` | Job ID |
| `xmpBJ:JobName` | Job name |

**Extraction approach**: Parse XMP packet with full namespace support.

---

## 7) GPano Photo Sphere Metadata (Not Implemented)

**Source**: Google GPano XMP namespace

| Field | Description |
|-------|-------------|
| `GPano:UsePanoramaViewer` | Viewer flag |
| `GPano:ProjectionType` | Projection type |
| `GPano:PoseHeadingDegrees` | Pose heading |
| `GPano:PosePitchDegrees` | Pose pitch |
| `GPano:PoseRollDegrees` | Pose roll |
| `GPano:InitialViewHeadingDegrees` | Initial view heading |
| `GPano:InitialViewPitchDegrees` | Initial view pitch |
| `GPano:InitialViewRollDegrees` | Initial view roll |
| `GPano:InitialHorizontalFOVDegrees` | Initial horizontal FOV |
| `GPano:InitialVerticalFOVDegrees` | Initial vertical FOV |
| `GPano:CroppedAreaImageWidthPixels` | Cropped width |
| `GPano:CroppedAreaImageHeightPixels` | Cropped height |
| `GPano:FullPanoWidthPixels` | Full pano width |
| `GPano:FullPanoHeightPixels` | Full pano height |
| `GPano:CroppedAreaLeftPixels` | Cropped left |
| `GPano:CroppedAreaTopPixels` | Cropped top |
| `GPano:SourcePhotosCount` | Source photo count |
| `GPano:StitchingSoftware` | Stitching software |
| `GPano:CaptureSoftware` | Capture software |
| `GPano:FirstPhotoDate` | First photo date |
| `GPano:LastPhotoDate` | Last photo date |
| `GPano:ExposureLockUsed` | Exposure lock flag |
| `GPano:InitialCameraDolly` | Camera dolly |

**Extraction approach**: Parse GPano namespace in XMP packet.

---

## Library Gaps

Current stack does not parse these container/standard layers:

- PNG/APNG: needs chunk-level parser
- WebP: needs RIFF parser or libwebp bindings
- HEIF/AVIF: needs item property parsing (libheif)
- JPEG XL: needs ISOBMFF box parser (libjxl)
- JUMBF/C2PA: needs c2patool or JUMBF parser
- XMP: needs full namespace coverage (xmpMM, xmpDM, xmpTPg, xmpBJ, GPano)
