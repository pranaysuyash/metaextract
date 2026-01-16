# METADATA COVERAGE RESEARCH: IMAGES v1.1

## Implementation-Ready Registry for Image File Types

**Document Version:** 1.1 (Corrected)  
**Target MIME Types:** image/jpeg, image/png, image/webp, image/tiff, image/gif, image/bmp, image/heic, image/avif, image/psd  
**Platform:** Python (primary)  
**Last Updated:** 2026-01-17

---

## 1) BIBLIOGRAPHY (Authoritative Sources)

### Primary Specifications and Standards Bodies

| Source                           | Citation                          | Version  | Relevance                                                          |
| -------------------------------- | --------------------------------- | -------- | ------------------------------------------------------------------ |
| **EXIF 3.0**                     | CIPA DC-008-Translation-2024      | 2024     | Core EXIF tags, GPS IFD, IFD structures (corrected from 2.32/2.33) |
| **EXIF 2.32**                    | CIPA DC-008-Translation-2019      | 2019     | Prior version with new tags                                        |
| **IPTC Photo Metadata Standard** | IPTC Photo Metadata Working Group | 2025.1   | IPTC Core 1.5, Extension schemas, AI content properties            |
| **XMP Specification Part 1**     | Adobe XMP Specification           | 2012     | Data model, namespaces, serialization                              |
| **XMP Specification Part 2**     | Adobe XMP Specification           | Feb 2022 | Standard schemas (Dublin Core, Photoshop, Rights, etc.)            |
| **ICC Profile Specification**    | ICC.1:2022 (Profile v4.4.0)       | 2022     | ICC profile headers, tags, colorimetry                             |
| **ITU-T T.81 (JPEG)**            | ITU-T Recommendation T.81         | 1992     | JPEG format, markers, segments                                     |
| **ISO/IEC 15948:2022 (PNG)**     | ISO/IEC 15948:2022                | 2022     | PNG chunks, tEXt, zTXt, iTXt, eXIf                                 |
| **ISO/IEC 23008-12:2017 (HEIF)** | ISO/IEC 23008-12:2017             | 2017     | HEIC/HEIF boxes, item properties                                   |
| **WebP Container Specification** | Google                            | 2023     | RIFF chunks: VP8, VP8L, VP8X, EXIF, XMP, ICC                       |
| **TIFF 6.0**                     | Adobe Systems                     | 1992     | Baseline TIFF, EXIF IFD, GPS IFD structures                        |

### Industry Tool Documentation

| Tool                   | Citation                       | Coverage Notes                                       |
| ---------------------- | ------------------------------ | ---------------------------------------------------- |
| **ExifTool**           | https://exiftool.org/TagNames/ | 29,026 tags (18,036 unique names) across all formats |
| **ExifTool Tag Count** | ExifTool documentation         | Confirms 29,026 total tag entries                    |

### Key Corrections from v1.0

- **EXIF Version**: Changed from "2.32/2.33" to "3.0 (2024)" - DC-008-Translation-2024 is Exif 3.0
- **Coverage Claims**: Removed "80% of 325 fields" - ExifTool alone has 29k tags, no fixed universe exists
- **Registry File**: Removed reference to "/Users/pranay/..." path (not verified written)

---

## 2) REGISTRY ARCHITECTURE

This document defines TWO separate registries, as recommended in feedback:

### Registry A: Embedded Metadata Registry

**Definition**: Fields actually stored inside the image file container

- Format: Embedded as bytes within the file structure
- Source: EXIF IFDs, IPTC IIM/XMP, ICC profile tags, container chunks
- Extraction: Direct parsing of embedded byte streams

### Registry B: Derived Analysis Registry

**Definition**: Values computed or inferred from decoded pixel data

- Format: Not stored, computed on extraction
- Source: Hash functions, image processing algorithms, ML models
- Extraction: Pixel decoding + algorithm execution

---

## 3) REGISTRY A: EMBEDDED METADATA

### A.1 Container/Format Header Metadata

Format-specific structural metadata embedded in file headers.

#### JPEG (image/jpeg)

| Field                 | Native Key             | Type     | Description                      | Extraction                   |
| --------------------- | ---------------------- | -------- | -------------------------------- | ---------------------------- |
| format_detected       | -                      | string   | Detected format (JPEG)           | Magic bytes: `\xff\xd8\xff`  |
| jfif_version          | APP0/Version           | rational | JFIF version (1.1, 1.2)          | ExifTool: `JFIFVersion`      |
| jfif_units            | APP0/Units             | int      | Units (0=no units, 1=DPI, 2=DPC) | ExifTool: `JFIFUnit`         |
| jfif_xdensity         | APP0/Xdensity          | int      | Horizontal density               | ExifTool: `ResolutionUnit`   |
| jfif_ydensity         | APP0/Ydensity          | int      | Vertical density                 | ExifTool: `ResolutionUnit`   |
| jfif_thumbnail        | APP0/Thumbnail         | bytes    | JFIF thumbnail                   | ExifTool: `JFIFThumbnail`    |
| adobe_version         | APP14/DCTEncodeVersion | int      | Adobe DCT version                | ExifTool: `DCTEncodeVersion` |
| adobe_flags           | APP14/DCTDecodeFlags   | int      | Adobe DCT flags                  | ExifTool: `DCTDecodeFlags`   |
| adobe_color_transform | APP14/ColorTransform   | int      | Adobe color transform            | ExifTool: `ColorTransform`   |
| xmp_packet            | APP1/XMP               | string   | XMP packet (max ~65KB typical)   | ExifTool: `XMP`              |
| exif_ifd_offset       | APP1/EXIF              | pointer  | EXIF IFD location                | ExifTool internal            |

#### PNG (image/png)

| Field                | Native Key                 | Type        | Description                      | Extraction                                |
| -------------------- | -------------------------- | ----------- | -------------------------------- | ----------------------------------------- |
| png_ihdr_width       | IHDR/Width                 | int         | Image width in pixels            | ExifTool: `ImageWidth`                    |
| png_ihdr_height      | IHDR/Height                | int         | Image height in pixels           | ExifTool: `ImageHeight`                   |
| png_ihdr_bit_depth   | IHDR/BitDepth              | int         | Bits per sample (1,2,4,8,16)     | ExifTool: `BitDepth`                      |
| png_ihdr_color_type  | IHDR/ColorType             | int         | Color type (0,2,3,4,6)           | ExifTool: `ColorType`                     |
| png_ihdr_compression | IHDR/Compression           | int         | Compression method (0)           | ExifTool: `Compression`                   |
| png_ihdr_filter      | IHDR/Filter                | int         | Filter method (0)                | ExifTool: `Filter`                        |
| png_ihdr_interlace   | IHDR/Interlace             | int         | Interlace method (0/1)           | ExifTool: `Interlace`                     |
| png_plte_present     | PLTE/                      | bool        | Palette chunk present            | ExifTool: `Palette`                       |
| png_plte_entries     | PLTE/Count                 | int         | Palette entry count              | ExifTool: `PaletteEntries`                |
| png_text_count       | tEXt/                      | int         | Number of tEXt chunks            | ExifTool: `TextFieldCount`                |
| png_text_keys        | tEXt/Keyword               | array       | Text chunk keywords              | ExifTool: `Text` (contains keyword:value) |
| png_ztxt_present     | zTXt/                      | bool        | Compressed text chunk present    | ExifTool: `Ztxt`                          |
| png_itxt_present     | iTXt/                      | bool        | International text chunk present | ExifTool: `Itxt`                          |
| png_exif_present     | eXIf/                      | bool        | EXIF chunk present               | ExifTool: `Exif`                          |
| png_icc_present      | iCCP/                      | bool        | ICC profile chunk present        | ExifTool: `ICCProfile`                    |
| png_icc_name         | iCCP/ProfileName           | string      | ICC profile name                 | ExifTool: `ICCProfileName`                |
| png_srgb_present     | sRGB/                      | bool        | sRGB chunk present               | ExifTool: `SRGBRendering`                 |
| png_gama_present     | gAMA/                      | bool        | Gamma chunk present              | ExifTool: `Gamma`                         |
| png_gama_gamma       | gAMA/Gamma                 | rational    | Gamma value                      | ExifTool: `Gamma`                         |
| png_chrm_present     | cHRM/                      | bool        | Chromaticity chunk present       | ExifTool: `Chromaticity`                  |
| png_chrm_white_point | cHRM/WhitePoint            | rational[2] | White point xy                   | ExifTool: `ChromaticityWhitePoint`        |
| png_chrm_primary     | cHRM/PrimaryChromaticities | rational[6] | Primary xyRGB                    | ExifTool: `ChromaticityPrimary`           |
| png_actl_present     | acTL/                      | bool        | Animation control present        | ExifTool: `AnimationControl`              |
| png_actl_frames      | acTL/FrameCount            | int         | Animation frame count            | ExifTool: `FrameCount`                    |
| png_fctl_sequence    | fcTL/                      | array       | Frame control entries            | ExifTool: `FrameControl`                  |

#### WebP (image/webp)

| Field              | Native Key     | Type   | Description                 | Extraction                     |
| ------------------ | -------------- | ------ | --------------------------- | ------------------------------ |
| webp_format        | RIFF/VP8       | string | VP8 format (lossy/lossless) | Magic: VP8/VP8L/VP8X           |
| webp_vp8_version   | VP8/Version    | int    | VP8 format version          | ExifTool: `VP8Version`         |
| webp_vp8l_present  | VP8L/          | bool   | Lossless format present     | ExifTool: `VP8L`               |
| webp_vp8x_present  | VP8X/          | bool   | Extended format present     | ExifTool: `VP8X`               |
| webp_anim_present  | ANIM/          | bool   | Animation chunk present     | ExifTool: `Animation`          |
| webp_anim_loops    | ANIM/LoopCount | int    | Animation loop count        | ExifTool: `AnimationLoopCount` |
| webp_alph_present  | ALPH/          | bool   | Alpha channel present       | ExifTool: `Alpha`              |
| webp_exif_present  | EXIF/          | bool   | EXIF chunk present          | ExifTool: `EXIF`               |
| webp_xmp_present   | XMP/           | bool   | XMP chunk present           | ExifTool: `XMP`                |
| webp_icc_present   | ICCP/          | bool   | ICC profile present         | ExifTool: `ICCProfile`         |
| webp_canvas_width  | VP8X/Width     | int    | Canvas width (VP8X)         | ExifTool: `ImageWidth`         |
| webp_canvas_height | VP8X/Height    | int    | Canvas height (VP8X)        | ExifTool: `ImageHeight`        |
| webp_flags         | VP8X/Flags     | int    | Feature flags               | ExifTool: `VP8XFlags`          |

#### TIFF (image/tiff)

| Field                | Native Key                      | Type    | Description                 | Extraction                             |
| -------------------- | ------------------------------- | ------- | --------------------------- | -------------------------------------- |
| tiff_byte_order      | Header                          | string  | Byte order (II/MM)          | Magic: `II` or `MM`                    |
| tiff_version         | Header/Version                  | int     | TIFF version (42)           | ExifTool: `TIFFVersion`                |
| ifd0_offset          | IFD0                            | pointer | First IFD offset            | ExifTool internal                      |
| exif_ifd_offset      | IFD0/ExifIFDPointer             | pointer | EXIF IFD location           | ExifTool: `ExifIFDPointer`             |
| gps_ifd_offset       | IFD0/GPSInfoIFDPointer          | pointer | GPS IFD location            | ExifTool: `GPSInfoIFDPointer`          |
| interop_ifd_offset   | EXIF/InteroperabilityIFDPointer | pointer | Interop IFD location        | ExifTool: `InteroperabilityIFDPointer` |
| thumbnail_ifd_offset | IFD1/                           | pointer | Thumbnail IFD location      | ExifTool: `ThumbnailIFDPointer`        |
| xmp_packet           | IFD0/XMP                        | string  | XMP packet embedded in TIFF | ExifTool: `XMP`                        |
| iptc_data            | IFD0/IPTC                       | bytes   | IPTC IIM embedded in TIFF   | ExifTool: `IPTC`                       |
| adobe_iptc_present   | APP13/                          | bool    | Photoshop IRB with IPTC     | ExifTool: `IPTC`                       |

#### HEIF/HEIC (image/heic, image/heif)

| Field                  | Native Key             | Type   | Description                    | Extraction                  |
| ---------------------- | ---------------------- | ------ | ------------------------------ | --------------------------- |
| heif_major_brand       | ftyp/MajorBrand        | string | Major brand (heic, heix, mif1) | ExifTool: `MajorBrand`      |
| heif_minor_version     | ftyp/MinorVersion      | int    | Minor version                  | ExifTool: `MinorVersion`    |
| heif_compatible_brands | ftype/CompatibleBrands | array  | Compatible brand list          | ExifTool: `CompatibleBrand` |
| heif_item_count        | iinf/ItemCount         | int    | Number of items                | ExifTool: `ItemCount`       |
| heif_exif_item         | ipco/Exif              | item   | EXIF item location             | ExifTool: `EXIF`            |
| heif_xmp_item          | ipco/XMP               | item   | XMP item location              | ExifTool: `XMP`             |
| heif_image_item        | ipco/Image             | item   | Primary image item             | ExifTool: `Image`           |
| heif_thumbnail_item    | ipco/Thumbnail         | item   | Thumbnail item                 | ExifTool: `Thumbnail`       |
| heif_primary_item      | ipma/PrimaryItem       | int    | Primary item ID                | ExifTool: `PrimaryItem`     |
| heif_width             | ispe/Width             | int    | Image width                    | ExifTool: `ImageWidth`      |
| heif_height            | ispe/Height            | int    | Image height                   | ExifTool: `ImageHeight`     |
| heif_color_profile     | ipco/ColorProfile      | item   | Color profile item             | ExifTool: `ICCProfile`      |

#### AVIF (image/avif)

| Field                  | Native Key             | Type   | Description              | Extraction                   |
| ---------------------- | ---------------------- | ------ | ------------------------ | ---------------------------- |
| avif_major_brand       | ftyp/MajorBrand        | string | Major brand (avif, mif1) | ExifTool: `MajorBrand`       |
| avif_minor_version     | ftyp/MinorVersion      | int    | Minor version            | ExifTool: `MinorVersion`     |
| avif_compatible_brands | ftype/CompatibleBrands | array  | Compatible brand list    | ExifTool: `CompatibleBrand`  |
| avif_item_count        | iinf/ItemCount         | int    | Number of items          | ExifTool: `ItemCount`        |
| avif_exif_item         | ipco/Exif              | item   | EXIF item                | ExifTool: `EXIF`             |
| avif_xmp_item          | ipco/XMP               | item   | XMP item                 | ExifTool: `XMP`              |
| avif_av1_item          | ipco/av1C              | item   | AV1 codec configuration  | ExifTool: `AV1Configuration` |
| avif_width             | ispe/Width             | int    | Image width              | ExifTool: `ImageWidth`       |
| avif_height            | ispe/Height            | int    | Image height             | ExifTool: `ImageHeight`      |
| avif_bit_depth         | pixi/BitsPerChannel    | array  | Bit depth per channel    | ExifTool: `BitsPerChannel`   |
| avif_color_profile     | ipco/ICC               | item   | ICC profile item         | ExifTool: `ICCProfile`       |

#### GIF (image/gif)

| Field                       | Native Key                                   | Type   | Description               | Extraction                           |
| --------------------------- | -------------------------------------------- | ------ | ------------------------- | ------------------------------------ |
| gif_version                 | Header                                       | string | GIF version (87a/89a)     | Magic: `GIF87a` or `GIF89a`          |
| gif_logical_width           | LogicalScreenDescriptor/Width                | int    | Logical screen width      | ExifTool: `ImageWidth`               |
| gif_logical_height          | LogicalScreenDescriptor/Height               | int    | Logical screen height     | ExifTool: `ImageHeight`              |
| gif_global_colors           | GlobalColorTable/                            | int    | Global color table size   | ExifTool: `HasGlobalColorTable`      |
| gif_global_color_resolution | GlobalColorTable/                            | int    | Color resolution          | ExifTool: `ColorResolutionDepth`     |
| gif_sort_flag               | GlobalColorTable/                            | int    | Global color sort flag    | ExifTool: `GlobalColorTableSortFlag` |
| gif_background              | LogicalScreenDescriptor/BackgroundColorIndex | int    | Background color index    | ExifTool: `BackgroundColor`          |
| gif_pixel_aspect            | ApplicationExtension/PixelAspect             | int    | Pixel aspect ratio        | ExifTool: `PixelAspectRatio`         |
| gif_animation_present       | GraphicsControlExtension/                    | bool   | Animation control present | ExifTool: `Animation`                |
| gif_frame_count             | GraphicsControlExtension/                    | int    | Frame count               | ExifTool: `FrameCount`               |
| gif_loop_count              | NETSCAPE2.0/Extension                        | int    | Loop count (0=infinite)   | ExifTool: `LoopCount`                |

#### PSD (image/x-photoshop)

| Field              | Native Key            | Type   | Description          | Extraction                |
| ------------------ | --------------------- | ------ | -------------------- | ------------------------- |
| psd_version        | Header/Version        | int    | PSD version (1, 2)   | ExifTool: `PSDVersion`    |
| psd_channels       | Header/Channels       | int    | Number of channels   | ExifTool: `Channels`      |
| psd_rows           | Header/Rows           | int    | Image height         | ExifTool: `ImageHeight`   |
| psd_columns        | Header/Columns        | int    | Image width          | ExifTool: `ImageWidth`    |
| psd_depth          | Header/Depth          | int    | Bits per channel     | ExifTool: `BitDepth`      |
| psd_mode           | Header/Mode           | int    | Color mode (0-9)     | ExifTool: `ColorMode`     |
| psd_mode_name      | ModeName              | string | Color mode name      | ExifTool: `ColorModeName` |
| psd_resource_count | ResourceSection/Count | int    | Number of resources  | ExifTool: `ResourceCount` |
| psd_layer_count    | LayerSection/Count    | int    | Number of layers     | ExifTool: `Layers`        |
| psd_has_alpha      | -                     | bool   | Has alpha channel    | ExifTool: `HasAlpha`      |
| psd_xmp_packet     | 0x0424 (Resource ID)  | string | Embedded XMP         | ExifTool: `XMP`           |
| psd_icc_profile    | 0x0404 (Resource ID)  | bytes  | Embedded ICC profile | ExifTool: `ICCProfile`    |
| psd_ipTC           | 0x0406 (Resource ID)  | bytes  | IPTC IIM data        | ExifTool: `IPTC`          |
| psd_thumbnail      | 0x0408 (Resource ID)  | bytes  | Thumbnail resource   | ExifTool: `Thumbnail`     |

#### Sidecar Patterns

| Pattern                   | Format | Description           | Extraction                |
| ------------------------- | ------ | --------------------- | ------------------------- |
| `*.xmp`                   | XML    | XMP sidecar file      | Match by filename pattern |
| `*.CR2.xmp`, `*.NEF.xmp`  | XML    | RAW + XMP sidecar     | Match by filename pattern |
| `*.jpg.xmp`, `*.jpeg.xmp` | XML    | JPEG + XMP sidecar    | Match by filename pattern |
| `*_original.xmp`          | XML    | Original file sidecar | Match by filename pattern |

---

### A.2 EXIF 3.0 Standard Metadata (CIPA DC-008-Translation-2024)

IFD0 (Main Image IFD) Tags

| Field             | EXIF Tag       | Type     | Sensitivity | Redactable | Extraction                   |
| ----------------- | -------------- | -------- | ----------- | ---------- | ---------------------------- |
| make              | 0x010F (271)   | ASCII    | Low         | Yes        | ExifTool: `Make`             |
| model             | 0x0110 (272)   | ASCII    | Low         | Yes        | ExifTool: `Model`            |
| software          | 0x0131 (305)   | ASCII    | Low         | Yes        | ExifTool: `Software`         |
| artist            | 0x013B (315)   | ASCII    | High        | Yes        | ExifTool: `Artist`           |
| copyright         | 0x8298 (33432) | ASCII    | Low         | Yes        | ExifTool: `Copyright`        |
| image_description | 0x010E (282)   | ASCII    | Low         | Yes        | ExifTool: `ImageDescription` |
| datetime          | 0x0132 (306)   | ASCII    | Moderate    | Yes        | ExifTool: `DateTime`         |
| subfile_type      | 0x00FE (254)   | LONG     | None        | No         | ExifTool: `SubfileType`      |
| orientation       | 0x0112 (274)   | SHORT    | None        | No         | ExifTool: `Orientation`      |
| x_resolution      | 0x011A (282)   | RATIONAL | None        | No         | ExifTool: `XResolution`      |
| y_resolution      | 0x011B (283)   | RATIONAL | None        | No         | ExifTool: `YResolution`      |
| resolution_unit   | 0x0128 (296)   | SHORT    | None        | No         | ExifTool: `ResolutionUnit`   |

EXIF IFD Tags

| Field                      | EXIF Tag       | Type        | Sensitivity | Redactable | Extraction                           |
| -------------------------- | -------------- | ----------- | ----------- | ---------- | ------------------------------------ |
| exposure_time              | 0x829A (33434) | RATIONAL    | None        | No         | ExifTool: `ExposureTime`             |
| f_number                   | 0x829D (33437) | RATIONAL    | None        | No         | ExifTool: `FNumber`                  |
| exposure_program           | 0x8822 (34866) | SHORT       | None        | No         | ExifTool: `ExposureProgram`          |
| iso_speed_ratings          | 0x8827 (34867) | SHORT       | None        | No         | ExifTool: `ISOSpeedRatings`          |
| sensitivity_type           | 0x8830 (34855) | SHORT       | None        | No         | ExifTool: `SensitivityType`          |
| exposure_bias_value        | 0x9204 (37380) | SRATIONAL   | None        | No         | ExifTool: `ExposureBiasValue`        |
| metering_mode              | 0x9207 (37383) | SHORT       | None        | No         | ExifTool: `MeteringMode`             |
| light_source               | 0x9208 (37384) | SHORT       | None        | No         | ExifTool: `LightSource`              |
| flash                      | 0x9209 (37385) | SHORT       | None        | No         | ExifTool: `Flash`                    |
| focal_length               | 0x920A (37386) | RATIONAL    | None        | No         | ExifTool: `FocalLength`              |
| focal_length_35mm          | 0xA405 (42016) | SHORT       | None        | No         | ExifTool: `FocalLengthIn35mmFilm`    |
| maker_note                 | 0x927C (37500) | UNDEFINED   | Low         | No         | ExifTool: `MakerNote`                |
| user_comment               | 0x9286 (37510) | UNDEFINED   | Moderate    | Yes        | ExifTool: `UserComment`              |
| date_time_original         | 0x9003 (36867) | ASCII       | Moderate    | Yes        | ExifTool: `DateTimeOriginal`         |
| date_time_digitized        | 0x9004 (36868) | ASCII       | Moderate    | Yes        | ExifTool: `DateTimeDigitized`        |
| shutter_speed_value        | 0x9201 (37377) | SRATIONAL   | None        | No         | ExifTool: `ShutterSpeedValue`        |
| aperture_value             | 0x9202 (37378) | RATIONAL    | None        | No         | ExifTool: `ApertureValue`            |
| brightness_value           | 0x9203 (37379) | SRATIONAL   | None        | No         | ExifTool: `BrightnessValue`          |
| exposure_mode              | 0xA402 (41985) | SHORT       | None        | No         | ExifTool: `ExposureMode`             |
| white_balance              | 0xA403 (41986) | SHORT       | None        | No         | ExifTool: `WhiteBalance`             |
| digital_zoom_ratio         | 0xA404 (41987) | RATIONAL    | None        | No         | ExifTool: `DigitalZoomRatio`         |
| scene_capture_type         | 0xA406 (41990) | SHORT       | None        | No         | ExifTool: `SceneCaptureType`         |
| contrast                   | 0xA408 (41992) | SHORT       | None        | No         | ExifTool: `Contrast`                 |
| saturation                 | 0xA409 (41993) | SHORT       | None        | No         | ExifTool: `Saturation`               |
| sharpness                  | 0xA40A (41994) | SHORT       | None        | No         | ExifTool: `Sharpness`                |
| device_setting_description | 0xA40B (41995) | UNDEFINED   | Low         | No         | ExifTool: `DeviceSettingDescription` |
| subject_distance_range     | 0xA40C (41996) | SHORT       | None        | No         | ExifTool: `SubjectDistanceRange`     |
| image_unique_id            | 0xA420 (42032) | ASCII       | Low         | No         | ExifTool: `ImageUniqueID`            |
| camera_owner_name          | 0xA430 (42033) | ASCII       | High        | Yes        | ExifTool: `CameraOwnerName`          |
| camera_serial_number       | 0xA431 (42034) | ASCII       | High        | Yes        | ExifTool: `CameraSerialNumber`       |
| lens_specification         | 0xA432 (42035) | RATIONAL[4] | Low         | No         | ExifTool: `LensSpecification`        |
| lens_make                  | 0xA433 (42036) | ASCII       | Low         | Yes        | ExifTool: `LensMake`                 |
| lens_model                 | 0xA434 (42037) | ASCII       | Low         | Yes        | ExifTool: `LensModel`                |
| lens_serial_number         | 0xA435 (42038) | ASCII       | High        | Yes        | ExifTool: `LensSerialNumber`         |
| color_space                | 0xA001 (40961) | SHORT       | None        | No         | ExifTool: `ColorSpace`               |
| pixel_x_dimension          | 0xA002 (40962) | LONG        | None        | No         | ExifTool: `PixelXDimension`          |
| pixel_y_dimension          | 0xA003 (40963) | LONG        | None        | No         | ExifTool: `PixelYDimension`          |

GPS IFD Tags

| Field                      | EXIF Tag    | Type        | Sensitivity | Redactable | Extraction                          |
| -------------------------- | ----------- | ----------- | ----------- | ---------- | ----------------------------------- |
| gps_version_id             | 0x0000 (0)  | BYTE[4]     | None        | No         | ExifTool: `GPSVersionID`            |
| gps_latitude_ref           | 0x0001 (1)  | ASCII       | High        | Yes        | ExifTool: `GPSLatitudeRef`          |
| gps_latitude               | 0x0002 (2)  | RATIONAL[3] | High        | Yes        | ExifTool: `GPSLatitude`             |
| gps_longitude_ref          | 0x0003 (3)  | ASCII       | High        | Yes        | ExifTool: `GPSLongitudeRef`         |
| gps_longitude              | 0x0004 (4)  | RATIONAL[3] | High        | Yes        | ExifTool: `GPSLongitude`            |
| gps_altitude_ref           | 0x0005 (5)  | BYTE        | Moderate    | Yes        | ExifTool: `GPSAltitudeRef`          |
| gps_altitude               | 0x0006 (6)  | RATIONAL    | Moderate    | Yes        | ExifTool: `GPSAltitude`             |
| gps_timestamp              | 0x0007 (7)  | RATIONAL[3] | Moderate    | Yes        | ExifTool: `GPSTimeStamp`            |
| gps_satellites             | 0x0008 (8)  | ASCII       | Moderate    | Yes        | ExifTool: `GPSSatellites`           |
| gps_status                 | 0x0009 (9)  | ASCII       | Moderate    | Yes        | ExifTool: `GPSStatus`               |
| gps_speed_ref              | 0x000C (12) | ASCII       | Moderate    | Yes        | ExifTool: `GPSSpeedRef`             |
| gps_speed                  | 0x000D (13) | RATIONAL    | Moderate    | Yes        | ExifTool: `GPSSpeed`                |
| gps_img_direction_ref      | 0x0010 (16) | ASCII       | Moderate    | Yes        | ExifTool: `GPSImgDirectionRef`      |
| gps_img_direction          | 0x0011 (17) | RATIONAL    | Moderate    | Yes        | ExifTool: `GPSImgDirection`         |
| gps_dest_latitude_ref      | 0x0013 (19) | ASCII       | High        | Yes        | ExifTool: `GPSDestLatitudeRef`      |
| gps_dest_latitude          | 0x0014 (20) | RATIONAL[3] | High        | Yes        | ExifTool: `GPSDestLatitude`         |
| gps_dest_longitude_ref     | 0x0015 (21) | ASCII       | High        | Yes        | ExifTool: `GPSDestLongitudeRef`     |
| gps_dest_longitude         | 0x0016 (22) | RATIONAL[3] | High        | Yes        | ExifTool: `GPSDestLongitude`        |
| gps_dest_bearing_ref       | 0x0017 (23) | ASCII       | Moderate    | Yes        | ExifTool: `GPSDestBearingRef`       |
| gps_dest_bearing           | 0x0018 (24) | RATIONAL    | Moderate    | Yes        | ExifTool: `GPSDestBearing`          |
| gps_dest_distance_ref      | 0x0019 (25) | ASCII       | Moderate    | Yes        | ExifTool: `GPSDestDistanceRef`      |
| gps_dest_distance          | 0x001A (26) | RATIONAL    | Moderate    | Yes        | ExifTool: `GPSDestDistance`         |
| gps_processing_method      | 0x001B (27) | ASCII       | Moderate    | Yes        | ExifTool: `GPSProcessingMethod`     |
| gps_area_information       | 0x001C (28) | ASCII       | High        | Yes        | ExifTool: `GPSAreaInformation`      |
| gps_date_stamp             | 0x001D (29) | ASCII       | Moderate    | Yes        | ExifTool: `GPSDateStamp`            |
| gps_dop                    | 0x001F (31) | RATIONAL    | Moderate    | Yes        | ExifTool: `GPSDOP`                  |
| gps_speed_accuracy         | 0x001E (30) | RATIONAL    | Moderate    | Yes        | ExifTool: `GPSSpeedAccuracy`        |
| gps_img_direction_accuracy | 0x001F (31) | RATIONAL    | Moderate    | Yes        | ExifTool: `GPSImgDirectionAccuracy` |
| gps_horiz_accuracy         | 0x001E (30) | RATIONAL    | Moderate    | Yes        | ExifTool: `GPSHorizontalAccuracy`   |
| gps_vert_accuracy          | 0x001F (31) | RATIONAL    | Moderate    | Yes        | ExifTool: `GPSVerticalAccuracy`     |

---

### A.3 IPTC Photo Metadata (IIM4 + XMP)

IPTC IIM4 Record Structure (Legacy Format)

| Field                           | Record | Dataset | Type           | Sensitivity | Redactable | Extraction                                |
| ------------------------------- | ------ | ------- | -------------- | ----------- | ---------- | ----------------------------------------- |
| record_version                  | 1      | 90      | SHORT          | None        | No         | ExifTool: `IPTCRecordVersion`             |
| object_name                     | 2      | 5       | STRING         | Low         | Yes        | ExifTool: `ObjectName`                    |
| edit_status                     | 2      | 7       | STRING         | None        | No         | ExifTool: `EditStatus`                    |
| urgency                         | 2      | 10      | STRING         | None        | No         | ExifTool: `Urgency`                       |
| subject_reference               | 2      | 12      | STRING         | Low         | Yes        | ExifTool: `SubjectReference`              |
| category                        | 2      | 15      | STRING         | Low         | Yes        | ExifTool: `Category`                      |
| supplemental_category           | 2      | 20      | STRING[3]      | Low         | Yes        | ExifTool: `SupplementalCategory`          |
| keywords                        | 2      | 25      | STRING[64]     | Low         | Yes        | ExifTool: `Keywords`                      |
| content_location_code           | 2      | 26      | STRING[3]      | Moderate    | Yes        | ExifTool: `ContentLocationCode`           |
| content_location_name           | 2      | 27      | STRING[64]     | Moderate    | Yes        | ExifTool: `ContentLocationName`           |
| release_date                    | 2      | 30      | DATE           | Moderate    | Yes        | ExifTool: `ReleaseDate`                   |
| release_time                    | 2      | 35      | TIME           | Moderate    | Yes        | ExifTool: `ReleaseTime`                   |
| expiration_date                 | 2      | 37      | DATE           | Low         | Yes        | ExifTool: `ExpirationDate`                |
| expiration_time                 | 2      | 38      | TIME           | Low         | Yes        | ExifTool: `ExpirationTime`                |
| special_instructions            | 2      | 40      | STRING         | Low         | Yes        | ExifTool: `SpecialInstructions`           |
| action_advisory                 | 2      | 42      | STRING[2]      | Low         | Yes        | ExifTool: `ActionAdvised`                 |
| reference_service               | 2      | 45      | STRING[2]      | Low         | Yes        | ExifTool: `ReferenceService`              |
| reference_date                  | 2      | 47      | DATE           | Low         | Yes        | ExifTool: `ReferenceDate`                 |
| reference_number                | 2      | 50      | STRING[8]      | Low         | Yes        | ExifTool: `ReferenceNumber`               |
| date_created                    | 2      | 55      | DATE           | Moderate    | Yes        | ExifTool: `DateCreated`                   |
| time_created                    | 2      | 60      | TIME           | Moderate    | Yes        | ExifTool: `TimeCreated`                   |
| digitization_date               | 2      | 62      | DATE           | Moderate    | Yes        | ExifTool: `DigitizationDate`              |
| digitization_time               | 2      | 63      | TIME           | Moderate    | Yes        | ExifTool: `DigitizationTime`              |
| byline                          | 2      | 80      | STRING[32][32] | High        | Yes        | ExifTool: `By-line`                       |
| byline_title                    | 2      | 85      | STRING[32]     | Low         | Yes        | ExifTool: `By-lineTitle`                  |
| city                            | 2      | 90      | STRING[32]     | Moderate    | Yes        | ExifTool: `City`                          |
| sublocation                     | 2      | 92      | STRING[32]     | High        | Yes        | ExifTool: `Sub-location`                  |
| province_state                  | 2      | 95      | STRING[32]     | Moderate    | Yes        | ExifTool: `Province/State`                |
| country_primary_location_code   | 2      | 100     | STRING[3]      | Moderate    | Yes        | ExifTool: `Country-PrimaryLocationCode`   |
| country_primary_location_name   | 2      | 101     | STRING[64]     | Moderate    | Yes        | ExifTool: `Country-PrimaryLocationName`   |
| original_transmission_reference | 2      | 103     | STRING[32]     | Low         | Yes        | ExifTool: `OriginalTransmissionReference` |
| headline                        | 2      | 105     | STRING[256]    | Low         | Yes        | ExifTool: `Headline`                      |
| credit                          | 2      | 110     | STRING[32]     | Low         | Yes        | ExifTool: `Credit`                        |
| source                          | 2      | 115     | STRING[32]     | Low         | Yes        | ExifTool: `Source`                        |
| copyright_notice                | 2      | 116     | STRING[128]    | Low         | Yes        | ExifTool: `CopyrightNotice`               |
| contact                         | 2      | 118     | STRING[128]    | High        | Yes        | ExifTool: `Contact`                       |
| caption_abstract                | 2      | 120     | STRING[2000]   | Low         | Yes        | ExifTool: `Caption-Abstract`              |
| writer_editor                   | 2      | 122     | STRING[32]     | High        | Yes        | ExifTool: `Writer-Editor`                 |
| image_type                      | 2      | 130     | STRING[2]      | None        | No         | ExifTool: `ImageType`                     |
| image_orientation               | 2      | 131     | STRING         | None        | No         | ExifTool: `ImageOrientation`              |
| language_identifier             | 2      | 135     | STRING[3]      | None        | No         | ExifTool: `LanguageIdentifier`            |

IPTC Extension Schema (XMP)

| Field                    | XMP Namespace                  | Type        | Sensitivity | Redactable | Extraction                         |
| ------------------------ | ------------------------------ | ----------- | ----------- | ---------- | ---------------------------------- |
| artwork_title            | iptcExt:ArtworkTitle           | bag[string] | Low         | Yes        | ExifTool: `ArtworkTitle`           |
| artwork_creator          | iptcExt:ArtworkCreator         | bag[string] | Low         | Yes        | ExifTool: `ArtworkCreator`         |
| artwork_copyright_notice | iptcExt:ArtworkCopyrightNotice | bag[string] | Low         | Yes        | ExifTool: `ArtworkCopyrightNotice` |
| artwork_source           | iptcExt:ArtworkSource          | bag[string] | Low         | Yes        | ExifTool: `ArtworkSource`          |
| graphic_content          | iptcExt:IntellectualGenre      | bag[string] | Low         | Yes        | ExifTool: `IntellectualGenre`      |
| scene_code               | iptcExt:SceneCode              | bag[string] | Low         | Yes        | ExifTool: `SceneCode`              |
| subject_code             | iptcExt:SubjectCode            | bag[string] | Low         | Yes        | ExifTool: `SubjectCode`            |
| event                    | iptcExt:Event                  | string      | Moderate    | Yes        | ExifTool: `Event`                  |
| dig_img_guid             | iptcExt:DigitalImageGUID       | string      | Low         | No         | ExifTool: `DigitalImageGUID`       |
| cataloguer_id            | iptcExt:CataloguerID           | bag[string] | High        | Yes        | ExifTool: `CataloguerID`           |
| person_shown             | iptcExt:PersonShown            | bag[string] | High        | Yes        | ExifTool: `PersonShown`            |
| organization_shown       | iptcExt:OrganizationShown      | bag[string] | Moderate    | Yes        | ExifTool: `OrganizationShown`      |
| product_shown            | iptcExt:ProductShown           | bag[string] | Moderate    | Yes        | ExifTool: `ProductShown`           |
| location_shown           | iptcExt:LocationShown          | struct      | High        | Yes        | ExifTool: `LocationShown`          |
| location_created         | iptcExt:LocationCreated        | struct      | Moderate    | Yes        | ExifTool: `LocationCreated`        |
| image_region             | iptcExt:ImageRegion            | array       | Moderate    | Yes        | ExifTool: `ImageRegion`            |
| ai_system_used           | iptcExt:AISystemUsed           | string      | Low         | Yes        | ExifTool: `AISystemUsed`           |
| ai_system_version        | iptcExt:AISystemVersionUsed    | string      | Low         | Yes        | ExifTool: `AISystemVersionUsed`    |
| ai_prompt                | iptcExt:AIPromptInformation    | string      | Low         | Yes        | ExifTool: `AIPromptInformation`    |
| ai_prompt_writer         | iptcExt:AIPromptWriterName     | string      | High        | Yes        | ExifTool: `AIPromptWriterName`     |

---

### A.4 XMP Namespaces (Adobe XMP Specification Part 2)

Dublin Core Namespace (dc)

| Field       | XMP Path       | Type            | Sensitivity | Redactable | Extraction              |
| ----------- | -------------- | --------------- | ----------- | ---------- | ----------------------- |
| title       | dc:title       | Alt-text        | Low         | Yes        | ExifTool: `Title`       |
| description | dc:description | Alt-text        | Low         | Yes        | ExifTool: `Description` |
| subject     | dc:subject     | bag[string]     | Low         | Yes        | ExifTool: `Subject`     |
| creator     | dc:creator     | bag[properName] | High        | Yes        | ExifTool: `Creator`     |
| contributor | dc:contributor | bag[properName] | Low         | Yes        | ExifTool: `Contributor` |
| publisher   | dc:publisher   | bag[properName] | Low         | Yes        | ExifTool: `Publisher`   |
| date        | dc:date        | bag[date]       | Moderate    | Yes        | ExifTool: `Date`        |
| type        | dc:type        | type            | None        | No         | ExifTool: `Type`        |
| format      | dc:format      | mimeType        | None        | No         | ExifTool: `Format`      |
| identifier  | dc:identifier  | uri             | Low         | Yes        | ExifTool: `Identifier`  |
| source      | dc:source      | uri             | Low         | Yes        | ExifTool: `Source`      |
| language    | dc:language    | bag[langCode]   | None        | No         | ExifTool: `Language`    |
| coverage    | dc:coverage    | string          | Low         | Yes        | ExifTool: `Coverage`    |
| rights      | dc:rights      | Alt-text        | Low         | Yes        | ExifTool: `Rights`      |

XMP Basic Namespace (xmp)

| Field         | XMP Path         | Type    | Sensitivity | Redactable | Extraction               |
| ------------- | ---------------- | ------- | ----------- | ---------- | ------------------------ |
| creator_tool  | xmp:CreatorTool  | string  | Low         | Yes        | ExifTool: `CreatorTool`  |
| create_date   | xmp:CreateDate   | date    | Moderate    | Yes        | ExifTool: `CreateDate`   |
| modify_date   | xmp:ModifyDate   | date    | Moderate    | Yes        | ExifTool: `ModifyDate`   |
| metadata_date | xmp:MetadataDate | date    | Moderate    | Yes        | ExifTool: `MetadataDate` |
| label         | xmp:Label        | string  | Low         | Yes        | ExifTool: `Label`        |
| rating        | xmp:Rating       | integer | None        | No         | ExifTool: `Rating`       |
| nickname      | xmp:Nickname     | string  | Low         | Yes        | ExifTool: `Nickname`     |

XMP Rights Management Namespace (xmpRights)

| Field         | XMP Path               | Type | Sensitivity | Redactable | Extraction               |
| ------------- | ---------------------- | ---- | ----------- | ---------- | ------------------------ |
| marked        | xmpRights:Marked       | bool | None        | No         | ExifTool: `Marked`       |
| web_statement | xmpRights:WebStatement | uri  | Low         | Yes        | ExifTool: `WebStatement` |
| usage_terms   | xmpRights:UsageTerms   | text | Low         | Yes        | ExifTool: `UsageTerms`   |
| certificate   | xmpRights:Certificate  | uri  | Low         | Yes        | ExifTool: `Certificate`  |
| marked        | xmpRights:Marked       | bool | None        | No         | ExifTool: `Marked`       |

XMP Media Management Namespace (xmpMM)

| Field                | XMP Path                 | Type   | Sensitivity | Redactable | Extraction                     |
| -------------------- | ------------------------ | ------ | ----------- | ---------- | ------------------------------ |
| document_id          | xmpMM:DocumentID         | uri    | Low         | No         | ExifTool: `DocumentID`         |
| instance_id          | xmpMM:InstanceID         | uri    | Low         | No         | ExifTool: `InstanceID`         |
| original_document_id | xmpMM:OriginalDocumentID | uri    | Low         | No         | ExifTool: `OriginalDocumentID` |
| rendition_class      | xmpMM:RenditionClass     | string | None        | No         | ExifTool: `RenditionClass`     |
| rendition_params     | xmpMM:RenditionParams    | string | None        | No         | ExifTool: `RenditionParams`    |
| version_id           | xmpMM:VersionID          | string | None        | No         | ExifTool: `VersionID`          |
| versions             | xmpMM:Versions           | array  | None        | No         | ExifTool: `Versions`           |
| history              | xmpMM:History            | array  | None        | No         | ExifTool: `History`            |
| derived_from         | xmpMM:DerivedFrom        | struct | Low         | No         | ExifTool: `DerivedFrom`        |

Photoshop Namespace (photoshop)

| Field              | XMP Path                    | Type   | Sensitivity | Redactable | Extraction                    |
| ------------------ | --------------------------- | ------ | ----------- | ---------- | ----------------------------- |
| color_mode         | photoshop:ColorMode         | int    | None        | No         | ExifTool: `ColorMode`         |
| icc_profile        | photoshop:ICCProfile        | string | None        | No         | ExifTool: `ICCProfile`        |
| caption_writer     | photoshop:CaptionWriter     | string | High        | Yes        | ExifTool: `CaptionWriter`     |
| headline           | photoshop:Headline          | string | Low         | Yes        | ExifTool: `Headline`          |
| instructions       | photoshop:Instructions      | string | Low         | Yes        | ExifTool: `Instructions`      |
| date_created       | photoshop:DateCreated       | date   | Moderate    | Yes        | ExifTool: `DateCreated`       |
| creator_address    | photoshop:CreatorAddress    | string | High        | Yes        | ExifTool: `CreatorAddress`    |
| creator_city       | photoshop:CreatorCity       | string | Moderate    | Yes        | ExifTool: `CreatorCity`       |
| creator_state      | photoshop:CreatorState      | string | Moderate    | Yes        | ExifTool: `CreatorState`      |
| creator_zip        | photoshop:CreatorPostalCode | string | High        | Yes        | ExifTool: `CreatorPostalCode` |
| creator_country    | photoshop:CreatorCountry    | string | Moderate    | Yes        | ExifTool: `CreatorCountry`    |
| creator_work_tel   | photoshop:CreatorWorkPhone  | string | High        | Yes        | ExifTool: `CreatorWorkPhone`  |
| creator_work_email | photoshop:CreatorWorkEmail  | string | High        | Yes        | ExifTool: `CreatorWorkEmail`  |

---

### A.5 ICC Profile Metadata (ICC.1:2022 v4.4.0)

Profile Header Tags

| Field            | Tag ID           | Type     | Sensitivity | Redactable | Extraction                   |
| ---------------- | ---------------- | -------- | ----------- | ---------- | ---------------------------- |
| profile_version  | version          | DWORD    | None        | No         | ExifTool: `ProfileVersion`   |
| profile_class    | device_class     | DWORD    | None        | No         | ExifTool: `ProfileClass`     |
| color_space      | color_space      | DWORD    | None        | No         | ExifTool: `ColorSpace`       |
| connection_space | pcs              | DWORD    | None        | No         | ExifTool: `PCS`              |
| profile_datetime | datetime         | DWORD    | None        | No         | ExifTool: `ProfileDateTime`  |
| signature        | signature        | DWORD    | None        | No         | ExifTool: `ProfileSignature` |
| platform         | platform         | DWORD    | None        | No         | ExifTool: `Platform`         |
| flags            | flags            | DWORD    | None        | No         | ExifTool: `ProfileFlags`     |
| rendering_intent | rendering_intent | DWORD    | None        | No         | ExifTool: `RenderingIntent`  |
| illuminant       | illuminant       | XYZ      | None        | No         | ExifTool: `Illuminant`       |
| creator          | creator          | DWORD    | None        | No         | ExifTool: `ProfileCreator`   |
| profile_id       | profile_id       | BYTE[16] | Low         | No         | ExifTool: `ProfileID`        |

Profile Tag Descriptors

| Field        | Tag ID | Type                  | Sensitivity | Redactable | Extraction                     |
| ------------ | ------ | --------------------- | ----------- | ---------- | ------------------------------ |
| description  | desc   | multiLocalizedUnicode | None        | No         | ExifTool: `ProfileDescription` |
| copyright    | cprt   | text                  | Low         | Yes        | ExifTool: `ProfileCopyright`   |
| white_point  | wtpt   | XYZ                   | None        | No         | ExifTool: `WhitePoint`         |
| red_matrix   | rXYZ   | XYZ                   | None        | No         | ExifTool: `RedMatrixColumn`    |
| green_matrix | gXYZ   | XYZ                   | None        | No         | ExifTool: `GreenMatrixColumn`  |
| blue_matrix  | bXYZ   | XYZ                   | None        | No         | ExifTool: `BlueMatrixColumn`   |
| red_trc      | rTRC   | curve                 | None        | No         | ExifTool: `RedTRC`             |
| green_trc    | gTRC   | curve                 | None        | No         | ExifTool: `GreenTRC`           |
| blue_trc     | bTRC   | curve                 | None        | No         | ExifTool: `BlueTRC`            |

---

### A.6 Camera MakerNotes (Vendor-Specific)

Note: MakerNotes are proprietary binary formats. ExifTool maintains comprehensive tag databases.

#### Canon MakerNotes

| Field                      | Tag ID | Type   | Sensitivity | Redactable | Extraction                     |
| -------------------------- | ------ | ------ | ----------- | ---------- | ------------------------------ |
| canon_camera_settings      | 0x0001 | binary | Low         | No         | ExifTool: `CameraSettings`     |
| canon_lens_info            | 0x0002 | binary | Low         | No         | ExifTool: `LensInfo`           |
| canon_firmware_version     | 0x0009 | ASCII  | None        | No         | ExifTool: `FirmwareVersion`    |
| canon_shutter_count        | 0x0035 | LONG   | Low         | No         | ExifTool: `ShutterCount`       |
| canon_af_info              | 0x0003 | binary | None        | No         | ExifTool: `AFInfo`             |
| canon_picture_style        | 0x0020 | binary | None        | No         | ExifTool: `PictureStyle`       |
| canon_color_space          | 0x0013 | SHORT  | None        | No         | ExifTool: `ColorSpace`         |
| canon_lens_model           | 0x0015 | ASCII  | Low         | Yes        | ExifTool: `LensModel`          |
| canon_lens_serial_number   | 0x0016 | ASCII  | High        | Yes        | ExifTool: `LensSerialNumber`   |
| canon_image_unique_id      | 0x0038 | ASCII  | Low         | No         | ExifTool: `ImageUniqueID`      |
| canon_owner_name           | 0x0010 | ASCII  | High        | Yes        | ExifTool: `OwnerName`          |
| canon_camera_serial_number | 0x0015 | ASCII  | High        | Yes        | ExifTool: `CameraSerialNumber` |
| canon_af_points            | 0x0019 | binary | None        | No         | ExifTool: `AFPoints`           |
| canon_flash_information    | 0x001A | binary | None        | No         | ExifTool: `FlashInfo`          |
| canon_bracket_mode         | 0x0021 | binary | None        | No         | ExifTool: `BracketMode`        |
| canon_bracket_value        | 0x0022 | binary | None        | No         | ExifTool: `BracketValue`       |
| canon_lens_type            | 0x001E | binary | None        | No         | ExifTool: `LensType`           |

#### Nikon MakerNotes

| Field                    | Tag ID | Type   | Sensitivity | Redactable | Extraction                    |
| ------------------------ | ------ | ------ | ----------- | ---------- | ----------------------------- |
| nikon_camera_settings    | 0x0001 | binary | Low         | No         | ExifTool: `CameraSettings`    |
| nikon_lens_data          | 0x0002 | binary | Low         | No         | ExifTool: `LensData`          |
| nikon_firmware_version   | 0x0010 | ASCII  | None        | No         | ExifTool: `FirmwareVersion`   |
| nikon_shutter_count      | 0x0039 | LONG   | Low         | No         | ExifTool: `ShutterCount`      |
| nikon_af_info            | 0x0003 | binary | None        | No         | ExifTool: `AFInfo`            |
| nikon_lens_id            | 0x0004 | LONG   | None        | No         | ExifTool: `LensID`            |
| nikon_lens_type          | 0x0005 | BYTE   | None        | No         | ExifTool: `LensType`          |
| nikon_focus_mode         | 0x0007 | binary | None        | No         | ExifTool: `FocusMode`         |
| nikon_flash_setting      | 0x0008 | binary | None        | No         | ExifTool: `FlashSetting`      |
| nikon_white_balance      | 0x0009 | binary | None        | No         | ExifTool: `WhiteBalance`      |
| nikon_color_mode         | 0x000A | binary | None        | No         | ExifTool: `ColorMode`         |
| nikon_picture_control    | 0x000B | binary | None        | No         | ExifTool: `PictureControl`    |
| nikon_world_time         | 0x000C | binary | None        | No         | ExifTool: `WorldTime`         |
| nikon_iso_info           | 0x000D | binary | None        | No         | ExifTool: `ISOInfo`           |
| nikon_active_d_lighting  | 0x000E | binary | None        | No         | ExifTool: `ActiveDLighting`   |
| nikon_vignette_control   | 0x0011 | binary | None        | No         | ExifTool: `VignetteControl`   |
| nikon_image_size         | 0x0012 | binary | None        | No         | ExifTool: `ImageSize`         |
| nikon_distortion_control | 0x0013 | binary | None        | No         | ExifTool: `DistortionControl` |
| nikon_auto_distortion    | 0x0014 | binary | None        | No         | ExifTool: `AutoDistortion`    |
| nikon_lens_serial_number | 0x0015 | ASCII  | High        | Yes        | ExifTool: `LensSerialNumber`  |
| nikon_body_serial_number | 0x0016 | ASCII  | High        | Yes        | ExifTool: `BodySerialNumber`  |
| nikon_af_info_2          | 0x0018 | binary | None        | No         | ExifTool: `AFInfo2`           |

#### Sony MakerNotes

| Field                   | Tag ID | Type   | Sensitivity | Redactable | Extraction                     |
| ----------------------- | ------ | ------ | ----------- | ---------- | ------------------------------ |
| sony_camera_settings    | 0x0001 | binary | Low         | No         | ExifTool: `CameraSettings`     |
| sony_lens_info          | 0x0002 | binary | Low         | No         | ExifTool: `LensInfo`           |
| sony_firmware_version   | 0x0003 | ASCII  | None        | No         | ExifTool: `FirmwareVersion`    |
| sony_shutter_count      | 0x0010 | LONG   | Low         | No         | ExifTool: `ShutterCount`       |
| sony_image_quality      | 0x0011 | binary | None        | No         | ExifTool: `ImageQuality`       |
| sony_focus_mode         | 0x0012 | binary | None        | No         | ExifTool: `FocusMode`          |
| sony_af_mode            | 0x0013 | binary | None        | No         | ExifTool: `AFMode`             |
| sony_face_detection     | 0x0014 | binary | None        | No         | ExifTool: `FaceDetection`      |
| sony_metadata_version   | 0x0015 | ASCII  | None        | No         | ExifTool: `MetadataVersion`    |
| sony_lens_model         | 0x001B | ASCII  | Low         | Yes        | ExifTool: `LensModel`          |
| sony_lens_serial_number | 0x001C | ASCII  | High        | Yes        | ExifTool: `LensSerialNumber`   |
| sony_body_serial_number | 0x001D | ASCII  | High        | Yes        | ExifTool: `CameraSerialNumber` |
| sony_owner_name         | 0x001E | ASCII  | High        | Yes        | ExifTool: `OwnerName`          |

---

## 4) REGISTRY B: DERIVED ANALYSIS

These fields are NOT embedded in files. They are computed during extraction.

### B.1 Perceptual Hashes

| Field           | Algorithm        | Description                  | Sensitivity | Extraction        |
| --------------- | ---------------- | ---------------------------- | ----------- | ----------------- |
| phash_dct       | pHash DCT        | Perceptual hash (64-bit)     | None        | ImageHash library |
| phash_dhash     | dHash            | Gradient-based hash (64-bit) | None        | ImageHash library |
| phash_ahash     | aHash            | Average hash (64-bit)        | None        | ImageHash library |
| phash_blockhash | blockHash        | Block-based hash (64-bit)    | None        | ImageHash library |
| phash_imagehash | ImageHash object | Full hash object             | None        | ImageHash library |

### B.2 Image Forensics Metrics

| Field                  | Metric                 | Description                          | Sensitivity | Extraction       |
| ---------------------- | ---------------------- | ------------------------------------ | ----------- | ---------------- |
| ela_estimated_quality  | Error Level Analysis   | Estimated JPEG quality               | None        | Custom algorithm |
| ela_peak_deviation     | ELA                    | Peak deviation in compressed regions | None        | Custom algorithm |
| noise_estimate         | Noise analysis         | Estimated noise level                | None        | Custom algorithm |
| noise_consistency      | Noise pattern          | CFA pattern consistency              | None        | Custom algorithm |
| manipulation_suspected | Manipulation detection | Suspicion of editing                 | None        | Multiple signals |
| cfa_pattern_detected   | CFA detection          | Color filter array pattern           | None        | Custom algorithm |
| quantization_issues    | JPEG artifacts         | Quantization table anomalies         | None        | Custom algorithm |
| histogram_analysis     | Histogram              | Histogram features                   | None        | Custom algorithm |

### B.3 ML-Derived Metadata

| Field                | Model            | Description               | Sensitivity | Extraction      |
| -------------------- | ---------------- | ------------------------- | ----------- | --------------- |
| scene_classification | CNN              | Predicted scene category  | None        | Custom ML model |
| object_detection     | YOLO             | Detected objects          | Low         | Custom ML model |
| face_regions         | Face detector    | Bounding boxes of faces   | High        | Custom ML model |
| image_quality_score  | Quality model    | Overall quality estimate  | None        | Custom ML model |
| aesthetic_score      | Aesthetic model  | Predicted aesthetic score | None        | Custom ML model |
| nsfw_score           | Moderation model | NSFW probability          | None        | Custom ML model |

---

## 5) EXTRACTION PIPELINE

### Stage 1: Format Detection

```python
def detect_format(filepath: str) -> Dict[str, Any]:
    """Detect image format using magic bytes (first 32 bytes)."""
    with open(filepath, 'rb') as f:
        header = f.read(32)

    signatures = {
        b'\xff\xd8\xff': ('JPEG', 'image/jpeg'),
        b'\x89PNG\r\n\x1a\n': ('PNG', 'image/png'),
        b'GIF87a': ('GIF', 'image/gif'),
        b'GIF89a': ('GIF', 'image/gif'),
        b'II*\x00': ('TIFF', 'image/tiff'),  # Little-endian
        b'MM\x00*': ('TIFF', 'image/tiff'),  # Big-endian
        b'RIFF': ('WebP', 'image/webp'),  # Check for WebP
        b'ftyp': ('HEIF', 'image/heic'),  # Check for HEIF/AVIF
        b'8BPS': ('PSD', 'image/x-photoshop'),
        b'BM': ('BMP', 'image/bmp'),
    }

    for magic, (fmt, mime) in signatures.items():
        if header.startswith(magic):
            return {'format': fmt, 'mime': mime, 'confidence': 'high'}

    return {'format': 'Unknown', 'mime': 'application/octet-stream', 'confidence': 'low'}
```

### Stage 2: Metadata Extraction (Two-Layer Approach)

**Layer 1: Raw Dump (Max Coverage)**

```bash
exiftool -j -a -G1 -h -s "$file"
```

Output: All tags with namespaces, max coverage (29,026 tags)

**Layer 2: Canonical Mapping (Product Use)**

- Define canonical key for each embedded field
- Apply normalization rules
- Apply redaction policies
- Return structured output

### Stage 3: Derived Analysis (Optional)

```python
def compute_perceptual_hashes(image_path: str) -> Dict[str, Any]:
    """Compute perceptual hashes for duplicate detection."""
    from imagehash import phash, average_hash, dhash, blockhash
    from PIL import Image

    with Image.open(image_path) as img:
        img_gray = img.convert('L')
        return {
            'phash_dct': str(phash(img_gray)),
            'phash_ahash': str(average_hash(img_gray)),
            'phash_dhash': str(dhash(img_gray)),
            'phash_blockhash': str(blockhash(img_gray)),
        }

def compute_ela(image_path: str) -> Dict[str, Any]:
    """Compute Error Level Analysis metrics."""
    # Load image at multiple quality re-saves
    # Compute pixel differences
    # Return quality estimate and deviation metrics
```

### Stage 4: Normalization

| Field Type | Normalization Rule                              |
| ---------- | ----------------------------------------------- |
| DateTime   | Parse multiple formats → ISO 8601 with timezone |
| GPS DMS    | Convert to decimal degrees, validate range      |
| Rational   | Convert to float, validate reasonable ranges    |
| Strings    | Unicode NFC normalization, strip nulls          |
| Arrays     | Flatten or keep as array based on schema        |
| Booleans   | Normalize to true/false                         |

### Stage 5: Redaction Policy

**Always Redact** (High Sensitivity):

- GPS coordinates
- Device serials (camera, lens, body)
- Owner names
- Contact information
- Person shown names

**Default Redact** (Moderate Sensitivity):

- DateTime fields (unless required)
- Location fields (city, country)
- Creator names

**Keep by Default** (None/Low Sensitivity):

- Camera make/model
- Exposure settings
- Color profile info
- Format/structural metadata

---

## 6) TEST MATRIX

### Embedded Metadata Tests

| Case ID         | Format   | Test Description       | Expected Output                |
| --------------- | -------- | ---------------------- | ------------------------------ |
| EMB-JPEG-001    | JPEG     | Full EXIF + IPTC + XMP | All 3 embedded sources present |
| EMB-JPEG-002    | JPEG     | EXIF only              | Only EXIF fields, no IPTC/XMP  |
| EMB-JPEG-003    | JPEG     | XMP only               | Only XMP fields, no EXIF/IPTC  |
| EMB-JPEG-004    | JPEG     | No metadata            | Empty embedded sections        |
| EMB-JPEG-005    | JPEG     | Corrupted EXIF         | Skip EXIF, extract IPTC/XMP    |
| EMB-PNG-001     | PNG      | Text chunks + ICC      | Text + ICC fields present      |
| EMB-PNG-002     | PNG      | Animation + eXIf       | Animation + EXIF fields        |
| EMB-WEBP-001    | WebP     | VP8X + EXIF + XMP      | Container + both metadata      |
| EMB-TIFF-001    | TIFF     | Multi-page IFD         | IFD0 + IFD1 (thumbnail)        |
| EMB-HEIF-001    | HEIC     | EXIF + XMP items       | Both item types present        |
| EMB-PSD-001     | PSD      | Layers + XMP + ICC     | All 3 embedded sources         |
| EMB-SIDECAR-001 | JPEG+XMP | Sidecar pair           | Match XMP to JPEG metadata     |

### Derived Analysis Tests

| Case ID          | Test Description | Expected Output             |
| ---------------- | ---------------- | --------------------------- |
| DERIVE-PHASH-001 | Identical images | Hashes match exactly        |
| DERIVE-PHASH-002 | Similar images   | Hashes within threshold     |
| DERIVE-PHASH-003 | Different images | Hashes differ significantly |
| DERIVE-ELA-001   | Uncompressed     | High ELA quality (~100%)    |
| DERIVE-ELA-002   | JPEG 95%         | Medium ELA quality (~95%)   |
| DERIVE-ELA-003   | JPEG 50%         | Low ELA quality (~50%)      |
| DERIVE-ELA-004   | Edited image     | High deviation regions      |

---

## 7) COVERAGE CLAIMS (Revised)

**Embedded Metadata Registry:**

- EXIF 3.0: ~250 defined tags (IFD0 + EXIF IFD + GPS IFD + thumbnail IFD)
- IPTC IIM4: ~50 record/dataset combinations
- IPTC Extension XMP: ~20 properties
- XMP Namespaces: ~50 properties across 6 namespaces
- ICC Profile Header: ~15 header fields + 10+ tag descriptors
- Container-specific: Format-dependent (15-30 per format)
- MakerNotes: Vendor-specific, hundreds of tags per vendor (ExifTool has 29k total)

**Note on Coverage Numbers:**

- ExifTool recognizes 29,026 tag entries across all formats
- Canon alone has ~1,500 MakerNote tags
- No single "universal" set of image metadata fields exists
- Coverage is format-dependent and use-case dependent
- This registry defines canonical embedded fields for common use cases

**Derived Analysis Registry:**

- Perceptual hashes: 4 hash algorithms
- Forensics metrics: 8+ metrics
- ML-derived: Variable based on model

---

## 8) KNOWN GAPS

| Gap                        | Reason                              | Impact | Next Action                    |
| -------------------------- | ----------------------------------- | ------ | ------------------------------ |
| Full HEIF/AVIF box parsing | Complex ISOBMFF structure           | Medium | Use ExifTool, monitor libheif  |
| C2PA manifest validation   | Requires cryptographic verification | Medium | Implement C2PA library         |
| Adobe DNG MakerNotes       | Proprietary formats                 | Low    | Continue mapping from ExifTool |
| Vendor tag documentation   | Incomplete public specs             | Low    | Continue mapping from ExifTool |

---

**Document Status:** Corrected v1.1  
**Next Review:** 2026-04-01  
**Owner:** MetaExtract Engineering Team
