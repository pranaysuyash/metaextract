**Scientific/Technical Metadata Deep Dive (15,000+ fields)**

Scope
- Goal: High coverage across DICOM, FITS, OME-TIFF, GeoTIFF, LAS/LAZ, and microscopy formats.
- Primary sources: pydicom, Pillow, and custom binary parsers.
- Output targets: `scientific` with format/type-specific fields.

Extraction Sources
- DICOM: pydicom for patient/study/series/image/equipment tags.
- FITS: header card parsing for astronomy keywords.
- OME-TIFF/OME-XML: TIFF tag parsing + XML inspection.
- GeoTIFF: GeoKeyDirectoryTag + model transforms.
- LAS/LAZ: header + VLR parsing (projection info).

Coverage Map (by category)
- DICOM: patient/study/series/image/equipment/VOI LUT/SOP tags.
- FITS: telescope, instrument, observation time, exposure, axes.
- GeoTIFF: pixel scale, tiepoints, transforms, geokeys.
- LAS/LAZ: header fields, point counts, scale/offsets, bounding box, projection VLRs.
- Microscopy: basic TIFF tags for CZI/LIF/ND2 and OME detection.

Current Implementation Notes
- GeoTIFF parsing reads core tags and parses GeoKeyDirectory with numeric/ascii params.
- LAS parsing reads standard header and projection VLRs (GeoTIFF keys, WKT).
- TIFF subtype detection distinguishes OME-TIFF vs GeoTIFF vs generic TIFF.

Gaps to Close (implementation targets)
- DICOM private tags and structured reports.
- FITS extensions and WCS keyword parsing.
- LAS extra bytes VLR parsing.
- HDF5/NetCDF integration in the main engine (currently in comprehensive engine).

Acceptance Criteria
- Scientific formats yield structured metadata without loss of core tags.
- GeoTIFF and LAS projection metadata are detected and surfaced.
