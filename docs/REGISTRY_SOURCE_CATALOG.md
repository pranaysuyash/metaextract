# Registry Source Catalog

This catalog lists the primary external sources for each placeholder or partial registry.
It is intended as a long-term reference for where to pull canonical field lists and
metadata dictionaries. No external sources were fetched during this update.

## Status Legend
- Planned: Source identified, not pulled yet.
- Restricted: Source exists but may require membership, licensing, or API keys.

## Aerospace
- Module: `server/extractor/modules/aerospace_registry.py`
- Targets: ARINC 429/717, flight data recorder parameters, CCSDS telemetry.
- Sources (Planned):
  - ARINC 429 and ARINC 717 label lists (ARINC specifications).
  - CCSDS Blue Books (packet telemetry and parameter dictionaries).
- Notes: ARINC documents are often licensed; CCSDS docs are publicly available.

## Agriculture
- Module: `server/extractor/modules/agriculture_registry.py`
- Targets: ISOBUS (ISO 11783) DDI list, precision farming logs, drone spectral data.
- Sources (Planned):
  - ISO 11783 DDI lists and Data Dictionary.
  - John Deere Operations Center field definitions.
  - AgGateway and ISOXML references.
- Notes: ISO specs are licensed; API fields often require developer access.

## Automotive
- Module: `server/extractor/modules/automotive_registry.py`
- Targets: SAE J1939 SPNs, SAE J1979 OBD-II PIDs, ISO 14229 UDS services.
- Sources (Planned):
  - SAE J1979 (OBD-II PID list).
  - SAE J1939 SPN registry.
  - ISO 14229 (UDS services and DIDs).
- Notes: SAE and ISO documents are licensed (Restricted).

## Broadcast Standards
- Module: `server/extractor/modules/broadcast_standards_registry.py`
- Targets: SMPTE RP 210 dictionary, MXF/GXF metadata sets.
- Sources (Planned):
  - SMPTE RP 210 metadata dictionary (Restricted).
  - SMPTE 377M/378M/379M MXF metadata sets.
  - GXF (General eXchange Format) documentation.
- Notes: SMPTE documents are typically paywalled (Restricted).

## CVE / Vulnerability
- Module: `server/extractor/modules/cve_vulnerability_registry.py`
- Targets: CVE/CWE fields and schemas.
- Sources (Planned):
  - NVD CVE JSON schema and feeds.
  - MITRE CWE list and XML schema.
- Local inventory sources:
  - `scripts/inventory_cybersecurity.py` (CVE field definitions list).
- Notes: Publicly accessible; rate limits may apply.

## Engineering CAD (Partial List Present)
- Module: `server/extractor/modules/engineering_cad_registry.py`
- Targets: Full DXF group codes, IFC property sets, STEP/IGES metadata.
- Sources (Planned):
  - Autodesk DXF Reference (R2018 or latest).
  - IFC4 and IFC2x3 property set definitions.
  - STEP AP203/AP214/AP242 metadata.
  - IGES 5.3 specification.
- Notes: Some specs are public; some may require registration.

## Financial / FinTech
- Module: `server/extractor/modules/financial_fintech_registry.py`
- Targets: XBRL taxonomies, OFX/QIF, SWIFT.
- Sources (Planned):
  - XBRL US GAAP taxonomy dictionaries.
  - IFRS taxonomy dictionaries.
  - OFX 2.x specification fields.
  - SWIFT MT/MX message field definitions (Restricted).
- Notes: SWIFT specs are typically restricted.

## Gaming Asset
- Module: `server/extractor/modules/gaming_asset_registry.py`
- Targets: Unity .meta keys, Unreal asset properties, glTF extensions, FBX properties.
- Sources (Planned):
  - Unity .meta YAML keys and ClassID reference.
  - Unreal Engine asset serialization and property tables.
  - glTF 2.0 schema and extension registry.
  - FBX SDK property definitions.
- Local inventory sources:
  - `scripts/inventory_gaming.py` (Unity and general gaming field lists).
- Notes: Some engine docs are public; detailed asset formats may require SDKs.

## IPTC NewsCodes
- Module: `server/extractor/modules/iptc_newscodes_registry.py`
- Targets: Subject/Scene/Genre codes.
- Sources (Planned):
  - IPTC NewsCodes registry (subject, scene, genre, etc.).
- Notes: IPTC NewsCodes are publicly documented; license terms apply.

## Legal Compliance
- Module: `server/extractor/modules/legal_compliance_registry.py`
- Targets: Load file fields and e-discovery schemas.
- Sources (Planned):
  - Concordance DAT load file fields.
  - Summation DII format fields.
  - EDRM XML schemas.
  - FOIA redaction metadata conventions.
- Notes: Some formats are vendor-specific; details may be partial in public docs.

## Physics / HEP
- Module: `server/extractor/modules/physics_registry.py`
- Targets: ROOT, HepMC, detector calibration fields.
- Sources (Planned):
  - CERN ROOT reference guide (TTree branches/metadata).
  - HepMC event record fields.
  - LHC experiment data model documentation (ATLAS/CMS).
- Notes: Publicly documented; requires curation of field lists.

## GIS / EPSG
- Module: `server/extractor/modules/gis_epsg_registry.py`
- Targets: Full EPSG Geodetic Parameter Dataset list.
- Sources (Planned):
  - EPSG Geodetic Parameter Dataset (official registry tables).
- Notes: EPSG dataset has usage terms; requires ingestion of the official table files.

## GIS / Geospatial (Open Standards)
- Module: `server/extractor/modules/gis_geospatial_registry.py`
- Targets: GeoTIFF, KML, GML, Shapefile, NetCDF CF metadata field lists.
- Sources (Planned):
  - GeoTIFF Specification
  - OGC KML 2.3
  - OGC GML 3.2.1
  - ESRI Shapefile Technical Specification
  - NetCDF CF Conventions
- Local inventory sources:
  - `scripts/inventory_geospatial.py` (open-standard field lists).

## Stub Extension Modules (No Registry Yet)
- Modules:
  - `server/extractor/modules/emerging_technology_ultimate_advanced_extension_iii.py`
  - `server/extractor/modules/forensic_security_ultimate_advanced_extension_ii.py`
  - `server/extractor/modules/makernotes_ultimate_advanced_extension_iii.py`
  - `server/extractor/modules/pdf_office_ultimate_advanced_extension_ii.py`
  - `server/extractor/modules/scientific_dicom_fits_ultimate_advanced_extension_ii.py`
  - `server/extractor/modules/scientific_dicom_fits_ultimate_advanced_extension_xxiii.py`
  - `server/extractor/modules/scientific_dicom_fits_ultimate_advanced_extension_xxiv.py`
  - `server/extractor/modules/scientific_dicom_fits_ultimate_advanced_extension_xxv.py`
  - `server/extractor/modules/scientific_dicom_fits_ultimate_advanced_extension_xxvi.py`
  - `server/extractor/modules/video_professional_ultimate_advanced_extension_ii.py`
- Sources (Planned):
  - To be assigned once domain scope is confirmed (each module is a placeholder).
- Notes: These modules need a defined schema before sourcing.

## Web Standards (Open)
- Module: `server/extractor/modules/web_social_metadata.py`
- Targets: Open Graph, Twitter Cards, Schema.org, Web App Manifest, PWA fields, security headers.
- Sources (Planned):
  - Open Graph Protocol
  - Twitter Cards documentation
  - Schema.org vocabulary
  - Web App Manifest spec
  - PWA and security header references
- Local inventory sources:
  - `scripts/inventory_web_standards.py` (open-standard field lists).

## Email Standards (Open)
- Module: `server/extractor/modules/email_metadata.py`
- Targets: RFC 5322 headers, MIME fields, DKIM/SPF/DMARC, MBOX metadata.
- Sources (Planned):
  - RFC 5322, RFC 2045/2049, RFC 6376, RFC 7208, RFC 7489.
- Local inventory sources:
  - `scripts/inventory_email.py` (open-standard field lists).
