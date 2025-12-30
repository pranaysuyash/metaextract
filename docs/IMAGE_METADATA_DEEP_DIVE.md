**Image Metadata Deep Dive (15,000+ fields)**

Scope
- Goal: Full, forensically reliable image metadata extraction across EXIF, MakerNotes, IPTC, XMP, ICC, and computational photography tags.
- Primary source of truth: ExifTool for breadth; Pillow/exifread for fallback; ICC via Pillow/ImageCms.
- Output targets: `exif`, `exif_ifd`, `gps`, `interoperability`, `thumbnail_metadata`, `embedded_thumbnails`, `makernote`, `iptc`, `xmp`, `xmp_namespaces`, `icc_profile`, `image_container`, `image`, `thumbnail`, `mobile_metadata`, `camera_360`, `normalized`.

Extraction Sources
- ExifTool CLI: full EXIF, MakerNotes, IPTC, XMP, ICC, composite, camera/vendor tags.
- Pillow: image properties, embedded ICC presence, thumbnail sizes.
- exifread: fallback EXIF/GPS when ExifTool unavailable.
- python-xmp-toolkit/iptcinfo3: fallback IPTC/XMP parsing.
- ImageCms (Pillow): ICC profile header details.

Coverage Map (by category)
- EXIF Core (1,200+): Full via ExifTool; fallback partial via exifread.
- GPS (50+): Full via ExifTool; fallback via exifread with decimal conversion.
- Interop IFD (30+): ExifTool InteropIFD surfaced in `interoperability` + `exif_ifd.interop`.
- Thumbnail IFD (15+): IFD1 + Preview tags surfaced in `thumbnail_metadata` + `exif_ifd.thumbnail`.
- MakerNotes (7,000+): ExifTool vendor groups mapped into `makernote` by manufacturer.
- IPTC Core/Extension (150+): ExifTool full; fallback via iptcinfo3 (Core).
- XMP (500+): ExifTool with full namespaces in `xmp` + `xmp_namespaces`; fallback via python-xmp-toolkit.
- Color Management (200+): ICC tags via ExifTool (`icc_profile`) + ICC presence/details via Pillow/ImageCms.
- Smartphone/Computational (300+): ExifTool MakerNotes + XMP namespaces (GCamera, GDepth, GPano, Apple) surfaced in `mobile_metadata`.

Key Vendor MakerNotes (sample groupings)
- Canon: CameraSettings, ShotInfo, PictureStyle, AFInfo, LensInfo
- Nikon: ISO, ShotInfo, ColorBalance, LensData, FlashInfo
- Sony: AFInfo, ShutterCount, InternalSerialNumber
- Fujifilm: FilmMode, GrainEffect, WhiteBalance
- Olympus: Equipment, ImageProcessing, FocusInfo
- Panasonic: Quality, SpecialMode, AFPointPosition
- DJI/GoPro: drone/action camera telemetry and camera settings

XMP Namespace Priorities
- Core: dc, xmp, xmpMM, xmpRights
- Adobe: photoshop, crs (Camera Raw), lr (Lightroom)
- IPTC: Iptc4xmpCore, Iptc4xmpExt
- Google: GCamera, GDepth, GPano
- Apple: Camera/LivePhoto attributes in MakerNotes + XMP
- Custom namespaces: preserved as-is under `xmp`

Normalization Targets
- Camera/lens normalization, exposure triangle, searchable text (see `metadata_mapper`).
- Standardized GPS lat/long decimal + map URLs.
- Unified vendor fields (e.g., shutter count, serials) when present.

Current Implementation Notes
- ExifTool runs with `-All` and grouped tags; MakerNotes are nested by manufacturer.
- EXIF IFDs are preserved in `exif_ifd` while `exif` stays flattened for mapper compatibility.
- XMP stored as raw tag dictionaries plus `xmp_namespaces` for canonical namespaces.
- Image properties include dimensions, DPI, animation, ICC presence; ICC header, tag table, and tag details live under `icc_profile`.
- Thumbnails include embedded payload extraction, generated preview dimensions, and EXIF IFD1/Preview tags.

Gaps to Close (implementation targets)
- Canonical normalization for additional MakerNote fields across vendors (e.g., focus and drive modes).
- Expand 360° camera vendor tags and GPano field coverage as new sample files appear.
- Optional extraction of binary thumbnail payloads (size-only vs actual data).
- 360/GPano enrichment in dedicated `camera_360` output (shared with mobile metadata).

Acceptance Criteria
- Image files with extensive MakerNotes report vendor fields without loss.
- Smartphone images report computational metadata (Live Photo, MotionPhoto, depth).
- ICC profile header fields extracted when present.
- EXIF/GPS/Interop/Thumbnail tags surfaced and countable in output.
