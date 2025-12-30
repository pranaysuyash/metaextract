# Image Metadata Roadmap (15,000+ fields)

Goal
- Deliver complete image metadata coverage across EXIF/IFD, MakerNotes, IPTC, XMP, ICC, and mobile/computational tags with minimal loss and clear grouping.

Completed (this pass)
- ExifTool grouping fixed to capture IFD0/ExifIFD/SubIFD/GPS/InteropIFD/IFD1 into `exif_ifd`, `interoperability`, and `thumbnail_metadata`.
- XMP namespaces expanded into `xmp_namespaces` while keeping `xmp` flat for mapper compatibility.
- ICC profile tags surfaced via ExifTool (`icc_profile`) plus header + tag table parsing in `image`.
- Mobile/computational parsing upgraded to use ExifTool MakerNotes + XMP namespaces (GCamera/GDepth/GPano) in `mobile_metadata`.
- New sections exposed in API responses: `exif_ifd`, `interoperability`, `thumbnail_metadata`, `image_container`, `icc_profile`, `xmp_namespaces`.
- MakerNote normalization for shutter count, serials, firmware, and focus fields into canonical keys.
- XMP namespace and interoperability sections surfaced in the UI.
- Embedded thumbnail payload extraction with hashes and MIME detection.
- 360/GPano metadata wired into `camera_360` output and surfaced in the UI.
- ICC tag-type parsing for desc/text/XYZ/curve/parametric data.

Short-Term (next sprint)

Mid-Term (phase 2)
- RAW container metadata deep dive (DNG/CR3/NEF/ARW/RAF).
- Computational photography metadata relationships (depth map linkages, motion photo offsets).
- Field-level provenance (which parser/tool sourced each tag).

Validation
- Synthetic unit test covers ExifTool group routing (IFD/GPS/ICC/XMP/MakerNotes).
- Real-world sample set from iPhone/Pixel/Samsung to verify mobile/computational tags.
