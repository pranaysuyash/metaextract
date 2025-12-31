# Pending Extraction Plan

This file lists items that require additional planning before implementation. Each entry includes the file, reason, and any field names currently available (or the gap if missing).

## Placeholder Registries (No Field Lists in Repo)
These modules only return a numeric count and do not include actual registry field definitions, so a full raw registry dump is not possible until the source registry lists are added.

## Notes
- ID3 extended tag mappings are now fully enumerated from `server/extractor/modules/id3_frames_complete.py`.
- `server/extractor/modules/aerospace_registry.py`
  - Reason: No registry list in code (count only). Needs ARINC 429/717 + CCSDS label registry source.
  - Field names: Not present in repo (needs import from official specs).
  - Source leads: ARINC 429/717 label lists, CCSDS packet data dictionaries (public CCSDS blue books).
- `server/extractor/modules/agriculture_registry.py`
  - Reason: No registry list in code (count only). Needs AgTech schema/field list.
  - Field names: Not present in repo.
  - Source leads: ISO 11783 (ISOBUS) DDI lists, John Deere Operations Center field definitions.
- `server/extractor/modules/automotive_registry.py`
  - Reason: No registry list in code (count only). Needs OBD-II + CAN signal dictionary.
  - Field names: Not present in repo.
  - Source leads: SAE J1979 OBD-II PIDs, SAE J1939 SPN lists, ISO 14229 (UDS) service identifiers.
- `server/extractor/modules/broadcast_standards_registry.py`
  - Reason: No registry list in code (count only). Needs SMPTE RP 210 dictionary + GXF/MXF dictionaries.
  - Field names: Not present in repo.
  - Source leads: SMPTE RP 210 metadata dictionary, SMPTE 377M/378M/379M MXF metadata sets, GXF docs.
- `server/extractor/modules/financial_fintech_registry.py`
  - Reason: No registry list in code (count only). Needs regulatory reporting schema.
  - Field names: Not present in repo.
  - Source leads: XBRL taxonomy dictionaries (US GAAP/IFRS), OFX/QIF specs, SWIFT MT/MX fields.
- `server/extractor/modules/iptc_newscodes_registry.py`
  - Reason: No registry list in code (count only). Needs IPTC NewsCodes registry data.
  - Field names: Not present in repo.
  - Source leads: IPTC NewsCodes subject/scene/genre lists.
- `server/extractor/modules/legal_compliance_registry.py`
  - Reason: No registry list in code (count only). Needs compliance metadata schema.
  - Field names: Not present in repo.
  - Source leads: EDRM XML fields, Concordance DAT/Summation DII load file specs, FOIA/redaction metadata.
- `server/extractor/modules/physics_registry.py`
  - Reason: No registry list in code (count only). Needs physics experiment schema/field list.
  - Field names: Not present in repo.
  - Source leads: CERN ROOT TTree branch conventions, HepMC event record fields.
- `server/extractor/modules/gis_epsg_registry.py`
  - Reason: Full EPSG list not present in repo; current extraction only detects codes from WKT/PRJ.
  - Field names: Uses `EPSG:{code}` unless code exists in `get_epsg_code_name`.
  - Source leads: EPSG Geodetic Parameter Dataset (official registry tables).

## Registries With Partial Field Lists (Needs Expansion)
- `server/extractor/modules/engineering_cad_registry.py`
  - Reason: Contains a starter list for DXF/IFC/Revit but is not exhaustive.
  - Field names: Basic DXF header/group codes + IFC Pset samples + Revit project info.
  - Source leads: Full DXF group code tables, IFC property set definitions (Pset*), STEP/IGES metadata sections.
- `server/extractor/modules/cve_vulnerability_registry.py`
  - Reason: Uses local CVE field definitions and pattern scan; full CVE/CWE registries still needed.
  - Field names: CVE field definitions from `scripts/inventory_cybersecurity.py`.
  - Source leads: NVD CVE JSON feeds, MITRE CWE lists.
- `server/extractor/modules/gaming_asset_registry.py`
  - Reason: Uses local gaming inventory list and basic glTF/Unity parsing; full engine schemas remain.
  - Field names: Gaming field lists from `scripts/inventory_gaming.py`.
  - Source leads: Unity/Unreal asset schema docs, glTF schema/extensions, FBX property tables.

## Registries With Field Lists But Missing Parsers
Registry data exists, but we need format-specific parsers to emit full raw registry dumps.

- `server/extractor/modules/fonts_complete_registry.py`
  - Reason: Basic SFNT tables are parsed now, but deeper glyph/feature extraction still needs a full OpenType parser (e.g., GSUB/GPOS lookup parsing).
  - Field names: `font_family_name`, `font_subfamily_name`, `font_full_name`, etc. (basic tables only).

## Pending Normalization / Coverage Expansion (Open Standards)
- `server/extractor/modules/web_social_metadata.py`
  - Reason: Registry now includes raw `og:*` and `twitter:*` plus normalized keys, but Schema.org properties are still only partially normalized.
  - Field names: `schema_*` is partial; needs explicit mapping to `schema.org:*` properties and type-specific coverage.
- `server/extractor/modules/geospatial_gis.py`
  - Reason: Format-specific extraction exists, but outputs are not fully normalized against registry fields for GeoJSON/KML/GML/GeoPackage.
  - Field names: Existing `geospatial_*` keys; needs stable mapping to registry keys for consistent counts.
- `server/extractor/modules/email_metadata.py`
  - Reason: Registry ingest is added, but DMARC/SPF/DKIM subfield parsing is shallow.
  - Field names: `email_*` extracted; parse DKIM/SPF/DMARC into structured subfields for higher coverage.
- `server/extractor/modules/gaming_asset_registry.py`
  - Reason: glTF/GLB/Unity/FBX basic parsing added; Unreal `.uasset` needs actual property parsing and Unity class IDs need deeper coverage.
  - Field names: `gltf.*`, `unity.meta.*`, `fbx.*`; needs engine-specific schemas.

## Pending Sample Validation (Needed for Reliable Tests)
- `docs/REQUIRED_SAMPLE_FILES.md`
  - GeoJSON FeatureCollection, KML with styles, GML with srsName, GeoPackage with geometry tables.
  - HTML + local web manifest JSON (for manifest parsing).
  - glTF/GLB with multiple scenes/nodes/materials.

## Stub Extractors (No Implementation Yet)
These extractors are currently placeholders; a full implementation needs a real schema and sample files.

- `server/extractor/modules/emerging_technology_ultimate_advanced_extension_iii.py`
  - Reason: Placeholder for quantum/DNA storage; no field list yet.
  - Field names: Not present in repo (count only).
- `server/extractor/modules/forensic_security_ultimate_advanced_extension_ii.py`
  - Reason: Placeholder extension; no field list yet.
  - Field names: Not present in repo.
- `server/extractor/modules/makernotes_ultimate_advanced_extension_iii.py`
  - Reason: Placeholder extension; no field list yet.
  - Field names: Not present in repo.
- `server/extractor/modules/pdf_office_ultimate_advanced_extension_ii.py`
  - Reason: Placeholder extension; no field list yet.
  - Field names: Not present in repo.
- `server/extractor/modules/scientific_dicom_fits_ultimate_advanced_extension_ii.py`
  - Reason: Placeholder extension; no field list yet.
  - Field names: Not present in repo.
- `server/extractor/modules/scientific_dicom_fits_ultimate_advanced_extension_xxiii.py`
  - Reason: Placeholder extension; no field list yet.
  - Field names: Not present in repo.
- `server/extractor/modules/scientific_dicom_fits_ultimate_advanced_extension_xxiv.py`
  - Reason: Placeholder extension; no field list yet.
  - Field names: Not present in repo.
- `server/extractor/modules/scientific_dicom_fits_ultimate_advanced_extension_xxv.py`
  - Reason: Placeholder extension; no field list yet.
  - Field names: Not present in repo.
- `server/extractor/modules/scientific_dicom_fits_ultimate_advanced_extension_xxvi.py`
  - Reason: Placeholder extension; no field list yet.
  - Field names: Not present in repo.
- `server/extractor/modules/video_professional_ultimate_advanced_extension_ii.py`
  - Reason: Placeholder extension; no field list yet.
  - Field names: Not present in repo.
